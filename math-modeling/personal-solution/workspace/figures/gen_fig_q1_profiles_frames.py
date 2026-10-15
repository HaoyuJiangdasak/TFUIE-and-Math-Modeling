# -*- coding: utf-8 -*-
"""问题一 100/600/1200/1800 s 四帧径向剖面小多图（温度与含水率双轴同框）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        axis_tint, panel_tag, declutter_axes)

p1 = load('problem_1_results.json')
pr = p1['profiles']
times = np.asarray(pr['times_s'], int)
r_cm = np.asarray(pr['r_cm'], float)
T_all = np.asarray(pr['T'], float)
C_all = np.asarray(pr['C'], float)
C0 = float(p1['moisture_bl']['C0'])

want = [100, 600, 1200, 1800]
idx = [int(np.argmin(np.abs(times - w))) for w in want]

T_lo, T_hi = float(T_all[idx].min()), float(T_all[idx].max())
C_lo, C_hi = float(C_all[idx].min()), C0
T_pad = 0.06 * (T_hi - T_lo)
C_pad = 0.06 * (C_hi - C_lo)

fig = plt.figure(figsize=(7.3, 4.15), layout='constrained')
gs = GridSpec(2, 2, figure=fig)
tags = ['a', 'b', 'c', 'd']
axes_T, axes_C = [], []

for k, j in enumerate(idx):
    ax = fig.add_subplot(gs[k // 2, k % 2])
    axb = ax.twinx()
    ax.plot(r_cm, T_all[j], color=C['blue_main'], lw=1.9, marker=M[0], ms=3.2,
            markevery=3, zorder=3, label='温度 $T$')
    axb.plot(r_cm, C_all[j], color=C['red_strong'], lw=1.9, ls='--', marker=M[2],
             ms=3.2, markevery=3, zorder=3, label='含水率 $C$')
    axb.axhline(C0, color=C['neutral_mid'], lw=0.9, ls=':', zorder=2,
                label='初始含水率 $C_0$=%.2f kg/kg' % C0)
    ax.set_xlim(0, r_cm.max())
    ax.set_ylim(T_lo - T_pad, T_hi + T_pad)
    axb.set_ylim(C_lo - C_pad, C_hi + C_pad)
    axb.grid(False)
    if k // 2 == 1:
        ax.set_xlabel('径向坐标 $r$ / cm')
    if k % 2 == 0:
        ax.set_ylabel('温度 $T$ / °C')
    else:
        axb.set_ylabel('含水率 $C$ / (kg/kg)')
    axis_tint(ax, C['blue_main'])
    axis_tint(axb, C['red_strong'])
    declutter_axes(ax, grid='on', grid_axis='both')
    panel_tag(ax, '%s  $t$=%d s' % (tags[k], times[j]))
    axes_T.append(ax)
    axes_C.append(axb)

legend_lane(fig, [axes_T[0], axes_C[0]], where='top', ncol=3, fontsize=8.6)
set_paper_placement(fig, 1.0)
finish(fig, 'fig_q1_profiles_frames.png')
