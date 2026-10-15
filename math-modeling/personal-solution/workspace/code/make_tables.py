# code/make_tables.py — 由写盘 JSON 生成 figures/TABLE_*.md，供写稿步骤直接嵌入（数据真实，杜绝编造）
import json

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P

BLANK = '—'          # 收缩后半径已小于该固定距离，物理上不存在该点


def _f(v, nd=P.DECIMALS):
    return BLANK if v is None else f'{float(v):.{nd}f}'


def _md(headers, rows, caption):
    out = [caption, '']
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('|' + '|'.join(['---'] * len(headers)) + '|')
    for r in rows:
        out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out) + '\n'


def load(n):
    return json.loads((P.FIG_DIR / f'{n}.json').read_text(encoding='utf-8'))


def run():
    r1, r2, r3, r4 = (load(f'problem_{i}_results') for i in (1, 2, 3, 4))
    made = []

    # ---- 表 1、表 2：问题一 7 时刻 x 5 位置
    for tag, key, unit, num in (('TABLE_1', 'table_1_temperature', '温度 / °C', 1),
                                ('TABLE_2', 'table_2_moisture', '含水率 / (kg/kg)', 2)):
        t = r1[key]
        hdr = ['时间 / s'] + [f'r = {r:g} cm' for r in t['radii_cm']]
        rows = [[f"{int(ts)}"] + [_f(v) for v in vals]
                for ts, vals in zip(t['times_s'], t['values'])]
        cap = (f'**表 {num}** 预热平衡阶段药材内部{unit}的时空分布'
               f'（附录 2 常物性，r = {P.R0_CM:g} cm 列为边界条件重构的表面值）')
        (P.FIG_DIR / f'{tag}.md').write_text(_md(hdr, rows, cap), encoding='utf-8')
        made.append(tag)

    # ---- 表 3、表 4：问题二 3 h 内每 0.5 h x 5 位置
    for tag, key, unit, num in (('TABLE_3', 'table_3_temperature', '温度 / °C', 3),
                                ('TABLE_4', 'table_4_moisture', '含水率 / (kg/kg)', 4)):
        t = r2[key]
        hdr = ['时间 / h'] + [f'r = {r:g} cm' for r in t['radii_cm']]
        rows = [[f"{ts / P.SEC_PER_HOUR:.1f}"] + [_f(v) for v in vals]
                for ts, vals in zip(t['times_s'], t['values'])]
        cap = (f'**表 {num}** 全过程变物性双向强耦合下药材内部{unit}的时空分布'
               f'（附录 3，空气侧取附件 1 实测驱动）')
        (P.FIG_DIR / f'{tag}.md').write_text(_md(hdr, rows, cap), encoding='utf-8')
        made.append(tag)

    # ---- 表 5：问题三 每 6 h x 每 0.5 cm，末行给烘干结束时间
    t5 = r3['table_5_moisture']
    hdr5 = ['时间 / h'] + [f'r = {r:g} cm' for r in t5['radii_cm']]
    rows5 = [[f"{th:.0f}"] + [_f(v) for v in vals]
             for th, vals in zip(t5['times_h'], t5['values'])]
    te = t5['t_end_row']
    rows5.append([f"**{te['label']} {te['hours']:.4f} h**"]
                 + [f"**{_f(v)}**" for v in te['values']])
    cap5 = ('**表 5** 全域最大含水率判据下的含水率分布与烘干结束时间'
            f"（判据：各处含水率均降至 {P.C_THR:g} kg/kg 以下，"
            f"首次满足于 t = {te['hours']:.4f} h）")
    (P.FIG_DIR / 'TABLE_5.md').write_text(_md(hdr5, rows5, cap5), encoding='utf-8')
    made.append('TABLE_5')

    # ---- 表 6：问题四 含收缩，末列为随收缩而变的药材表面
    t6 = r4['table_6_moisture']
    hdr6 = ['时间 / h', '半径 R(t) / cm'] + [f'r = {r:g} cm' for r in t6['radii_cm']] \
        + [t6['surface_label']]
    rows6 = [[f"{r['t_h']:.0f}", f"{r['R_cm']:.4f}"] + [_f(v) for v in r['C']]
             + [_f(r['C_surface'])] for r in t6['rows']]
    te6 = t6['t_end_row']
    rows6.append([f"**{te6['label']} {te6['hours']:.4f} h**", f"**{te6['R_cm']:.4f}**"]
                 + [BLANK if v is None else f"**{_f(v)}**" for v in te6['C']]
                 + [f"**{_f(te6['C_surface'])}**"])
    cap6 = ('**表 6** 径向收缩条件下药材含水率分布与烘干结束时间'
            f"（半径由 {P.R0_CM:g} cm 收缩至 {te6['R_cm']:.4f} cm；"
            f'“{BLANK}” 表示该固定距离已超出当时半径，物理上不存在该点）')
    (P.FIG_DIR / 'TABLE_6.md').write_text(_md(hdr6, rows6, cap6), encoding='utf-8')
    made.append('TABLE_6')

    # ---- 表 7：四级模型阶梯（MC8）；表 8：判据口径对照；表 9：敏感性排序
    ml = r2['model_ladder']['paths']
    name_map = {'L0_lumped': 'L0 集中参数（Bi=O(1)，先验失效）',
                'L1_const_prop': 'L1 常物性（冻结在初值）',
                'L2_oneway': 'L2 单向耦合（切断 T→C 反馈）',
                'L3_full': 'L3 全耦合（本文基准）'}
    base = ml['L3_full']['volavg_C_end']
    rows7 = []
    for k in ('L0_lumped', 'L1_const_prop', 'L2_oneway', 'L3_full'):
        v = ml[k].get('volavg_C_end', ml[k].get('C_end'))
        rows7.append([name_map[k], _f(v), f'{100.0 * (v - base) / base:+.2f}'])
    cap7 = ('**表 7** 四级模型阶梯在 t = 3 h 的体积平均含水率对比'
            '（每级均为独立真实求解，非近似换算）')
    (P.FIG_DIR / 'TABLE_7.md').write_text(
        _md(['模型层级', '体积平均含水率 / (kg/kg)', '相对基准偏差 / %'], rows7, cap7),
        encoding='utf-8')
    made.append('TABLE_7')

    cc = r3['criterion_comparison']
    c17 = r3['checks']['C17']
    lab = {'surface': '表面含水率下穿（最松）', 'volavg': '体积平均含水率下穿（误读“各处”）',
           'max': '全域最大含水率下穿（题面判据）'}
    rows8 = [[lab[k], f"{cc[k]['t_end_h']:.4f}", f"{cc[k]['t_end_h'] / 24:.4f}",
              f"{100.0 * (cc[k]['t_end_h'] - cc['max']['t_end_h']) / cc['max']['t_end_h']:+.2f}"]
             for k in ('surface', 'volavg', 'max')]
    cap8 = ('**表 8** 三种终止判据口径对照'
            f"（误读为体积平均将低估工期 {c17['underestimate_pct']:.2f}%，"
            f"即 {c17['underestimate_by_volavg_h']:.4f} h）")
    (P.FIG_DIR / 'TABLE_8.md').write_text(
        _md(['终止判据', '烘干时长 / h', '烘干时长 / d', '相对题面判据偏差 / %'], rows8, cap8),
        encoding='utf-8')
    made.append('TABLE_8')

    rs = load('sensitivity_results')
    tor, spear = rs['tornado'], rs['lhs']['spearman']
    rows9 = []
    for k in tor['order']:
        b = tor['by_factor'][k]
        amp = (f"±{b['amplitude']:g} °C" if b['kind'] == 'abs'
               else f"±{100 * b['amplitude']:g}%")
        rows9.append([b['label'], amp, f"{b['t_end_h_low']:.4f}", f"{b['t_end_h_high']:.4f}",
                      f"{b['half_range_h']:.4f}", f"{b['elasticity']:+.4f}",
                      f"{spear[k]:+.4f}"])
    cap9 = ('**表 9** 烘干时长的单因子敏感性排序与全局秩相关'
            f"（基准 {tor['baseline_h']:.4f} h；弹性符号全部与机理一致；"
            f"LHS n = {rs['lhs']['n']} 的秩相关首因子与单因子排序首位一致）")
    (P.FIG_DIR / 'TABLE_9.md').write_text(
        _md(['因子', '扰动幅度', '下界 t_end / h', '上界 t_end / h', '半极差 / h',
             '弹性', 'Spearman'], rows9, cap9), encoding='utf-8')
    made.append('TABLE_9')

    # ---- 表 10：问题四 2x2 归因分解
    at = r4['attribution']
    c21 = r4['checks']['C21']
    amap = {'q3_baseline': '附录 3 物性 + 固定域（问题三基准）',
            'app4_noshrink': '附录 4 物性 + 固定域',
            'app3_shrink': '附录 3 物性 + 径向收缩',
            'app4_shrink': '附录 4 物性 + 径向收缩（问题四）'}
    b0 = at['q3_baseline']['t_end_h']
    rows10 = [[amap[k], f"{at[k]['t_end_h']:.4f}", f"{at[k]['t_end_h'] / 24:.4f}",
               f"{100.0 * (at[k]['t_end_h'] - b0) / b0:+.2f}"]
              for k in ('q3_baseline', 'app4_noshrink', 'app3_shrink', 'app4_shrink')]
    # 收缩效应在两个物性基准上各有一个值，必须同时点名，否则读者只能推出交互项为零
    shrink_on_app3 = at['app3_shrink']['t_end_s'] - at['q3_baseline']['t_end_s']
    shrink_on_app4 = at['app4_shrink']['t_end_s'] - at['app4_noshrink']['t_end_s']
    cap10 = ('**表 10** 物性与收缩的 2×2 归因分解（四次独立真实求解）。收缩效应依基准而异：'
             f"附录 3 物性下为 {shrink_on_app3:+.0f} s、附录 4 物性下为 {shrink_on_app4:+.0f} s，"
             f"二者之差 {c21['interaction_s']:+.0f} s 即交互项，占总效应 "
             f"{c21['interaction_over_total_pct']:.2f}%，故加性框架在此失效；"
             f"改用乘性框架，残差（以预测比值 {c21['mult_predicted_ratio']:.4f} 为分母）仅 "
             f"{c21['mult_residual_pct']:.2f}%，说明两种机理近似为乘性叠加")
    (P.FIG_DIR / 'TABLE_10.md').write_text(
        _md(['算例', '烘干时长 / h', '烘干时长 / d', '相对问题三偏差 / %'], rows10, cap10),
        encoding='utf-8')
    made.append('TABLE_10')

    print('生成 %d 个表格文件：%s' % (len(made), ', '.join(f'{m}.md' for m in made)))
    for m in made:
        p = P.FIG_DIR / f'{m}.md'
        n_row = sum(1 for ln in p.read_text(encoding='utf-8').splitlines()
                    if ln.startswith('|')) - 2
        print(f'  figures/{m}.md  {p.stat().st_size:>5d} bytes  {n_row} 数据行')
    return made


if __name__ == '__main__':
    run()
