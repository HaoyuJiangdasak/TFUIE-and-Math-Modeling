# -*- coding: utf-8 -*-
"""(h_m, D0) 双因子对干燥时长的三维响应面，底面投影等值线。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        CMAP_HEAT)

sens = load('sensitivity_results.json')
rs = sens['response_surface']
d0 = np.asarray(rs['d0_mult'], float)
hm = np.asarray(rs['hm_mult'], float)
Z = np.asarray(rs['grid'], float)        # grid[i][j] ↔ (d0_mult[j], hm_mult[i])
base_h = float(sens['baseline']['t_end_h'])
X, Y = np.meshgrid(d0, hm, indexing='xy')

i0 = int(np.argmin(np.abs(hm - 1.0)))
j0 = int(np.argmin(np.abs(d0 - 1.0)))
floor = np.floor(Z.min() / 5.0) * 5.0 - 3.0

fig = plt.figure(figsize=(6.6, 4.05), layout='constrained')
gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 0.048], wspace=0.02)
ax = fig.add_subplot(gs[0, 0], projection='3d')

surf = ax.plot_surface(X, Y, Z, cmap=CMAP_HEAT, rstride=1, cstride=1,
                       linewidth=0.35, edgecolor=C['neutral_light'],
                       antialiased=True, alpha=0.95, zorder=2)
ax.contour(X, Y, Z, levels=8, zdir='z', offset=floor,
           cmap=CMAP_HEAT, linewidths=0.9, zorder=1)
ax.plot([d0[j0]] * 2, [hm[i0]] * 2, [floor, Z[i0, j0]], color=C['blue_main'],
        lw=1.4, ls='--', zorder=6)
ax.plot([d0[j0]], [hm[i0]], [Z[i0, j0]], ls='none', marker=M[0], ms=7.0,
        color=C['blue_main'], zorder=7,
        label='基准工况 $t_{end}$=%.2f h' % base_h)
ax.plot([d0[0]], [hm[0]], [Z[0, 0]], ls='none', marker=M[2], ms=7.4,
        mfc='none', mec=C['red_strong'], mew=1.8, zorder=7,
        label='最慢角点 %.1f h' % Z[0, 0])
ax.plot([d0[-1]], [hm[-1]], [Z[-1, -1]], ls='none', marker=M[3], ms=7.4,
        mfc='none', mec=C['teal'], mew=1.8, zorder=7,
        label='最快角点 %.1f h' % Z[-1, -1])

ax.set_xlabel('扩散前因子倍率 $D_0/D_0^{base}$')
ax.set_ylabel('传质系数倍率 $h_m/h_m^{base}$')
ax.set_zlabel('干燥时长 $t_{end}$ / h')
ax.set_xlim(d0.min(), d0.max())
ax.set_ylim(hm.min(), hm.max())
ax.set_zlim(floor, Z.max() * 1.02)
ax.view_init(elev=24, azim=-131)
ax.set_box_aspect((1.0, 1.0, 0.72))
ax.xaxis.pane.set_alpha(0.0)
ax.yaxis.pane.set_alpha(0.0)
ax.zaxis.pane.set_alpha(0.0)
ax.grid(True)

cax = fig.add_subplot(gs[0, 1])
cb = fig.colorbar(surf, cax=cax)
cb.set_label('干燥时长 $t_{end}$ / h，角点比 %.2f' %
             float(sens['checks']['V3.11']['corner_ratio']))

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q3_sensitivity_surface.png')
