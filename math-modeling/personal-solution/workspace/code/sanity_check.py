# code/sanity_check.py — 结果自检：只打印结论与至多 5 条违规样本，绝不回显数据体
import json

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P

MAX_SAMPLES = 5

# 出图清单对键名的硬需求：每张计划中的图都必须能在 JSON 里找到自己的数据块
FIGURE_KEYS = {
    'problem_1_results': ['air_input', 'temp_field_3d', 'profiles', 'semi_analytic',
                          'moisture_bl', 'mesh_ladder', 'timeseries', 'heatmap',
                          'characteristics', 'table_1_temperature', 'table_2_moisture',
                          'summary', 'checks'],
    'problem_2_results': ['timeseries', 'heatmap', 'profiles', 'model_ladder', 'mesh_ladder',
                          'D_response_surface', 'table_3_temperature', 'table_4_moisture',
                          'summary', 'checks'],
    'problem_3_results': ['drying_curve', 'heatmap', 'profiles', 'criterion_comparison',
                          'mesh_ladder', 'table_5_moisture', 't_end', 'summary', 'checks'],
    'problem_4_results': ['radius_curve', 'shrink_consistency', 'moving_boundary_frames',
                          'compare_q3', 'mass_balance', 'drying_curve', 'heatmap',
                          'attribution', 'table_6_moisture', 'summary', 'checks'],
    'sensitivity_results': ['oat', 'tornado', 'response_surface', 'lhs', 'lhs_q4',
                            'robustness_pair', 'latent_scan', 'baseline_q4', 'checks'],
    'all_results': ['headline', 'model_ladder', 'criterion_comparison', 'q4_attribution',
                    'cross_problem_ledger', 'checks'],
}

