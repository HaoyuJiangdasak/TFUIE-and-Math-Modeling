# -*- coding: utf-8 -*-
"""问题四四帧真实几何含水率分布：横轴物理半径，域随时间收缩。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, panel_tag, proxy_patch, time_colors)

p4 = load('problem_4_results.json')
frames = p4['moving_boundary_frames']
thr = float(p4['compare_q3']['threshold'])
R0 = float(p4['radius_curve']['R_data_cm'][0])

want = [12.0, 24.0, 36.0, 48.0]
sel = [min(frames, key=lambda f, w=w: abs(float(f['t_h']) - w)) for w in want]
cols = time_colors(len(sel))

fig = plt.figure(figsize=(7.0, 4.35), layout='constrained')
gs = GridSpec(2, 2, figure=fig)

for k, fr in enumerate(sel):
    ax = fig.add_subplot(gs[k // 2, k % 2])
    r = np.asarray(fr['r_cm'], float)
    Cp = np.asarray(fr['C'], float)
    R = float(fr['R_cm'])
    # 体积平均：圆柱几何 2∫C r dr / R²，由该帧剖面直接积分
    vavg = 2.0 * np.trapezoid(Cp * r, r) / R ** 2

    ax.fill_betweenx([0.03, 3.0], R, R0, facecolor='none', hatch='\\\\\\',
                     edgecolor=C['neutral_light'], linewidth=0.0, zorder=1)
    ax.fill_between(r, 0.03, Cp, facecolor=cols[k], alpha=0.4, lw=0.0,
                    zorder=2)
    ax.plot(r, Cp, color=cols[k], lw=2.0, zorder=4, label='含水率剖面 $C(r)$')
    ax.plot([R], [Cp[-1]], ls='none', marker=M[0], ms=6.6, mfc='none',
            mec=C['red_strong'], mew=1.6, zorder=6, label='当前表面 $r=R(t)$')
    ax.plot([0.0], [vavg], ls='none', marker=M[3], ms=6.4,
            color=C['neutral_dark'], zorder=6, label='体积平均 $\\bar{C}$')
    ax.axhline(thr, color=C['neutral_dark'], lw=1.0, ls=':', zorder=3,
               label='达标阈值 $C^{*}$=%.2f kg/kg' % thr)
    if k == 0:
        proxy_patch(ax, 'none', '已收缩掉的区域 $R(t)<r\\leq R_0$',
                    edgecolor=C['neutral_mid'], hatch='\\\\\\')

    ax.set_yscale('log')
    ax.set_xlim(0.0, R0 * 1.02)
    ax.set_ylim(0.04, 2.1)
    if k // 2 == 1:
        ax.set_xlabel('物理半径 $r$ / cm')
    else:
        ax.set_xticklabels([])
    if k % 2 == 0:
        ax.set_ylabel('含水率 $C$ / (kg/kg)')
    else:
        ax.set_yticklabels([])
    declutter_axes(ax, grid='on', grid_axis='both')
    panel_tag(ax, '%s  $t$=%d h，$R$=%.3f cm' % ('abcd'[k], int(round(fr['t_h'])), R))

legend_lane(fig, fig.axes, where='top', ncol=3)
set_paper_placement(fig, 0.96)
finish(fig, 'fig_q4_moving_boundary_frames.png')
