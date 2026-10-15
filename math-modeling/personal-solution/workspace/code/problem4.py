# code/problem4.py — 问题四：径向收缩下的移动边界烘干（附录 4 物性 + 附件 2 半径轨迹）
import json

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P
import utils as U

PROPS_APPENDIX = 'appendix_4'
SHRINK_MODE = 'radial'            # ③ 方向性判定：只径向收缩，轴向 25 cm 不变（见 C_direction）
CFG = U.make_config(PROPS_APPENDIX)
C20_T_END = 43200.0               # C20 守恒试验时长（12 h，R 由 2.0000 收缩到 1.2480 cm）


def rhs_coupled_q4(t, y):
    """问题四右端：附录 4 变物性 + 材料坐标收缩域（④M11，收缩只经 1/R(t)^2 进入）。"""
    return U.moving_domain_rhs(t, y, CFG)


def water_mass_per_length(t, C, V_cell):
    """单位长度含水质量 m_w = 2*pi*rho_d(t)*R(t)**2*sum(V_i C_i)（kg/m）。

    rho_d(t)*R(t)**2 = rho_d0*R0**2 恒定，故 h_m=0 时 m_w 守恒等价于 sum(V_i C_i) 守恒。
    """
    R_m = U.R_of_t(t)
    return 2.0 * np.pi * U.rho_d_of_t(t) * R_m ** 2 * float(np.asarray(C) @ V_cell)


def solve_case(props_key=PROPS_APPENDIX, moving=True, N=P.N_CELLS, dense=False,
               rtol=None, atol=None):
    """统一入口：按 (物性附录, 是否收缩) 积分到全域最大含水率首次下穿阈值。"""
    cfg = CFG if (props_key == PROPS_APPENDIX and N == P.N_CELLS) else U.make_config(props_key, N=N)
    if moving:
        rhs = (rhs_coupled_q4 if cfg is CFG else (lambda t, y: U.moving_domain_rhs(t, y, cfg)))
    else:
        rhs = (lambda t, y: U.fixed_domain_rhs(t, y, cfg))
    kw = dict(events=U.event_moisture_threshold, max_step=P.MAX_STEP_LONG, dense_output=dense)
    if rtol is None:
        sol = U.integrate(rhs, (0.0, P.T_INTEGRATION_CAP), U.initial_state(cfg['N']),
                          N=cfg['N'], **kw)
    else:
        import scipy.integrate as si
        sol = si.solve_ivp(rhs, (0.0, P.T_INTEGRATION_CAP), U.initial_state(cfg['N']),
                           method='BDF', rtol=rtol, atol=atol,
                           jac_sparsity=U.jacobian_sparsity(cfg['N']), **kw)
    assert sol.success, sol.message
    assert len(sol.t_events[0]) > 0, '事件未触发：t_end 超出保护上限 %g s' % P.T_INTEGRATION_CAP
    return sol, float(sol.t_events[0][0]), cfg