# FIGURE_MANIFEST 的 24 张 DATA 图 -> 各自赖以成图的 JSON 路径（点号分隔）。
# PROBLEM_ANALYSIS 第 6 步要求「数据齐备，禁止用占位数据画图」，故本步骤必须逐图坐实数据来源。
# HTML 流程图 5 张与 TikZ 机理图 3 张为示意性绘制，不消费数值，故不在此表。
FIGURE_DATA_MAP = {
    'fig_q1_air_input': ['problem_1_results.air_input.t_obs_s', 'problem_1_results.air_input.Ta_obs_C',
                         'problem_1_results.air_input.Ca_obs'],
    'fig_q1_temp_field_3d': ['problem_1_results.temp_field_3d.t_s', 'problem_1_results.temp_field_3d.r_cm',
                             'problem_1_results.temp_field_3d.T'],
    'fig_q1_profiles_frames': ['problem_1_results.profiles.times_s', 'problem_1_results.profiles.T',
                               'problem_1_results.profiles.C'],
    'fig_q1_validate_analytic': ['problem_1_results.semi_analytic.residual_C',
                                 'problem_1_results.semi_analytic.T_analytic_full',
                                 'problem_1_results.semi_analytic.r_cm'],
    'fig_q1_moisture_bl': ['problem_1_results.moisture_bl.depth_from_surface_cm',
                           'problem_1_results.moisture_bl.C_cells',
                           'problem_1_results.moisture_bl.penetration_depth_cm'],
    'fig_q1_grid_conv': ['problem_1_results.mesh_ladder'],
    'fig_q2_model_ladder': ['problem_2_results.model_ladder.paths'],
    'fig_q2_spacetime_heatmap': ['problem_2_results.heatmap.t_s', 'problem_2_results.heatmap.r_cm',
                                 'problem_2_results.heatmap.T', 'problem_2_results.heatmap.C'],
    'fig_q2_stage_compare': ['problem_2_results.table_3_temperature.values',
                             'problem_2_results.table_4_moisture.values'],
    'fig_q2_coupling_flux': ['problem_2_results.timeseries.q_conv_W_m2',
                             'problem_2_results.timeseries.j_mass_kg_m2_s'],
    'fig_q2_model_compare': ['problem_2_results.model_ladder.paths', 'problem_2_results.checks'],
    'fig_q2_D_response_surface': ['problem_2_results.D_response_surface.C_axis',
                                  'problem_2_results.D_response_surface.T_axis_C',
                                  'problem_2_results.D_response_surface.D_m2_s',
                                  'problem_2_results.D_response_surface.trajectory_C_T'],
    'fig_q3_drying_curve': ['problem_3_results.drying_curve.t_h', 'problem_3_results.drying_curve.C_max',
                            'problem_3_results.drying_curve.C_volavg'],
    'fig_q3_threshold_map': ['problem_3_results.heatmap.t_h', 'problem_3_results.heatmap.r_cm',
                             'problem_3_results.heatmap.C'],
    'fig_q3_uniformity': ['problem_3_results.profiles.times_s', 'problem_3_results.profiles.C'],
    'fig_q3_sensitivity_tornado': ['sensitivity_results.tornado.order',
                                   'sensitivity_results.tornado.by_factor'],
    'fig_q3_sensitivity_surface': ['sensitivity_results.response_surface.hm_mult',
                                   'sensitivity_results.response_surface.d0_mult',
                                   'sensitivity_results.response_surface.grid'],
    'fig_q34_robustness': ['sensitivity_results.robustness_pair.t_end_h_q3',
                           'sensitivity_results.robustness_pair.t_end_h_q4',
                           'sensitivity_results.lhs_q4.t_end_h'],
    'fig_q4_radius_fit': ['problem_4_results.radius_curve.R_data_cm',
                          'problem_4_results.radius_curve.R_pchip_cm',
                          'problem_4_results.radius_curve.R_weibull_cm',
                          'problem_4_results.radius_curve.dRdt_cm_per_s'],
    'fig_q4_shrink_consistency': ['problem_4_results.shrink_consistency.bland_altman.mean',
                                  'problem_4_results.shrink_consistency.bland_altman.diff',
                                  'problem_4_results.shrink_consistency.bland_altman.loa_upper'],
    'fig_q4_moving_boundary_frames': ['problem_4_results.moving_boundary_frames'],
    'fig_q4_compare_q3': ['problem_4_results.compare_q3.probe_cross_h_q3',
                          'problem_4_results.compare_q3.probe_cross_h_q4',
                          'problem_4_results.compare_q3.attribution_runs_h'],
    'fig_q4_mass_balance': ['problem_4_results.mass_balance.m_w_kg_per_m',
                            'problem_4_results.mass_balance.cumulative_loss_kg_per_m',
                            'problem_4_results.mass_balance.closure_rel_gap'],
    'fig_q4_3d_cylinder': ['problem_4_results.moving_boundary_frames'],
}

# 关键标量的物理区间：越界即为硬失败
RANGES = {
    ('problem_1_results', 'T_center_1800s'): (P.T0_C, 41.5130),
    ('problem_1_results', 'T_surface_1800s'): (P.T0_C, 41.5130),
    ('problem_1_results', 'C_center_1800s'): (P.C_THR, P.C0),
    ('problem_1_results', 'C_surface_1800s'): (0.0, P.C0),
    ('problem_1_results', 'herb_T_max'): (P.T0_C, 41.5130),
    ('problem_1_results', 'herb_T_min'): (P.T0_C - 1e-9, 41.5130),
    ('problem_1_results', 'herb_C_max'): (0.0, P.C0),
    ('problem_2_results', 'T_center_end'): (P.T0_C, 50.2460),
    ('problem_2_results', 'T_surface_end'): (P.T0_C, 50.2460),
    ('problem_2_results', 'C_center_end'): (P.C_THR, P.C0),
    ('problem_2_results', 'volavg_C_end'): (0.0, P.C0),
    ('problem_3_results', 't_end_h'): (1.0, 240.0),
    ('problem_3_results', 't_end_days'): (0.1 * P.DUR_DAYS_LOW, 10 * P.DUR_DAYS_HIGH),
    ('problem_4_results', 't_end_h'): (1.0, 240.0),
    ('problem_4_results', 't_end_days'): (0.1 * P.DUR_DAYS_LOW, 10 * P.DUR_DAYS_HIGH),
    ('problem_4_results', 'R_min_cm'): (1.198, P.R0_CM),
    ('problem_4_results', 'R_max_cm'): (1.198, P.R0_CM),
}


