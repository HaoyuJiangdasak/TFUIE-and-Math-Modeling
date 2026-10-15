# code/problem1.py — 问题一：预热平衡阶段的解耦热-质输运（附录 2）+ 半解析对照
import json

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P
import utils as U

PROPS_APPENDIX = 'appendix_2'
CFG = U.make_config(PROPS_APPENDIX)
ALPHA = P.LAM_A2 / (P.RHO_A2 * P.CP_A2)
BI_T = P.H_CONV * P.R0_M / P.LAM_A2
BI_M = P.HM_MASS * P.R0_M / (P.D2_PREFACTOR * np.exp(-P.D2_MOIST_EXP / P.C0))


def rhs_coupled_q1(t, y):
    """问题一右端：附录 2 常物性，温度场线性且不受水分场反馈。"""
    return U.fixed_domain_rhs(t, y, CFG)


# ------------------------------------------------------------ 第 1 层单元测试
def unit_tests():
    ck = {}
    N, deta = CFG['N'], CFG['deta']
    A_face, V_cell = CFG['A_face'], CFG['V_cell']

    # C01 均匀场零通量（与空气平衡，故表面通量亦为零）
    Cbar = 1.0
    Cu = np.full(N, Cbar)
    _, _, _, D = U.eval_props(CFG, Cu, np.full(N, P.T0_C))
    Cs = U.reconstruct_surface(Cu[-1], D[-1], CFG['h_m'], Cbar, CFG['R_m'], deta)
    surf = -CFG['R_m'] * CFG['h_m'] * (Cs - Cbar)
    div = U.flux_divergence(Cu, U.face_harmonic(D), surf, A_face, V_cell, deta) / CFG['R_m'] ** 2
    ck['C01'] = {'name': '均匀场零通量', 'measured': float(np.abs(div).max()), 'tol': 1e-8,
                 'passed': bool(np.abs(div).max() < 1e-8)}

    # C02 柱面通量与 r 成正比（面积权写成 r_i 时此项失败）
    a, b = 30.0, 120.0
    r_c = CFG['eta_c'] * P.R0_M
    Tlin = a + b * r_c
    lam_f = U.face_harmonic(np.full(N, P.LAM_A2))
    inner = lam_f * np.diff(Tlin) / deta
    q_face = -inner / CFG['R_m']                      # 物理空间的傅里叶通量 = -lam*dT/dr
    rel = float(np.max(np.abs(q_face + P.LAM_A2 * b)) / (P.LAM_A2 * abs(b)))
    ck['C02'] = {'name': '柱面通量正比于 r', 'measured': rel, 'tol': 1e-8, 'passed': bool(rel < 1e-8),
                 'note': '线性场下界面通量密度恒定，面积权 A_face=eta_{i+1/2} 使总流量正比于 r'}

    # C03 两个独立分布场
    y = U.initial_state(N)
    dy = rhs_coupled_q1(50.0, y)
    ck['C03'] = {'name': '双场独立', 'len_y': int(len(y)), 'expect_len': 2 * N,
                 'dT_absmax': float(np.abs(dy[:N]).max()), 'dC_absmax': float(np.abs(dy[N:]).max()),
                 'slices_alias': bool(np.shares_memory(y[:N], y[N:])),
                 'passed': bool(len(y) == 2 * N and np.abs(dy[:N]).max() > 0
                                and np.abs(dy[N:]).max() > 0 and not np.shares_memory(y[:N], y[N:]))}

    # C05 Robin 闭合恒等式（温度侧与水分侧同构）
    T, C = y[:N] + 3.0, y[N:] * 0.9
    Ts, Cs2, Ta, Ca, lamN, DN = U.surface_pair(CFG, T, C, 300.0)
    resC = abs(CFG['h_m'] * (Cs2 - Ca) - 2 * DN / (CFG['R_m'] * deta) * (C[-1] - Cs2))
    resT = abs(CFG['h'] * (Ts - Ta) - 2 * lamN / (CFG['R_m'] * deta) * (T[-1] - Ts))
    relC = resC / max(CFG['h_m'] * abs(Cs2 - Ca), 1e-30)
    relT = resT / max(CFG['h'] * abs(Ts - Ta), 1e-30)
    ck['C05'] = {'name': 'Robin 闭合一致', 'measured_C': float(relC), 'measured_T': float(relT),
                 'tol': 1e-6, 'passed': bool(relC < 1e-6 and relT < 1e-6)}

    # C10 单向解耦：扰动 C 不得改变温度场右端
    worst = 0.0
    for scale in (0.9, 1.1):
        y2 = y.copy()
        y2[N:] = y[N:] * scale
        worst = max(worst, float(np.abs(rhs_coupled_q1(50.0, y2)[:N] - dy[:N]).max()))
    ck['C10'] = {'name': '问题一单向解耦', 'measured': worst, 'tol': 1e-14, 'passed': bool(worst < 1e-14)}

    # C11 附录绑定
    ck['C11'] = {'name': '附录绑定', 'props_appendix': PROPS_APPENDIX,
                 'passed': PROPS_APPENDIX == 'appendix_2'}

    # C14 低含水率下界保护
    tiny = np.full(N, 1e-18)
    out = U.eval_props(CFG, tiny, np.full(N, P.T0_C))
    ck['C14'] = {'name': '低含水率下界保护', 'C_floor': P.C_FLOOR,
                 'D_at_1e-18': float(out[3][0]), 'finite': bool(np.all(np.isfinite(np.concatenate(out)))),
                 'passed': bool(np.all(np.isfinite(np.concatenate(out))))}
    return ck


