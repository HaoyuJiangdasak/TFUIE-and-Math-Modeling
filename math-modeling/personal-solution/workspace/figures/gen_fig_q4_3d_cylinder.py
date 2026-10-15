# -*- coding: utf-8 -*-
"""问题四四帧圆柱三维剖切渲染：外壁与剖面按含水率着色，半径按真实值缩放。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from _figcommon import (C, load, finish, set_paper_placement, legend_lane,
                        panel_tag, proxy_line, CMAP_MOIST)

p4 = load('problem_4_results.json')
frames = p4['moving_boundary_frames']
R0 = float(p4['radius_curve']['R_data_cm'][0])

want = [12.0, 24.0, 36.0, 48.0]
sel = [min(frames, key=lambda f, w=w: abs(float(f['t_h']) - w)) for w in want]

allC = np.concatenate([np.asarray(f['C'], float) for f in sel])
norm = LogNorm(vmin=allC.min(), vmax=allC.max())
L = 6.0                                   # 只渲染 25 cm 柱体中的一段
TH_CUT = 1.5 * np.pi                      # 剖去 90° 楔形以露出内部
th = np.linspace(0.0, TH_CUT, 64)
zz = np.linspace(0.0, L, 12)

fig = plt.figure(figsize=(7.0, 4.9), layout='constrained')
gs = GridSpec(2, 3, figure=fig, width_ratios=[1.0, 1.0, 0.052], wspace=0.02)

for k, fr in enumerate(sel):
    ax = fig.add_subplot(gs[k // 2, k % 2], projection='3d')
    r = np.asarray(fr['r_cm'], float)
    Cp = np.asarray(fr['C'], float)
    R = float(fr['R_cm'])
    rr = np.linspace(r.min(), R, 44)
    Cr = np.interp(rr, r, Cp)

    TH, ZZ = np.meshgrid(th, zz, indexing='xy')
    wall = np.full(TH.shape, Cp[-1])
    ax.plot_surface(R * np.cos(TH), R * np.sin(TH), ZZ, rstride=1, cstride=1,
                    facecolors=CMAP_MOIST(norm(wall)), linewidth=0.0,
                    antialiased=True, shade=False, zorder=2)

    RR, TT = np.meshgrid(rr, th, indexing='xy')
    top = CMAP_MOIST(norm(np.tile(Cr, (th.size, 1))))
    ax.plot_surface(RR * np.cos(TT), RR * np.sin(TT), np.full(RR.shape, L),
                    rstride=1, cstride=1, facecolors=top, linewidth=0.0,
                    antialiased=True, shade=False, zorder=3)

    RC, ZC = np.meshgrid(rr, zz, indexing='xy')
    face = CMAP_MOIST(norm(np.tile(Cr, (zz.size, 1))))
    for ang in (0.0, TH_CUT):
        ax.plot_surface(RC * np.cos(ang), RC * np.sin(ang), ZC, rstride=1,
                        cstride=1, facecolors=face, linewidth=0.0,
                        antialiased=True, shade=False, zorder=4)

    ax.plot(R0 * np.cos(th), R0 * np.sin(th), np.full(th.size, L),
            color=C['neutral_dark'], lw=1.0, ls=':', zorder=5)

    ax.set_xlim(-R0 * 1.05, R0 * 1.05)
    ax.set_ylim(-R0 * 1.05, R0 * 1.05)
    ax.set_zlim(0.0, L)
    ax.set_xlabel('$x$ / cm')
    ax.set_ylabel('$y$ / cm')
    ax.set_zticks([])
    ax.set_box_aspect((1.0, 1.0, 0.78))
    ax.view_init(elev=21, azim=-58)
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    panel_tag(ax, '%s  $t$=%d h，$R$=%.3f cm'
              % ('abcd'[k], int(round(fr['t_h'])), R))
    if k == 0:
        proxy_line(ax, '外壁：表面含水率', color=C['blue_main'], lw=2.0)
        proxy_line(ax, '剖面：径向含水率分布', color=C['teal'], lw=2.0, ls='--')
        proxy_line(ax, '初始半径 $R_0$=%.1f cm 参考轮廓' % R0,
                   color=C['neutral_dark'], lw=1.0, ls=':')

cax = fig.add_subplot(gs[:, 2])
cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP_MOIST), cax=cax)
cb.set_label('含水率 $C$ / (kg/kg)（四帧共用对数标尺）')

legend_lane(fig, [fig.axes[0]], where='top', ncol=3)
set_paper_placement(fig, 0.96)
finish(fig, 'fig_q4_3d_cylinder.png')
