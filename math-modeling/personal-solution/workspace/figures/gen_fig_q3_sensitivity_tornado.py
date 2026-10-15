# -*- coding: utf-8 -*-
"""问题三八参数龙卷风敏感度：双向变化幅度 + 归一化弹性对照。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, axis_tint, declutter_axes as _dc)

sens = load('sensitivity_results.json')
tor = sens['tornado']
order = list(tor['order'])
base_h = float(tor['baseline_h'])

rows = [tor['by_factor'][k] for k in order]
low = np.array([float(v['delta_pct_low']) for v in rows])
high = np.array([float(v['delta_pct_high']) for v in rows])
elas = np.array([float(v['elasticity']) for v in rows])
amp = np.array([float(v['amplitude']) for v in rows])
kind = [v['kind'] for v in rows]

# 刻度标签必须单行：双行标签实测占 92.6 px，而八行的行距只有 79.5 px，
# 必然上下穿插。符号写成 mathtext 还顺带绕开长标签的字符截断分支。
SHORT = {'act_scale': '活化温度 $E_a/R$', 'moist_scale': '水分抑制 $b$',
         'd_scale': '扩散前因子 $D_0$', 'h_m': '传质系数 $h_m$',
         'ta_plateau': '热风温度 $T_a$', 'C0': '初始含水率 $C_0$',
         'ca_plateau': '空气含湿 $C_a$', 'h': '换热系数 $h$'}
labels = []
for k, a, kd in zip(order, amp, kind):
    unit = '±%.0f °C' % a if kd == 'abs' else '±%.0f%%' % (100.0 * a)
    labels.append('%s %s' % (SHORT[k], unit))

y = np.arange(len(order))
fig, ax = plt.subplots(figsize=(6.7, 4.15), layout='constrained')

ax.barh(y - 0.185, low, height=0.33, left=0.0, color=C['blue_main'],
        edgecolor=C['neutral_black'], linewidth=0.5, zorder=3,
        label='参数取下界')
ax.barh(y + 0.185, high, height=0.33, left=0.0, color=C['red_strong'],
        edgecolor=C['neutral_black'], linewidth=0.5, zorder=3,
        label='参数取上界')
ax.axvline(0.0, color=C['neutral_black'], lw=1.0, zorder=4,
           label='基准 $t_{end}$=%.2f h' % base_h)

ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel('干燥时长相对基准的变化 / %')
ax.set_xlim(-46.0, 80.0)
ax.set_ylim(len(order) - 0.42, -0.58)
declutter_axes(ax, grid='on', grid_axis='x')

axe = ax.twiny()
pos = elas > 0
axe.plot(np.abs(elas[pos]), y[pos], ls='none', marker=M[0], ms=6.4,
         color=C['violet'], zorder=6, label='弹性 $e>0$')
axe.plot(np.abs(elas[~pos]), y[~pos], ls='none', marker=M[0], ms=6.4,
         mfc='none', mec=C['violet'], mew=1.5, zorder=6,
         label='弹性 $e<0$')
axe.set_xscale('log')
# 弹性绝对值真实跨 3.9 个量级（1.5e-3 ~ 11.2），坐标轴贴着数据给
axe.set_xlim(10 ** (np.floor(np.log10(np.abs(elas).min())) - 0.2),
             10 ** (np.ceil(np.log10(np.abs(elas).max())) + 0.9))
axe.set_ylim(ax.get_ylim())
axe.set_xlabel('归一化弹性 $|e|$（无量纲）')
axis_tint(axe, C['violet'], which='x')
axe.grid(False)

# 图例走右侧通道：顶部那条已被弹性副轴的刻度与轴标题占住，而副轴标签会随
# 保存钩子的字号放大一起长高，顶部通道放不下
legend_lane(fig, [ax, axe], where='right', ncol=1)
set_paper_placement(fig, 0.94)
finish(fig, 'fig_q3_sensitivity_tornado.png')
