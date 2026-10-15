# -*- coding: utf-8 -*-
"""问题一预热段温度场 T(r,t) 三维曲面 + 底面等值线投影（全域 / 中心区放大）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

from _figcommon import (C, load, finish, set_paper_placement, panel_tag,
                        CMAP_HEAT)

p1 = load('problem_1_results.json')
f3 = p1['temp_field_3d']

t_min = np.asarray(f3['t_s'], float) / 60.0
r_cm = np.asarray(f3['r_cm'], float)
T = np.asarray(f3['T'], float)          # (n_t, n_r)
Rg, Tg = np.meshgrid(r_cm, t_min, indexing='xy')

zmin, zmax = float(T.min()), float(T.max())
floor = zmin - 0.14 * (zmax - zmin)

fig = plt.figure(figsize=(7.3, 3.35), layout='constrained')
gs = GridSpec(1, 3, figure=fig, width_ratios=[1.0, 1.0, 0.055])

ax0 = fig.add_subplot(gs[0, 0], projection='3d')
ax0.plot_surface(Rg, Tg, T, cmap=CMAP_HEAT, vmin=zmin, vmax=zmax,
                 rstride=1, cstride=1, linewidth=0, antialiased=True,
                 alpha=0.97)
ax0.contour(Rg, Tg, T, levels=9, zdir='z', offset=floor, cmap=CMAP_HEAT,
            vmin=zmin, vmax=zmax, linewidths=0.75)
ax0.set_xlim(0, r_cm.max())
ax0.set_zlim(floor, zmax)
ax0.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
ax0.set_xlabel('径向坐标 $r$ / cm', labelpad=-1)
ax0.set_ylabel('时间 $t$ / min', labelpad=-1)
ax0.set_zlabel('温度 $T$ / °C', labelpad=-2)
ax0.view_init(elev=22, azim=-127)
ax0.tick_params(pad=-1.5)
panel_tag(ax0, 'a  全域 $r\\in[0,2]$ cm')

# 中心区放大：只取内层 1/4 半径，凸显预热期中心几乎不动
mask = r_cm <= 0.5 + 1e-9
r_in = r_cm[mask]
T_in = T[:, mask]
Rin, Tin = np.meshgrid(r_in, t_min, indexing='xy')
zin_min, zin_max = float(T_in.min()), float(T_in.max())
floor_in = zin_min - 0.14 * (zin_max - zin_min)

ax1 = fig.add_subplot(gs[0, 1], projection='3d')
ax1.plot_surface(Rin, Tin, T_in, cmap=CMAP_HEAT, vmin=zin_min, vmax=zin_max,
                 rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.97)
ax1.contour(Rin, Tin, T_in, levels=8, zdir='z', offset=floor_in, cmap=CMAP_HEAT,
            vmin=zin_min, vmax=zin_max, linewidths=0.75)
ax1.set_xlim(0, r_in.max())
ax1.set_zlim(floor_in, zin_max)
ax1.set_xticks([0.0, 0.25, 0.5])
ax1.set_xlabel('径向坐标 $r$ / cm', labelpad=-1)
ax1.set_ylabel('时间 $t$ / min', labelpad=-1)
ax1.set_zlabel('温度 $T$ / °C', labelpad=-2)
ax1.view_init(elev=22, azim=-127)
ax1.tick_params(pad=-1.5)
panel_tag(ax1, 'b  中心区 $r\\in[0,0.5]$ cm')

cax = fig.add_subplot(gs[0, 2])
mappable = plt.cm.ScalarMappable(cmap=CMAP_HEAT)
mappable.set_clim(zmin, zmax)
cb = fig.colorbar(mappable, cax=cax)
cb.set_label('温度 $T$ / °C')

set_paper_placement(fig, 1.0)
finish(fig, 'fig_q1_temp_field_3d.png')
