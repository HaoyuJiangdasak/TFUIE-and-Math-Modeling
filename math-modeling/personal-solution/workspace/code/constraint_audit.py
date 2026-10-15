# code/constraint_audit.py — 约束复核：把 C01-C23 与 V 系列判据在写盘 JSON 上重新断言一次
# 与各问 run() 内的自检互为独立复核：这里只读 JSON，重算门限与序关系，不重跑 PDE。
import json

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P

MAX_SAMPLES = 5

# 契约表：约束号 -> (来源 JSON, checks 里的键, 该约束要复核的量与门限)
CONTRACT = [
    ('C01', 'problem_1_results', 'C01', '均匀场零通量', 'measured', '<', 1e-12),
    ('C02', 'problem_1_results', 'C02', '柱面通量正比于 r', 'measured', '<', 1e-12),
    ('C03', 'problem_1_results', 'C03', '双场独立（两场同时活跃且不共享内存）',
     'dC_absmax', '>', 0.0),
    ('C04', 'problem_1_results', 'C04', '表面值网格无关性', 'measured', '<', 1e-3),
    ('C05', 'problem_1_results', 'C05', 'Robin 闭合一致', 'measured_T', '<', 1e-10),
    ('C09', 'problem_1_results', 'C09', '半解析解 147 点对照', 'measured_max_abs_C', '<', 1e-3),
    ('C10', 'problem_1_results', 'C10', '问题一单向解耦', 'measured', '<', 1e-12),
    ('C12', 'problem_2_results', 'C12', '五个物性偏导非零', None, None, None),
    ('C08', 'problem_2_results', 'C08', '附件 1 复现与衔接连续', 'sample_rel_err_Ta', '<', 1e-9),
    ('C15', 'problem_2_results', 'C15', '模型对比两两可分辨', 'measured_min_gap', '>', 1e-6),
    ('C17', 'problem_3_results', 'C17', '判据口径序关系', 'gap_max_minus_volavg_s', '>', 60.0),
    ('C19', 'problem_3_results', 'C19', '首次下穿', 'measured_endpoint_gap', '<', 1e-5),
    ('C18', 'problem_4_results', 'C18', '半径单调且复现附件 2', 'sample_repro_max_abs_cm', '<', 1e-9),
    ('C20', 'problem_4_results', 'C20', '绝干骨架水量守恒', 'forward_rel_drift', '<', 1e-10),
    ('C21', 'problem_4_results', 'C21', '归因分解四例可分辨', 'min_pairwise_gap_s', '>', 60.0),
    ('C22', 'problem_4_results', 'C22', 't=0 收缩域退化为固定域', 'measured_max_abs_diff', '<', 1e-12),
    ('C23', 'sensitivity_results', 'C23', '敏感性逐点真实重算', 'min_abs_gap_to_baseline_s', '>', 60.0),
]


def load(name):
    return json.loads((P.FIG_DIR / f'{name}.json').read_text(encoding='utf-8'))


