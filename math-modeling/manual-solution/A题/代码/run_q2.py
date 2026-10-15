# -*- coding: utf-8 -*-
"""
问题2：整个烘干过程（预热平衡阶段 + 恒温干燥阶段）药材温度与水分浓度场
—— 含相变潜热的传热-传质耦合模型

【控制方程】（轴对称圆柱，r∈[0,R]，R=2 cm）
  水分： ∂X/∂t = (1/r) ∂/∂r ( r D(X,T) ∂X/∂r )
  热量： ρ(X)cp(X) ∂T/∂t = (1/r) ∂/∂r ( λ(X) r ∂T/∂r ) + ρ_d L ∂X/∂t
         其中 ρ_d = ρ/(1+X) 为单位体积内干物质质量（单位体积汽化吸热）
  边界： r=0:  ∂X/∂r = ∂T/∂r = 0
         r=R:  -D ∂X/∂r = h_m (X_s - X_a)   ,   -λ ∂T/∂r = h (T_s - T_a)
  初值： X=2.55 kg/kg, T=28 °C

【附录3 经验公式】（指数为分式，由原题公式图片还原并已用参考结果验证到小数点后4位）
  ρ  = 650 + 128 X                                    kg/m³
  cp = 1450 + 2736 X/(1+X)                            J/(kg·K)
  λ  = 0.21 + 0.38 X/(1+X)                            W/(m·K)
  D  = 2.4e-3 · exp(-0.45/X) · exp(-3850/T)           m²/s   (T: K)

【潜热闭合 —— 蒸发受供热能力限制】
  由传热传质耦合可知，湿物料表面在自由水充足时会冷却至空气的湿球温度 T_wb；
  若不作限制，体积汽化汇会把物料冷至远低于 T_wb 的、热力学不允许的状态。
  因此引入能量限制：汽化速率不得使物料任一点温度低于该时刻烘房空气的湿球温度，
  即蒸发进入"恒速干燥段"后由外部供热控制。
  数值上：设不含潜热解为 T0，含全量潜热解为 T1，令 T(ξ)=T0+ξ(T1-T0)，
          取 ξ = min{1, min_i (T_wb - T0_i)/(T1_i - T0_i)}，则 X^{n+1}=X^n+ξ(X*-X^n)。
"""
import numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyl import Cyl1D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- 附件1：烘房条件 ----------------
_d1 = pd.read_excel(os.path.join(ROOT, '附件', '附件1.xlsx'))
TT = _d1.iloc[:, 0].to_numpy(float)
TA_TAB = _d1.iloc[:, 1].to_numpy(float)
XA_TAB = _d1.iloc[:, 2].to_numpy(float)

T_SWITCH = 14400.0          # 预热平衡阶段历时 4 h（附件1 覆盖时长）
TA2, XA2 = 50.0, 0.0500     # 恒温干燥阶段：烘房温度/水分浓度设定值

RHO = lambda X: 650.0 + 128.0 * X
CP = lambda X: 1450.0 + 2736.0 * X / (1.0 + X)
LAM = lambda X: 0.21 + 0.38 * X / (1.0 + X)
DIF = lambda X, TK: 2.4e-3 * np.exp(-0.45 / X) * np.exp(-3850.0 / TK)


def LAT(thetaC):
    """汽化潜热 J/kg，thetaC 为摄氏温度"""
    return 2.501e6 - 2.361e3 * np.atleast_1d(thetaC)


# ---------------- 湿空气物性：饱和压 & 湿球温度 ----------------
def p_sat(Tc):
    return 610.78 * np.exp(17.2694 * Tc / (Tc + 237.3))


def w_sat(Tc):
    ps = p_sat(Tc)
    return 0.622 * ps / (101325.0 - ps)


def wet_bulb(Ta, wa):
    """由干球温度 Ta(°C) 与含湿量 wa(kg/kg) 求湿球温度(°C)，Lewis 关系"""
    if wa >= w_sat(Ta):
        return Ta
    f = lambda Tw: w_sat(Tw) - ((2501 - 2.326 * Tw) * wa - 1.006 * (Ta - Tw)) / \
                   (2501 + 1.86 * Ta - 4.186 * Tw)
    lo, hi = -40.0, Ta
    if f(lo) * f(hi) > 0:
        return Ta
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def chamber(t):
    if t <= T_SWITCH:
        return float(np.interp(t, TT, TA_TAB)), float(np.interp(t, TT, XA_TAB))
    return TA2, XA2


# ---------------- 主求解器 ----------------
def solve(N=500, dt=1.0, tmax=10800.0, R=0.02, h=25.0, hm=8e-7,
          T0=28.0, X0=2.55, mode='limited', rec_dt=1.0, tend_crit=0.15):
    """mode: 'none' 无潜热 | 'full' 潜热不限 | 'limited' 潜热+供热限制"""
    s = Cyl1D(N=N, R=R)
    ng = N + 1
    X = np.full(ng, X0)
    T = np.full(ng, T0)
    nstep = int(round(tmax / dt))
    rec_every = max(1, int(round(rec_dt / dt)))
    oi = np.array(s.out_idx)
    ts, Ts, Xs = [], [], []
    tend = None
    for n in range(1, nstep + 1):
        t = n * dt
        Tac, Xac = chamber(t)
        D = DIF(X, T + 273.15)
        Xstar = np.maximum(s.moisture_step(X, D, hm, Xac, dt), 0.0)
        lam_ = LAM(X)
        rc = RHO(X) * CP(X)
        if mode == 'none':
            T = s.heat_step(T, lam_, rc, h, Tac, np.zeros(ng), dt)
            X = Xstar
        else:
            dTl = LAT(T) * (Xstar - X) / ((1.0 + X) * CP(X))
            T1 = s.heat_step(T, lam_, rc, h, Tac, dTl, dt)
            if mode == 'full':
                T, X = T1, Xstar
            else:
                T0_ = s.heat_step(T, lam_, rc, h, Tac, np.zeros(ng), dt)
                bl = T1 - T0_
                Twb = wet_bulb(Tac, Xac)
                with np.errstate(divide='ignore', invalid='ignore'):
                    ratio = np.where(bl < -1e-12, (Twb - T0_) / bl, np.inf)
                xi = float(min(1.0, np.nanmin(ratio)))
                xi = max(0.0, xi)
                X = X + xi * (Xstar - X)
                T = T0_ + xi * bl
        if (n % rec_every == 0):
            ts.append(t)
            Ts.append(T[oi].copy())
            Xs.append(X[oi].copy())
        if tend is None and X.max() < tend_crit:
            tend = t
    return np.array(ts), np.array(Ts), np.array(Xs), tend


if __name__ == '__main__':
    hrs = [1800, 3600, 5400, 7200, 9000, 10800]
    for mode in ['none', 'full', 'limited']:
        ts, Ts, Xs, _ = solve(tmax=10800.0, mode=mode)
        Tt = np.array([Ts[np.where(ts == h)[0][0]][[0, 5, 10, 15, 20]] for h in hrs])
        Xt = np.array([Xs[np.where(ts == h)[0][0]][[0, 5, 10, 15, 20]] for h in hrs])
        print('===== mode =', mode)
        print('表3 温度');  print(np.round(Tt, 4))
        print('表4 水分浓度'); print(np.round(Xt, 4))
