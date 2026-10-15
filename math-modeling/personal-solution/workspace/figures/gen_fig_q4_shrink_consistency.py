# -*- coding: utf-8 -*-
"""几何体积比与密度式推断体积比的 Bland-Altman 一致性检验。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.pyplot as plt

from _figcommon import (C, M, load, finish, set_paper_placement, legend_lane,
                        declutter_axes, CMAP_MOIST)

p4 = load('problem_4_results.json')
ba = p4['shrink_consistency']['bland_altman']
mean = np.asarray(ba['mean'], float)
diff = np.asarray(ba['diff'], float)
cv = np.asarray(ba['volavg_C'], float)
vg = np.asarray(ba['volume_ratio_geometric'], float)
vd = np.asarray(ba['volume_ratio_from_density'], float)
bias = float(ba['bias'])
sd = float(ba['sd_diff'])
lo = float(ba['loa_lower'])
hi = float(ba['loa_upper'])
n = int(ba['n_pairs'])
n_out = int(ba['n_outside_loa'])

fig, ax = plt.subplots(figsize=(6.6, 3.95), layout='constrained')
norm = Normalize(vmin=cv.min(), vmax=cv.max())
ax.scatter(mean, diff, c=cv, cmap=CMAP_MOIST, norm=norm, s=26.0,
           edgecolor=C['neutral_dark'], linewidth=0.4, zorder=4,
           label='配对样本（%d 对，按体积平均含水率着色）' % n)
ax.axhline(bias, color=C['red_strong'], lw=1.6, zorder=3,
           label='系统偏差 $\\bar{d}$=%.4f' % bias)
ax.axhline(hi, color=C['blue_main'], lw=1.2, ls='--', zorder=3,
           label='95%% 一致性界 [%.4f, %.4f]' % (lo, hi))
ax.axhline(lo, color=C['blue_main'], lw=1.2, ls='--', zorder=3)
ax.axhline(0.0, color=C['neutral_dark'], lw=0.9, ls=':', zorder=2,
           label='零偏差参考线')
out = (diff > hi) | (diff < lo)
ax.plot(mean[out], diff[out], ls='none', marker=M[4], ms=9.0, mfc='none',
        mec=C['violet'], mew=1.5, zorder=5,
        label='界外点 %d 个，占 %.1f%%' % (n_out, 100.0 * n_out / n))

ax.set_xlabel('两路径体积比均值 $(V_g+V_\\rho)/2$')
ax.set_ylabel('体积比之差 $V_\\rho-V_g$')
ax.set_xlim(0.33, 1.03)
ax.set_ylim(-0.055, 0.215)
declutter_axes(ax, grid='on', grid_axis='both')
cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP_MOIST), ax=ax,
                  pad=0.02, aspect=24)
cb.set_label('体积平均含水率 $\\bar{C}$ / (kg/kg)')

axi = ax.inset_axes([0.115, 0.545, 0.375, 0.40])
axi.plot([0.3, 1.05], [0.3, 1.05], color=C['neutral_dark'], lw=1.0, ls=':')
axi.scatter(vg, vd, c=cv, cmap=CMAP_MOIST, norm=norm, s=13.0,
            edgecolor=C['neutral_dark'], linewidth=0.3)
axi.set_xlabel('几何 $V_g$')
axi.set_ylabel('密度式 $V_\\rho$')
axi.set_xlim(0.33, 1.03)
axi.set_ylim(0.33, 1.03)
axi.set_aspect('equal')
axi.grid(True, alpha=0.28)

legend_lane(fig, [ax], where='top', ncol=3)
set_paper_placement(fig, 0.92)
finish(fig, 'fig_q4_shrink_consistency.png')
