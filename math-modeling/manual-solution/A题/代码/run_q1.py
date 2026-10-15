# -*- coding: utf-8 -*-
"""问题1：预热平衡阶段 —— 用于标定边界条件形式（与 结果/tab1.npy, tab2.npy 对照）"""
import numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyl import Cyl1D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 附件1：烘房温度与水分浓度
d1 = pd.read_excel(os.path.join(ROOT, '附件', '附件1.xlsx'))
tt = d1.iloc[:, 0].to_numpy(float)
Ta_tab = d1.iloc[:, 1].to_numpy(float)
Xa_tab = d1.iloc[:, 2].to_numpy(float)


def Ta_of(t):
    return np.interp(t, tt, Ta_tab)


def Xa_of(t):
    return np.interp(t, tt, Xa_tab)


def run_q1(N=500, dt=1.0, nsteps=1800, latent=False, L=2.26e6,
           rho=820.0, cp=2600.0, lam=0.36, h=25.0, hm=8e-7,
           T0=28.0, X0=2.55, R=0.02, record=True):
    s = Cyl1D(N=N, R=R)
    ng = N + 1
    X = np.full(ng, X0)
    T = np.full(ng, T0)
    rec_t, rec_T, rec_X = [], [], []
    for n in range(1, nsteps + 1):
        t = n * dt
        Tac, Xac = Ta_of(t), Xa_of(t)
        D = 7e-9 * np.exp(-0.89 * X)
        Xn = s.moisture_step(X, D, hm, Xac, dt)
        dX = Xn - X
        if latent:
            dTl = L * dX / ((1.0 + X) * cp)
        else:
            dTl = np.zeros(ng)
        Tn = s.heat_step(T, np.full(ng, lam), np.full(ng, rho * cp), h, Tac, dTl, dt)
        X, T = Xn, Tn
        if record and (n % 100 == 0):
            rec_t.append(t)
            rec_T.append(T[s.out_idx].copy())
            rec_X.append(X[s.out_idx].copy())
    if record:
        return np.array(rec_t), np.array(rec_T), np.array(rec_X)
    return T, X


if __name__ == '__main__':
    ref_T = np.load(os.path.join(ROOT, '结果', 'tab1.npy'))
    ref_X = np.load(os.path.join(ROOT, '结果', 'tab2.npy'))
    for lat in [False, True]:
        t, T, X = run_q1(latent=lat)
        print('=== latent =', lat)
        print('T  (100..1800):')
        print(np.hstack([t[:, None], T]))
        print('X  (100..1800):')
        print(np.hstack([t[:, None], X]))
        print('ref T:'); print(ref_T)
        print('max|dT| =', np.abs(T - ref_T[:, 1:]).max(), ' max|dX| =', np.abs(X - ref_X[:, 1:]).max())
