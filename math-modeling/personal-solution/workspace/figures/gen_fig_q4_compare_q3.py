# -*- coding: utf-8 -*-
"""固定几何与收缩几何五测点达标时刻斜率图（测点取物质坐标 eta=r/R(t)）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, time_colors)

p4 = load('problem_4_results.json')
cq = p4['compare_q3']
eta = np.asarray(cq['probe_eta'], float)
h3 = np.asarray(cq['probe_cross_h_q3'], float)
h4 = np.asarray(cq['probe_cross_h_q4'], float)
t3 = float(cq['t_end_q3_h'])
t4 = float(cq['t_end_q4_h'])

x = np.array([0.0, 1.0])
cols = time_colors(len(eta))
# 线型与颜色双编码：五条同族绿-蓝仅靠色相区分，灰度打印会并到一起
STYLES = ['-', (0, (6, 2)), (0, (4, 1.6, 1, 1.6)), (0, (1.4, 1.6)),
          (0, (8, 2, 1, 2))]
fig, ax = plt.subplots(figsize=(6.7, 4.05), layout='constrained')

for k in range(len(eta)):
    up = h4[k] > h3[k]
    ax.plot(x, [h3[k], h4[k]], color=cols[k], lw=2.0, ls=STYLES[k], zorder=3,
            label='$\\eta$=%.2f，%s %.2f h'
            % (eta[k], '推迟' if up else '提前', abs(h4[k] - h3[k])))
    ax.plot([x[0]], [h3[k]], ls='none', marker=M[0], ms=7.0, color=cols[k],
            mec=C['neutral_dark'], mew=0.6, zorder=5,
            label='固定域测点' if k == 0 else None)
    ax.plot([x[1]], [h4[k]], ls='none', marker=M[2], ms=7.4, mfc='none',
            mec=cols[k], mew=1.7, zorder=5,
            label='收缩域同物质坐标测点' if k == 0 else None)

ax.set_xticks(x)
# 每行不超过 9 个字：字号被保存钩子放大到 14.4 pt 后，12 字一行的标签会顶到画布
ax.set_xticklabels(['问题三口径\n附录 3 + 固定域\n$t_{end}$=%.2f h' % t3,
                    '问题四口径\n附录 4 + 径向收缩\n$t_{end}$=%.2f h' % t4])
# 轴标签必须短到不触发折行（阈值 10 字）：折行后两行在 90° 旋转下横向并排，
# 实测行距不足会让笔画互相穿插
ax.set_ylabel('达标时刻 / h')
ax.set_xlim(-0.34, 1.34)
ax.set_ylim(8.0, 63.0)
ax.set_yticks([12, 24, 36, 48, t3])
ax.set_yticklabels(['12', '24', '36', '48', '%.1f' % t3])
declutter_axes(ax, grid='on', grid_axis='y')

# 默认 w_pad 只留 12 px 边距，纵轴标签会贴着画布左缘，读起来像被裁掉
fig.get_layout_engine().set(w_pad=0.16, h_pad=0.10)
legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q4_compare_q3.png')
