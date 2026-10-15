# -*- coding: utf-8 -*-
"""同一 LHS 矩阵下问题三/四干燥时长分布雨云图（半小提琴 + 箱 + 抖动散点）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, proxy_patch)

sens = load('sensitivity_results.json')
rp = sens['robustness_pair']
q3 = np.asarray(rp['t_end_h_q3'], float)
q4 = np.asarray(rp['t_end_h_q4'], float)
ratio = np.asarray(rp['ratio_q4_over_q3'], float)
base3 = float(rp['baseline_q3_h'])
base4 = float(rp['baseline_q4_h'])
shorter = float(rp['q4_shorter_fraction'])

rng = np.random.default_rng(int(sens['seed']))
groups = [(q3, rp['label_q3'], C['blue_main'], base3, 0),
          (q4, rp['label_q4'], C['teal'], base4, 1)]

fig, ax = plt.subplots(figsize=(6.8, 3.95), layout='constrained')

for data, label, col, base, k in groups:
    kde = gaussian_kde(data)
    xs = np.linspace(data.min(), data.max(), 300)
    dens = kde(xs)
    dens = 0.36 * dens / dens.max()
    ax.fill_between(xs, k, k + dens, facecolor=col, alpha=0.55, lw=0.0,
                    zorder=2)
    ax.plot(xs, k + dens, color=col, lw=1.3, zorder=3)
    # 雨云三件套之二：箱体（上方半小提琴由 KDE 手画，下方为 strip 抖动散点）
    ax.boxplot([data], positions=[k - 0.135], vert=False, widths=0.115,
               showfliers=False, patch_artist=True, zorder=4,
               medianprops=dict(color=C['neutral_black'], lw=1.3),
               whiskerprops=dict(color=C['neutral_dark'], lw=1.0),
               capprops=dict(color=C['neutral_dark'], lw=1.0),
               boxprops=dict(facecolor=col, edgecolor=C['neutral_dark'],
                             alpha=0.85, lw=0.8))
    jitter = k - 0.30 + 0.075 * rng.standard_normal(data.size)
    ax.plot(data, np.clip(jitter, k - 0.42, k - 0.19), ls='none', marker='.',
            ms=3.0, color=col, alpha=0.5, zorder=3)
    ax.plot([base], [k - 0.135], ls='none', marker=M[4], ms=8.0, mfc='none',
            mec=C['red_strong'], mew=1.8, zorder=6,
            label='确定性基准 $t_{end}$：%.1f h / %.1f h' % (base3, base4)
            if k == 0 else None)

proxy_patch(ax, C['blue_main'], '问题三：固定域，%d 次抽样' % len(q3))
proxy_patch(ax, C['teal'], '问题四：径向收缩，%d 次抽样' % len(q4))

ax.set_yticks([0, 1])
ax.set_yticklabels(['问题三口径\n附录 3 + 固定域', '问题四口径\n附录 4 + 径向收缩'])
ax.set_xlabel('干燥时长 $t_{end}$ / h')
ax.set_xlim(20.0, 132.0)
ax.set_ylim(-0.52, 1.44)
declutter_axes(ax, grid='on', grid_axis='x')

axi = ax.inset_axes([0.60, 0.615, 0.375, 0.345])
axi.hist(ratio, bins=22, color=C['green_2'], edgecolor=C['neutral_dark'],
         linewidth=0.5)
axi.plot([np.median(ratio)] * 2, [0, 1], transform=axi.get_xaxis_transform(),
         color=C['red_strong'], lw=1.3, ls='--')
axi.set_xlabel('配对比值 $t_{end}^{Q4}/t_{end}^{Q3}$')
axi.set_ylabel('样本数')
axi.set_xlim(0.76, 1.0)
axi.grid(True, axis='y', alpha=0.28)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.94)
finish(fig, 'fig_q34_robustness.png')