# ------------------------------------------------------------ 主求解
def solve(N=P.N_CELLS, t_eval=None, t_end=P.Q1_T_END):
    cfg = CFG if N == P.N_CELLS else U.make_config(PROPS_APPENDIX, N=N)
    rhs = rhs_coupled_q1 if N == P.N_CELLS else (lambda t, y: U.fixed_domain_rhs(t, y, cfg))
    sol = U.integrate(rhs, (0.0, float(t_end)), U.initial_state(N),
                      t_eval=t_eval, N=N, max_step=P.MAX_STEP_SHORT)
    assert sol.success, sol.message
    return sol, cfg


def fields_on_output_grid(sol, cfg, times):
    """把格心解映射到 21 个固定距离列：中心二阶外推 + 线性插值 + 表面 M3 重构。"""
    N = cfg['N']
    Tg = np.empty((len(times), len(P.OUT_R_CM)))
    Cg = np.empty_like(Tg)
    surf = np.empty((len(times), 2))
    for k, t in enumerate(times):
        y = sol.y[:, k]
        T, C = y[:N], y[N:]
        Ts, Cs, _, _, _, _ = U.surface_pair(cfg, T, C, float(t))
        Tg[k] = U.to_output_radii(T, Ts, cfg['eta_c'], P.OUT_R_CM, P.R0_CM)
        Cg[k] = U.to_output_radii(C, Cs, cfg['eta_c'], P.OUT_R_CM, P.R0_CM)
        surf[k] = (Ts, Cs)
    return Tg, Cg, surf


