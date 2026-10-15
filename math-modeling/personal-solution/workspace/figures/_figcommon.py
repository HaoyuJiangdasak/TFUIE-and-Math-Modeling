# -*- coding: utf-8 -*-
"""Nature 风格数据图公用样板：路径、样式、配色、产物读取、保存。"""
import json
import os
import sys

import numpy as np
import matplotlib

matplotlib.use('Agg')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FIGDIR = os.path.join(ROOT, 'figures')

from _utils.plot_utils import (  # noqa: E402
    setup_style, save_fig, set_paper_placement, auto_legend, shared_legend,
    consolidate_shared_legends, uncertainty_band, dynamic_limits,
    declutter_axes, draw_vector_heatmap, nature_palette, nature_markers,
    smart_labels,
)

setup_style(palette='nature')
C = nature_palette()
M = nature_markers()

SEQ = [C['blue_main'], C['red_strong'], C['teal'], C['green_3'], C['gold'],
       C['violet'], C['blue_secondary'], C['neutral_mid']]


def load(name):
    """读取 figures/ 下的 JSON 产物；缺失即报错，绝不返回空字典。"""
    path = os.path.join(FIGDIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def _gather(axes):
    handles, labels, seen = [], [], set()
    for ax in axes:
        hh, ll = ax.get_legend_handles_labels()
        for h, l in zip(hh, ll):
            l = str(l).strip()
            if not l or l.startswith('_') or l in seen:
                continue
            seen.add(l)
            handles.append(h)
            labels.append(l)
    return handles, labels


def panel_legend(ax, extra_axes=(), proxies=(), **kw):
    """面板内合并图例（含 twin 轴系列与代理图元），交由 auto_legend 实测避让。"""
    handles, labels = _gather([ax] + list(extra_axes))
    for handle, label in proxies:
        handles.append(handle)
        labels.append(label)
    if not handles:
        return None
    return auto_legend(ax, handles=handles, labels=labels, **kw)


def legend_lane(fig, axes, *, where='top', ncol=None, **kw):
    """图级共享图例通道：为图例预留独立行/列，不压数据。"""
    axes = list(axes)
    handles, labels = _gather(axes)
    if not handles:
        return None
    if ncol is None:
        ncol = min(len(labels), 4)
    return shared_legend(fig, axes, where=where, ncol=ncol, **kw)


def proxy_patch(ax, color, label, *, edgecolor=None, hatch=None):
    """空面片代理：只为图例登记一个色块，不在数据区留下任何图元。"""
    return ax.fill_between([], [], [], facecolor=color, label=label,
                           edgecolor=edgecolor or C['neutral_light'],
                           linewidth=0.6, hatch=hatch)


def proxy_line(ax, label, **kw):
    """空线条代理：为图例登记一条线型，不落在数据区。"""
    return ax.plot([], [], label=label, **kw)[0]


def axis_tint(ax, color, which='y'):
    """把某一坐标轴的标签与刻度染成对应系列的颜色（双轴可读性）。"""
    if which == 'y':
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)
    else:
        ax.xaxis.label.set_color(color)
        ax.tick_params(axis='x', colors=color)


def panel_tag(ax, text, *, size=10.5):
    """面板标签走 set_title(loc='left')：由布局引擎托管，天然不压数据。"""
    ax.set_title(text, loc='left', fontsize=size, fontweight='bold',
                 color=C['neutral_black'], pad=3.0)


def _cmap(name, colors):
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(name, colors, N=256)


# 全部由 nature_palette() 运行时取色派生，不出现任何硬编码色值
CMAP_MOIST = _cmap('mh_moist', [C['green_1'], C['green_2'], C['green_3'],
                                C['teal'], C['blue_secondary'], C['blue_main']])
CMAP_HEAT = _cmap('mh_heat', [C['red_1'], C['red_2'], C['gold'],
                              C['red_strong'], C['violet'], C['neutral_black']])
CMAP_DIV = _cmap('mh_div', [C['blue_main'], C['blue_secondary'], C['green_1'],
                            C['red_2'], C['red_strong']])


def time_colors(n):
    """按时间序列取 n 个渐深色，供多帧曲线着色。

    起点不低于 0.34：色标低端是 green_1（极浅），画成线条后在白底上几乎看不见，
    图例色样也就无法与曲线对应。
    """
    return [CMAP_MOIST(v) for v in np.linspace(0.34, 0.97, n)]


def finish(fig, filename):
    save_fig(fig, os.path.join(FIGDIR, filename))
    print('[ok] ' + filename)