def _walk_numbers(node, path='', out=None, cap=200000):
    """遍历 JSON 里的全部数值，用于统一做有限性与 NaN 体检。"""
    if out is None:
        out = []
    if len(out) >= cap:
        return out
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_numbers(v, f'{path}.{k}', out, cap)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            _walk_numbers(v, f'{path}[{i}]', out, cap)
    elif isinstance(node, bool):
        pass
    elif isinstance(node, (int, float)):
        out.append((path, float(node)))
    return out


def _same_label(got, want):
    """表头比对：pandas 会把 '2.0' 读成数值 2.0（打印为 2），故数值列按数值比。"""
    a, b = str(got).strip(), str(want).strip()
    if a == b:
        return True
    try:
        return abs(float(a) - float(b)) < 1e-12
    except ValueError:
        return False


def check_xlsx():
    """写盘文件体检：行列数、表头口径、空白单元格分布（只报数字，不打印内容）。"""
    import pandas as pd
    rows = []
    spec = {1: (len(P.Q1_OUT_TIMES), 22, ['温度', '水分浓度'], '2.0'),
            2: (len(P.Q2_OUT_TIMES), 22, ['温度', '水分浓度'], '2.0'),
            3: (None, 22, ['Sheet1'], '2.0'),
            4: (None, 22, ['Sheet1'], P.SURFACE_LABEL)}
    for k, (n_rows, n_cols, sheets, last_col) in spec.items():
        xl = pd.ExcelFile(P.RESULT_FILES[k])
        got_sheets = list(xl.sheet_names)
        for sh in got_sheets:
            df = xl.parse(sh, header=0)
            body = df.iloc[:, 1:]
            n_blank = int(body.isna().to_numpy().sum())
            rows.append({'file': f'result{k}.xlsx', 'sheet': sh, 'n_rows': int(len(df)),
                         'n_cols': int(df.shape[1]),
                         'last_col': str(df.columns[-1]).strip(),
                         'n_blank_cells': n_blank,
                         'rows_ok': (n_rows is None or len(df) == n_rows),
                         'cols_ok': df.shape[1] == n_cols,
                         'last_col_ok': _same_label(df.columns[-1], last_col),
                         'sheets_ok': got_sheets == sheets,
                         'blank_ok': (n_blank == 0 if k != 4 else n_blank > 0)})
    return rows