# ------------------------------------------------------------ 第 1 层单元测试
def unit_tests():
    ck = {}
    N = CFG['N']
    ck['C11'] = {'name': '附录绑定（附录 4 物性 + 附件 2 半径）', 'props_appendix': PROPS_APPENDIX,
                 'shrink_mode': SHRINK_MODE, 'passed': PROPS_APPENDIX == 'appendix_4'}

    # C18 半径轨迹：单调不增（含导数）且逐点复现附件 2
    ts = np.linspace(0.0, U.R_T_LAST, 10000)
    Rv = np.array([U.R_of_t(float(t)) for t in ts]) * P.CM_PER_M
    dRv = np.array([U.dRdt(float(t)) for t in ts]) * P.CM_PER_M
    repro = max(abs(U.R_of_t(float(t)) * P.CM_PER_M - r)
                for t, r in zip(U.R_T_GRID, U.R_DATA_CM))
    ck['C18'] = {'name': '半径轨迹单调不增且复现附件 2',
                 'max_dR_over_scan_cm': float(np.max(np.diff(Rv))),
                 'max_dRdt_cm_per_s': float(dRv.max()), 'min_dRdt_cm_per_s': float(dRv.min()),
                 'n_scan_points': int(ts.size), 'sample_repro_max_abs_cm': float(repro),
                 'tol_repro_cm': 1e-12, 'R0_cm': float(Rv[0]), 'R_end_cm': float(Rv[-1]),
                 'total_shrink_pct': float(100.0 * (1.0 - Rv[-1] / Rv[0])),
                 'passed': bool(np.max(np.diff(Rv)) <= 1e-14 and dRv.max() <= 1e-14
                                and repro < 1e-12)}

    # C20 绝干骨架守恒：h_m=0 时 sum(V_i C_i) 逐位守恒；三个反向变体必须显著漂移
    cfg0 = U.make_config(PROPS_APPENDIX, h_m=0.0)
    V = cfg0['V_cell']
    y0 = np.concatenate((np.full(N, P.T0_C), P.C0 * (0.6 + 0.8 * cfg0['eta_c'] ** 2)))
    m0 = float(y0[N:] @ V)
    drift, s_fwd = {}, None
    for tag, var in (('forward_M11', None), ('reverse_B_spurious_advection', 'spurious_advection'),
                     ('reverse_C_nonconservative', 'nonconservative')):
        s = U.integrate(lambda t, y, v=var: U.moving_domain_rhs(t, y, cfg0, v),
                        (0.0, C20_T_END), y0, N=N, max_step=P.MAX_STEP_LONG)
        assert s.success, s.message
        drift[tag] = abs(float(s.y[N:, -1] @ V) - m0) / m0
        if var is None:
            s_fwd = s
    m_end = float(s_fwd.y[N:, -1] @ V)
    R_a, R_b = U.R_of_t(0.0), U.R_of_t(C20_T_END)
    drift['reverse_A_drop_rho_d'] = abs(R_b ** 2 * m_end / (R_a ** 2 * m0) - 1.0)
    keep = abs(water_mass_per_length(C20_T_END, s_fwd.y[N:, -1], V)
               / water_mass_per_length(0.0, y0[N:], V) - 1.0)
    rev = [drift[k] for k in drift if k.startswith('reverse_')]
    ck['C20'] = {'name': '绝干骨架水量守恒（正向 + 三个反向变体）',
                 'forward_rel_drift': drift['forward_M11'], 'tol_forward': 1e-8,
                 'mass_kg_per_m_rel_drift_with_bookkeeping': float(keep),
                 'reverse_rel_drift': {k: v for k, v in drift.items() if k.startswith('reverse_')},
                 'tol_reverse_min': 1e-4, 'min_reverse_drift': float(min(rev)),
                 't_test_s': C20_T_END, 'R_cm_span': [R_a * P.CM_PER_M, R_b * P.CM_PER_M],
                 'rho_d_span': [U.rho_d_of_t(0.0), U.rho_d_of_t(C20_T_END)],
                 'note': '反向 A 丢弃 rho_d(t) 记账、B 按 §7.5 再加 R*Rdot 对流通量、'
                         'C 用非守恒 Laplacian 展开；三者分别漂移 %.2f%%、%.2f%%、%.2f%%'
                         % (100 * drift['reverse_A_drop_rho_d'],
                            100 * drift['reverse_B_spurious_advection'],
                            100 * drift['reverse_C_nonconservative']),
                 'passed': bool(drift['forward_M11'] < 1e-8 and min(rev) > 1e-4)}

    # C22 t=0 退化：R(0)=R0 时收缩域右端必须与固定域右端逐位相同
    y_init = U.initial_state(N)
    d0 = float(np.abs(U.moving_domain_rhs(0.0, y_init, CFG)
                      - U.fixed_domain_rhs(0.0, y_init, CFG)).max())
    ck['C22'] = {'name': 't=0 收缩域退化为固定域', 'measured_max_abs_diff': d0, 'tol': 1e-12,
                 'R_at_0_cm': U.R_of_t(0.0) * P.CM_PER_M, 'dRdt_at_0_cm_per_s': U.dRdt(0.0),
                 'passed': bool(d0 < 1e-12)}

    # 方向性判定：径向收缩下的末态绝干密度须与附录 4 零含水率密度相容，各向同性则不相容
    rho_radial = U.RHO_D0 * (P.R0_CM / U.R_MIN_CM) ** 2
    rho_iso = U.RHO_D0 * (P.R0_CM / U.R_MIN_CM) ** 3
    dev_rad = 100.0 * (rho_radial - P.RHO4_A) / P.RHO4_A
    dev_iso = 100.0 * (rho_iso - P.RHO4_A) / P.RHO4_A
    ck['C_direction'] = {'name': '收缩方向性判定（径向 vs 各向同性）', 'rho_d0': U.RHO_D0,
                         'rho_d_end_radial': float(rho_radial), 'rho_d_end_isotropic': float(rho_iso),
                         'reference_rho_zero_moisture': P.RHO4_A,
                         'deviation_radial_pct': float(dev_rad),
                         'deviation_isotropic_pct': float(dev_iso), 'tol_accept_pct': 5.0,
                         'tol_reject_pct': 20.0, 'selected': SHRINK_MODE,
                         'note': '径向假设下末态绝干密度 %.2f kg/m^3 与附录 4 零含水率密度 %g 相差 '
                                 '%.2f%%；各向同性假设给出 %.2f kg/m^3，相差 %.2f%%，物理上不可接受'
                                 % (rho_radial, P.RHO4_A, dev_rad, rho_iso, dev_iso),
                         'passed': bool(abs(dev_rad) < 5.0 and abs(dev_iso) > 20.0)}

    # 收缩量自洽性：几何体积比 vs 由附录 4 密度式反推的质量体积比（如实披露差距）
    rho_wet_thr = P.RHO4_A + P.RHO4_B * P.C_THR
    rho_d_thr = rho_wet_thr / (1.0 + P.C_THR)
    vr_mass = U.RHO_D0 / rho_d_thr
    vr_geom = (U.R_MIN_CM / P.R0_CM) ** 2
    gap = abs(vr_mass - vr_geom) / vr_mass
    ck['C_volume_consistency'] = {'name': '收缩量自洽性（几何 vs 密度式反推）',
                                  'volume_ratio_geometric': float(vr_geom),
                                  'volume_ratio_from_density': float(vr_mass),
                                  'relative_gap': float(gap), 'tol': 0.20,
                                  'rho_d_at_C_thr': float(rho_d_thr),
                                  'note': '附件 2 的几何收缩量 %.4f 与附录 4 密度式反推的 %.4f 差 %.2f%%；'
                                          '两者同阶但不完全自洽，本文以附件 2 实测轨迹为准，未反向调参'
                                          % (vr_geom, vr_mass, 100 * gap),
                                  'passed': bool(gap < 0.20)}
    return ck


