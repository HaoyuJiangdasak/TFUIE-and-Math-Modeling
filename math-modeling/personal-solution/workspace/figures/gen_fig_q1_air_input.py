# -*- coding: utf-8 -*-
"""附件 1 热风温度与空气含湿量双轴时程（问题一窗口 + 全 3 h 窗口）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        axis_tint, panel_tag, declutter_axes, proxy_patch)

p1 = load('problem_1_results.json')
p2 = load('problem_2_results.json')

ai = p1['air_input']
t_obs = np.asarray(ai['t_obs_s'], float) / 60.0
Ta_obs = np.asarray(ai['Ta_obs_C'], float)
Ca_obs = np.asarray(ai['Ca_obs'], float)
t_in = np.asarray(ai['t_interp_s'], float) / 60.0
Ta_in = np.asarray(ai['Ta_interp_C'], float)
Ca_in = np.asarray(ai['Ca_interp'], float)

ts = p2['timeseries']
t2 = np.asarray(ts['t_s'], float) / 60.0
Ta2 = np.asarray(ts['Ta'], float)
Ca2 = np.asarray(ts['Ca'], float)

# 平台判据：首次进入终段均值 ±0.5 °C 邻域后不再离开
Ta_bar = float(Ta2[t2 >= 150.0].mean())
Ca_bar = float(Ca2[t2 >= 150.0].mean())
inside = np.abs(Ta2 - Ta_bar) <= 0.5
k = len(inside) - 1
while k > 0 and inside[k - 1]:
    k -= 1
t_split = float(t2[k])

fig = plt.figure(figsize=(7.3, 3.25), layout='constrained')
fig.get_layout_engine().set(w_pad=0.05, wspace=0.10)
gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.15])

ax0 = fig.add_subplot(gs[0, 0])
ax0b = ax0.twinx()
ax0.plot(t_in, Ta_in, color=C['blue_main'], lw=1.9, zorder=3, label='$T_a$ 插值')
ax0.plot(t_obs, Ta_obs, ls='none', marker=M[0], ms=3.8, mfc='none',
         mec=C['blue_main'], mew=1.0, zorder=4, label='$T_a$ 实测')
ax0b.plot(t_in, Ca_in, color=C['red_strong'], lw=1.9, ls='--', zorder=3,
          label='$C_a$ 插值')
ax0b.plot(t_obs, Ca_obs, ls='none', marker=M[2], ms=3.6, mfc='none',
          mec=C['red_strong'], mew=1.0, zorder=4, label='$C_a$ 实测')
ax0.set_xlabel('时间 $t$ / min')
ax0.set_ylabel('热风温度 / °C')
ax0b.set_ylabel('含湿量 / (kg/kg)')
axis_tint(ax0, C['blue_main'])
axis_tint(ax0b, C['red_strong'])
ax0.set_xlim(0, 30)
ax0.set_ylim(26.5, 44.5)
ax0b.set_ylim(0.018, 0.0375)
ax0b.grid(False)
declutter_axes(ax0, grid='on', grid_axis='both')

panel_tag(ax0, 'a')

ax1 = fig.add_subplot(gs[0, 1])
ax1b = ax1.twinx()
ax1.axvspan(0, t_split, ymin=0.0, ymax=0.045, color=C['green_2'], zorder=1)
ax1.axvspan(t_split, t2[-1], ymin=0.0, ymax=0.045, color=C['red_2'], zorder=1)
ax1.plot(t2, Ta2, color=C['blue_main'], lw=1.8, zorder=3, label='$T_a$ 插值')
ax1b.plot(t2, Ca2, color=C['red_strong'], lw=1.8, ls='--', zorder=3,
          label='$C_a$ 插值')
ax1.axhline(Ta_bar, color=C['neutral_dark'], lw=1.0, ls=':', zorder=2,
            label='$T_a$ 平台均值')
ax1.axvline(t_split, color=C['neutral_dark'], lw=1.0, zorder=2)
ax1.set_xticks([0, 60, round(t_split), 180])
ax1.set_xlabel('时间 $t$ / min')
ax1.set_ylabel('热风温度 / °C')
ax1b.set_ylabel('含湿量 / (kg/kg)')
axis_tint(ax1, C['blue_main'])
axis_tint(ax1b, C['red_strong'])
ax1.set_xlim(0, t2[-1])
ax1.set_ylim(26.0, 53.5)
ax1b.set_ylim(0.017, 0.0565)
ax1b.grid(False)
declutter_axes(ax1, grid='on', grid_axis='both')
panel_tag(ax1, 'b')

proxy_patch(ax1, C['green_2'], '升温段')
proxy_patch(ax1, C['red_2'], '平台段')
legend_lane(fig, [ax0, ax0b, ax1, ax1b], where='top', ncol=4, fontsize=8.4)
set_paper_placement(fig, 1.0)
finish(fig, 'fig_q1_air_input.png')
