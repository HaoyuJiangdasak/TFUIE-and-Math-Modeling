# -*- coding: utf-8 -*-
"""问题二预热段与恒温干燥段五测点温升、失水量哑铃对比。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        panel_tag, declutter_axes)

p2 = load('problem_2_results.json')
t3 = p2['table_3_temperature']
t4 = p2['table_4_moisture']

times = np.asarray(t3['times_s'], int)
radii = np.asarray(t3['radii_cm'], float)
Tv = np.asarray(t3['values'], float)      # (n_t, n_r)
Cv = np.asarray(t4['values'], float)

T_pre, T_end = Tv[0], Tv[-1]
C_pre, C_end = Cv[0], Cv[-1]
y = np.arange(len(radii))
labels = [('中心 $r$=0' if abs(v) < 1e-9 else
           ('表面 $r$=%.1f cm' % v if abs(v - radii.max()) < 1e-9 else
            '$r$=%.1f cm' % v)) for v in radii]

fig = plt.figure(figsize=(7.3, 3.25), layout='constrained')
gs = GridSpec(1, 2, figure=fig)

ax0 = fig.add_subplot(gs[0, 0])
ax0.hlines(y, T_pre, T_end, color=C['neutral_light'], lw=3.0, zorder=1,
           capstyle='round')
ax0.scatter(T_pre, y, marker=M[0], s=49.0, color=C['blue_main'], zorder=3,
            label='预热段末 $t$=%d min' % (times[0] // 60))
ax0.scatter(T_end, y, marker=M[2], s=49.0, color=C['red_strong'], zorder=3,
            label='干燥段末 $t$=%d min' % (times[-1] // 60))
ax0.set_yticks(y)
ax0.set_yticklabels(labels)
ax0.invert_yaxis()
ax0.set_xlabel('温度 $T$ / °C')
ax0.set_xlim(30.0, 52.5)
declutter_axes(ax0, grid='on', grid_axis='x')
panel_tag(ax0, 'a  温度')

ax1 = fig.add_subplot(gs[0, 1])
ax1.hlines(y, C_end, C_pre, color=C['neutral_light'], lw=3.0, zorder=1,
           capstyle='round')
ax1.scatter(C_pre, y, marker=M[0], s=49.0, color=C['blue_main'], zorder=3,
            label='预热段末 $t$=%d min' % (times[0] // 60))
ax1.scatter(C_end, y, marker=M[2], s=49.0, color=C['red_strong'], zorder=3,
            label='干燥段末 $t$=%d min' % (times[-1] // 60))
ax1.set_yticks(y)
ax1.set_yticklabels([])
ax1.invert_yaxis()
ax1.set_xlabel('含水率 $C$ / (kg/kg)')
ax1.set_xlim(0.9, 2.65)
declutter_axes(ax1, grid='on', grid_axis='x')
panel_tag(ax1, 'b  含水率')

legend_lane(fig, [ax0], where='top', ncol=2)
set_paper_placement(fig, 1.0)
finish(fig, 'fig_q2_stage_compare.png')
