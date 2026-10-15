# -*- coding: utf-8 -*-
"""附件 2 半径实测点与收缩模型：上板 PCHIP/Weibull 拟合，下板 Weibull 残差。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, axis_tint, panel_tag)

p4 = load('problem_4_results.json')
rc = p4['radius_curve']
t_d = np.asarray(rc['t_data_s'], float) / 3600.0
R_d = np.asarray(rc['R_data_cm'], float)
t_x = np.asarray(rc['t_dense_s'], float) / 3600.0
R_p = np.asarray(rc['R_pchip_cm'], float)
R_w = np.asarray(rc['R_weibull_cm'], float)
dRdt = np.asarray(rc['dRdt_cm_per_s'], float) * 3600.0        # cm/h
wp = rc['weibull_params']
t_end = float(rc['t_end_s']) / 3600.0
R_end = float(rc['R_at_t_end_cm'])
rmse = float(rc['weibull_rmse_cm'])
maxabs = float(rc['weibull_max_abs_cm'])

# Weibull 描述式在实测时刻上的残差（形式已与产物逐点核对，最大差 0）
R_hat = (wp['R_inf_cm'] + (R_d[0] - wp['R_inf_cm'])
         * np.exp(-(t_d * 3600.0 / wp['tau_s']) ** wp['k']))
res = (R_d - R_hat) * 1e3                                      # μm

fig = plt.figure(figsize=(6.7, 4.5), layout='constrained')
gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 0.56], hspace=0.06)

ax0 = fig.add_subplot(gs[0, 0])
ax0b = ax0.twinx()
ax0.plot(t_d, R_d, ls='none', marker=M[0], ms=4.2, mfc='none',
         mec=C['neutral_dark'], mew=0.8, zorder=3,
         label='附件 2 实测半径（%d 点）' % len(t_d))
ax0.plot(t_x, R_p, color=C['blue_main'], lw=2.0, zorder=4,
         label='保单调 PCHIP 插值（PDE 采用）')
ax0.plot(t_x, R_w, color=C['red_strong'], lw=1.5, ls='--', zorder=5,
         label='Weibull 描述式 $k$=%.3f，$\\tau$=%.2f h' % (wp['k'], wp['tau_s'] / 3600.0))
ax0.plot([t_end], [R_end], ls='none', marker=M[4], ms=8.0, mfc='none',
         mec=C['violet'], mew=1.8, zorder=6,
         label='$t_{end}$=%.2f h 时 $R$=%.2f cm' % (t_end, R_end))
ax0b.plot(t_x, dRdt, color=C['teal'], lw=1.4, ls=':', zorder=3,
          label='收缩速率 $\\mathrm{d}R/\\mathrm{d}t$')
ax0.set_ylabel('半径 $R$ / cm')
ax0b.set_ylabel('$\\mathrm{d}R/\\mathrm{d}t$ / (cm·h$^{-1}$)')
ax0.set_xlim(0.0, t_d.max())
ax0.set_ylim(1.14, 2.06)
ax0b.set_ylim(-0.30, 0.02)
ax0.set_xticklabels([])
axis_tint(ax0b, C['teal'])
ax0b.grid(False)
declutter_axes(ax0, grid='on', grid_axis='both')
panel_tag(ax0, 'a  收缩曲线')

ax1 = fig.add_subplot(gs[1, 0])
ax1.vlines(t_d, 0.0, res, color=C['neutral_mid'], lw=0.8, zorder=2)
ax1.plot(t_d, res, ls='none', marker=M[0], ms=3.8, color=C['red_strong'],
         zorder=3, label='Weibull 残差 $R_{obs}-R_{fit}$')
ax1.axhline(0.0, color=C['neutral_black'], lw=0.9, zorder=1)
for sgn in (1.0, -1.0):
    ax1.axhline(sgn * rmse * 1e3, color=C['blue_main'], lw=1.0, ls='--',
                zorder=2,
                label='$\\pm$RMSE=%.1f μm，最大 %.1f μm' % (rmse * 1e3, maxabs * 1e3)
                if sgn > 0 else None)
ax1.set_xlabel('时间 $t$ / h')
ax1.set_ylabel('残差 / μm')
ax1.set_xlim(0.0, t_d.max())
ax1.set_ylim(-24.0, 24.0)
declutter_axes(ax1, grid='on', grid_axis='y')
panel_tag(ax1, 'b  拟合残差')

legend_lane(fig, [ax0, ax0b, ax1], where='top', ncol=3)
set_paper_placement(fig, 0.94)
finish(fig, 'fig_q4_radius_fit.png')