def run():
    J = {n: load(n) for n in ('problem_1_results', 'problem_2_results', 'problem_3_results',
                              'problem_4_results', 'sensitivity_results', 'all_results')}
    rows, fails = [], []

    def rec(cid, name, ok, detail):
        rows.append({'id': cid, 'name': name, 'passed': bool(ok), 'detail': detail})
        if not ok:
            fails.append(f'{cid} {name}: {detail}')

    # ---- 契约表逐条复核：既要 checks 自报 passed，也要门限在本文件里重算一遍
    for cid, src, key, name, field, op, tol in CONTRACT:
        ck = J[src]['checks'].get(key)
        if ck is None:
            rec(cid, name, False, f'{src}.checks.{key} 缺失')
            continue
        ok = bool(ck.get('passed'))
        det = f"self={ok}"
        if field is not None:
            v = ck.get(field)
            if v is None:
                ok, det = False, f'{field} 缺失'
            else:
                num = float(v)
                gate = (num < tol) if op == '<' else (num > tol)
                ok = ok and gate
                det = f'{field}={num:.6g} {op} {tol:g} -> {gate}'
        rec(cid, name, ok, det)

    # ---- C06/C07/C13/C14/C16/C11：在四问里重复出现，逐问复核
    for cid, name in (('C06', '剖面单调'), ('C07', '全域最大含水率在中心'),
                      ('C13', '干燥方向性'), ('C14', '低含水率下界保护'),
                      ('C16', '写盘-读回往返一致'), ('C11', '附录绑定')):
        hits = [(n, J[n]['checks'][cid]['passed']) for n in J
                if n != 'all_results' and cid in J[n].get('checks', {})]
        rec(cid, name + f'（{len(hits)} 处）', bool(hits) and all(p for _n, p in hits),
            ','.join(f'{n.split("_")[1]}:{int(p)}' for n, p in hits))

    # ---- 附录绑定的实际取值：问题一用附录 2，问题二三用附录 3，问题四用附录 4
    want_app = {'problem_1_results': 'appendix_2', 'problem_2_results': 'appendix_3',
                'problem_3_results': 'appendix_3', 'problem_4_results': 'appendix_4'}
    bad_app = [n for n, w in want_app.items() if J[n]['props_appendix'] != w]
    rec('C11b', '各问物性附录绑定正确', not bad_app,
        'ok' if not bad_app else f'错绑 {bad_app[:MAX_SAMPLES]}')

    # ---- C12 五个偏导都必须严格非零，三个惰性偏导必须严格为零
    p12 = J['problem_2_results']['checks']['C12']
    rec('C12b', '物性偏导结构（5 非零 / 3 恒零）',
        all(float(v) > 1e-12 for v in p12['partials'].values())
        and all(float(v) == 0.0 for v in p12['inert_partials_expected_zero'].values()),
        f"min|partial|={min(float(v) for v in p12['partials'].values()):.3e}")

    # ---- C20 反向对照：三个错误变体的漂移必须比正向大若干个数量级
    c20 = J['problem_4_results']['checks']['C20']
    fwd = float(c20['forward_rel_drift'])
    revs = {k: float(v) for k, v in c20['reverse_rel_drift'].items()}
    rec('C20b', 'C20 反向变体全部显著破坏守恒',
        all(v > 1e-4 for v in revs.values()) and fwd < 1e-10,
        f"forward={fwd:.3e}; reverse min={min(revs.values()):.4%}")

    # ---- C17 三判据序关系必须是 surface < volavg < max（误读『各处』会低估工期）
    cc = J['problem_3_results']['criterion_comparison']
    ts, tv, tm = (cc['surface']['t_end_h'], cc['volavg']['t_end_h'], cc['max']['t_end_h'])
    rec('C17b', '判据序关系 surface<volavg<max', ts < tv < tm,
        f'{ts:.4f} < {tv:.4f} < {tm:.4f} h')

    # ---- V3.6/C15 四级模型阶梯必须两两可分辨且方向合理
    ml = J['problem_2_results']['model_ladder']['paths']
    vals = {k: (ml[k]['volavg_C_end'] if 'volavg_C_end' in ml[k] else ml[k]['C_end'])
            for k in ml}
    gaps = [abs(a - b) for i, a in enumerate(vals.values())
            for b in list(vals.values())[i + 1:]]
    rec('V3.6', '四级模型阶梯两两可分辨', min(gaps) > 1e-6, f'min gap={min(gaps):.6g}')

    # ---- V3.10 敏感性弹性符号必须与机理一致
    v310 = J['sensitivity_results']['checks']['V3.10']
    rec('V3.10', '单因子弹性符号与机理一致', not v310['mismatch'],
        f"mismatch={v310['mismatch']}")

    # ---- V3.4 潜热方向探针：t_end 必须随 chi 单调增大
    v34 = J['sensitivity_results']['checks']['V3.4']
    seq = [x for x in v34['t_end_h_by_chi'] if x is not None]
    rec('V3.4', 't_end 随潜热系数 chi 单调增大',
        all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)),
        ' < '.join(f'{x:.4f}' for x in seq) + ' h')

    # ---- V3.2 网格收敛：四问的最细两档差值都必须落在各自门限内
    g32 = []
    for n in ('problem_1_results', 'problem_2_results', 'problem_3_results', 'problem_4_results'):
        c = J[n]['checks'].get('V3.2')
        if c:
            g32.append((n.split('_')[1], bool(c['passed'])))
    rec('V3.2', '网格收敛阶梯（四问）', all(p for _n, p in g32),
        ','.join(f'{n}:{int(p)}' for n, p in g32))

    # ---- V3.3 时间容差：问题三、四的 t_end 变化都必须 < 60 s
    g33 = [(n.split('_')[1], float(J[n]['checks']['V3.3']['measured_dt_end_s']))
           for n in ('problem_3_results', 'problem_4_results')]
    rec('V3.3', '时间容差对照 t_end < 60 s', all(v < 60.0 for _n, v in g33),
        ','.join(f'{n}:{v:.3f}s' for n, v in g33))

    # ---- XA2 问题三前 10800 s 必须与问题二逐格恒等
    xa2 = float(J['problem_3_results']['checks']['XA2']['measured_max_abs_diff'])
    rec('XA2', '问题三与问题二逐格恒等', xa2 < 1e-9, f'{xa2:.3e}')

    # ---- V3.12 烘干时长与题面 2-3 天同量级
    d3 = J['problem_3_results']['summary']['t_end_days']
    d4 = J['problem_4_results']['summary']['t_end_days']
    rec('V3.12', '烘干时长与题面 2-3 天同量级',
        all(0.1 * P.DUR_DAYS_LOW <= d <= 10 * P.DUR_DAYS_HIGH for d in (d3, d4)),
        f'Q3={d3:.4f} d, Q4={d4:.4f} d（题面参照 {P.DUR_DAYS_LOW:g}-{P.DUR_DAYS_HIGH:g} d）')

    # ---- 单位与量纲：D 必须在 m^2/s 量级，Bi 必须 O(1)（否决集中参数）
    ch = J['problem_1_results']['characteristics']
    bi_ok = 0.1 < ch['Bi_T'] < 100 and 0.1 < ch['Bi_m'] < 100
    rec('U01', 'Biot 数 O(1)（集中参数不成立）', bi_ok,
        f"Bi_T={ch['Bi_T']:.4f}, Bi_m={ch['Bi_m']:.4f}")
    d_span = J['problem_2_results']['D_response_surface']
    rec('U02', 'D 落在 1e-11..1e-6 m^2/s',
        1e-11 < d_span['D_min'] and d_span['D_max'] < 1e-6,
        f"D in [{d_span['D_min']:.3e}, {d_span['D_max']:.3e}] m^2/s")

    # ---- 干基口径：含水率允许 > 1，且四问都不得出现归一化痕迹
    c_max = max(J[n]['summary'].get('herb_C_max', J[n]['summary'].get('C_max_at_t_end', 0.0))
                for n in ('problem_1_results', 'problem_2_results'))
    rec('U03', '干基含水率保留 >1 的量级（未被归一化）', c_max > 1.0,
        f'max C={c_max:.4f} kg/kg, C0={P.C0:g}')

    # ---- 台账：bound/observed/reason 三段式必须齐全且全部满足
    led = json.loads((P.ROOT / 'CROSS_PROBLEM_LEDGER.json').read_text(encoding='utf-8'))
    full = all(('bound' in it and it.get('observed') is not None and it.get('reason'))
               for it in led['items'])
    rec('XP', f"跨问题台账（{led['n_items']} 项）", full and led['all_satisfied'],
        f"observed 齐全={full}, 违规={led['violations']}")

    n_pass = sum(1 for r in rows if r['passed'])
    print('=== 约束复核（独立于各问自检，只读写盘 JSON）===')
    for r in rows:
        print(f"{r['id']:<7} {'PASS' if r['passed'] else 'FAIL'}  {r['name']}  |  {r['detail']}")
    print(f'\n约束复核 {n_pass}/{len(rows)} 通过')
    if fails:
        print('FAILED（至多列 %d 条）：' % MAX_SAMPLES)
        for f in fails[:MAX_SAMPLES]:
            print('  -', f)

    out = {'n_constraints': len(rows), 'n_passed': n_pass, 'all_passed': not fails,
           'rows': rows, 'failures': fails}
    (P.FIG_DIR / 'constraint_audit.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out


if __name__ == '__main__':
    raise SystemExit(0 if run()['all_passed'] else 1)
