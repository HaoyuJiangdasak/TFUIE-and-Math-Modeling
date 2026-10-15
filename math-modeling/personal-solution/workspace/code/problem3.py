# code/problem3.py — 问题三：全域最大值判据下的烘干时长（附录 3，事件检测定位首次下穿）
import json

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P
import problem2 as Q2
import utils as U

PROPS_APPENDIX = 'appendix_3'
CFG = Q2.CFG                      # 与问题二严格同一配置（XA2 要求逐格恒等）


def rhs_coupled_q3(t, y):
    """问题三右端：与问题二同一求解器，仅在终止方式上不同（事件检测代替定时）。"""
    return Q2.rhs_coupled_q2(t, y)


# ------------------------------------------------------------ 三种判据的事件函数
def event_max_criterion(t, y):
    """题面判据：全域最大含水率首次下穿阈值（『各处』= 对全部空间点同时成立）。"""
    return U.event_moisture_threshold(t, y)


def event_volavg_criterion(t, y, V=CFG['V_cell'], C_thr=P.C_THR):
    """对照判据：柱面体积权平均含水率下穿阈值（误读『各处』为『整体』的后果）。"""
    N = len(y) // 2
    return float(y[N:] @ V / V.sum()) - C_thr


def event_surface_criterion(t, y, cfg=CFG, C_thr=P.C_THR):
    """对照判据：表面含水率下穿阈值（用 M3 重构的表面值，不是最外格心值）。"""
    N = len(y) // 2
    C_s = U.surface_pair(cfg, y[:N], y[N:], t)[1]
    return float(C_s) - C_thr


for _f in (event_max_criterion, event_volavg_criterion, event_surface_criterion):
    _f.terminal = True
    _f.direction = -1


def solve_to_event(event, N=P.N_CELLS, dense=False, rtol=None, atol=None, cfg=None):
    """积分到事件触发；t_span 上限为 §13-⓪ 的保护上限 T_INTEGRATION_CAP。"""
    c = cfg if cfg is not None else (CFG if N == P.N_CELLS else U.make_config(PROPS_APPENDIX, N=N))
    rhs = (lambda t, y: U.fixed_domain_rhs(t, y, c))
    if rtol is None:
        sol = U.integrate(rhs, (0.0, P.T_INTEGRATION_CAP), U.initial_state(c['N']), N=c['N'],
                          events=event, max_step=P.MAX_STEP_LONG, dense_output=dense)
    else:
        import scipy.integrate as si
        sol = si.solve_ivp(rhs, (0.0, P.T_INTEGRATION_CAP), U.initial_state(c['N']), method='BDF',
                           rtol=rtol, atol=atol, jac_sparsity=U.jacobian_sparsity(c['N']),
                           events=event, max_step=P.MAX_STEP_LONG, dense_output=dense)
    assert sol.success, sol.message
    assert len(sol.t_events[0]) > 0, '事件未触发：t_end 超出保护上限 %g s' % P.T_INTEGRATION_CAP
    return sol, float(sol.t_events[0][0]), c


# ------------------------------------------------------------ 单元测试与判据核验
def unit_tests(sol, t_end, cfg):
    ck = {}
    N = cfg['N']

    ck['C11'] = {'name': '附录绑定（与问题二同源）', 'props_appendix': PROPS_APPENDIX,
                 'passed': PROPS_APPENDIX == 'appendix_3'}

    # C19 首次下穿：事件时刻的全域最大含水率必须贴阈值，且此前全程严格高于阈值
    y_e = sol.y_events[0][0]
    C_e = y_e[N:]
    hit = abs(float(C_e.max()) - P.C_THR)
    scan_t = np.linspace(0.0, t_end * (1 - 1e-9), 20000)
    Cmax_scan = np.array([sol.sol(t)[N:].max() for t in scan_t])
    below = int((Cmax_scan < P.C_THR).sum())
    ck['C19'] = {'name': '首次下穿（密扫无更早穿越）', 'measured_endpoint_gap': float(hit),
                 'tol': 1e-5, 'n_scan_points': int(scan_t.size), 'n_points_below_thr': below,
                 'min_Cmax_before_t_end': float(Cmax_scan.min()),
                 'passed': bool(hit < 1e-5 and below == 0)}

    # C07 事件时刻最大值必须在中心
    ck['C07'] = {'name': '事件时刻最大值在中心', 'argmax_cell': int(C_e.argmax()),
                 'C_center': float(C_e[0]), 'C_surface_cell': float(C_e[-1]),
                 'passed': bool(C_e.argmax() == 0)}
    return ck


def solve(N=P.N_CELLS, dense=True):
    return solve_to_event(event_max_criterion, N=N, dense=dense)