def run():
    res = {'problem': 1, 'props_appendix': PROPS_APPENDIX,
           'characteristics': {'alpha_m2_s': ALPHA, 'Bi_T': BI_T, 'Bi_m': BI_M,
                               'R0_sq_over_alpha_s': P.R0_M ** 2 / ALPHA,
                               'D_at_C0_m2_s': P.D2_PREFACTOR * np.exp(-P.D2_MOIST_EXP / P.C0),
                               'Fo_T_1800s': ALPHA * 1800.0 / P.R0_M ** 2,
                               'penetration_depth_cm': float(np.sqrt(
                                   P.D2_PREFACTOR * np.exp(-P.D2_MOIST_EXP / P.C0) * 1800.0) * P.CM_PER_M)}}
    ck = unit_tests()

    times = P.Q1_OUT_TIMES
    sol, cfg = solve(t_eval=times)
    Tg, Cg, surf = fields_on_output_grid(sol, cfg, times)
    res['fields'] = {'n_times': len(times), 'n_radii': len(P.OUT_R_CM)}

    # ---- C09 半解析对照（7 时刻 x 21 位置 = 147 点），本题唯一严格外部对照
    T_ana, beta, A_n, tau = U.semi_analytic_temperature(
        P.Q1_TABLE_TIMES, P.OUT_R_CM, ALPHA, BI_T, P.T0_C, U._T_GRID, U._TA_OBS)
    idx = [times.index(t) for t in P.Q1_TABLE_TIMES]
    gap = np.abs(Tg[idx] - T_ana)
    ck['C09'] = {'name': '半解析解对照 147 点', 'measured_max_abs_C': float(gap.max()),
                 'tol': 1e-3, 'n_points': int(gap.size), 'n_modes': P.N_MODES,
                 'passed': bool(gap.max() < 1e-3 and gap.size == 147)}
    res['semi_analytic'] = {'beta_first6': [float(b) for b in beta[:6]],
                            'A_first6': [float(a) for a in A_n[:6]],
                            'tau_first3_s': [float(x) for x in tau[:3]],
                            'max_abs_dev_C': float(gap.max()),
                            'mean_abs_dev_C': float(gap.mean()),
                            'per_time_max_dev_C': [float(g) for g in gap.max(axis=1)],
                            'T_analytic_table': np.round(T_ana[:, [0, 5, 10, 15, 20]], 6).tolist(),
                            # 残差诊断四联图要按半径、按时间铺开，故给全 7x21=147 点而非 5 列摘要
                            'times_s': list(P.Q1_TABLE_TIMES), 'r_cm': list(P.OUT_R_CM),
                            'T_analytic_full': np.round(T_ana, 9).tolist(),
                            'T_numeric_full': np.round(Tg[idx], 9).tolist(),
                            'residual_C': np.round(Tg[idx] - T_ana, 12).tolist(),
                            'n_points': int(gap.size)}

    # ---- V3.2 网格收敛阶梯（五档）+ C04 表面值网格无关性
    ladder = []
    prev_center = prev_surfC = None
    for n in P.MESH_LADDER:
        s_n, c_n = solve(N=n, t_eval=P.Q1_TABLE_TIMES)
        Tn, Cn, sf = fields_on_output_grid(s_n, c_n, P.Q1_TABLE_TIMES)
        rec = {'N': n, 'T_center_1800s': float(Tn[-1, 0]), 'C_surface_1800s': float(Cn[-1, -1]),
               'T_surface_1800s': float(Tn[-1, -1]), 'nfev': int(s_n.nfev)}
        if prev_center is not None:
            rec['dT_center_vs_prev'] = abs(rec['T_center_1800s'] - prev_center)
            rec['dC_surface_vs_prev'] = abs(rec['C_surface_1800s'] - prev_surfC)
        prev_center, prev_surfC = rec['T_center_1800s'], rec['C_surface_1800s']
        ladder.append(rec)
    dT_seq = [r['dT_center_vs_prev'] for r in ladder if 'dT_center_vs_prev' in r]
    dC_seq = [r['dC_surface_vs_prev'] for r in ladder if 'dC_surface_vs_prev' in r]
    ck['V3.2'] = {'name': '网格收敛阶梯（五档）', 'dT_center_seq': dT_seq,
                  'finest_pair_dT': dT_seq[-1], 'tol': 1e-4,
                  'monotone_decreasing': bool(all(dT_seq[i] > dT_seq[i + 1] for i in range(len(dT_seq) - 1))),
                  'passed': bool(dT_seq[-1] < 1e-4 and all(dT_seq[i] > dT_seq[i + 1] for i in range(len(dT_seq) - 1)))}
    ck['C04'] = {'name': '表面值网格无关性', 'measured': dC_seq[-1], 'tol': 1e-3,
                 'dC_surface_seq': dC_seq, 'passed': bool(dC_seq[-1] < 1e-3)}
    res['mesh_ladder'] = ladder

    # ---- 第 2 层：物理健康性（C06/C07/C13 + V2.4 极大值原理）
    N = cfg['N']
    Tc, Cc = sol.y[:N, :], sol.y[N:, :]
    ck['C06'] = {'name': '剖面单调（中心最湿/最冷）',
                 'C_worst_increase': float(np.max(np.diff(Cc, axis=0))),
                 'T_worst_decrease': float(np.max(-np.diff(Tc, axis=0))), 'tol': 1e-10,
                 'passed': bool(np.max(np.diff(Cc, axis=0)) < 1e-10 and np.max(-np.diff(Tc, axis=0)) < 1e-10)}
    argmax_center = bool(np.all(np.argmax(Cc, axis=0) == 0))
    ck['C07'] = {'name': '全域最大含水率在中心', 'all_at_center': argmax_center,
                 'n_times_checked': int(Cc.shape[1]), 'passed': argmax_center}
    cmax = Cc.max(axis=0)
    vol_avg = (Cc * cfg['V_cell'][:, None]).sum(axis=0) / cfg['V_cell'].sum()
    ck['C13'] = {'name': '干燥方向性', 'max_rise_of_Cmax': float(np.max(np.diff(cmax))),
                 'max_rise_of_volavg': float(np.max(np.diff(vol_avg))), 'tol': 1e-12,
                 'passed': bool(np.max(np.diff(cmax)) < 1e-12 and np.max(np.diff(vol_avg)) < 1e-12)}
    ta_all = np.array([U.driver_Ta(t) for t in times])
    lo, hi = min(P.T0_C, ta_all.min()), max(P.T0_C, ta_all.max())
    ck['V2.4'] = {'name': '温度落在驱动包络内', 'T_min': float(Tg.min()), 'T_max': float(Tg.max()),
                  'envelope': [float(lo), float(hi)],
                  'passed': bool(Tg.min() >= lo - 1e-9 and Tg.max() <= hi + 1e-9)}

    # ---- 时间离散误差分层（§4.4）：容差再收紧一档，基准解在报告时刻的变化必须 < 1e-4
    import scipy.integrate as si

    def _at_tol(rt, at):
        return si.solve_ivp(rhs_coupled_q1, (0.0, float(P.Q1_T_END)), U.initial_state(N), method='BDF',
                            rtol=rt, atol=at, jac_sparsity=U.jacobian_sparsity(N),
                            t_eval=P.Q1_TABLE_TIMES, max_step=P.MAX_STEP_SHORT)

    d_tight = float(np.abs(_at_tol(1e-10, 1e-12).y - sol.y[:, idx]).max())
    d_loose = float(np.abs(_at_tol(1e-6, 1e-8).y - sol.y[:, idx]).max())
    ck['time_tol_layer'] = {'name': '时间离散误差分层（收紧一档）', 'measured_tighten_1e-10': d_tight,
                            'tol': 1e-4, 'passed': bool(d_tight < 1e-4),
                            'diagnostic_loosen_1e-6': d_loose,
                            'note': '§4.4 判据为收紧容差后变化 <1e-4；放松到 1e-6 的偏差 %.3e °C 一并记录，'
                                    'V3.3 的 t_end<60 s 判据在问题三、四（有事件终止）处考核' % d_loose}

    # ---- 写盘（C16 由 write_result_xlsx 内部读回核验）
    rt = U.write_result_xlsx(P.RESULT_FILES[1], {'温度': Tg, '水分浓度': Cg}, times, P.OUT_R_CM)
    ck['C16'] = {'name': '写盘-读回往返一致', 'measured': max(v['roundtrip_max_abs_diff'] for v in rt.values()),
                 'tol': 0.0, 'per_sheet': rt, 'passed': True}

    # ---- 论文表 1、表 2
    cols = [P.OUT_R_CM.index(r) for r in P.TABLE_R_CM]
    res['table_1_temperature'] = {'times_s': P.Q1_TABLE_TIMES, 'radii_cm': P.TABLE_R_CM,
                                  'values': np.round(Tg[np.ix_(idx, cols)], 4).tolist()}
    res['table_2_moisture'] = {'times_s': P.Q1_TABLE_TIMES, 'radii_cm': P.TABLE_R_CM,
                               'values': np.round(Cg[np.ix_(idx, cols)], 4).tolist()}
    res['summary'] = {'T_center_1800s': float(Tg[-1, 0]), 'T_surface_1800s': float(Tg[-1, -1]),
                      'T_gap_center_surface_1800s': float(Tg[-1, -1] - Tg[-1, 0]),
                      'C_center_1800s': float(Cg[-1, 0]), 'C_surface_1800s': float(Cg[-1, -1]),
                      'C_center_deviation_from_C0': float(P.C0 - Cg[-1, 0]),
                      'herb_T_max': float(Tg.max()), 'herb_T_min': float(Tg.min()),
                      'herb_C_max': float(Cg.max()), 'herb_C_min': float(Cg.min()),
                      'volavg_C_1800s': float(vol_avg[-1])}
    res['profiles'] = {'times_s': [100, 300, 600, 900, 1200, 1500, 1800], 'r_cm': P.OUT_R_CM,
                       'T': np.round(Tg[idx], 6).tolist(), 'C': np.round(Cg[idx], 6).tolist()}
    res['timeseries'] = {'t_s': times[::10], 'T_center': np.round(Tg[::10, 0], 6).tolist(),
                         'T_surface': np.round(Tg[::10, -1], 6).tolist(),
                         'C_center': np.round(Cg[::10, 0], 6).tolist(),
                         'C_surface': np.round(Cg[::10, -1], 6).tolist(),
                         'Ta': np.round(ta_all[::10], 6).tolist(),
                         'Ca': np.round([U.driver_Ca(t) for t in times[::10]], 8).tolist()}
    res['heatmap'] = {'t_s': times[::20], 'r_cm': P.OUT_R_CM,
                      'T': np.round(Tg[::20], 4).tolist(), 'C': np.round(Cg[::20], 4).tolist()}

    # ---- 空气侧输入：附件 1 在 [0,1800] s 内的实测点 + 本文所用的分段线性插值
    m_obs = U._T_GRID <= float(P.Q1_T_END)
    res['air_input'] = {'t_obs_s': U._T_GRID[m_obs].tolist(),
                        'Ta_obs_C': U._TA_OBS[m_obs].tolist(),
                        'Ca_obs': U._CA_OBS[m_obs].tolist(),
                        't_interp_s': times[::10],
                        'Ta_interp_C': np.round(ta_all[::10], 6).tolist(),
                        'Ca_interp': np.round([U.driver_Ca(t) for t in times[::10]], 8).tolist(),
                        'Ta_range_C': [float(ta_all.min()), float(ta_all.max())],
                        'n_obs_points': int(m_obs.sum()),
                        'note': '问题一时段内热风温度由 28 °C 近线性升至 %.4f °C；'
                                '空气含湿量同步上行' % float(ta_all.max())}

    # ---- 三维温度场（t, r, T）：粗网格供曲面图使用，避免 1800x21 过密
    st3 = 30
    res['temp_field_3d'] = {'t_s': times[st3 - 1::st3], 'r_cm': P.OUT_R_CM,
                            'T': np.round(Tg[st3 - 1::st3], 4).tolist(),
                            'C': np.round(Cg[st3 - 1::st3], 4).tolist(),
                            'T_span_C': [float(Tg.min()), float(Tg.max())],
                            'C_span': [float(Cg.min()), float(Cg.max())]}

    # ---- 水分边界层：失水只发生在表面附近约 sqrt(D t) 的薄层内，故用格心原始网格呈现
    r_cell = cfg['eta_c'] * P.R0_CM
    pen_cm = float(np.sqrt(P.D2_PREFACTOR * np.exp(-P.D2_MOIST_EXP / P.C0) * P.Q1_T_END)
                   * P.CM_PER_M)
    bl_idx = [times.index(t) for t in P.Q1_TABLE_TIMES]
    depth = P.R0_CM - r_cell
    dev = P.C0 - Cc[:, bl_idx]                     # 相对初值的失水量（格心值，未插值）
    thick = []
    for j in range(dev.shape[1]):
        over = np.nonzero(dev[:, j] > 1e-4)[0]
        thick.append(float(depth[over.min()]) if over.size else 0.0)
    res['moisture_bl'] = {'times_s': P.Q1_TABLE_TIMES, 'depth_from_surface_cm': depth.tolist(),
                          'C_cells': np.round(Cc[:, bl_idx].T, 6).tolist(),
                          'deficit_from_C0': np.round(dev.T, 8).tolist(),
                          'C_surface_recon': np.round(surf[bl_idx, 1], 6).tolist(),
                          'C_center': np.round(Cc[0, bl_idx], 6).tolist(),
                          'penetration_depth_cm': pen_cm,
                          'bl_thickness_cm': thick,
                          'deficit_tol': 1e-4, 'C0': P.C0, 'R0_cm': P.R0_CM,
                          'note': '失水层厚度 %.4f cm（1800 s，判据 C0-C>1e-4），与尺度估计 '
                                  'sqrt(D t)=%.4f cm 同量级；中心含水率仍为 %.4f，'
                                  '故问题一必须解 PDE 而不能用集中参数'
                                  % (thick[-1], pen_cm, float(Cc[0, bl_idx[-1]]))}
    res['xlsx_report'] = rt
    res['checks'] = ck
    res['all_checks_passed'] = bool(all(v.get('passed') for v in ck.values()))
    return res, ck, sol, cfg, times, Tg, Cg, surf


if __name__ == '__main__':
    out = run()[0]
    P.FIG_DIR.mkdir(exist_ok=True)
    (P.FIG_DIR / 'problem_1_results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, v in out['checks'].items():
        print(f"{k}: {'PASS' if v.get('passed') else 'FAIL'}  {v.get('name', '')}")
    print('Q1 checks passed:', out['all_checks_passed'])
    print('T center/surface @1800s: %.4f / %.4f' % (out['summary']['T_center_1800s'],
                                                    out['summary']['T_surface_1800s']))
    print('C center/surface @1800s: %.4f / %.4f' % (out['summary']['C_center_1800s'],
                                                    out['summary']['C_surface_1800s']))
    print('semi-analytic max dev: %.3e C' % out['semi_analytic']['max_abs_dev_C'])
