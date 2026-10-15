# -*- coding: utf-8 -*-
"""问题四水分质量平衡瀑布图：初始持水量 − 累计蒸发 − 残余 = 闭合残差。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, proxy_patch, axis_tint)

p4 = load('problem_4_results.json')
mb = p4['mass_balance']
t_h = np.asarray(mb['t_h'], float)
m_w = np.asarray(mb['m_w_kg_per_m'], float)
cum = np.asarray(mb['cumulative_loss_kg_per_m'], float)
gap = float(mb['closure_rel_gap'])
m0, m1 = float(m_w[0]), float(m_w[-1])
resid = m0 - cum[-1] - m1                      # 闭合残差，与 closure_rel_gap 同源
TOP = m0 * 1.16

x = np.arange(4)
fig, ax = plt.subplots(figsize=(6.7, 4.0), layout='constrained')

# 前三级同尺度：起量、蒸发落差、终态残余
ax.bar(x[0], m0, bottom=0.0, width=0.58, color=C['blue_main'],
       edgecolor=C['neutral_dark'], linewidth=0.6, zorder=3)
ax.bar(x[1], -cum[-1], bottom=m0, width=0.58, color=C['red_strong'],
       edgecolor=C['neutral_dark'], linewidth=0.6, zorder=3)
ax.bar(x[2], m1, bottom=0.0, width=0.58, color=C['teal'],
       edgecolor=C['neutral_dark'], linewidth=0.6, zorder=3)
ax.plot([x[0] + 0.29, x[1] - 0.29], [m0, m0], color=C['neutral_dark'], lw=0.9,
        ls='--', zorder=2)
ax.plot([x[1] + 0.29, x[2] - 0.29], [m0 - cum[-1]] * 2, color=C['neutral_dark'],
        lw=0.9, ls='--', zorder=2)

# 第四级必须换轴：残差只有起量的 9.4e-05，同轴画就是零高柱；靠 ×10^4 硬拉又会
# 让最小项反压过终态残余。副轴单位写在轴标题上，比例关系不含糊
axr = ax.twinx()
axr.bar(x[3], abs(resid) / 1e-5, bottom=0.0, width=0.58, color=C['violet'],
        edgecolor=C['neutral_dark'], linewidth=0.6, zorder=3)
axr.set_ylim(0.0, 24.0)
axr.set_ylabel('闭合残差 $|\\varepsilon|$ / ($10^{-5}$ kg·m$^{-1}$)')
axis_tint(axr, C['violet'], which='y')
axr.grid(False)

proxy_patch(ax, C['blue_main'], '初始持水量 %.5f kg/m' % m0)
proxy_patch(ax, C['red_strong'], '累计蒸发 %.5f kg/m' % cum[-1])
proxy_patch(ax, C['teal'], '终态残余 %.5f kg/m' % m1)
proxy_patch(ax, C['violet'], '闭合残差 %.2e kg/m，相对间隙 %.2e' % (resid, gap))

ax.set_xticks(x)
ax.set_xticklabels(['初始持水量\n$m_w(0)$',
                    '累计蒸发\n$-\\int j\\,\\mathrm{d}A\\,\\mathrm{d}t$',
                    '终态残余\n$m_w(t_{end})$',
                    '闭合残差\n$\\varepsilon$（右轴）'])
ax.set_ylabel('单位柱长水分质量 / (kg·m$^{-1}$)')
ax.set_xlim(-0.62, 3.38)
ax.set_ylim(0.0, TOP)
declutter_axes(ax, grid='on', grid_axis='y')

# 插图画残差的时间过程，单柱只能给终值，逐时曲线才说明全程都闭合。
# 单条曲线不需要图例，轴标题即可自明，也就不会在插图里再挤出一个遮挡源。
axi = ax.inset_axes([0.585, 0.565, 0.375, 0.395])
axi.plot(t_h, (m_w - (m0 - cum)) / 1e-5, color=C['violet'], lw=1.5)
axi.set_xlabel('$t$ / h')
axi.set_ylabel('$|\\varepsilon(t)|$ / $10^{-5}$')
axi.set_xlim(0.0, t_h.max())
axi.set_ylim(0.0, 9.6)
axi.grid(True, alpha=0.28)
axi.set_facecolor('white')
axi.patch.set_alpha(1.0)

legend_lane(fig, [ax], where='top', ncol=2)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q4_mass_balance.png')
