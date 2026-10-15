# -*- coding: utf-8 -*-
"""扩散系数 D(C,T) 等值线填充图，叠加问题二实际工况轨迹。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, CMAP_MOIST)

p2 = load('problem_2_results.json')
rs = p2['D_response_surface']
C_axis = np.asarray(rs['C_axis'], float)
T_axis = np.asarray(rs['T_axis_C'], float)
D = np.asarray(rs['D_m2_s'], float)
traj = np.asarray(rs['trajectory_C_T'], float)
ratio = float(rs['ratio_max_over_min'])
D_min, D_max = float(rs['D_min']), float(rs['D_max'])

# 产物中 D[i][j] 对应 (C_axis[j], T_axis[i])，已按解析式逐点核对
Cg, Tg = np.meshgrid(C_axis, T_axis, indexing='xy')
Z = D

fig, ax = plt.subplots(figsize=(6.3, 3.85), layout='constrained')
norm = LogNorm(vmin=D_min, vmax=D_max)
cf = ax.contourf(Cg, Tg, Z, levels=32, cmap=CMAP_MOIST, norm=norm)
ax.contour(Cg, Tg, Z, levels=7, colors=[C['neutral_black']],
           linewidths=0.65, alpha=0.6)

ax.plot(traj[:, 0], traj[:, 1], color=C['red_strong'], lw=2.2, zorder=4,
        label='问题二中心工况轨迹')
ax.plot(traj[0, 0], traj[0, 1], marker=M[0], ms=7.0, color=C['red_strong'],
        zorder=5, label='轨迹起点 $t$=0')
ax.plot(traj[-1, 0], traj[-1, 1], marker=M[4], ms=8.0, mfc='none',
        mec=C['red_strong'], mew=1.8, zorder=5, label='轨迹终点 $t$=3 h')

ax.set_xlabel('含水率 $C$ / (kg/kg)')
ax.set_ylabel('温度 $T$ / °C')
ax.set_xlim(C_axis.min(), C_axis.max())
ax.set_ylim(T_axis.min(), T_axis.max())
declutter_axes(ax, grid='off')
cb = fig.colorbar(cf, ax=ax, pad=0.02, aspect=24)
cb.set_label('扩散系数 $D$ / (m$^2$·s$^{-1}$)，极差 %.1f 倍' % ratio)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.9)
finish(fig, 'fig_q2_D_response_surface.png')
