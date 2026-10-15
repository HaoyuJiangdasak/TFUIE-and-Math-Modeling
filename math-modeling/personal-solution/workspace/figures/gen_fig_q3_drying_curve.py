# -*- coding: utf-8 -*-
"""问题三全程干燥曲线：三口径含水率多段衰减 + 0.15 阈值与达标时刻。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes)

p3 = load('problem_3_results.json')
allr = load('all_results.json')
dc = p3['drying_curve']
t = np.asarray(dc['t_h'], float)
C_max = np.asarray(dc['C_max'], float)
C_avg = np.asarray(dc['C_volavg'], float)
C_srf = np.asarray(dc['C_surface'], float)
thr = float(dc['threshold'])

crit = allr['criterion_comparison']
t_max = float(crit['max']['t_end_h'])
t_avg = float(crit['volavg']['t_end_h'])
t_srf = float(crit['surface']['t_end_h'])

fig, ax = plt.subplots(figsize=(6.6, 3.9), layout='constrained')

ax.plot(t, C_max, color=C['red_strong'], lw=2.0, zorder=4,
        label='最大含水率 $C_{max}$（本文判据）')
ax.plot(t, C_avg, color=C['blue_main'], lw=1.8, ls='--', zorder=3,
        label='体积平均含水率 $\\bar{C}$')
ax.plot(t, C_srf, color=C['teal'], lw=1.6, ls='-.', zorder=3,
        label='表面含水率 $C_s$')
ax.axhline(thr, color=C['neutral_dark'], lw=1.2, ls=':', zorder=2,
           label='达标阈值 $C^{*}$=%.2f kg/kg' % thr)

for tc, col, mk, lab in [(t_srf, C['teal'], M[2], '表面达标 %.2f h' % t_srf),
                         (t_avg, C['blue_main'], M[1], '平均达标 %.2f h' % t_avg),
                         (t_max, C['red_strong'], M[0], '全域达标 %.2f h' % t_max)]:
    ax.plot([tc], [thr], ls='none', marker=mk, ms=8.0, mfc='none', mec=col,
            mew=1.9, zorder=6, label=lab)

ax.set_xlabel('时间 $t$ / h')
ax.set_ylabel('含水率 $C$ / (kg/kg)')
ax.set_yscale('log')
ax.set_xlim(0.0, t.max())
ax.set_ylim(0.04, 3.0)
ax.set_xticks([0, 12, t_srf, 24, 36, t_avg, 48, t_max])
ax.set_xticklabels(['0', '12', '', '24', '36', '', '48', '%.1f' % t_max])
declutter_axes(ax, grid='on', grid_axis='both')

# 干燥速率 inset：跨三个量级，故取对数纵轴
rate = -np.gradient(C_avg, t)
axi = ax.inset_axes([0.575, 0.545, 0.395, 0.415])
axi.plot(C_avg, rate, color=C['violet'], lw=1.5)
axi.plot([C_avg[0]], [rate[0]], ls='none', marker=M[0], ms=4.6,
         color=C['violet'])
axi.set_xscale('log')
axi.set_yscale('log')
axi.invert_xaxis()
axi.set_xlabel('$\\bar{C}$ / (kg/kg)')
axi.set_ylabel('$-\\mathrm{d}\\bar{C}/\\mathrm{d}t$ / h$^{-1}$')
axi.grid(True, which='major', alpha=0.28)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q3_drying_curve.png')
