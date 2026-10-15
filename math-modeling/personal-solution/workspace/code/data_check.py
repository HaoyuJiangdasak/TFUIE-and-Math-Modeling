# code/data_check.py — 第 0 层：读盘与口径核验（V0.1—V0.5），只打印结论
import json

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P

TOL_STEP = 1e-9


def load_attachment1():
    df = pd.read_excel(P.ATT1_XLSX, sheet_name=0)
    df.columns = ['t_s', 'Ta_C', 'Ca']
    return df.astype(float)


def load_attachment2():
    df = pd.read_excel(P.ATT2_XLSX, sheet_name=0)
    df.columns = ['t_s', 'R_cm']
    return df.astype(float)


def plateau_stats(df1):
    m = df1['t_s'].to_numpy() >= P.PLATEAU_WINDOW_START
    return int(m.sum()), float(df1['Ta_C'].to_numpy()[m].mean()), float(df1['Ca'].to_numpy()[m].mean())


def template_signature(path, sheet):
    """模板为示意式：表头 0.0,0.1,0.2,…,末列，时间列 1,2,3,… —— '…' 表示按步长续排。"""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header = [str(v).strip() for v in raw.iloc[0].tolist()]
    times = [str(v).strip() for v in raw.iloc[1:, 0].tolist()]
    return {'n_cols': len(header), 'corner': header[0], 'r_head': header[1:4],
            'ellipsis_col': header[4], 'last_header': header[-1],
            'time_head': times[:3], 'time_ellipsis': times[-1]}


def run():
    res, fails = {}, []

    df1, df2 = load_attachment1(), load_attachment2()
    d1 = np.diff(df1['t_s'].to_numpy())
    v01 = (len(df1) == 241 and np.all(np.abs(d1 - 60.0) < TOL_STEP)
           and abs(df1['t_s'].iloc[-1] - 14400.0) < TOL_STEP
           and abs(df1['Ta_C'].iloc[-1] - 50.165) < 5e-4
           and abs(df1['Ca'].iloc[-1] - 0.04986) < 5e-6)
    res['V0.1'] = {'passed': bool(v01), 'n_rows': int(len(df1)), 'step_s': float(d1[0]),
                   'last_point': [float(df1['t_s'].iloc[-1]), float(df1['Ta_C'].iloc[-1]), float(df1['Ca'].iloc[-1])],
                   'Ta_peak': float(df1['Ta_C'].max()), 'Ca_peak': float(df1['Ca'].max()),
                   'Ta_peak_t': float(df1.loc[df1['Ta_C'].idxmax(), 't_s'])}

    d2 = np.diff(df2['t_s'].to_numpy())
    dR = np.diff(df2['R_cm'].to_numpy())
    v02 = (len(df2) == 145 and np.all(np.abs(d2 - 1800.0) < TOL_STEP)
           and float(dR.max()) <= 1e-14 and abs(df2['R_cm'].iloc[-1] - 1.198) < 5e-4
           and abs(df2['R_cm'].iloc[0] - P.R0_CM) < 1e-12)
    res['V0.2'] = {'passed': bool(v02), 'n_rows': int(len(df2)), 'step_s': float(d2[0]),
                   'R_first_cm': float(df2['R_cm'].iloc[0]), 'R_last_cm': float(df2['R_cm'].iloc[-1]),
                   'max_dR': float(dR.max()), 't_last_s': float(df2['t_s'].iloc[-1])}

    n_pl, Ta_bar, Ca_bar = plateau_stats(df1)
    v03 = (n_pl == 121 and abs(Ta_bar - 49.9685) < 5e-4 and abs(Ca_bar - 0.049865) < 5e-6)
    res['V0.3'] = {'passed': bool(v03), 'n_plateau': n_pl, 'Ta_bar_C': Ta_bar, 'Ca_bar': Ca_bar,
                   'Ta_std': float(df1['Ta_C'].to_numpy()[df1['t_s'].to_numpy() >= P.PLATEAU_WINDOW_START].std(ddof=1)),
                   'join_step_C': float(df1['Ta_C'].iloc[-1] - Ta_bar)}

    sig = {'result1_温度': template_signature(P.TEMPLATES[1], '温度'),
           'result1_水分浓度': template_signature(P.TEMPLATES[1], '水分浓度'),
           'result2_温度': template_signature(P.TEMPLATES[2], '温度'),
           'result2_水分浓度': template_signature(P.TEMPLATES[2], '水分浓度'),
           'result3': template_signature(P.TEMPLATES[3], 0),
           'result4': template_signature(P.TEMPLATES[4], 0)}
    r_head_ok = all(s['r_head'] == ['0.0', '0.1', '0.2'] and s['ellipsis_col'] == '…' for s in sig.values())
    corner_ok = all(s['corner'] == '时间\\到药材中心的距离' and s['time_ellipsis'] == '…' for s in sig.values())
    v04 = (r_head_ok and corner_ok
           and all(s['n_cols'] == 6 for s in sig.values())
           and sig['result1_温度']['time_head'] == ['1', '2', '3']
           and sig['result2_温度']['time_head'] == ['1', '2', '3']
           and sig['result3']['time_head'] == ['60', '120', '180']
           and sig['result4']['time_head'] == ['60', '120', '180']
           and sig['result4']['last_header'] == P.SURFACE_LABEL
           and sig['result3']['last_header'] == '2.0'
           and sig['result1_温度']['last_header'] == '2.0')
    res['V0.4'] = {'passed': bool(v04), 'signatures': sig,
                   'note': '模板为示意式（6 列含 … 占位）；按 0.1 cm 步长展开为 1+21 列，时间按模板首三行的步长续排',
                   'expanded_cols': {'result1': 22, 'result2': 22, 'result3': 22, 'result4': 22},
                   'expanded_last_col': {'result1': '2.0', 'result2': '2.0',
                                         'result3': '2.0', 'result4': P.SURFACE_LABEL}}

    v05 = (abs(P.R0_M - 0.02) < 1e-15 and abs(P.L_M - 0.25) < 1e-15
           and abs((P.T0_C + P.KELVIN_OFFSET) - 301.15) < 1e-12
           and 1e-10 < P.D2_PREFACTOR < 1e-8 and P.C0 > 1.0)
    res['V0.5'] = {'passed': bool(v05), 'R0_m': P.R0_M, 'L_m': P.L_M, 'T0_K': P.T0_C + P.KELVIN_OFFSET,
                   'D_unit': 'm^2/s', 'moisture_basis': 'dry', 'C0': P.C0}

    for k, v in res.items():
        if not v['passed']:
            fails.append(k)
        print(f"{k}: {'PASS' if v['passed'] else 'FAIL'}")
    print(f"V0 summary: {5 - len(fails)}/5 passed")
    if fails:
        print('FAILED:', ','.join(fails))

    P.TMP_DIR.mkdir(exist_ok=True)
    (P.TMP_DIR / 'data_check.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    return res, fails


if __name__ == '__main__':
    _, bad = run()
    raise SystemExit(1 if bad else 0)
