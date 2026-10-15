# -*- coding: utf-8 -*-
"""
2026 CUMCM A题《药材的烘干问题》数值求解器  (v2 优化版)

圆柱(径向一维) 热传导 + 水分扩散 耦合模型，有限体积/有限差分法（归一化坐标 xi=r/R(t)）。

与 v1 的关键差异
----------------
1. 【修正】移动边界(问题4)去除"伪对流项"。
   v1 由欧拉方程 ∂C/∂t|_r = (1/r)∂_r(rD∂_rC) 直接做坐标变换，得到一个
   对流项 (xi*dRdt/R)∂C/∂xi。但对"干基含水率 X"（水/绝干物料）而言，空间
   守恒方程含固相牵连速度 v_s：
        ∂X/∂t + v_s ∂X/∂r = (1/r)∂_r(r D ∂X/∂r)
   在仿射(均匀)收缩 r = xi*R(t) 下 v_s = xi*dR/dt，相对速度 (v_s - xi*dR/dt)/R ≡ 0，
   对流项恒为零。v1 漏掉固相牵连速度、只保留网格速度，等价于让含水率
   "随网格收缩被凭空浓缩"，会系统性拉长烘干时间（+约3%）。
   本版去掉该项：∂X/∂t|_xi = (1/(R^2 xi))∂_xi(xi D ∂_xi X)，与固定域同形，R=R(t)。

2. 【性能】物性与右端项全部向量化(NumPy)，并向 BDF 提供带状 Jacobian 稀疏结构，
   使 N=641/801 的高分辨率网格在可接受时间内完成。

3. 【精度】R(t) 用 PCHIP 保形插值(单调保持，无虚假振荡)；空气环境用附件1
   线性插值 + 恒温段(50 ℃ / 0.05 kg/kg)。

4. 【输出】问题4 输出采用"物质坐标" r0 = xi*R0 （结果模板最后一列为"药材表面"）。
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix
from scipy.interpolate import PchipInterpolator
import openpyxl
import os

# ---------------- 常数 ----------------
R0 = 0.02        # 初始半径 m
T0 = 28.0        # 初始温度 °C
C0 = 2.55        # 初始干基含水率 kg/kg
h  = 25.0        # 对流换热系数 W/(m^2 K)
hm = 8e-7        # 对流传质系数 m/s

T_HOLD, C_HOLD = 50.0, 0.05   # 恒温干燥阶段烘房环境
T_SWITCH = 14400.0            # 预热平衡阶段结束时刻 s (=附件1末时刻)

# ---------------- 物性参数(向量化) ----------------
def props(mode, C, T_C):
    """返回 rho, cp, k, D —— 支持标量/数组"""
    C = np.asarray(C, float)
    Tk = np.asarray(T_C, float) + 273.15
    if mode == 2:          # 附录2 (问题1)
        z = np.zeros_like(C)
        return (820.0 + z, 2600.0 + z, 0.36 + z, 7e-9 * np.exp(-0.89 / C))
    if mode == 3:          # 附录3 (问题2、3)
        return (650.0 + 128.0 * C,
                1450.0 + 2736.0 * C / (C + 1.0),
                0.21 + 0.38 * C / (C + 1.0),
                2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / Tk))
    if mode == 4:          # 附录4 (问题4)
        return (760.0 + 90.0 * C,
                1850.0 + 2150.0 * C / (C + 1.0),
                0.12 + 0.20 * C / (C + 1.0),
                4.2e-4 * np.exp(-0.30 / C) * np.exp(-3850.0 / Tk))
    raise ValueError("unknown mode")


# ---------------- 附件数据 ----------------
BASE = os.path.dirname(os.path.abspath(__file__))
ATT  = os.path.join(BASE, "附件")

_wb1 = openpyxl.load_workbook(os.path.join(ATT, "附件1.xlsx"), data_only=True)
_ws1 = _wb1["Sheet1"]
t1, Ta, Ca = [], [], []
for r in range(2, _ws1.max_row + 1):
    t1.append(_ws1.cell(r, 1).value)
    Ta.append(_ws1.cell(r, 2).value)
    Ca.append(_ws1.cell(r, 3).value)
t1 = np.array(t1, float); Ta = np.array(Ta, float); Ca = np.array(Ca, float)

_wb2 = openpyxl.load_workbook(os.path.join(ATT, "附件2.xlsx"), data_only=True)
_ws2 = _wb2["Sheet1"]
t2, Rad = [], []
for r in range(2, _ws2.max_row + 1):
    t2.append(_ws2.cell(r, 1).value)
    Rad.append(_ws2.cell(r, 2).value)
t2 = np.array(t2, float); Rad = np.array(Rad, float)   # Rad 单位 cm

# --- 半径插值器：PCHIP(保形) ；线性备用 ---
_PCHIP_R = PchipInterpolator(t2, Rad / 100.0, extrapolate=True)
R_MODE = "pchip"          # "pchip" 或 "linear"


def Tair(t):
    """烘房温度 °C：0~14400 s 用附件1线性插值，之后恒温 50 °C"""
    t = np.asarray(t, float)
    return np.where(t <= T_SWITCH, np.interp(t, t1, Ta), T_HOLD)


def Cair(t):
    """烘房水分浓度 kg/kg：0~14400 s 附件1插值，之后恒 0.05"""
    t = np.asarray(t, float)
    return np.where(t <= T_SWITCH, np.interp(t, t1, Ca), C_HOLD)


def Rfunc(t):
    """半径(米)"""
    tc = np.clip(t, t2[0], t2[-1])
    if R_MODE == "pchip":
        v = np.asarray(_PCHIP_R(tc), float)
    else:
        v = np.interp(tc, t2, Rad) / 100.0
    return v


# ---------------- 统一 FVM/FD 离散 (xi = r/R) ----------------
def make_rhs(N, mode, moving=False):
    """顶点式有限体积法：节点 xi_j=j*dxi (j=0..N-1, xi_{N-1}=1)，
    控制体为 [xi_{j-1/2}, xi_{j+1/2}]（中心/表面为半单元），
    守恒形式 d/dt∫C·xi dxi = (1/R²)[xi·D·∂_xi C]_面 ，在面处严格施加第三类边界。"""
    dxi = 1.0 / (N - 1)
    xi = np.linspace(0.0, 1.0, N)
    xif = (np.arange(N - 1) + 0.5) * dxi      # 内部面 xi_{i+1/2}
    # 表面单元体积权重 ∫_{1-dxi/2}^{1} xi dxi = dxi/2 - dxi^2/8
    vol_surf = 0.5 * dxi * (1.0 - 0.25 * dxi)

    def rhs(t, y):
        T = y[:N]; C = y[N:]
        R = float(Rfunc(t)) if moving else R0
        Ta_ = float(Tair(t)); Ca_ = float(Cair(t))
        invR2 = 1.0 / (R * R)

        rho, cp, kk, D = props(mode, C, T)
        Cf = 0.5 * (C[:-1] + C[1:]); Tf = 0.5 * (T[:-1] + T[1:])
        _, _, kf, Df = props(mode, Cf, Tf)     # 内部面物性(算术平均)

        dT = np.empty(N); dC = np.empty(N)

        # 内部面通量  q[i] 表示面 xi_{i+1/2} 上的 xi*D*∂_xi(·)
        qT = xif * kf * (T[1:] - T[:-1]) / dxi
        qC = xif * Df * (C[1:] - C[:-1]) / dxi

        # ---- 中心节点 i=0（半单元 [0,dxi/2]，由对称性）----
        dT[0] = 4.0 * kk[0] / (rho[0] * cp[0]) * invR2 / (dxi * dxi) * (T[1] - T[0])
        dC[0] = 4.0 * D[0] * invR2 / (dxi * dxi) * (C[1] - C[0])

        # ---- 内部节点 i=1..N-2 ----
        sl = slice(1, N - 1)
        divT = (qT[1:] - qT[:-1]) / dxi
        divC = (qC[1:] - qC[:-1]) / dxi
        dT[sl] = divT / (xi[sl] * R * R * rho[sl] * cp[sl])
        dC[sl] = divC / (xi[sl] * R * R)

        # ---- 表面节点 i=N-1（半单元 [1-dxi/2, 1]，面通量严格用第三类边界）----
        i = N - 1
        xi_w = 1.0 - 0.5 * dxi
        # 西面(xi_w)：xi*D*∂_xi(·)
        fC_w = xi_w * Df[i - 1] * (C[i] - C[i - 1]) / dxi
        fT_w = xi_w * kf[i - 1] * (T[i] - T[i - 1]) / dxi
        # 东面(xi=1)：xi*D*∂_xi C = -R*hm*(C_s-Ca) ; xi*k*∂_xi T = R*h*(Ta-T_s)
        fC_e = -R * hm * (C[i] - Ca_)
        fT_e = R * h * (Ta_ - T[i])
        dC[i] = (fC_e - fC_w) / (vol_surf * R * R)
        dT[i] = (fT_e - fT_w) / (vol_surf * R * R * rho[i] * cp[i])

        return np.concatenate([dT, dC])

    return rhs


# ---------------- 求解 ----------------
def _banded_sparsity(N):
    """状态向量 [T(N); C(N)] 的 Jacobian 带状稀疏结构"""
    n = 2 * N
    S = lil_matrix((n, n), dtype=float)
    for i in range(N):
        for di in (-1, 0, 1):
            j = i + di
            if 0 <= j < N:
                S[i, j] = 1; S[N + i, N + j] = 1
        # T <-> C 通过物性耦合(同一节点)
        S[i, N + i] = 1; S[N + i, i] = 1
    return S.tocsc()


def solve_problem(mode, t_end, moving=False, N=641, t_eval=None,
                  rtol=1e-7, atol=1e-9, max_step=np.inf, use_sparse=True):
    rhs = make_rhs(N, mode, moving)
    y0 = np.concatenate([np.full(N, T0), np.full(N, C0)])
    if t_eval is None:
        t_eval = np.linspace(0, t_end, 2)
    kw = {}
    if use_sparse and N >= 200:
        kw["jac_sparsity"] = _banded_sparsity(N)
    sol = solve_ivp(rhs, (0.0, t_end), y0, method='BDF', t_eval=t_eval,
                    rtol=rtol, atol=atol, max_step=max_step, **kw)
    if not sol.success:
        raise RuntimeError("solve_ivp failed: " + str(sol.message))
    return sol, N


def extract_profile(sol, N, field, r_cm, moving=False):
    """提取 field('T'或'C') 在指定半径(厘米)处的值 -> (nt, nr) 数组。

    问题4 采用【物质坐标】r0 = xi*R0（该质点 t=0 时到中心的距离），
    因此与固定半径情形形式一致，最后一列即表面 xi=1。
    """
    xi = np.linspace(0, 1, N)
    t = np.asarray(sol.t, float)
    rq = np.asarray(r_cm, float)
    nt = len(t); nr = len(rq)
    out = np.full((nt, nr), np.nan)
    r_phys = xi * R0 * 100.0          # 物质坐标(cm)
    for j in range(nt):
        yv = sol.y[:N, j] if field == 'T' else sol.y[N:, j]
        out[j] = np.interp(rq, r_phys, yv, left=yv[0], right=yv[-1])
    return out


def surface_value(sol, N, field):
    """表面节点(xi=1)的时间序列"""
    return sol.y[(N - 1) if field == 'T' else (N + (N - 1)), :]


def profile_at_time(sol, N, field, tq, r_cm):
    """在任意时刻 tq 处(时间上线性插值)取样 field 在 r_cm(物质坐标 cm) 的值"""
    t = sol.t
    if tq <= t[0]:
        yv = sol.y[:, 0]
    elif tq >= t[-1]:
        yv = sol.y[:, -1]
    else:
        i = int(np.clip(np.searchsorted(t, tq), 1, len(t) - 1))
        w = (tq - t[i - 1]) / (t[i] - t[i - 1])
        yv = (1.0 - w) * sol.y[:, i - 1] + w * sol.y[:, i]
    y = yv[:N] if field == 'T' else yv[N:]
    r_phys = np.linspace(0.0, 1.0, N) * R0 * 100.0
    return np.interp(np.asarray(r_cm, float), r_phys, y)


def crossing_time(sol, N, thresh=0.15):
    """max_over_r C 首次 < thresh 的时刻(线性插值到精确交点)"""
    Cmax = sol.y[N:, :].max(axis=0)
    idx = np.where(Cmax < thresh)[0]
    if len(idx) == 0:
        return np.inf, None
    i1 = int(idx[0])
    if i1 == 0:
        return float(sol.t[0]), i1
    t0, t1_ = sol.t[i1 - 1], sol.t[i1]
    c0, c1 = Cmax[i1 - 1], Cmax[i1]
    tc = t0 + (thresh - c0) * (t1_ - t0) / (c1 - c0)
    return float(tc), i1
