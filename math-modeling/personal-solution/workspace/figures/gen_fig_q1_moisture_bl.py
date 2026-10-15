# -*- coding: utf-8 -*-
"""问题一表面失水边界层：含水率沿表面深度分布，近表面 0.1 cm 放大 inset。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, time_colors, CMAP_MOIST)

p1 = load('problem_1_results.json')
mb = p1['moisture_bl']
times = np.asarray(mb['times_s'], int)
depth = np.asarray(mb['depth_from_surface_cm'], float)
C_cells = np.asarray(mb['C_cells'], float)
C_surf = np.asarray(mb['C_surface_recon'], float)
C0 = float(mb['C0'])
pen = float(mb['penetration_depth_cm'])
bl = np.asarray(mb['bl_thickness_cm'], float)

order = np.argsort(depth)
depth = depth[order]
C_cells = C_cells[:, order]
cols = time_colors(len(times))

fig, ax = plt.subplots(figsize=(6.4, 3.85), layout='constrained')
for k in range(len(times)):
    ax.plot(depth, C_cells[k], color=cols[k], lw=1.7)
    ax.plot(0.0, C_surf[k], marker=M[k % len(M)], ms=4.4, mfc='none',
            mec=cols[k], mew=1.1)
ax.axhline(C0, color=C['neutral_mid'], lw=1.0, ls=':',
           label='初始含水率 $C_0$=%.2f kg/kg' % C0)
ax.axvline(pen, color=C['red_strong'], lw=1.2, ls='--',
           label='尺度估计 $\\sqrt{Dt}$=%.3f cm' % pen)
ax.axvline(bl[-1], color=C['violet'], lw=1.2, ls='-.',
           label='1800 s 失水层厚 %.3f cm' % bl[-1])
ax.plot([], [], ls='none', marker=M[0], ms=4.4, mfc='none',
        mec=C['neutral_dark'], mew=1.1, label='重构表面值 $C_s$')
ax.set_xlabel('自表面向内的深度 $R_0-r$ / cm')
ax.set_ylabel('含水率 $C$ / (kg/kg)')
ax.set_xlim(-0.03, depth.max())
ax.set_ylim(C_cells.min() - 0.06, C0 + 0.06)
declutter_axes(ax, grid='on', grid_axis='both')

sm = plt.cm.ScalarMappable(cmap=CMAP_MOIST)
sm.set_clim(times.min(), times.max())
cb = fig.colorbar(sm, ax=ax, pad=0.015, aspect=26)
cb.set_label('取样时刻 $t$ / s')
cb.set_ticks([times.min(), 600, 1200, times.max()])

axin = ax.inset_axes([0.52, 0.13, 0.44, 0.40])
sel = depth <= 0.1
for k in range(len(times)):
    axin.plot(depth[sel], C_cells[k][sel], color=cols[k], lw=1.5)
    axin.plot(0.0, C_surf[k], marker=M[k % len(M)], ms=3.6, mfc='none',
              mec=cols[k], mew=1.0)
axin.set_xlim(-0.004, 0.1)
axin.set_xlabel('$R_0-r$ / cm', labelpad=1.5)
axin.set_ylabel('$C$ / (kg/kg)', labelpad=1.5)
axin.tick_params(labelsize=8.4, pad=1.5)
axin.xaxis.label.set_size(8.4)
axin.yaxis.label.set_size(8.4)
axin.grid(True, lw=0.4, alpha=0.5)
for spine in axin.spines.values():
    spine.set_linewidth(0.7)
    spine.set_color(C['neutral_mid'])

legend_lane(fig, [ax], where='top', ncol=2)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q1_moisture_bl.png')