def check_tables():
    """表 1—表 4 的内容判据（P1-C3、P2-C3）：行时刻、列位置、四位小数、逐格与 result*.xlsx 相符。

    能力项的 required_output 是 paper/main.md，属后续写稿步骤；本函数只核内容判据，
    使写稿步骤嵌入 figures/TABLE_*.md 后即可直接闭合，不必重算 PDE。
    """
    import re

    import pandas as pd
    spec = ((1, '温度', 'TABLE_1', P.Q1_TABLE_TIMES, 1.0),
            (1, '水分浓度', 'TABLE_2', P.Q1_TABLE_TIMES, 1.0),
            (2, '温度', 'TABLE_3', P.Q2_TABLE_TIMES, P.SEC_PER_HOUR),
            (2, '水分浓度', 'TABLE_4', P.Q2_TABLE_TIMES, P.SEC_PER_HOUR))
    rows = []
    for k, sheet, tag, want_t, mul in spec:
        lines = [ln for ln in (P.FIG_DIR / f'{tag}.md').read_text(encoding='utf-8').splitlines()
                 if ln.startswith('|')]
        hdr = [c.strip() for c in lines[0].strip('|').split('|')]
        body = [[c.strip() for c in ln.strip('|').split('|')] for ln in lines[2:]]
        df = pd.read_excel(P.RESULT_FILES[k], sheet_name=sheet)
        col_of = {}
        for c in df.columns[1:]:
            try:
                col_of[round(float(c), 6)] = c
            except (TypeError, ValueError):
                pass
        got_t = [float(r[0]) * mul for r in body]
        max_d, n_cmp = 0.0, 0
        for r, ts in zip(body, want_t):
            sub = df[np.abs(df[df.columns[0]] - ts) < 1e-9]
            if len(sub) != 1:
                max_d = float('inf')
                break
            for rc, v in zip(P.TABLE_R_CM, r[1:]):
                max_d = max(max_d, abs(float(v) - round(float(sub.iloc[0][col_of[round(rc, 6)]]),
                                                        P.DECIMALS)))
                n_cmp += 1
        rows.append({'tag': tag, 'file': f'result{k}.xlsx', 'sheet': sheet, 'n_cells': n_cmp,
                     'max_abs_diff': max_d,
                     'cols_ok': hdr[1:] == [f'r = {c:g} cm' for c in P.TABLE_R_CM],
                     'times_ok': (len(got_t) == len(want_t)
                                  and all(abs(a - b) < 1e-9 for a, b in zip(got_t, want_t))),
                     'decimals_ok': all(re.fullmatch(r'-?\d+\.\d{%d}' % P.DECIMALS, v)
                                        for r in body for v in r[1:]),
                     'cells_ok': max_d < 5e-13})
    return rows


