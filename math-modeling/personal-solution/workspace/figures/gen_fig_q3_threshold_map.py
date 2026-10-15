# -*- coding: utf-8 -*-
"""问题三达标时空图：C(r,t) 云图叠加 C*=0.15 等值线，未达标区随时间收缩。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        axis_tint, CMAP_MOIST)

p3 = load('problem_3_results.json')
hm = p3['heatmap']
t = np.asarray(hm['t_h'], float)
r = np.asarray(hm['r_cm'], float)
Cm = np.asarray(hm['C'], float)                  # (n_t, n_r)
thr = float(p3['drying_curve']['threshold'])
t_end = float(p3['t_end']['hours'])
R = r.max()

# 未达标边界 r*(t)：C 沿半径单调递减，逐时刻线性插值求 C=C* 的位置
r_star = np.empty_like(t)
for k, row in enumerate(Cm):
    if row[0] <= thr:
        r_star[k] = 0.0
    elif row[-1] >= thr:
        r_star[k] = R
    else:
        i = int(np.argmax(row < thr))
        c0, c1 = row[i - 1], row[i]
        r_star[k] = r[i - 1] + (thr - c0) / (c1 - c0) * (r[i] - r[i - 1])

fig = plt.figure(figsize=(6.9, 3.85), layout='constrained')
gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 0.035])
ax = fig.add_subplot(gs[0, 0])

mesh = ax.pcolormesh(t, r, Cm.T, cmap=CMAP_MOIST, shading='gouraud',
                     norm=LogNorm(vmin=Cm.min(), vmax=Cm.max()),
                     rasterized=True)
ax.fill_between(t, 0.0, r_star, facecolor='none', hatch='////',
                edgecolor=C['red_strong'], linewidth=0.0, zorder=3,
                label='未达标区 $C>C^{*}$')
ax.plot(t, r_star, color=C['red_strong'], lw=2.0, zorder=4,
        label='达标前沿 $r^{*}(t)$，即 $C$=%.2f 等值线' % thr)
ax.plot([t_end], [0.0], ls='none', marker=M[0], ms=8.0, mfc='none',
        mec=C['neutral_black'], mew=1.9, zorder=5,
        label='全域达标 $t_{end}$=%.2f h' % t_end)

ax.set_xlabel('时间 $t$ / h')
ax.set_ylabel('径向坐标 $r$ / cm')
ax.set_xlim(0.0, t_end)
ax.set_ylim(0.0, R)
ax.set_xticks([0, 12, 24, 36, 48, t_end])
ax.set_xticklabels(['0', '12', '24', '36', '48', '%.1f' % t_end])
ax.set_frame_on(False)

# 右轴把 r* 直接换算成未达标体积占比 (r*/R)^2：圆柱几何下二者一一对应，
# 省掉一幅只是单调重述 r*(t) 的插图
axt = ax.twinx()
axt.set_ylim(ax.get_ylim())
fr_ticks = np.array([2.0, 10.0, 25.0, 50.0, 75.0, 100.0])
axt.set_yticks(R * np.sqrt(fr_ticks / 100.0))
axt.set_yticklabels(['%g' % v for v in fr_ticks])
axt.set_ylabel('未达标体积占比 $(r^{*}/R_0)^2$ / %')
for side in ('top', 'bottom', 'left'):
    axt.spines[side].set_visible(False)
axis_tint(axt, C['red_strong'], which='y')
axt.grid(False)

cax = fig.add_subplot(gs[0, 1])
cb = fig.colorbar(mesh, cax=cax)
cb.set_label('含水率 $C$ / (kg/kg)')
cb.ax.axhline(thr, color=C['red_strong'], lw=1.4)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.94)
finish(fig, 'fig_q3_threshold_map.png')
