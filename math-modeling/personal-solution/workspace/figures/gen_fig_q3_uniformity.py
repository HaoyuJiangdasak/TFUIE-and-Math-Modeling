# -*- coding: utf-8 -*-
"""问题三径向含水率分布山脊线图：九个时刻的剖面形状与达标前沿内移。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, proxy_patch, time_colors)

p3 = load('problem_3_results.json')
pr = p3['profiles']
dc = p3['drying_curve']
r = np.asarray(pr['r_cm'], float)
prof = np.asarray(pr['C'], float)                 # (n_t, n_r)
times_h = np.asarray(pr['times_s'], float) / 3600.0
thr = float(dc['threshold'])
n = len(times_h)

STEP = 1.0
SCALE = 1.35 / prof[:, 0].max()
cols = time_colors(n)

fig, ax = plt.subplots(figsize=(6.5, 4.15), layout='constrained')

ticks, labels = [], []
for k in range(n):
    base = (n - 1 - k) * STEP
    y = base + SCALE * prof[k]
    ax.fill_between(r, base, y, facecolor=cols[k], alpha=0.72, lw=0.0,
                    zorder=2 + 2 * k)
    ax.plot(r, y, color=C['neutral_black'], lw=1.05, zorder=3 + 2 * k)
    ax.plot([r[0], r[-1]], [base + SCALE * thr] * 2, color=C['neutral_dark'],
            lw=0.9, ls=':', zorder=3 + 2 * k,
            label='达标阈值 $C^{*}$=%.2f kg/kg' % thr if k == 0 else None)
    row = prof[k]
    if row[0] > thr > row[-1]:
        i = int(np.argmax(row < thr))
        rr = r[i - 1] + (thr - row[i - 1]) / (row[i] - row[i - 1]) * (r[i] - r[i - 1])
        ax.plot([rr], [base + SCALE * thr], ls='none', marker=M[0], ms=5.2,
                mfc=C['red_strong'], mec=C['neutral_black'], mew=0.6,
                zorder=4 + 2 * k,
                label='达标前沿 $r^{*}$' if k == 1 else None)
    ticks.append(base)
    labels.append('$t$=%d h\n$C_c$=%.2f' % (int(round(times_h[k])), row[0]))

proxy_patch(ax, cols[n // 2], '径向含水率剖面 $C(r)$（共用 $C$ 标尺）')

ax.set_yticks(ticks)
ax.set_yticklabels(labels)
ax.set_xlabel('径向坐标 $r$ / cm')
# 山脊只画到 r=2 cm，x 轴右端留白专供插图落座；刻度写死，避免自动刻度
# 在留白区补出一个 2.5 与插图轴标签相撞
ax.set_xlim(0.0, 2.92)
ax.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
ax.set_ylim(-0.34, (n - 1) * STEP + 1.62)
declutter_axes(ax, grid='off')
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)

# 相对不均匀度：时间轴向下，与山脊行序同向
t = np.asarray(dc['t_h'], float)
rel = ((np.asarray(dc['C_center'], float) - np.asarray(dc['C_surface'], float))
       / np.asarray(dc['C_volavg'], float))
axi = ax.inset_axes([0.775, 0.055, 0.165, 0.885])
axi.plot(rel, t, color=C['red_strong'], lw=1.5)
k_pk = int(np.argmax(rel))
axi.plot([rel[k_pk]], [t[k_pk]], ls='none', marker=M[4], ms=5.6, mfc='none',
         mec=C['red_strong'], mew=1.5)
axi.invert_yaxis()
axi.set_xlabel('$(C_c-C_s)/\\bar{C}$')
axi.set_ylabel('$t$ / h')
axi.set_xlim(0.0, 1.02)
axi.set_ylim(t.max(), 0.0)
axi.set_xticks([0.0, 0.5, 1.0])
axi.grid(True, alpha=0.28)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q3_uniformity.png')
