# -*- coding: utf-8 -*-
"""问题一 Duhamel-Bessel 半解析级数解与有限体积解的残差四联诊断。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
from scipy import stats
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, panel_tag,
                        declutter_axes, time_colors, legend_lane, CMAP_MOIST)

p1 = load('problem_1_results.json')
sa = p1['semi_analytic']
times = np.asarray(sa['times_s'], int)
r_cm = np.asarray(sa['r_cm'], float)
res = np.asarray(sa['residual_C'], float) * 1e5      # 单位换算为 1e-5 °C
per_t = np.asarray(sa['per_time_max_dev_C'], float) * 1e5
flat = res.ravel()
max_dev = float(sa['max_abs_dev_C']) * 1e5
mean_dev = float(sa['mean_abs_dev_C']) * 1e5
n_pts = int(sa['n_points'])
cols = time_colors(len(times))

fig = plt.figure(figsize=(7.3, 4.65), layout='constrained')
gs = GridSpec(2, 2, figure=fig)

ax0 = fig.add_subplot(gs[0, 0])
for k in range(len(times)):
    ax0.plot(r_cm, res[k], color=cols[k], lw=1.5, marker=M[k % len(M)], ms=3.0,
             markevery=4)
ax0.set_xlabel('径向坐标 $r$ / cm')
ax0.set_ylabel('残差 / ($10^{-5}$ °C)')
ax0.set_xlim(0, r_cm.max())
declutter_axes(ax0, grid='on', grid_axis='both')
sm = plt.cm.ScalarMappable(cmap=CMAP_MOIST)
sm.set_clim(times.min(), times.max())
cb0 = fig.colorbar(sm, ax=ax0, pad=0.02, aspect=24)
cb0.set_label('取样时刻 $t$ / s')
cb0.set_ticks([times.min(), 600, 1200, times.max()])
panel_tag(ax0, 'a')

ax1 = fig.add_subplot(gs[0, 1])
ax1.plot(times, per_t, color=C['blue_main'], lw=1.9, marker=M[0], ms=4.4,
         label='逐时刻最大绝对偏差')
ax1.axhline(max_dev, color=C['red_strong'], lw=1.1, ls='--',
            label='全局最大 %.2f' % max_dev)
ax1.axhline(mean_dev, color=C['teal'], lw=1.1, ls=':',
            label='全局平均 %.2f' % mean_dev)
ax1.set_xlabel('时间 $t$ / s')
ax1.set_ylabel('绝对偏差 / ($10^{-5}$ °C)')
ax1.set_xlim(0, times.max() * 1.03)
ax1.set_ylim(0, max_dev * 1.18)
declutter_axes(ax1, grid='on', grid_axis='both')
panel_tag(ax1, 'b')

ax2 = fig.add_subplot(gs[1, 0])
osm, osr = stats.probplot(flat, dist='norm', fit=False)
slope, intercept, rval = stats.linregress(osm, osr)[:3]
ax2.plot(osm, osr, ls='none', marker=M[7], ms=3.0, mfc='none',
         mec=C['blue_main'], mew=0.8, label='残差样本分位点')
ax2.plot(osm, slope * osm + intercept, color=C['red_strong'], lw=1.4,
         label='正态参考线 $R^2$=%.4f' % rval ** 2)
ax2.set_xlabel('标准正态理论分位数')
ax2.set_ylabel('样本分位数 / ($10^{-5}$ °C)')
declutter_axes(ax2, grid='on', grid_axis='both')
panel_tag(ax2, 'c')

ax3 = fig.add_subplot(gs[1, 1])
ax3.hist(flat, bins=22, color=C['green_3'], edgecolor=C['neutral_dark'],
         linewidth=0.5, label='残差频数（共 %d 点）' % n_pts)
ax3.axvline(float(flat.mean()), color=C['blue_main'], lw=1.4,
            label='残差均值 %.2f' % flat.mean())
ax3.set_xlabel('残差 / ($10^{-5}$ °C)')
ax3.set_ylabel('频数')
declutter_axes(ax3, grid='on', grid_axis='y')
panel_tag(ax3, 'd')

legend_lane(fig, [ax1, ax2, ax3], where='top', ncol=4)
set_paper_placement(fig, 1.0)
finish(fig, 'fig_q1_validate_analytic.png')