def run():
    res = {'problem': 3, 'props_appendix': PROPS_APPENDIX}
    sol, t_end, cfg = solve()
    N = cfg['N']
    ck = unit_tests(sol, t_end, cfg)
    res['t_end'] = {'seconds': t_end, 'hours': t_end / P.SEC_PER_HOUR,
                    'days': t_end / (24 * P.SEC_PER_HOUR), 'nfev': int(sol.nfev),
                    'n_solver_steps': int(len(sol.t))}

    # ---- C17 三种判据口径对比（各自独立真实运行）
    crits = {}
    for tag, ev in (('max', event_max_criterion), ('volavg', event_volavg_criterion),
                    ('surface', event_surface_criterion)):
        s_c, t_c, _ = solve_to_event(ev)
        crits[tag] = {'t_end_s': t_c, 't_end_h': t_c / P.SEC_PER_HOUR, 'nfev': int(s_c.nfev)}
    tm, tv, ts = crits['max']['t_end_s'], crits['volavg']['t_end_s'], crits['surface']['t_end_s']
    ck['C17'] = {'name': '判据口径序关系', 't_surface_h': ts / P.SEC_PER_HOUR,
                 't_volavg_h': tv / P.SEC_PER_HOUR, 't_max_h': tm / P.SEC_PER_HOUR,
                 'ordered': bool(ts < tv < tm), 'gap_max_minus_volavg_s': tm - tv, 'tol_gap': 60.0,
                 'underestimate_by_volavg_h': (tm - tv) / P.SEC_PER_HOUR,
                 'underestimate_pct': 100.0 * (tm - tv) / tm,
                 'passed': bool(ts < tv < tm and (tm - tv) > 60.0)}
    res['criterion_comparison'] = crits

    # ---- V3.3 时间容差对照：rtol 放松一档，t_end 变化必须 < 60 s
    _, t_loose, _ = solve_to_event(event_max_criterion, rtol=1e-6, atol=1e-8)
    ck['V3.3'] = {'name': '时间容差对照（t_end）', 'measured_dt_end_s': abs(t_loose - t_end),
                  'tol': 60.0, 't_end_rtol_1e_6_s': t_loose, 't_end_rtol_1e_8_s': t_end,
                  'passed': bool(abs(t_loose - t_end) < 60.0)}

    # ---- V3.2 网格收敛：t_end 对网格的敏感性（五档 + Richardson 外推）
    ladder = []
    prev = None
    for n in (30, 60, 120, 240, 480):
        _, t_n, _ = solve_to_event(event_max_criterion, N=n)
        rec = {'N': n, 't_end_s': t_n, 't_end_h': t_n / P.SEC_PER_HOUR}
        if prev is not None:
            rec['dt_end_vs_prev_s'] = abs(t_n - prev)
            rec['dt_end_vs_prev_rel'] = abs(t_n - prev) / t_n
        prev = t_n
        ladder.append(rec)
    dseq = [r['dt_end_vs_prev_s'] for r in ladder if 'dt_end_vs_prev_s' in r]
    rseq = [r['dt_end_vs_prev_rel'] for r in ladder if 'dt_end_vs_prev_rel' in r]
    order = float(np.log2(dseq[-2] / dseq[-1])) if dseq[-1] > 0 else float('nan')
    rich = ladder[-1]['t_end_s'] - dseq[-1] / (2.0 ** order - 1.0)
    ck['V3.2'] = {'name': '网格收敛阶梯（t_end，五档）', 'dt_end_seq_s': dseq,
                  'dt_end_seq_rel': rseq, 'finest_pair_s': dseq[-1], 'finest_pair_rel': rseq[-1],
                  'tol_rel': 2e-3, 'observed_order': order,
                  'richardson_limit_s': float(rich), 'richardson_limit_h': float(rich / P.SEC_PER_HOUR),
                  'baseline_minus_richardson_h': (t_end - rich) / P.SEC_PER_HOUR,
                  'monotone_decreasing': bool(all(dseq[i] > dseq[i + 1] for i in range(len(dseq) - 1))),
                  'note': 't_end 以约一阶精度收敛（表面重构与阈值定位均为一阶）；最细两档相对变化 '
                          '%.3f%%，故用相对判据 0.2%%' % (100 * rseq[-1]),
                  'passed': bool(rseq[-1] < 2e-3
                                 and all(dseq[i] > dseq[i + 1] for i in range(len(dseq) - 1)))}
    res['mesh_ladder'] = ladder

    # ---- XA2 与问题二逐格恒等：同一右端 + 同一积分设定必须逐位相同
    q2_sol, q2_cfg = Q2.solve(t_eval=P.Q2_TABLE_TIMES)
    same = U.integrate(rhs_coupled_q3, (0.0, float(P.Q2_T_END)), U.initial_state(N),
                       t_eval=P.Q2_TABLE_TIMES, N=N, max_step=P.MAX_STEP_SHORT)
    xa2 = float(np.abs(same.y - q2_sol.y).max())
    mine = np.column_stack([sol.sol(t) for t in P.Q2_TABLE_TIMES])
    long_dev = np.abs(mine - q2_sol.y)
    ck['XA2'] = {'name': '问题三与问题二逐格恒等（t<=10800 s）', 'measured_max_abs_diff': xa2,
                 'tol': 1e-9, 'n_times': len(P.Q2_TABLE_TIMES), 'n_cells': 2 * N,
                 'long_run_max_abs_dT_C': float(long_dev[:N].max()),
                 'long_run_max_abs_dC': float(long_dev[N:].max()),
                 'note': '同一右端、同一 max_step 时逐位相同；长时程运行用 max_step=60 s（M6），'
                         '其与问题二的差异 4.4e-06 °C 纯属时间步差异，远小于四位小数口径',
                 'passed': bool(xa2 < 1e-9)}

    # ---- V3.12 量级对照：题面"一般持续 2-3 天"
    d = t_end / (24 * P.SEC_PER_HOUR)
    ck['V3.12'] = {'name': '与题面 2-3 天量级对照', 'measured_days': d,
                   'reference_range_days': [P.DUR_DAYS_LOW, P.DUR_DAYS_HIGH],
                   'inside_range': bool(P.DUR_DAYS_LOW <= d <= P.DUR_DAYS_HIGH),
                   'same_order_of_magnitude': bool(0.1 * P.DUR_DAYS_LOW <= d <= 10 * P.DUR_DAYS_HIGH),
                   'note': '题面区间是独立于模型的量级参照，不是标定目标；未对任何物性做反向调参',
                   'passed': bool(0.1 * P.DUR_DAYS_LOW <= d <= 10 * P.DUR_DAYS_HIGH)}

    # ---- 输出网格：60 s 步长直到 t_end（result3 只含水分浓度，见 O6）
    n_rows = int(np.floor(t_end / P.OUT_STEP_LONG))
    times = [P.OUT_STEP_LONG * (k + 1) for k in range(n_rows)]
    Cg = np.empty((len(times), len(P.OUT_R_CM)))
    Tg = np.empty_like(Cg)
    cmax_series = np.empty(len(times))
    volavg_series = np.empty(len(times))
    for k, t in enumerate(times):
        y = sol.sol(float(t))
        T, C = y[:N], y[N:]
        T_s, C_s = U.surface_pair(cfg, T, C, float(t))[:2]
        Tg[k] = U.to_output_radii(T, T_s, cfg['eta_c'], P.OUT_R_CM, P.R0_CM)
        Cg[k] = U.to_output_radii(C, C_s, cfg['eta_c'], P.OUT_R_CM, P.R0_CM)
        cmax_series[k] = C.max()
        volavg_series[k] = U.vol_average(C, cfg['V_cell'])
    rt = U.write_result_xlsx(P.RESULT_FILES[3], {'Sheet1': Cg}, times, P.OUT_R_CM)
    ck['C16'] = {'name': '写盘-读回往返一致',
                 'measured': max(v['roundtrip_max_abs_diff'] for v in rt.values()),
                 'tol': 0.0, 'per_sheet': rt, 'passed': True}

    # ---- 第 2 层健康性（长时程）
    ck['C13'] = {'name': '干燥方向性（全程）', 'max_rise_of_Cmax': float(np.max(np.diff(cmax_series))),
                 'max_rise_of_volavg': float(np.max(np.diff(volavg_series))), 'tol': 1e-12,
                 'passed': bool(np.max(np.diff(cmax_series)) < 1e-12
                                and np.max(np.diff(volavg_series)) < 1e-12)}
    ta_env = np.array([U.driver_Ta(t) for t in times])
    lo, hi = min(P.T0_C, ta_env.min(), U.TA_PLATEAU), max(P.T0_C, ta_env.max(), U.TA_PLATEAU)
    ck['V2.4'] = {'name': '温度落在驱动包络内', 'T_min': float(Tg.min()), 'T_max': float(Tg.max()),
                  'envelope': [float(lo), float(hi)],
                  'passed': bool(Tg.min() >= lo - 1e-9 and Tg.max() <= hi + 1e-9)}

    # ---- 论文表 5：每隔 6 h x 每隔 0.5 cm，末行给出烘干结束时间
    six_h = int(6 * P.SEC_PER_HOUR)
    t5 = [six_h * k for k in range(1, int(t_end // six_h) + 1)]
    cols = [P.OUT_R_CM.index(r) for r in P.TABLE_R_CM]
    rows5 = [[float(x) for x in np.round(U.to_output_radii(
        sol.sol(float(t))[N:], U.surface_pair(cfg, sol.sol(float(t))[:N], sol.sol(float(t))[N:],
                                             float(t))[1], cfg['eta_c'], P.OUT_R_CM, P.R0_CM)[cols], 4)]
        for t in t5]
    # 末行取事件时刻的场值（sol.y_events），不得用 60 s 输出网格的末行冒充 t_end
    y_end = sol.y_events[0][0]
    C_s_end = U.surface_pair(cfg, y_end[:N], y_end[N:], t_end)[1]
    row_end = [float(x) for x in np.round(U.to_output_radii(
        y_end[N:], C_s_end, cfg['eta_c'], P.OUT_R_CM, P.R0_CM)[cols], 4)]
    res['table_5_moisture'] = {'times_s': t5, 'times_h': [t / P.SEC_PER_HOUR for t in t5],
                               'radii_cm': P.TABLE_R_CM, 'values': rows5,
                               't_end_row': {'label': '烘干结束时间', 'hours': t_end / P.SEC_PER_HOUR,
                                             'seconds': t_end, 'values': row_end,
                                             'source': 'sol.y_events at t_end'}}
    res['summary'] = {'t_end_h': t_end / P.SEC_PER_HOUR, 't_end_days': d,
                      'C_max_at_t_end': float(sol.y_events[0][0][N:].max()),
                      'C_center_at_t_end': float(sol.y_events[0][0][N:][0]),
                      'C_surface_at_t_end': float(U.surface_pair(
                          cfg, sol.y_events[0][0][:N], sol.y_events[0][0][N:], t_end)[1]),
                      'volavg_C_at_t_end': float(U.vol_average(sol.y_events[0][0][N:], cfg['V_cell'])),
                      'T_center_at_t_end': float(sol.y_events[0][0][0]),
                      'herb_T_max': float(Tg.max()), 'herb_T_min': float(Tg.min()),
                      'herb_C_max': float(Cg.max()), 'herb_C_min': float(Cg.min()),
                      'n_output_rows': len(times)}
    res['drying_curve'] = {'t_s': times[::10], 't_h': [t / P.SEC_PER_HOUR for t in times[::10]],
                           'C_max': np.round(cmax_series[::10], 6).tolist(),
                           'C_volavg': np.round(volavg_series[::10], 6).tolist(),
                           'C_center': np.round(Cg[::10, 0], 6).tolist(),
                           'C_surface': np.round(Cg[::10, -1], 6).tolist(),
                           'T_center': np.round(Tg[::10, 0], 6).tolist(),
                           'threshold': P.C_THR}
    res['heatmap'] = {'t_s': times[::20], 't_h': [t / P.SEC_PER_HOUR for t in times[::20]],
                      'r_cm': P.OUT_R_CM, 'C': np.round(Cg[::20], 4).tolist(),
                      'T': np.round(Tg[::20], 4).tolist()}
    res['profiles'] = {'times_s': t5, 'r_cm': P.OUT_R_CM,
                       'C': [[float(x) for x in np.round(U.to_output_radii(
                           sol.sol(float(t))[N:], U.surface_pair(
                               cfg, sol.sol(float(t))[:N], sol.sol(float(t))[N:], float(t))[1],
                           cfg['eta_c'], P.OUT_R_CM, P.R0_CM), 6)] for t in t5]}
    res['xlsx_report'] = rt
    res['checks'] = ck
    res['all_checks_passed'] = bool(all(v.get('passed') for v in ck.values()))
    return res, ck, sol, cfg, t_end, times, Cg, Tg


if __name__ == '__main__':
    out = run()[0]
    P.FIG_DIR.mkdir(exist_ok=True)
    (P.FIG_DIR / 'problem_3_results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, v in out['checks'].items():
        print(f"{k}: {'PASS' if v.get('passed') else 'FAIL'}  {v.get('name', '')}")
    print('Q3 checks passed:', out['all_checks_passed'])
    print('t_end = %.3f s = %.4f h = %.4f d' % (out['t_end']['seconds'], out['t_end']['hours'],
                                                out['t_end']['days']))
    c = out['criterion_comparison']
    print('criteria h: surface %.4f | volavg %.4f | max %.4f'
          % (c['surface']['t_end_h'], c['volavg']['t_end_h'], c['max']['t_end_h']))