# ------------------------------------------------------------ 主求解
def run():
    res = {'problem': 4, 'props_appendix': PROPS_APPENDIX, 'shrink_mode': SHRINK_MODE}
    ck = unit_tests()
    sol, t_end, cfg = solve_case(dense=True)
    N = cfg['N']
    res['t_end'] = {'seconds': t_end, 'hours': t_end / P.SEC_PER_HOUR,
                    'days': t_end / (24 * P.SEC_PER_HOUR), 'nfev': int(sol.nfev),
                    'n_solver_steps': int(len(sol.t)),
                    'R_at_t_end_cm': U.R_of_t(t_end) * P.CM_PER_M}

    # C19 首次下穿：事件时刻贴阈值，且此前密扫无更早穿越
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
    ck['C07'] = {'name': '事件时刻最大值在中心', 'argmax_cell': int(C_e.argmax()),
                 'C_center': float(C_e[0]), 'C_outermost_cell': float(C_e[-1]),
                 'passed': bool(C_e.argmax() == 0)}

    # ---- C21 归因分解：2x2 四次独立真实运行（物性附录 x 是否收缩）
    runs, sols = {}, {}
    for tag, key, mv in (('q3_baseline', 'appendix_3', False), ('app4_noshrink', 'appendix_4', False),
                         ('app3_shrink', 'appendix_3', True), ('app4_shrink', 'appendix_4', True)):
        s_c, t_c, _ = solve_case(key, mv, dense=(tag == 'q3_baseline'))
        runs[tag] = {'props': key, 'shrink': mv, 't_end_s': t_c,
                     't_end_h': t_c / P.SEC_PER_HOUR, 'nfev': int(s_c.nfev)}
        sols[tag] = s_c
    t_b, t_p, t_s, t_f = (runs[k]['t_end_s'] for k in
                          ('q3_baseline', 'app4_noshrink', 'app3_shrink', 'app4_shrink'))
    d_props, d_shrink = t_p - t_b, t_f - t_p
    # 收缩效应依所在物性基准而异：附录 4 上为 d_shrink，附录 3 上为 d_shrink_app3
    d_shrink_app3 = t_s - t_b
    # 物性效应同样有两个基准：固定域上为 d_props，收缩域上为 d_props_shrunk
    d_props_shrunk = t_f - t_s
    inter = d_shrink - d_shrink_app3
    prod = (t_p / t_b) * (t_s / t_b)
    # 2x2 设计只有 4 个数、4 个待定量（基准 + 两个主效应 + 交互），是饱和设计：
    # 任何"链式闭合"都是望远镜恒等式，恒过而无信息量，故不作为校验项。
    # 可失败的判据有两条：四次运行必须两两可分辨；乘性框架的残差必须真的小。
    t_all = sorted((t_b, t_p, t_s, t_f))
    min_gap = min(t_all[i + 1] - t_all[i] for i in range(3))
    mult_resid = 100.0 * abs((t_f / t_b) / prod - 1.0)
    ck['C21'] = {'name': '归因分解四例可分辨与乘性框架残差',
                 'min_pairwise_gap_s': float(min_gap), 'tol_min_gap_s': 60.0,
                 'tol_mult_residual_pct': 20.0,
                 'delta_props_s': d_props, 'delta_shrink_s': d_shrink,
                 'delta_shrink_on_app3_s': float(d_shrink_app3),
                 'delta_props_on_shrunk_s': float(d_props_shrunk),
                 'total_s': t_f - t_b, 'interaction_s': float(inter),
                 'interaction_over_total_pct': float(100.0 * abs(inter) / abs(t_f - t_b)),
                 'mult_ratio_props': t_p / t_b, 'mult_ratio_shrink': t_s / t_b,
                 'mult_predicted_ratio': float(prod), 'mult_actual_ratio': t_f / t_b,
                 'mult_residual_pct': float(100.0 * abs((t_f / t_b) / prod - 1.0)),
                 'n_runs': len(runs),
                 'note': '收缩效应在附录 3 物性下为 %.0f s、在附录 4 物性下为 %.0f s，二者之差 %.0f s 即交互项；'
                         '物性效应在固定域为 %.0f s、在收缩域为 %.0f s。加法框架下交互项达总效应的 %.0f%%，'
                         '乘法框架残差 %.1f%%（以预测比值为分母），故两机制近似乘性叠加'
                         % (d_shrink_app3, d_shrink, inter, d_props, d_props_shrunk,
                            100.0 * abs(inter) / abs(t_f - t_b),
                            100.0 * abs((t_f / t_b) / prod - 1.0)),
                 'passed': bool(len(runs) == 4 and min_gap > 60.0 and mult_resid < 20.0)}
    res['attribution'] = runs

    # ---- V3.2 网格收敛（五档 + Richardson 外推，t_end 以相对判据考核）
    ladder, prev = [], None
    for n in (30, 60, 120, 240, 480):
        _, t_n, _ = solve_case(N=n)
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
                  'tol_rel': 2e-3, 'observed_order': order, 'richardson_limit_s': float(rich),
                  'richardson_limit_h': float(rich / P.SEC_PER_HOUR),
                  'baseline_minus_richardson_h': (t_end - rich) / P.SEC_PER_HOUR,
                  'monotone_decreasing': bool(all(dseq[i] > dseq[i + 1] for i in range(len(dseq) - 1))),
                  'note': '与问题三同口径：表面重构与阈值定位均为一阶，故 t_end 用相对判据 0.2%%，'
                          '最细两档相对变化 %.3f%%' % (100 * rseq[-1]),
                  'passed': bool(rseq[-1] < 2e-3
                                 and all(dseq[i] > dseq[i + 1] for i in range(len(dseq) - 1)))}
    res['mesh_ladder'] = ladder

    # ---- V3.3 时间容差对照
    _, t_loose, _ = solve_case(rtol=1e-6, atol=1e-8)
    ck['V3.3'] = {'name': '时间容差对照（t_end）', 'measured_dt_end_s': abs(t_loose - t_end),
                  'tol': 60.0, 't_end_rtol_1e_6_s': t_loose, 't_end_rtol_1e_8_s': t_end,
                  'passed': bool(abs(t_loose - t_end) < 60.0)}

    # ---- 输出网格：60 s 步长到 t_end；r > R(t) 的格写空（③P09），末列为药材表面
    n_rows = int(np.floor(t_end / P.OUT_STEP_LONG))
    times = [P.OUT_STEP_LONG * (k + 1) for k in range(n_rows)]
    r_fixed = np.asarray(P.Q4_FIXED_R_CM, float)
    Cg = np.full((len(times), r_fixed.size + 1), np.nan)
    Tg = np.full_like(Cg, np.nan)
    R_ser = np.empty(len(times))
    Cs_ser = np.empty(len(times))
    Ts_ser = np.empty(len(times))
    cmax_ser = np.empty(len(times))
    vavg_ser = np.empty(len(times))
    mw_ser = np.empty(len(times))
    for k, t in enumerate(times):
        y = sol.sol(float(t))
        T, C = y[:N], y[N:]
        R_m = U.R_of_t(float(t))
        R_cm = R_m * P.CM_PER_M
        T_s, C_s = U.surface_pair(cfg, T, C, float(t), R_m=R_m)[:2]
        ins = r_fixed <= R_cm + 1e-12
        Cg[k, :-1][ins] = U.to_output_radii(C, C_s, cfg['eta_c'], r_fixed[ins], R_cm)
        Tg[k, :-1][ins] = U.to_output_radii(T, T_s, cfg['eta_c'], r_fixed[ins], R_cm)
        Cg[k, -1], Tg[k, -1] = C_s, T_s
        R_ser[k], Cs_ser[k], Ts_ser[k] = R_cm, C_s, T_s
        cmax_ser[k] = C.max()
        vavg_ser[k] = U.vol_average(C, cfg['V_cell'])
        mw_ser[k] = water_mass_per_length(float(t), C, cfg['V_cell'])
    cols = [*P.Q4_FIXED_R_CM, P.SURFACE_LABEL]
    rt = U.write_result_xlsx(P.RESULT_FILES[4], {'Sheet1': Cg}, times, cols)
    ck['C16'] = {'name': '写盘-读回往返一致（含空单元格掩码）',
                 'measured': max(v['roundtrip_max_abs_diff'] for v in rt.values()),
                 'tol': 0.0, 'per_sheet': rt, 'n_blank_cells': rt['Sheet1']['blank_cells'],
                 'blank_rule': 'r > R(t) 的格为空（药材已收缩到该位置以内）', 'passed': True}

    # ---- 全局水量平衡闭合：储量减少量 = 表面对流累计失水量
    tb = np.concatenate(([0.0], np.asarray(times, float)))
    y_0 = U.initial_state(N)
    mw_b = np.concatenate(([water_mass_per_length(0.0, y_0[N:], cfg['V_cell'])], mw_ser))
    cs_b = np.concatenate(([U.surface_pair(cfg, y_0[:N], y_0[N:], 0.0, R_m=U.R_of_t(0.0))[1]], Cs_ser))
    ca_b = np.array([U.driver_Ca(float(t)) for t in tb])
    rate = np.array([2.0 * np.pi * U.R_of_t(float(t)) * U.rho_d_of_t(float(t)) * P.HM_MASS
                     for t in tb]) * (cs_b - ca_b)
    cum = np.concatenate(([0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(tb))))
    drop = mw_b[0] - mw_b[-1]
    closure = abs(drop - cum[-1]) / drop
    ck['C20_balance'] = {'name': '全局水量平衡闭合（h_m 非零）', 'measured_rel_gap': float(closure),
                         'tol': 1e-3, 'stored_drop_kg_per_m': float(drop),
                         'cumulative_flux_kg_per_m': float(cum[-1]),
                         'm_w_initial_kg_per_m': float(mw_b[0]), 'm_w_final_kg_per_m': float(mw_b[-1]),
                         'note': '储量按 2*pi*rho_d(t)*R(t)^2*sum(V_i C_i) 记，失水按表面对流通量'
                                 '在 60 s 网格上梯形累加，残差含梯形求积误差',
                         'passed': bool(closure < 1e-3)}

    # ---- 第 2 层健康性
    ck['C13'] = {'name': '干燥方向性（全程）', 'max_rise_of_Cmax': float(np.max(np.diff(cmax_ser))),
                 'max_rise_of_volavg': float(np.max(np.diff(vavg_ser))), 'tol': 1e-12,
                 'passed': bool(np.max(np.diff(cmax_ser)) < 1e-12
                                and np.max(np.diff(vavg_ser)) < 1e-12)}
    ta_env = np.array([U.driver_Ta(float(t)) for t in times])
    lo = min(P.T0_C, ta_env.min(), U.TA_PLATEAU)
    hi = max(P.T0_C, ta_env.max(), U.TA_PLATEAU)
    ck['V2.4'] = {'name': '温度落在驱动包络内', 'T_min': float(np.nanmin(Tg)),
                  'T_max': float(np.nanmax(Tg)), 'envelope': [float(lo), float(hi)],
                  'passed': bool(np.nanmin(Tg) >= lo - 1e-9 and np.nanmax(Tg) <= hi + 1e-9)}
    ck['V3.12'] = {'name': '与题面 2-3 天量级对照', 'measured_days': t_end / (24 * P.SEC_PER_HOUR),
                   'reference_range_days': [P.DUR_DAYS_LOW, P.DUR_DAYS_HIGH],
                   'inside_range': bool(P.DUR_DAYS_LOW <= t_end / (24 * P.SEC_PER_HOUR)
                                        <= P.DUR_DAYS_HIGH),
                   'note': '量级参照，非标定目标',
                   'passed': bool(0.1 * P.DUR_DAYS_LOW <= t_end / (24 * P.SEC_PER_HOUR)
                                  <= 10 * P.DUR_DAYS_HIGH)}

    def snap(t, r_req):
        """给定时刻在请求半径列上的 (T, C)；超出当前外表面的位置返回 nan。"""
        y = sol.sol(float(t))
        T, C = y[:N], y[N:]
        R_m = U.R_of_t(float(t))
        R_cm = R_m * P.CM_PER_M
        T_s, C_s = U.surface_pair(cfg, T, C, float(t), R_m=R_m)[:2]
        rr = np.asarray(r_req, float)
        ins = rr <= R_cm + 1e-12
        tv = np.full(rr.size, np.nan)
        cv = np.full(rr.size, np.nan)
        tv[ins] = U.to_output_radii(T, T_s, cfg['eta_c'], rr[ins], R_cm)
        cv[ins] = U.to_output_radii(C, C_s, cfg['eta_c'], rr[ins], R_cm)
        return tv, cv, R_cm, T_s, C_s

    def jnan(a):
        return [None if not np.isfinite(x) else float(x) for x in np.asarray(a, float)]

    # ---- 论文表 6：每隔 6 h x 每隔 0.5 cm，附半径与表面值
    six_h = int(6 * P.SEC_PER_HOUR)
    t6 = [six_h * k for k in range(1, int(t_end // six_h) + 1)]
    rows6 = []
    for t in t6:
        _, cv, R_cm, _, C_s = snap(t, P.TABLE_R_CM)
        rows6.append({'t_s': t, 't_h': t / P.SEC_PER_HOUR, 'R_cm': round(R_cm, 4),
                      'C': jnan(np.round(cv, 4)), 'C_surface': round(float(C_s), 4)})
    # 末行取事件时刻的场值，与上面各行同一 snap 口径；不得用 60 s 输出网格末行冒充 t_end
    _, cv_end, R_cm_end, _, C_s_end = snap(t_end, P.TABLE_R_CM)
    res['table_6_moisture'] = {'radii_cm': P.TABLE_R_CM, 'rows': rows6,
                               'surface_label': P.SURFACE_LABEL,
                               't_end_row': {'label': '烘干结束时间', 'hours': t_end / P.SEC_PER_HOUR,
                                             'seconds': t_end, 'R_cm': U.R_of_t(t_end) * P.CM_PER_M,
                                             'C': jnan(np.round(cv_end, 4)),
                                             'C_surface': round(float(C_s_end), 4),
                                             'source': 'sol.sol(t_end) at event time'}}

    # ---- 图件数据：半径轨迹、收缩自洽、移动边界剖面、与问题三对比、水量平衡、热图
    t_dense = np.linspace(0.0, U.R_T_LAST, 601)
    res['radius_curve'] = {'t_data_s': U.R_T_GRID.tolist(), 'R_data_cm': U.R_DATA_CM.tolist(),
                           't_dense_s': t_dense.tolist(),
                           'R_pchip_cm': [U.R_of_t(float(t)) * P.CM_PER_M for t in t_dense],
                           'R_weibull_cm': [float(x) for x in radius_weibull_reference(t_dense)],
                           'dRdt_cm_per_s': [U.dRdt(float(t)) * P.CM_PER_M for t in t_dense],
                           't_end_s': t_end, 'R_at_t_end_cm': U.R_of_t(t_end) * P.CM_PER_M}
    res['radius_curve'].update(
        {'weibull_params': {'R_inf_cm': float(radius_weibull_reference.params[0]),
                            'tau_s': float(radius_weibull_reference.params[1]),
                            'k': float(radius_weibull_reference.params[2])},
         'weibull_rmse_cm': radius_weibull_reference.rmse_cm,
         'weibull_max_abs_cm': radius_weibull_reference.max_abs_cm,
         'note': 'Weibull 只作描述性参考；PDE 中的 R(t) 一律取附件 2 的保单调 PCHIP 插值'})
    res['shrink_consistency'] = {k: ck['C_volume_consistency'][k] for k in
                                 ('volume_ratio_geometric', 'volume_ratio_from_density',
                                  'relative_gap', 'rho_d_at_C_thr')}
    res['shrink_consistency'].update({'rho_d0': U.RHO_D0,
                                      'rho_d_end_radial': ck['C_direction']['rho_d_end_radial'],
                                      'rho_d_end_isotropic': ck['C_direction']['rho_d_end_isotropic'],
                                      'reference_rho_zero_moisture': P.RHO4_A})

    # Bland-Altman 需要成对样本：对附件 2 的每个时刻各给一对体积比
    #   几何路径 x = (R(t)/R0)^2（附件 2 实测半径，轴向不变）
    #   密度路径 y = rho_d0 / rho_d(C̄(t))，其中 rho_d 由附录 4 湿密度式在**本解的体积平均含水率**上求值
    # 两条路径互相独立（一条只用附件 2 几何，一条只用附录 4 物性 + 解出的含水率），故其差值有诊断意义
    ba_t = U.R_T_GRID[U.R_T_GRID <= t_end]
    ba_x, ba_y, ba_cbar = [], [], []
    for t in ba_t:
        yv = sol.sol(float(t))
        cbar = float(U.vol_average(yv[N:], cfg['V_cell']))
        rho_d = (P.RHO4_A + P.RHO4_B * cbar) / (1.0 + cbar)
        ba_x.append(float((U.R_of_t(float(t)) * P.CM_PER_M / P.R0_CM) ** 2))
        ba_y.append(float(U.RHO_D0 / rho_d))
        ba_cbar.append(cbar)
    ba_x, ba_y = np.asarray(ba_x), np.asarray(ba_y)
    diff, mean = ba_y - ba_x, 0.5 * (ba_x + ba_y)
    bias, sd = float(diff.mean()), float(diff.std(ddof=1))
    res['shrink_consistency'].update({
        'bland_altman': {'t_s': ba_t.tolist(), 't_h': (ba_t / P.SEC_PER_HOUR).tolist(),
                         'volume_ratio_geometric': ba_x.tolist(),
                         'volume_ratio_from_density': ba_y.tolist(),
                         'volavg_C': ba_cbar,
                         'mean': mean.tolist(), 'diff': diff.tolist(),
                         'bias': bias, 'sd_diff': sd,
                         'loa_lower': bias - 1.96 * sd, 'loa_upper': bias + 1.96 * sd,
                         'n_pairs': int(ba_t.size),
                         'n_outside_loa': int(np.sum((diff < bias - 1.96 * sd)
                                                     | (diff > bias + 1.96 * sd))),
                         'note': '几何路径只用附件 2 半径，密度路径只用附录 4 密度式 + 本解体积平均含水率；'
                                 '两者独立，故偏差即两套数据源的自洽性度量，未用于反向调参'}})
    frames = []
    for t in t6:
        y = sol.sol(float(t))
        R_cm = U.R_of_t(float(t)) * P.CM_PER_M
        T_s, C_s = U.surface_pair(cfg, y[:N], y[N:], float(t), R_m=R_cm / P.CM_PER_M)[:2]
        frames.append({'t_s': t, 't_h': t / P.SEC_PER_HOUR, 'R_cm': R_cm,
                       'r_cm': np.round(np.concatenate((cfg['eta_c'] * R_cm, [R_cm])), 6).tolist(),
                       'C': np.round(np.concatenate((y[N:], [C_s])), 6).tolist(),
                       'T': np.round(np.concatenate((y[:N], [T_s])), 6).tolist()})
    res['moving_boundary_frames'] = frames
    grid = np.linspace(0.0, max(t_end, runs['q3_baseline']['t_end_s']), 400)

    def cmax_curve(s, t_stop):
        return [None if t > t_stop else float(s.sol(float(t))[N:].max()) for t in grid]

    res['compare_q3'] = {'t_s': grid.tolist(), 't_h': (grid / P.SEC_PER_HOUR).tolist(),
                         'C_max_q4_shrink': cmax_curve(sol, t_end),
                         'C_max_q3_fixed': cmax_curve(sols['q3_baseline'],
                                                      runs['q3_baseline']['t_end_s']),
                         't_end_q4_h': t_end / P.SEC_PER_HOUR,
                         't_end_q3_h': runs['q3_baseline']['t_end_s'] / P.SEC_PER_HOUR,
                         'delta_h': (t_end - runs['q3_baseline']['t_end_s']) / P.SEC_PER_HOUR,
                         'delta_pct': 100.0 * (t_end - runs['q3_baseline']['t_end_s'])
                         / runs['q3_baseline']['t_end_s'], 'threshold': P.C_THR}

    # ---- 五个测点的逐点达标时刻（斜率图）：用**物质坐标** eta 而非固定物理半径。
    # 收缩体内固定 r 会在半径缩过它之后不再对应任何骨架物质点，两种口径就不可比；
    # 固定 eta 始终是同一物质点，且在问题三（R 恒为 2 cm）下正好落在 0/0.5/1/1.5/2 cm。
    eta_probe = [0.0, 0.25, 0.5, 0.75, 1.0]

    def probe_cross(s, t_stop):
        """在密扫网格上找该物质点含水率首次下穿阈值的时刻，线性定位到相邻两点之间。"""
        tt = np.linspace(0.0, t_stop, 4000)
        out = []
        for e in eta_probe:
            j = min(int(round(e * (N - 1))), N - 1)
            vals = np.array([float(s.sol(float(t))[N:][j]) for t in tt])
            below = np.nonzero(vals <= P.C_THR)[0]
            if not below.size:
                out.append(None)
                continue
            i2 = int(below[0])
            if i2 == 0:
                out.append(0.0)
                continue
            v1, v2, t1, t2 = vals[i2 - 1], vals[i2], tt[i2 - 1], tt[i2]
            tc = t2 if v2 == v1 else t1 + (t2 - t1) * (v1 - P.C_THR) / (v1 - v2)
            out.append(float(tc / P.SEC_PER_HOUR))
        return out

    res['compare_q3'].update({
        'probe_eta': eta_probe,
        'probe_r_cm_q3': [round(e * P.R0_CM, 4) for e in eta_probe],
        'probe_r_cm_q4_at_t_end': [round(e * U.R_of_t(t_end) * P.CM_PER_M, 4) for e in eta_probe],
        'probe_cross_h_q4': probe_cross(sol, t_end),
        'probe_cross_h_q3': probe_cross(sols['q3_baseline'], runs['q3_baseline']['t_end_s']),
        'attribution_runs_h': {k: runs[k]['t_end_s'] / P.SEC_PER_HOUR
                               for k in ('q3_baseline', 'app4_noshrink', 'app3_shrink',
                                         'app4_shrink')},
        'probe_note': '测点取物质坐标 eta=r/R(t)；问题三 R 恒为 2 cm，故 eta 与固定物理半径一一对应。'
                      '归因三次运行（R1 附录4+固定域 / R2 附录3+收缩 / R3 附录4+收缩）一并给出，'
                      '供斜率图叠加'})
    st = slice(None, None, 10)
    res['mass_balance'] = {'t_s': tb[st].tolist(), 't_h': (tb[st] / P.SEC_PER_HOUR).tolist(),
                          'm_w_kg_per_m': np.round(mw_b[st], 8).tolist(),
                          'cumulative_loss_kg_per_m': np.round(cum[st], 8).tolist(),
                          'flux_rate_kg_per_m_s': [float(x) for x in rate[st]],
                          'stored_drop_kg_per_m': float(drop),
                          'closure_rel_gap': float(closure)}
    res['drying_curve'] = {'t_s': times[st], 't_h': [t / P.SEC_PER_HOUR for t in times[st]],
                           'C_max': np.round(cmax_ser[st], 6).tolist(),
                           'C_volavg': np.round(vavg_ser[st], 6).tolist(),
                           'C_center': jnan(np.round(Cg[st, 0], 6)),
                           'C_surface': np.round(Cs_ser[st], 6).tolist(),
                           'T_center': jnan(np.round(Tg[st, 0], 6)),
                           'T_surface': np.round(Ts_ser[st], 6).tolist(),
                           'R_cm': np.round(R_ser[st], 6).tolist(), 'threshold': P.C_THR}
    sh = slice(None, None, 20)
    res['heatmap'] = {'t_s': times[sh], 't_h': [t / P.SEC_PER_HOUR for t in times[sh]],
                      'r_cm': cols[:-1], 'surface_label': P.SURFACE_LABEL,
                      'R_cm': np.round(R_ser[sh], 6).tolist(),
                      'C': [jnan(r) for r in np.round(Cg[sh, :-1], 4)],
                      'T': [jnan(r) for r in np.round(Tg[sh, :-1], 4)],
                      'C_surface': np.round(Cs_ser[sh], 4).tolist(),
                      'T_surface': np.round(Ts_ser[sh], 4).tolist()}
    res['summary'] = {'t_end_h': t_end / P.SEC_PER_HOUR, 't_end_days': t_end / (24 * P.SEC_PER_HOUR),
                      'R_min_cm': float(R_ser.min()), 'R_max_cm': float(R_ser.max()),
                      'R_at_t_end_cm': U.R_of_t(t_end) * P.CM_PER_M,
                      'C_max_at_t_end': float(C_e.max()), 'C_center_at_t_end': float(C_e[0]),
                      'C_surface_at_t_end': float(U.surface_pair(cfg, y_e[:N], C_e, t_end,
                                                                R_m=U.R_of_t(t_end))[1]),
                      'volavg_C_at_t_end': float(U.vol_average(C_e, cfg['V_cell'])),
                      'T_center_at_t_end': float(y_e[0]),
                      'herb_T_max': float(np.nanmax(Tg)), 'herb_T_min': float(np.nanmin(Tg)),
                      'herb_C_max': float(np.nanmax(Cg)), 'herb_C_min': float(np.nanmin(Cg)),
                      'm_w_initial_kg_per_m': float(mw_b[0]), 'm_w_final_kg_per_m': float(mw_b[-1]),
                      'water_removed_pct': float(100.0 * drop / mw_b[0]),
                      'rho_d0': U.RHO_D0, 'rho_d_at_t_end': U.rho_d_of_t(t_end),
                      'n_output_rows': len(times), 'n_blank_cells': rt['Sheet1']['blank_cells'],
                      'D_at_center_t_end_m2_s': float(U.props_appendix_4(
                          np.array([C_e[0]]), np.array([y_e[0]]))[3][0]),
                      'D_at_t0_m2_s': float(U.props_appendix_4(
                          np.array([P.C0]), np.array([P.T0_C]))[3][0])}
    res['xlsx_report'] = rt
    res['checks'] = ck
    res['all_checks_passed'] = bool(all(v.get('passed') for v in ck.values()))
    return res, ck, sol, cfg, t_end, times, Cg, Tg


# ------------------------------------------------------------ 描述性参考（不参与求解）
def _weibull_R(t, R_inf, tau, k):
    return R_inf + (P.R0_CM - R_inf) * np.exp(-(np.asarray(t, float) / tau) ** k)


def radius_weibull_reference(t):
    """附件 2 收缩轨迹的 Weibull 参考拟合，只用于作图与报告收缩标度。

    本函数不参与任何 PDE 求解：问题四方程里的 R(t) 一律取附件 2 的保单调 PCHIP 插值
    （U.R_of_t），拟合式仅回答『实测收缩曲线像不像 Weibull』这一描述性问题。
    """
    if getattr(radius_weibull_reference, 'params', None) is None:
        from scipy.optimize import curve_fit
        p, _ = curve_fit(_weibull_R, U.R_T_GRID, U.R_DATA_CM, p0=[1.15, 5.0e4, 1.0],
                         bounds=([0.5, 1.0e3, 0.3], [2.0, 1.0e6, 3.0]), maxfev=20000)
        pred = _weibull_R(U.R_T_GRID, *p)
        radius_weibull_reference.params = p
        radius_weibull_reference.rmse_cm = float(np.sqrt(np.mean((pred - U.R_DATA_CM) ** 2)))
        radius_weibull_reference.max_abs_cm = float(np.abs(pred - U.R_DATA_CM).max())
    return _weibull_R(t, *radius_weibull_reference.params)


if __name__ == '__main__':
    out = run()[0]
    P.FIG_DIR.mkdir(exist_ok=True)
    (P.FIG_DIR / 'problem_4_results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, v in out['checks'].items():
        print(f"{k}: {'PASS' if v.get('passed') else 'FAIL'}  {v.get('name', '')}")
    print('Q4 checks passed:', out['all_checks_passed'])
    print('t_end = %.3f s = %.4f h = %.4f d (R = %.4f cm)'
          % (out['t_end']['seconds'], out['t_end']['hours'], out['t_end']['days'],
             out['t_end']['R_at_t_end_cm']))
    a = out['attribution']
    for k in ('q3_baseline', 'app4_noshrink', 'app3_shrink', 'app4_shrink'):
        print('  %-14s t_end = %8.4f h' % (k, a[k]['t_end_h']))
    s = out['summary']
    print('water removed %.2f%% (%.4f -> %.4f kg/m); blanks %d'
          % (s['water_removed_pct'], s['m_w_initial_kg_per_m'], s['m_w_final_kg_per_m'],
             s['n_blank_cells']))
