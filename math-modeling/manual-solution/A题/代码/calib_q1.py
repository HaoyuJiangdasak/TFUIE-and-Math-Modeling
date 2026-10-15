# -*- coding: utf-8 -*-
"""标定：问题1 水分浓度的传质边界条件形式"""
import numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyl import Cyl1D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d1 = pd.read_excel(os.path.join(ROOT, '附件', '附件1.xlsx'))
tt = d1.iloc[:, 0].to_numpy(float)
Xa_tab = d1.iloc[:, 2].to_numpy(float)


def solve(hm=8e-7, dscale=1.0, N=500, dt=1.0, nsteps=1800, bc='X'):
    s = Cyl1D(N=N, R=0.02)
    ng = N + 1
    X = np.full(ng, 2.55)
    snap = {}
    for n in range(1, nsteps + 1):
        t = n * dt
        Xac = np.interp(t, tt, Xa_tab)
        D = dscale * 7e-9 * np.exp(-0.89 * X)
        if bc == 'X':
            X = s.moisture_step(X, D, hm, Xac, dt)
        elif bc == 'dirichlet':
            Xn = s.moisture_step(X, D, 1e9, Xac, dt)
            X = Xn
        if t in (100, 300, 600, 900, 1200, 1500, 1800):
            snap[t] = X[s.out_idx][[0, 5, 10, 15, 20]]
    return snap


ref = np.load(os.path.join(ROOT, '结果', 'tab2.npy'))
print('ref   :')
for row in ref:
    print(int(row[0]), row[1:])
print()
for hm in [8e-7, 4e-7, 2e-7, 1e-7, 5e-8]:
    sn = solve(hm=hm)
    err = max(abs(sn[int(r[0])][4] - r[5]) for r in ref)
    print('hm=%.1e  surf: ' % hm, ['%.4f' % sn[int(r[0])][4] for r in ref], ' maxerr=%.4f' % err)
print()
for ds in [0.1, 0.25, 0.5, 1.0]:
    sn = solve(hm=8e-7, dscale=ds)
    err = max(abs(sn[int(r[0])][4] - r[5]) for r in ref)
    print('Dscale=%.2f  surf: ' % ds, ['%.4f' % sn[int(r[0])][4] for r in ref], ' maxerr=%.4f' % err)
