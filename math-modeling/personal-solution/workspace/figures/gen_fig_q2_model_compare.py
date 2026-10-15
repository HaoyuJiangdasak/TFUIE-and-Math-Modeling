# -*- coding: utf-8 -*-
"""四级模型阶梯 × 六项指标的方法对比热图（相对全耦合基准的偏差）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figcommon import (C, load, finish, set_paper_placement,
                        draw_vector_heatmap, CMAP_DIV)

allr = load('all_results.json')
p2 = load('problem_2_results.json')
paths = allr['model_ladder']['paths']
ladder = p2['mesh_ladder']

ref = paths['L3_full']
ref_vals = {
    'C_center_end': float(ref['C_center_end']),
    'C_surface_end': float(ref['C_surface_end']),
    'volavg_C_end': float(ref['volavg_C_end']),
    'T_center_end': float(ref['T_center_end']),
}
# 第五行：全耦合模型在最粗网格上的解，衡量离散误差与建模误差的量级差
coarse = ladder[0]
coarse_vals = {
    'C_center_end': float(coarse['C_center_end']),
    'C_surface_end': float(coarse['C_surface_end']),
    'volavg_C_end': np.nan,
    'T_center_end': float(coarse['T_center_end']),
}

rows = []
row_labels = []


def rel(value, key):
    if not np.isfinite(value):
        return np.nan
    return 100.0 * (value - ref_vals[key]) / ref_vals[key]


for key, label in [('L0_lumped', 'L0 集中参数'),
                   ('L1_const_prop', 'L1 常物性常扩散'),
                   ('L2_oneway', 'L2 变扩散单向解耦'),
                   ('L3_full', 'L3 全耦合（本文）')]:
    node = paths[key]
    if key == 'L0_lumped':
        cc = cs = va = float(node['C_end'])
        tc = float(node['T_end'])
        series = np.asarray(node['C_series'], float)
    else:
        cc = float(node['C_center_end'])
        cs = float(node['C_surface_end'])
        va = float(node['volavg_C_end'])
        tc = float(node['T_center_end'])
        series = np.asarray(node['volavg_C_series'], float)
    # 径向不均匀度：中心与表面之差；轨迹偏差：全时段体积平均含水率的 RMSE
    ref_series = np.asarray(paths['L3_full']['volavg_C_series'], float)
    rmse = float(np.sqrt(np.mean((series - ref_series) ** 2)))
    rows.append([rel(cc, 'C_center_end'), rel(cs, 'C_surface_end'),
                 rel(va, 'volavg_C_end'), rel(tc, 'T_center_end'),
                 100.0 * ((cc - cs) - (ref_vals['C_center_end'] - ref_vals['C_surface_end']))
                 / (ref_vals['C_center_end'] - ref_vals['C_surface_end']),
                 100.0 * rmse / ref_vals['volavg_C_end']])
    row_labels.append(label)

rows.append([rel(coarse_vals['C_center_end'], 'C_center_end'),
             rel(coarse_vals['C_surface_end'], 'C_surface_end'),
             np.nan,
             rel(coarse_vals['T_center_end'], 'T_center_end'),
             100.0 * ((coarse_vals['C_center_end'] - coarse_vals['C_surface_end'])
                      - (ref_vals['C_center_end'] - ref_vals['C_surface_end']))
             / (ref_vals['C_center_end'] - ref_vals['C_surface_end']),
             np.nan])
row_labels.append('L3 粗网格 $N$=%d' % int(coarse['N']))

data = np.asarray(rows, float)
mask = ~np.isfinite(data)
col_labels = ['中心含水率', '表面含水率', '体积平均含水率', '中心温度',
              '径向不均匀度', '全程轨迹 RMSE']

lim = float(np.nanmax(np.abs(data)))

fig, ax = plt.subplots(figsize=(6.9, 3.0), layout='constrained')
draw_vector_heatmap(ax, data, xlabels=col_labels, ylabels=row_labels,
                    mask=mask, annot=True, fmt='.2f', cmap=CMAP_DIV,
                    vmin=-lim, vmax=lim, center=0.0, cbar=True,
                    cbar_label='相对 L3 全耦合基准的偏差 / %')
ax.set_frame_on(False)
set_paper_placement(fig, 0.98)
finish(fig, 'fig_q2_model_compare.png')
