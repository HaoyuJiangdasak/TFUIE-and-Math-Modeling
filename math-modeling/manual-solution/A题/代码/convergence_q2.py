# -*- coding: utf-8 -*-
"""问题2（含潜热）网格与时间步长无关性验证"""
import numpy as np, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_q2 import solve

if __name__ == '__main__':
    print('--- 网格无关性（dt=0.5 s, 3 h）---')
    ref = None
    for N in [100, 200, 300, 500, 800]:
        ts, Ts, Xs, _ = solve(N=N, dt=0.5, tmax=10800.0, mode='limited', rec_dt=0.5)
        k = np.argmin(abs(ts - 10800.0))
        v = (Xs[k][20], Ts[k][20], Ts[k][0])
        if N == 800:
            ref = np.array(v)
        print('N=%4d  X_表面(3h)=%.6f  T_表面=%.4f  T_中心=%.4f' % (N, v[0], v[1], v[2]))
    print('  收敛值参考(N=800):', ref)

    print('--- 时间步长无关性（N=500, 3 h）---')
    for dt in [0.25, 0.5, 1.0, 2.0, 5.0]:
        ts, Ts, Xs, _ = solve(N=500, dt=dt, tmax=10800.0, mode='limited', rec_dt=dt)
        k = np.argmin(abs(ts - 10800.0))
        print('dt=%.2f s  X_表面(3h)=%.6f  T_表面=%.4f  T_中心=%.4f' % (dt, Xs[k][20], Ts[k][20], Ts[k][0]))

    print('--- 烘干总时长（含潜热）网格/步长敏感性 ---')
    for N, dt in [(200, 8.0), (300, 4.0), (500, 2.0), (500, 1.0)]:
        t0 = time.time()
        _, _, _, tend = solve(N=N, dt=dt, tmax=345600.0, mode='limited', rec_dt=1e9)
        print('N=%4d dt=%.1f -> t_end = %.3f h   (%.0f s, 用时%.0fs)' % (N, dt, tend / 3600, tend, time.time() - t0))
