# -*- coding: utf-8 -*-
"""四级模型阶梯（集中参数/常物性/单向解耦/全耦合）关键含水率指标棒棒糖对比。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes)

allr = load('all_results.json')
paths = allr['model_ladder']['paths']
base = float(allr['model_ladder']['baseline_volavg_C_end'])

order = ['L0_lumped', 'L1_const_prop', 'L2_oneway', 'L3_full']
names = ['L0\n集中参数', 'L1\n常物性常扩散', 'L2\n变扩散单向解耦', 'L3\n全耦合（本文）']
volavg, center = [], []
for key in order:
    node = paths[key]
    if key == 'L0_lumped':
        volavg.append(float(node['C_end']))
        center.append(float(node['C_end']))
    else:
        volavg.append(float(node['volavg_C_end']))
        center.append(float(node['C_center_end']))
volavg = np.asarray(volavg)
center = np.asarray(center)
x = np.arange(len(order))

# 竖向棒棒糖：模型名放 x 轴，中文标签有整格宽度可用，不必截断
fig, ax = plt.subplots(figsize=(6.5, 3.5), layout='constrained')
lo = np.minimum(volavg, center)
hi = np.maximum(volavg, center)
ax.vlines(x, lo, hi, color=C['neutral_light'], lw=2.6, zorder=1,
          capstyle='round')
ax.plot(x, volavg, ls='none', marker=M[0], ms=8.0, color=C['blue_main'],
        zorder=3, label='体积平均含水率 $\\bar{C}$')
ax.plot(x, center, ls='none', marker=M[2], ms=7.5, mfc='none',
        mec=C['red_strong'], mew=1.8, zorder=3, label='中心含水率 $C_c$')
ax.axhline(base, color=C['teal'], lw=1.2, ls='--', zorder=2,
           label='L3 基准 $\\bar{C}$=%.4f kg/kg' % base)

ax.set_xticks(x)
ax.set_xticklabels(names)
ax.set_xlim(-0.62, len(order) - 0.38)
ax.set_ylabel('3 h 时刻含水率 / (kg/kg)')
ax.set_ylim(0.95, 2.35)
declutter_axes(ax, grid='on', grid_axis='y')

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.9)
finish(fig, 'fig_q1_model_ladder.png')
