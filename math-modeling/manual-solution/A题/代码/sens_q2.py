# -*- coding: utf-8 -*-
"""
问题2 模型参数灵敏度分析 + GRA / DEA / FA / (FCE 模糊综合评价)
把 12 个影响因素各做 ±1 档扰动，构成 25 个"情景"(DMU)，计算 6 个响应指标，
再分别做灰色关联分析、因子分析、数据包络分析、模糊综合评价。
"""
import numpy as np, pandas as pd, os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyl import Cyl1D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, '结果')

_d1 = pd.read_excel(os.path.join(ROOT, '附件', '附件1.xlsx'))
TT = _d1.iloc[:, 0].to_numpy(float)
TA_TAB = _d1.iloc[:, 1].to_numpy(float)
XA_TAB = _d1.iloc[:, 2].to_numpy(float)


def p_sat(Tc):
    return 610.78 * np.exp(17.2694 * Tc / (Tc + 237.3))


def w_sat(Tc):
    ps = p_sat(Tc)
    return 0.622 * ps / (101325.0 - ps)


def wet_bulb(Ta, wa):
    if wa >= w_sat(Ta):
        return Ta
    f = lambda Tw: w_sat(Tw) - ((2501 - 2.326 * Tw) * wa - 1.006 * (Ta - Tw)) / \
                   (2501 + 1.86 * Ta - 4.186 * Tw)
    lo, hi = -40.0, Ta
    if f(lo) * f(hi) > 0:
        return Ta
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ---------- 可调参数的通用求解器 ----------
def solve_p(p, dt=8.0, N=200, tmax=345600.0, xcrit=0.15, rec_dt=1800.0):
    R = 0.02 * p['R']
    X0 = 2.55 * p['X0']
    dTa = p['Ta']
    xa_k = p['Xa']
    h = 25.0 * p['h']
    hm = 8e-7 * p['hm']
    rho_k, cp_k, lam_k, D_k, L_k = p['rho'], p['cp'], p['lam'], p['D'], p['L']
    tsw = 14400.0 * p['tsw']

    s = Cyl1D(N=N, R=R)
    ng = N + 1
    X = np.full(ng, X0)
    T = np.full(ng, 28.0)
    oi = np.array(s.out_idx)
    nstep = int(round(tmax / dt))
    rec_every = max(1, int(round(rec_dt / dt)))
    hr = [0.5, 1, 2, 3, 4, 6]
    out = {}
    rec_t, rec_T, rec_X = [], [], []
    tend = None
    heat = 0.0
    for n in range(1, nstep + 1):
        t = n * dt
        if t <= tsw:
            Tac = float(np.interp(t, TT, TA_TAB)) + dTa
            Xac = float(np.interp(t, TT, XA_TAB)) * xa_k
        else:
            Tac, Xac = 50.0 + dTa, 0.05 * xa_k
        TK = T + 273.15
        D = D_k * 2.4e-3 * np.exp(-0.45 / X) * np.exp(-3850.0 / TK)
        Xstar = np.maximum(s.moisture_step(X, D, hm, Xac, dt), 0.0)
        lam = lam_k * (0.21 + 0.38 * X / (1.0 + X))
        cp = cp_k * (1450.0 + 2736.0 * X / (1.0 + X))
        rc = rho_k * (650.0 + 128.0 * X) * cp
        L = L_k * (2.501e6 - 2.361e3 * np.atleast_1d(T))
        dTl = L * (Xstar - X) / ((1.0 + X) * cp)
        T1 = s.heat_step(T, lam, rc, h, Tac, dTl, dt)
        T0_ = s.heat_step(T, lam, rc, h, Tac, np.zeros(ng), dt)
        bl = T1 - T0_
        Twb = wet_bulb(Tac, Xac)
        with np.errstate(divide='ignore', invalid='ignore'):
            ratio = np.where(bl < -1e-12, (Twb - T0_) / bl, np.inf)
        xi = max(0.0, min(1.0, float(np.nanmin(ratio))))
        X = X + xi * (Xstar - X)
        T = T0_ + xi * bl
        # 累计换热量（自烘房取得的热量）J/m
        heat += h * (Tac - T[ng - 1]) * 2 * np.pi * R * dt
        if (n % rec_every == 0):
            rec_t.append(t); rec_T.append(T[oi].copy()); rec_X.append(X[oi].copy())
        for hh in hr:
            if abs(t - hh * 3600) < dt / 2 and hh not in out:
                out[hh] = (T[oi][[0, 10, 20]].copy(), X[oi][[0, 10, 20]].copy())
        if tend is None and X.max() < xcrit:
            tend = t
            break
    if tend is None:
        tend = tmax
    rec_t = np.array(rec_t); rec_T = np.array(rec_T); rec_X = np.array(rec_X)
    r = np.array([0.1 * k for k in range(21)]) / 100.0
    w21 = np.concatenate([[r[0] ** 2 / 2], [(r[i] + 0.0005) ** 2 - (r[i] - 0.0005) ** 2 for i in range(1, 20)],
                          [r[20] ** 2 - (r[20] - 0.0005) ** 2]]) / 2
    dr = R / N
    rf = np.arange(ng) * dr
    wf = np.empty(ng)
    wf[0] = (dr / 2) ** 2 / 2
    wf[1:N] = ((rf[1:N] + dr / 2) ** 2 - (rf[1:N] - dr / 2) ** 2) / 2
    wf[N] = (rf[N] ** 2 - (rf[N] - dr / 2) ** 2) / 2
    Xavg = (rec_X * w21).sum(axis=1) / w21.sum()
    out['tend_h'] = tend / 3600.0
    out['Xc_3h'] = out[3][1][0]; out['Xs_3h'] = out[3][1][2]
    out['Tc_3h'] = out[3][0][0]; out['Ts_3h'] = out[3][0][2]
    out['v6'] = (X0 - Xavg[np.argmin(abs(rec_t - 21600))]) / 6.0   # 前6h平均干燥速率
    out['E'] = heat / 1e6                                          # MJ/m
    out['Xavg_end'] = float((X * wf).sum() / wf.sum())
    out['rec_t'] = rec_t; out['rec_X'] = rec_X; out['rec_T'] = rec_T
    return out


