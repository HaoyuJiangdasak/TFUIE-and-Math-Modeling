# -*- coding: utf-8 -*-
"""问题一网格无关性：逐次加密的解变化量随 N 的收敛，附二阶参考斜率。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        axis_tint, declutter_axes)

p1 = load('problem_1_results.json')
ladder = p1['mesh_ladder']

N = np.asarray([row['N'] for row in ladder], float)
dT = np.asarray([row.get('dT_center_vs_prev', np.nan) for row in ladder], float)
dC = np.asarray([row.get('dC_surface_vs_prev', np.nan) for row in ladder], float)
ok = np.isfinite(dT) & np.isfinite(dC)
N_ok, dT_ok, dC_ok = N[ok], dT[ok], dC[ok]

fig, ax = plt.subplots(figsize=(6.2, 3.55), layout='constrained')
axb = ax.twinx()

ax.plot(N_ok, dT_ok, color=C['blue_main'], lw=1.9, marker=M[0], ms=5.0,
        label='中心温度变化 $|\\Delta T_c|$')
axb.plot(N_ok, dC_ok, color=C['red_strong'], lw=1.9, ls='--', marker=M[2],
         ms=5.0, label='表面含水率变化 $|\\Delta C_s|$')

# 二阶参考斜率：过首个数据点、按 N^{-2} 衰减
ref = dT_ok[0] * (N_ok / N_ok[0]) ** -2.0
ax.plot(N_ok, ref, color=C['neutral_mid'], lw=1.2, ls=':',
        label='二阶收敛参考 $\\propto N^{-2}$')
ax.axvline(120, color=C['teal'], lw=1.1, ls='-.', label='本文采用 $N$=120')

ax.set_xscale('log')
ax.set_yscale('log')
axb.set_yscale('log')
ax.set_xticks(N)
ax.set_xticklabels([('%d' % v) for v in N])
ax.set_xlabel('径向控制体数 $N$')
ax.set_ylabel('$|\\Delta T_c|$ / °C')
axb.set_ylabel('$|\\Delta C_s|$ / (kg/kg)')
axis_tint(ax, C['blue_main'])
axis_tint(axb, C['red_strong'])
axb.grid(False)
declutter_axes(ax, grid='on', grid_axis='both')

legend_lane(fig, [ax, axb], where='top', ncol=2)
set_paper_placement(fig, 0.86)
finish(fig, 'fig_q1_grid_conv.png')
