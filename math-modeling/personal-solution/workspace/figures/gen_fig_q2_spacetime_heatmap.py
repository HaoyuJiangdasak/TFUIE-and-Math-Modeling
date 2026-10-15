# -*- coding: utf-8 -*-
"""问题二 3 h 内温度场与含水率场的时空矩阵热图。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, load, finish, set_paper_placement, panel_tag,
                        CMAP_HEAT, CMAP_MOIST)

p2 = load('problem_2_results.json')
hm = p2['heatmap']
t_min = np.asarray(hm['t_s'], float) / 60.0
r_cm = np.asarray(hm['r_cm'], float)
T = np.asarray(hm['T'], float).T          # (n_r, n_t)
Cm = np.asarray(hm['C'], float).T

fig = plt.figure(figsize=(7.3, 3.05), layout='constrained')
gs = GridSpec(1, 2, figure=fig)

ax0 = fig.add_subplot(gs[0, 0])
mesh0 = ax0.pcolormesh(t_min, r_cm, T, cmap=CMAP_HEAT, shading='gouraud',
                       rasterized=True)
# 等值线只描形状不标数值：色标高值端接近纯黑，任何固定色的行内标注都读不清
ax0.contour(t_min, r_cm, T, levels=6, colors=[C['neutral_light']],
            linewidths=0.7, alpha=0.85)
ax0.set_xlabel('时间 $t$ / min')
ax0.set_ylabel('径向坐标 $r$ / cm')
ax0.set_frame_on(False)
cb0 = fig.colorbar(mesh0, ax=ax0, pad=0.02, aspect=22)
cb0.set_label('温度 $T$ / °C')
panel_tag(ax0, 'a  温度场 $T(r,t)$')

ax1 = fig.add_subplot(gs[0, 1])
mesh1 = ax1.pcolormesh(t_min, r_cm, Cm, cmap=CMAP_MOIST, shading='gouraud',
                       rasterized=True)
ax1.contour(t_min, r_cm, Cm, levels=6, colors=[C['neutral_light']],
            linewidths=0.7, alpha=0.85)
ax1.set_xlabel('时间 $t$ / min')
ax1.set_ylabel('径向坐标 $r$ / cm')
ax1.set_frame_on(False)
cb1 = fig.colorbar(mesh1, ax=ax1, pad=0.02, aspect=22)
cb1.set_label('含水率 $C$ / (kg/kg)')
panel_tag(ax1, 'b  含水率场 $C(r,t)$')

set_paper_placement(fig, 1.0)
finish(fig, 'fig_q2_spacetime_heatmap.png')