FACTORS = [
    ('烘房温度 T_a', 'Ta', 3.0, '°C 偏移'),
    ('空气水分浓度 X_a', 'Xa', 0.20, '相对'),
    ('对流换热系数 h', 'h', 0.20, '相对'),
    ('对流传质系数 h_m', 'hm', 0.20, '相对'),
    ('初始含水率 X_0', 'X0', 0.10, '相对'),
    ('药材半径 R', 'R', 0.10, '相对'),
    ('密度系数 ρ', 'rho', 0.10, '相对'),
    ('比热系数 c_p', 'cp', 0.10, '相对'),
    ('热导率系数 λ', 'lam', 0.10, '相对'),
    ('扩散系数前因子 D_0', 'D', 0.20, '相对'),
    ('汽化潜热 L', 'L', 0.10, '相对'),
    ('预热阶段时长 t_sw', 'tsw', 0.20, '相对'),
]
BASE = dict(Ta=0.0, Xa=1.0, h=1.0, hm=1.0, X0=1.0, R=1.0, rho=1.0, cp=1.0, lam=1.0, D=1.0, L=1.0, tsw=1.0)


def build_scenarios():
    sc = [('基准', dict(BASE))]
    for nm, key, amp, kind in FACTORS:
        if kind == '相对':
            for sgn, lb in [(1, '+'), (-1, '-')]:
                q = dict(BASE); q[key] = 1.0 + sgn * amp
                sc.append((f'{nm} {lb}{amp*100:.0f}%', q))
        else:
            for sgn, lb in [(1, '+'), (-1, '-')]:
                q = dict(BASE); q[key] = sgn * amp
                sc.append((f'{nm} {lb}{amp:.0f}°C', q))
    return sc


if __name__ == '__main__':
    sc = build_scenarios()
    print('情景数 =', len(sc))
    t0 = time.time()
    rows = []
    for i, (nm, p) in enumerate(sc):
        o = solve_p(p)
        rows.append(dict(情景=nm, tend_h=o['tend_h'], Xc_3h=o['Xc_3h'], Xs_3h=o['Xs_3h'],
                         Tc_3h=o['Tc_3h'], Ts_3h=o['Ts_3h'], v6=o['v6'], E=o['E']))
        print('%2d/%-22s tend=%.2fh Xc3h=%.4f Xs3h=%.4f Tc3h=%.2f E=%.3f  (%.1fs)' %
              (i, nm, o['tend_h'], o['Xc_3h'], o['Xs_3h'], o['Tc_3h'], o['E'], time.time() - t0))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES, 'q2_sensitivity.csv'), index=False, encoding='utf-8-sig')
    print(df.to_string(index=False))