def run():
    fails, notes = [], []
    print('=== JSON 结构与出图键位 ===')
    loaded = {}
    for name, keys in FIGURE_KEYS.items():
        p = P.FIG_DIR / f'{name}.json'
        if not p.exists():
            fails.append(f'{name}: 文件缺失')
            print(f'{name}: MISSING')
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        loaded[name] = d
        missing = [k for k in keys if k not in d]
        size_kb = p.stat().st_size / 1024.0
        print(f'{name}: {"OK" if not missing else "MISSING " + ",".join(missing[:MAX_SAMPLES])}'
              f'  ({len(d)} keys, {size_kb:.0f} KB)')
        if missing:
            fails.append(f'{name}: 缺键 {missing[:MAX_SAMPLES]}')

    print('\n=== 数值有限性（NaN/Inf 体检）===')
    for name, d in loaded.items():
        nums = _walk_numbers(d, name)
        bad = [(p2, v) for p2, v in nums if not np.isfinite(v)]
        print(f'{name}: {len(nums)} 个数值，非有限 {len(bad)} 个'
              + ('' if not bad else '  样本 ' + '; '.join(f'{p2}={v}' for p2, v in bad[:MAX_SAMPLES])))
        if bad:
            fails.append(f'{name}: {len(bad)} 个非有限数值')

    print('\n=== 关键标量物理区间 ===')
    for (name, key), (lo, hi) in RANGES.items():
        d = loaded.get(name)
        if d is None:
            continue
        src = d.get('summary', {})
        val = src.get(key, d.get('t_end', {}).get(key.replace('t_end_', '')
                                                  if key.startswith('t_end_') else key))
        if val is None:
            fails.append(f'{name}.summary.{key} 缺失')
            print(f'{name}.{key}: MISSING')
            continue
        ok = lo - 1e-9 <= float(val) <= hi + 1e-9
        print(f'{name}.{key} = {float(val):.6g}  [{lo:g}, {hi:g}]  {"OK" if ok else "OUT OF RANGE"}')
        if not ok:
            fails.append(f'{name}.{key}={val} 越界 [{lo}, {hi}]')

    print('\n=== 全部自检项汇总 ===')
    n_ck = n_pass = 0
    for name, d in loaded.items():
        if name == 'all_results':
            continue
        ck = d.get('checks', {})
        bad = [k for k, v in ck.items() if not v.get('passed')]
        n_ck += len(ck)
        n_pass += len(ck) - len(bad)
        print(f'{name}: {len(ck) - len(bad)}/{len(ck)} passed'
              + ('' if not bad else '  FAILED: ' + ','.join(bad[:MAX_SAMPLES])))
        if bad:
            fails.append(f'{name}: 自检失败 {bad[:MAX_SAMPLES]}')
    print(f'合计 {n_pass}/{n_ck}')

    print('\n=== 竞赛结果文件 ===')
    for r in check_xlsx():
        flags = [k for k in ('rows_ok', 'cols_ok', 'last_col_ok', 'sheets_ok', 'blank_ok')
                 if not r[k]]
        print(f"{r['file']}[{r['sheet']}]: {r['n_rows']} 行 x {r['n_cols']} 列，末列 "
              f"{r['last_col']}，空白 {r['n_blank_cells']}  {'OK' if not flags else 'BAD ' + ','.join(flags)}")
        if flags:
            fails.append(f"{r['file']}[{r['sheet']}]: {flags}")

    print('\n=== FIGURE_MANIFEST 24 张 DATA 图的数据齐备性 ===')
    bad_fig = []
    for fig, paths in FIGURE_DATA_MAP.items():
        miss = []
        for dotted in paths:
            head, *rest = dotted.split('.')
            node = loaded.get(head)
            for seg in rest:
                node = node.get(seg) if isinstance(node, dict) else None
                if node is None:
                    break
            if node is None or (isinstance(node, (list, dict, str)) and len(node) == 0):
                miss.append(dotted)
        if miss:
            bad_fig.append((fig, miss))
    print(f'{len(FIGURE_DATA_MAP)} 张图，数据齐备 {len(FIGURE_DATA_MAP) - len(bad_fig)} 张')
    for fig, miss in bad_fig[:MAX_SAMPLES]:
        print(f'  MISSING {fig}: {miss[:3]}')
        fails.append(f'{fig} 缺数据 {miss[:3]}')

    print('\n=== 论文表 1—表 4 内容判据（P1-C3、P2-C3）===')
    for r in check_tables():
        flags = [k for k in ('cols_ok', 'times_ok', 'decimals_ok', 'cells_ok') if not r[k]]
        print(f"{r['tag']} vs {r['file']}[{r['sheet']}]: 逐格 {r['n_cells']} 点，"
              f"最大差 {r['max_abs_diff']:.3e}  {'OK' if not flags else 'BAD ' + ','.join(flags)}")
        if flags:
            fails.append(f"{r['tag']}: {flags}")

    print('\n=== 跨问题台账 ===')
    lp = P.ROOT / 'CROSS_PROBLEM_LEDGER.json'
    if lp.exists():
        led = json.loads(lp.read_text(encoding='utf-8'))
        n_obs = sum(1 for it in led['items'] if it.get('observed') is not None)
        print(f"{led['n_items']} 项，observed 已回填 {n_obs} 项，违规 {len(led['violations'])} 项"
              + ('' if not led['violations'] else '  ' + ','.join(led['violations'][:MAX_SAMPLES])))
        if led['violations']:
            fails.append(f"台账违规 {led['violations'][:MAX_SAMPLES]}")
        if n_obs != led['n_items']:
            fails.append('台账 observed 未全部回填')
        if not led['module_available']:
            notes.append('_utils/cross_problem_check.py 不存在（已如实记录模块名）')
    else:
        fails.append('CROSS_PROBLEM_LEDGER.json 缺失')

    print('\n=== 结论 ===')
    for n in notes:
        print('NOTE:', n)
    if fails:
        print('SANITY FAIL（%d 项）：' % len(fails))
        for f in fails[:MAX_SAMPLES]:
            print('  -', f)
    else:
        print('SANITY OK：结构、数值、区间、自检、写盘、台账全部通过')
    return fails


if __name__ == '__main__':
    raise SystemExit(1 if run() else 0)
