# -*- coding: utf-8 -*-
"""问题二表面对流热流与蒸发质流的面积时程，量化热-质耦合强度。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, load, finish, set_paper_placement, legend_lane,
                        axis_tint, panel_tag, declutter_axes)

p2 = load('problem_2_results.json')
ts = p2['timeseries']
t = np.asarray(ts['t_s'], float) / 60.0
q = np.asarray(ts['q_conv_W_m2'], float)
# JSON 键名 j_mass_kg_m2_s 沿用历史写法，其存储量实为 h_m(C_s-C_a)，
# 量纲为 (m/s)·(kg/kg)，即单位干骨架质量的比蒸发通量；此处按该量纲作图
j = np.asarray(ts['j_mass_kg_m2_s'], float) * 1e6
T_surf = np.asarray(ts['T_surf_recon'], float)
C_surf = np.asarray(ts['C_surf_recon'], float)

# 累积量由通量对时间积分得到，作为耦合总量的度量
t_s = np.asarray(ts['t_s'], float)
Q_cum = np.concatenate([[0.0], np.cumsum(0.5 * (q[1:] + q[:-1]) * np.diff(t_s))])
J_cum = np.concatenate([[0.0], np.cumsum(0.5 * (j[1:] + j[:-1]) * np.diff(t_s))])
Q_cum = Q_cum / 1e3                                    # kJ/m²
J_cum = J_cum / 1e3                                    # 比蒸发通量的时间积分

fig = plt.figure(figsize=(7.3, 3.2), layout='constrained')
gs = GridSpec(1, 2, figure=fig)

ax0 = fig.add_subplot(gs[0, 0])
ax0b = ax0.twinx()
ax0.fill_between(t, 0.0, q, color=C['red_2'], alpha=0.75, zorder=1,
                 label='对流热流密度 $q_{conv}$')
ax0.plot(t, q, color=C['red_strong'], lw=1.7, zorder=3)
ax0b.plot(t, Q_cum, color=C['neutral_dark'], lw=1.6, ls='--', zorder=3,
          label='累积供热量 $\\int q\\,dt$')
ax0.set_xlabel('时间 $t$ / min')
ax0.set_ylabel('$q_{conv}$ / (W·m$^{-2}$)')
ax0b.set_ylabel('累积供热 / (kJ·m$^{-2}$)')
axis_tint(ax0, C['red_strong'])
axis_tint(ax0b, C['neutral_dark'])
ax0.set_xlim(0, t.max())
ax0.set_ylim(0, q.max() * 1.08)
ax0b.set_ylim(0, Q_cum.max() * 1.08)
ax0b.grid(False)
declutter_axes(ax0, grid='on', grid_axis='both')
panel_tag(ax0, 'a  热流')

ax1 = fig.add_subplot(gs[0, 1])
ax1b = ax1.twinx()
ax1.fill_between(t, 0.0, j, color=C['green_2'], alpha=0.8, zorder=1,
                 label='比蒸发通量 $h_m\\Delta C$')
ax1.plot(t, j, color=C['teal'], lw=1.7, zorder=3)
ax1b.plot(t, J_cum, color=C['blue_main'], lw=1.6, ls='--', zorder=3,
          label='比蒸发通量的累积 $\\int h_m\\Delta C\\,dt$')
ax1.set_xlabel('时间 $t$ / min')
ax1.set_ylabel('$h_m\\Delta C$ / $10^{-6}$(m·s$^{-1}$)(kg/kg)')
ax1b.set_ylabel('累积 / $10^{-3}$(m)(kg/kg)')
axis_tint(ax1, C['teal'])
axis_tint(ax1b, C['blue_main'])
ax1.set_xlim(0, t.max())
ax1.set_ylim(0, j.max() * 1.08)
ax1b.set_ylim(0, J_cum.max() * 1.08)
ax1b.grid(False)
declutter_axes(ax1, grid='on', grid_axis='both')
panel_tag(ax1, 'b  质流')

legend_lane(fig, [ax0, ax0b, ax1, ax1b], where='top', ncol=2)
set_paper_placement(fig, 1.0)
finish(fig, 'fig_q2_coupling_flux.png')
