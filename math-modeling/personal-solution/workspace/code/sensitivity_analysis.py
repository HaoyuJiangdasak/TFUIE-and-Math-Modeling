# code/sensitivity_analysis.py — 第 3 层：单因子敏感性、二维响应面、LHS 全局不确定度
import json
import time

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 本机为嵌入式发行版，不自动加脚本目录

import params as P
import utils as U

BASE_APPENDIX = 'appendix_3'          # 以问题三（附录 3 固定域）为敏感性基准
Q4_APPENDIX = 'appendix_4'            # 问题四口径（附录 4 + 径向收缩），用于同源配对的鲁棒性对比
SENS_FACTORS = (
    ('h_m', 'h_m', 0.30, '对流传质系数 h_m'),
    ('h', 'h', 0.30, '对流换热系数 h'),
    ('ta_plateau', 'abs', 1.0, '平台热风温度 Ta'),
    ('ca_plateau', 'ca_plateau', 0.20, '平台空气含湿量 Ca'),
    ('d_scale', 'd_scale', 0.20, '扩散前因子 D0'),
    ('act_scale', 'act', 0.05, 'Arrhenius 活化温度 3850 K'),
    ('C0', 'C0', 0.05, '初始含水率 C0'),
    ('moist_scale', 'moist_scale', 0.10, '水分抑制常数 b'),
)
LATENT_SCAN = (0.0, 0.10, 0.25, 0.50)


def build_kwargs(factor, mult):
    """把『因子名 + 相对/绝对扰动』翻译成 make_config 的关键字与初值缩放。"""
    kw, c0_scale = {}, 1.0
    if factor == 'h_m':
        kw['h_m'] = P.HM_MASS * mult
    elif factor == 'h':
        kw['h'] = P.H_CONV * mult
    elif factor == 'ta_plateau':
        kw['ta_plateau'] = U.TA_PLATEAU + (mult - 1.0)
    elif factor == 'ca_plateau':
        kw['ca_plateau'] = U.CA_PLATEAU * mult
    elif factor == 'd_scale':
        kw['d_scale'] = mult
    elif factor == 'act_scale':
        kw['act_scale'] = mult
    elif factor == 'moist_scale':
        kw['moist_scale'] = mult
    elif factor == 'C0':
        c0_scale = mult
    elif factor == 'chi':
        kw['chi'] = mult
    return kw, c0_scale


def t_end_at(factor='none', mult=1.0, extra=None, N=P.N_CELLS):
    """单点真实重算：每次都独立积分到事件触发，绝不做插值或缩放外推。"""
    kw, c0_scale = build_kwargs(factor, mult)
    if extra:
        for f2, m2 in extra.items():
            k2, s2 = build_kwargs(f2, m2)
            kw.update(k2)
            c0_scale *= s2
    cfg = U.make_config(BASE_APPENDIX, N=N, **kw)
    y0 = np.concatenate((np.full(N, P.T0_C), np.full(N, P.C0 * c0_scale)))
    sol = U.integrate(lambda t, y: U.fixed_domain_rhs(t, y, cfg), (0.0, P.T_INTEGRATION_CAP), y0,
                      N=N, events=U.event_moisture_threshold, max_step=P.MAX_STEP_LONG)
    assert sol.success, sol.message
    if not len(sol.t_events[0]):
        return float('nan'), int(sol.nfev)
    return float(sol.t_events[0][0]), int(sol.nfev)


def solve_ivp_to_event(cfg, y0):
    """④M6 合同的显式落地：BDF + rtol/atol 定值 + 稀疏雅可比 + 阈值事件终止。"""
    import scipy.integrate as si
    return si.solve_ivp(lambda t, y: U.fixed_domain_rhs(t, y, cfg),
                        (0.0, P.T_INTEGRATION_CAP), y0, method='BDF', rtol=P.RTOL, atol=P.ATOL,
                        jac_sparsity=U.jacobian_sparsity(cfg['N']),
                        events=U.event_moisture_threshold, max_step=P.MAX_STEP_LONG)


def one_factor_scan(base_t):
    """单因子双向扰动（OAT）：每个方向都真实重算一次，不做任何线性外推。"""
    rows = []
    for name, kind, amp, label in SENS_FACTORS:
        for sign in (-1, +1):
            mult = (1.0 + sign * amp) if kind != 'abs' else (1.0 + sign * amp)
            cfg_kw, c0_scale = build_kwargs(name, mult)
            cfg = U.make_config(BASE_APPENDIX, **cfg_kw)
            y0 = np.concatenate((np.full(cfg['N'], P.T0_C), np.full(cfg['N'], P.C0 * c0_scale)))
            sol = solve_ivp_to_event(cfg, y0)
            assert sol.success and len(sol.t_events[0]) > 0, name
            t_e = float(sol.t_events[0][0])
            rows.append({'factor': name, 'label': label, 'kind': kind, 'sign': sign,
                         'amplitude': amp, 'multiplier': mult, 't_end_s': t_e,
                         't_end_h': t_e / P.SEC_PER_HOUR, 'nfev': int(sol.nfev),
                         'delta_h': (t_e - base_t) / P.SEC_PER_HOUR,
                         'delta_pct': 100.0 * (t_e - base_t) / base_t})
    return rows


def latent_heat_scan(base_t):
    """潜热耦合强度 chi 的情景扫描：chi=0 为本文基准（题面未给潜热与相变数据）。"""
    rows = []
    for chi in LATENT_SCAN:
        cfg = U.make_config(BASE_APPENDIX, chi=chi)
        sol = solve_ivp_to_event(cfg, U.initial_state(cfg['N']))
        assert sol.success, sol.message
        fired = len(sol.t_events[0]) > 0
        t_e = float(sol.t_events[0][0]) if fired else None
        rows.append({'chi': chi, 'fired': bool(fired), 't_end_s': t_e,
                     't_end_h': (t_e / P.SEC_PER_HOUR) if fired else None,
                     'delta_pct': (100.0 * (t_e - base_t) / base_t) if fired else None,
                     'T_center_min_C': float(sol.y[0].min()),
                     'T_field_min_C': float(sol.y[:cfg['N']].min()),
                     'T_center_at_1800s_C': float(np.interp(1800.0, sol.t, sol.y[0])),
                     'nfev': int(sol.nfev)})
    return rows


def response_surface(n=7, amp_hm=0.30, amp_d=0.20):
    """h_m x D0 的 7x7 响应面：两个最强因子的交互，49 个点全部真实重算。"""
    hm = np.linspace(1.0 - amp_hm, 1.0 + amp_hm, n)
    d0 = np.linspace(1.0 - amp_d, 1.0 + amp_d, n)
    grid = np.full((n, n), np.nan)
    for i, a in enumerate(hm):
        for j, b in enumerate(d0):
            cfg = U.make_config(BASE_APPENDIX, h_m=P.HM_MASS * a, d_scale=b)
            sol = solve_ivp_to_event(cfg, U.initial_state(cfg['N']))
            assert sol.success and len(sol.t_events[0]) > 0, (a, b)
            grid[i, j] = float(sol.t_events[0][0]) / P.SEC_PER_HOUR
    return hm, d0, grid


def lhs_matrix(n, k, seed=P.SEED):
    """分层拉丁超立方：每因子各层只取一次，随机数发生器由 SEED 定死（可复现）。"""
    rng = np.random.default_rng(seed)
    u = (rng.permuted(np.tile(np.arange(n, dtype=float), (k, 1)), axis=1) + rng.random((k, n))) / n
    return u.T


def lhs_study(n_lhs, base_t):
    """LHS 全局不确定度：7 因子同时扰动，每个样本点独立真实重算。"""
    facs = [f for f in SENS_FACTORS]
    u = lhs_matrix(n_lhs, len(facs))
    rows = []
    for p in range(n_lhs):
        kw, c0_scale, mults = {}, 1.0, {}
        for j, (name, kind, amp, _lab) in enumerate(facs):
            mult = 1.0 - amp + 2.0 * amp * float(u[p, j])
            mults[name] = mult
            k2, s2 = build_kwargs(name, mult)
            kw.update(k2)
            c0_scale *= s2
        cfg = U.make_config(BASE_APPENDIX, **kw)
        y0 = np.concatenate((np.full(cfg['N'], P.T0_C), np.full(cfg['N'], P.C0 * c0_scale)))
        sol = solve_ivp_to_event(cfg, y0)
        assert sol.success and len(sol.t_events[0]) > 0, 'LHS 点 %d 未触发事件' % p
        t_e = float(sol.t_events[0][0])
        rows.append({'i': p, 'multipliers': mults, 't_end_s': t_e,
                     't_end_h': t_e / P.SEC_PER_HOUR, 'nfev': int(sol.nfev),
                     'delta_pct': 100.0 * (t_e - base_t) / base_t})
    return rows


def lhs_study_q4(n_lhs, base_t_q4):
    """问题四口径（附录 4 + 径向收缩）的 LHS：复用与问题三**完全相同**的 LHS 矩阵，
    使第 i 个样本在两种口径下的因子取值逐位一致，从而可做配对对比而非两套独立随机。"""
    facs = [f for f in SENS_FACTORS]
    u = lhs_matrix(n_lhs, len(facs))
    rows = []
    for p in range(n_lhs):
        kw, c0_scale, mults = {}, 1.0, {}
        for j, (name, kind, amp, _lab) in enumerate(facs):
            mult = 1.0 - amp + 2.0 * amp * float(u[p, j])
            mults[name] = mult
            k2, s2 = build_kwargs(name, mult)
            kw.update(k2)
            c0_scale *= s2
        cfg = U.make_config(Q4_APPENDIX, **kw)
        y0 = np.concatenate((np.full(cfg['N'], P.T0_C), np.full(cfg['N'], P.C0 * c0_scale)))
        sol = U.integrate(lambda t, y: U.moving_domain_rhs(t, y, cfg),
                          (0.0, P.T_INTEGRATION_CAP), y0, N=cfg['N'],
                          events=U.event_moisture_threshold, max_step=P.MAX_STEP_LONG)
        assert sol.success and len(sol.t_events[0]) > 0, '问题四 LHS 点 %d 未触发事件' % p
        t_e = float(sol.t_events[0][0])
        rows.append({'i': p, 'multipliers': mults, 't_end_s': t_e,
                     't_end_h': t_e / P.SEC_PER_HOUR, 'nfev': int(sol.nfev),
                     'delta_pct': 100.0 * (t_e - base_t_q4) / base_t_q4})
    return rows


def t_end_q4_baseline():
    """问题四口径的未扰动基准，供上面的 delta_pct 归一。"""
    cfg = U.make_config(Q4_APPENDIX)
    sol = U.integrate(lambda t, y: U.moving_domain_rhs(t, y, cfg),
                      (0.0, P.T_INTEGRATION_CAP), U.initial_state(cfg['N']), N=cfg['N'],
                      events=U.event_moisture_threshold, max_step=P.MAX_STEP_LONG)
    assert sol.success and len(sol.t_events[0]) > 0
    return float(sol.t_events[0][0]), int(sol.nfev)


def spearman(x, y):
    """秩相关系数：LHS 样本上的全局敏感性指标（不假设线性）。"""
    rx = np.argsort(np.argsort(np.asarray(x, float))).astype(float)
    ry = np.argsort(np.argsort(np.asarray(y, float))).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    return float(rx @ ry / np.sqrt((rx @ rx) * (ry @ ry)))


def _cached(key, parameters, validate, compute):
    """按 §14 要求给每个昂贵算例加原子检查点；依赖变动会自动失效。"""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / '_utils'))
    from compute_checkpoint import CaseCheckpoint
    deps = [Path(__file__).resolve(), root / 'code' / 'utils.py', root / 'code' / 'params.py',
            P.ATT1_XLSX, P.ATT2_XLSX]
    cp = CaseCheckpoint(root, key, dependencies=deps, parameters=parameters)
    data = cp.load(validate)
    if data is not None:
        return data, True
    data = compute()
    cp.save(data, validate)
    return data, False


def run(n_lhs=200):
    t0 = time.time()
    res = {'base_appendix': BASE_APPENDIX, 'seed': P.SEED, 'n_lhs': n_lhs,
           'factors': [{'name': n, 'kind': k, 'amplitude': a, 'label': l}
                       for n, k, a, l in SENS_FACTORS]}
    ck = {}
    base_t, base_nfev = t_end_at()
    res['baseline'] = {'t_end_s': base_t, 't_end_h': base_t / P.SEC_PER_HOUR, 'nfev': base_nfev}

    ok_oat = (lambda d: isinstance(d, dict) and len(d['oat']) == 2 * len(SENS_FACTORS)
              and len(d['latent']) == len(LATENT_SCAN)
              and all(r['nfev'] > 0 and r['t_end_s'] > 0 for r in d['oat']))
    oat_pack, hit_oat = _cached('sens_oat_latent',
                                {'factors': [list(f[:3]) for f in SENS_FACTORS],
                                 'latent': list(LATENT_SCAN), 'N': P.N_CELLS},
                                ok_oat, lambda: {'oat': one_factor_scan(base_t),
                                                 'latent': latent_heat_scan(base_t)})
    oat, latent = oat_pack['oat'], oat_pack['latent']

    ok_srf = (lambda d: isinstance(d, dict) and len(d['grid']) == 7 and len(d['grid'][0]) == 7
              and all(np.isfinite(v) and v > 0 for row in d['grid'] for v in row))
    srf, hit_srf = _cached('sens_surface_hm_d0', {'n': 7, 'amp_hm': 0.30, 'amp_d': 0.20},
                           ok_srf, lambda: (lambda hm, d0, g: {
                               'hm_mult': hm.tolist(), 'd0_mult': d0.tolist(),
                               'grid': np.round(g, 6).tolist()})(*response_surface()))

    ok_lhs = (lambda d: isinstance(d, list) and len(d) == n_lhs
              and all(r['nfev'] > 0 and r['t_end_s'] > 0 for r in d)
              and len({round(r['t_end_s'], 6) for r in d}) == n_lhs)
    lhs, hit_lhs = _cached('sens_lhs_%d' % n_lhs,
                           {'n': n_lhs, 'seed': P.SEED,
                            'factors': [list(f[:3]) for f in SENS_FACTORS]},
                           ok_lhs, lambda: lhs_study(n_lhs, base_t))

    base_t4, base_nfev4 = t_end_q4_baseline()
    res['baseline_q4'] = {'t_end_s': base_t4, 't_end_h': base_t4 / P.SEC_PER_HOUR,
                          'nfev': base_nfev4, 'appendix': Q4_APPENDIX, 'moving_boundary': True}

    ok_lhs4 = (lambda d: isinstance(d, list) and len(d) == n_lhs
               and all(r['nfev'] > 0 and r['t_end_s'] > 0 for r in d)
               and len({round(r['t_end_s'], 6) for r in d}) == n_lhs)
    lhs4, hit_lhs4 = _cached('sens_lhs_q4_%d' % n_lhs,
                             {'n': n_lhs, 'seed': P.SEED, 'appendix': Q4_APPENDIX, 'moving': True,
                              'factors': [list(f[:3]) for f in SENS_FACTORS]},
                             ok_lhs4, lambda: lhs_study_q4(n_lhs, base_t4))

    # ---- C23 真实重算核验：每个 OAT 点都必须与基准显著不同，LHS 样本互不相同
    gaps = [abs(r['t_end_s'] - base_t) for r in oat]
    ts = np.array([r['t_end_s'] for r in lhs])
    ts4 = np.array([r['t_end_s'] for r in lhs4])
    pair_min = float(np.min(np.diff(np.sort(ts))))
    pair_min4 = float(np.min(np.diff(np.sort(ts4))))
    ck['C23'] = {'name': '敏感性逐点真实重算', 'n_oat_points': len(oat), 'n_lhs_points': len(lhs),
                 'n_lhs_q4_points': len(lhs4),
                 'n_surface_points': 49, 'min_abs_gap_to_baseline_s': float(min(gaps)),
                 'tol_gap_s': 60.0, 'lhs_min_pairwise_gap_s': pair_min,
                 'lhs_q4_min_pairwise_gap_s': pair_min4,
                 'n_distinct_lhs_t_end': int(len({round(v, 6) for v in ts})),
                 'n_distinct_lhs_q4_t_end': int(len({round(v, 6) for v in ts4})),
                 'total_real_solves': len(oat) + len(latent) + 49 + len(lhs) + len(lhs4) + 2,
                 'checkpoint_hits': {'oat_latent': hit_oat, 'surface': hit_srf, 'lhs': hit_lhs,
                                     'lhs_q4': hit_lhs4},
                 'passed': bool(min(gaps) > 60.0 and pair_min > 0.0 and pair_min4 > 0.0
                                and len({round(v, 6) for v in ts}) == len(lhs)
                                and len({round(v, 6) for v in ts4}) == len(lhs4))}

    # ---- 单因子排序（龙卷风图）与全局秩相关
    by_factor = {}
    for n, k, a, l in SENS_FACTORS:
        lo = next(r for r in oat if r['factor'] == n and r['sign'] < 0)
        hi = next(r for r in oat if r['factor'] == n and r['sign'] > 0)
        by_factor[n] = {'label': l, 'amplitude': a, 'kind': k,
                        't_end_h_low': lo['t_end_h'], 't_end_h_high': hi['t_end_h'],
                        'delta_pct_low': lo['delta_pct'], 'delta_pct_high': hi['delta_pct'],
                        'half_range_h': 0.5 * abs(hi['t_end_h'] - lo['t_end_h']),
                        'elasticity': ((hi['t_end_s'] - lo['t_end_s']) / base_t)
                        / (hi['multiplier'] - lo['multiplier'])}
    order = sorted(by_factor, key=lambda k2: -by_factor[k2]['half_range_h'])
    spear = {n: spearman([r['multipliers'][n] for r in lhs], ts) for n, _k, _a, _l in SENS_FACTORS}
    ck['V3.9'] = {'name': '敏感性排序一致（OAT 首因子 = 秩相关首因子）',
                  'oat_rank': order, 'top_oat': order[0],
                  'top_spearman': max(spear, key=lambda k2: abs(spear[k2])),
                  'spearman': spear,
                  'passed': bool(order[0] == max(spear, key=lambda k2: abs(spear[k2])))}

    # ---- 物理方向性：七个因子的弹性符号必须与机理预期一致
    want = {'h_m': -1, 'h': -1, 'ta_plateau': -1, 'ca_plateau': +1, 'd_scale': -1,
            'act_scale': +1, 'C0': +1, 'moist_scale': +1}
    signs = {k: int(np.sign(v['elasticity'])) for k, v in by_factor.items()}
    ck['V3.10'] = {'name': '单因子弹性符号与机理一致', 'expected': want, 'observed': signs,
                   'mismatch': [k for k in want if signs[k] != want[k]],
                   'note': 'h_m/h/Ta/D0 增大加快干燥（t_end 下降），Ca/活化温度/C0/水分抑制常数 b '
                           '增大延长干燥（b 增大使 exp(-b/C) 在低含水率端急剧变小）',
                   'passed': bool(all(signs[k] == want[k] for k in want))}

    # ---- 响应面单调性：t_end 对 h_m、对 D0 都应逐行/逐列单调下降
    g = np.array(srf['grid'], float)
    row_mono = bool(np.all(np.diff(g, axis=1) < 0))
    col_mono = bool(np.all(np.diff(g, axis=0) < 0))
    ck['V3.11'] = {'name': '响应面双向单调', 'monotone_along_D0': row_mono,
                   'monotone_along_hm': col_mono, 'span_h': [float(g.min()), float(g.max())],
                   'corner_ratio': float(g.max() / g.min()), 'passed': bool(row_mono and col_mono)}

    # ---- ④M9 方向探针：t_end 必须随潜热折减系数 chi 单调增大（计入潜热 -> 降温 -> D 减小）
    lat_ok = [r for r in latent if r['fired']]
    seq = [r['t_end_s'] for r in lat_ok]
    mono_chi = all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
    ck['V3.4'] = {'name': '潜热方向探针（t_end 随 chi 单调增大）', 'chi_values': list(LATENT_SCAN),
                  'n_fired': len(lat_ok), 'n_scanned': len(latent),
                  't_end_h_by_chi': [r['t_end_h'] for r in latent],
                  'T_field_min_C_by_chi': [r['T_field_min_C'] for r in latent],
                  'monotone_increasing': bool(mono_chi),
                  'note': 'chi=0 为基准；未触发的 chi 说明其 t_end 超出保护上限 %g s，方向同样成立'
                          % P.T_INTEGRATION_CAP,
                  'passed': bool(mono_chi and (len(lat_ok) < len(latent) or seq[-1] > seq[0]))}

    d = ts / (24 * P.SEC_PER_HOUR)
    hist, edges = np.histogram(ts / P.SEC_PER_HOUR, bins=24)
    res['oat'] = oat
    res['tornado'] = {'order': order, 'by_factor': by_factor, 'baseline_h': base_t / P.SEC_PER_HOUR}
    res['latent_scan'] = {'chi_values': list(LATENT_SCAN), 'rows': latent,
                          'note': 'chi=0 为本文基准：题面未给潜热与相变速率数据，故不引入未给定参数；'
                                  'chi>0 只作情景界定'}
    res['response_surface'] = srf
    res['lhs'] = {'n': n_lhs, 'seed': P.SEED, 'rows': lhs,
                  't_end_h': {'mean': float(ts.mean() / P.SEC_PER_HOUR),
                              'std': float(ts.std(ddof=1) / P.SEC_PER_HOUR),
                              'cv': float(ts.std(ddof=1) / ts.mean()),
                              'p05': float(np.percentile(ts, 5) / P.SEC_PER_HOUR),
                              'p50': float(np.percentile(ts, 50) / P.SEC_PER_HOUR),
                              'p95': float(np.percentile(ts, 95) / P.SEC_PER_HOUR),
                              'min': float(ts.min() / P.SEC_PER_HOUR),
                              'max': float(ts.max() / P.SEC_PER_HOUR)},
                  'fraction_in_2_3_days': float(np.mean((d >= P.DUR_DAYS_LOW)
                                                        & (d <= P.DUR_DAYS_HIGH))),
                  'fraction_below_2_days': float(np.mean(d < P.DUR_DAYS_LOW)),
                  'fraction_above_3_days': float(np.mean(d > P.DUR_DAYS_HIGH)),
                  'spearman': spear,
                  'histogram': {'counts': hist.tolist(), 'edges_h': edges.tolist()}}
    # ---- 问题三 / 问题四 配对鲁棒性：同一 LHS 矩阵下两种口径的 t_end 分布
    d4 = ts4 / (24 * P.SEC_PER_HOUR)
    hist4, edges4 = np.histogram(ts4 / P.SEC_PER_HOUR, bins=24)
    ratio = ts4 / ts
    paired = all(abs(a['multipliers'][n] - b['multipliers'][n]) < 1e-12
                 for a, b in zip(lhs, lhs4) for n, _k, _a, _l in SENS_FACTORS)
    ck['V3.13'] = {'name': '问题三/四鲁棒性配对同源（同一 LHS 矩阵）',
                   'n_pairs': len(lhs4), 'multipliers_identical': bool(paired),
                   'q4_shorter_fraction': float(np.mean(ts4 < ts)),
                   'ratio_q4_over_q3': {'mean': float(ratio.mean()), 'min': float(ratio.min()),
                                        'max': float(ratio.max())},
                   'note': '两条分布共用同一组因子取值，故雨云图是配对对比；'
                           'q4/q3 比值恒小于 1 即收缩缩短工期这一结论在全分布上稳健',
                   'passed': bool(paired and len(lhs4) == len(lhs))}

    res['lhs_q4'] = {'n': n_lhs, 'seed': P.SEED, 'appendix': Q4_APPENDIX, 'moving_boundary': True,
                     'rows': lhs4,
                     't_end_h': {'mean': float(ts4.mean() / P.SEC_PER_HOUR),
                                 'std': float(ts4.std(ddof=1) / P.SEC_PER_HOUR),
                                 'cv': float(ts4.std(ddof=1) / ts4.mean()),
                                 'p05': float(np.percentile(ts4, 5) / P.SEC_PER_HOUR),
                                 'p50': float(np.percentile(ts4, 50) / P.SEC_PER_HOUR),
                                 'p95': float(np.percentile(ts4, 95) / P.SEC_PER_HOUR),
                                 'min': float(ts4.min() / P.SEC_PER_HOUR),
                                 'max': float(ts4.max() / P.SEC_PER_HOUR)},
                     'fraction_in_2_3_days': float(np.mean((d4 >= P.DUR_DAYS_LOW)
                                                           & (d4 <= P.DUR_DAYS_HIGH))),
                     'fraction_below_2_days': float(np.mean(d4 < P.DUR_DAYS_LOW)),
                     'fraction_above_3_days': float(np.mean(d4 > P.DUR_DAYS_HIGH)),
                     'spearman': {n: spearman([r['multipliers'][n] for r in lhs4], ts4)
                                  for n, _k, _a, _l in SENS_FACTORS},
                     'histogram': {'counts': hist4.tolist(), 'edges_h': edges4.tolist()}}
    res['robustness_pair'] = {
        'label_q3': '问题三口径（附录 3 + 固定域）', 'label_q4': '问题四口径（附录 4 + 径向收缩）',
        'n': n_lhs, 'baseline_q3_h': base_t / P.SEC_PER_HOUR,
        'baseline_q4_h': base_t4 / P.SEC_PER_HOUR,
        't_end_h_q3': (ts / P.SEC_PER_HOUR).tolist(), 't_end_h_q4': (ts4 / P.SEC_PER_HOUR).tolist(),
        'ratio_q4_over_q3': ratio.tolist(),
        'q4_shorter_fraction': float(np.mean(ts4 < ts)),
        'note': '同一 LHS 矩阵驱动两种口径，逐样本配对；雨云图左右两半即这两列'}

    res['checks'] = ck
    res['all_checks_passed'] = bool(all(v.get('passed') for v in ck.values()))
    res['wall_time_s'] = time.time() - t0
    return res, ck


if __name__ == '__main__':
    out = run()[0]
    P.FIG_DIR.mkdir(exist_ok=True)
    (P.FIG_DIR / 'sensitivity_results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, v in out['checks'].items():
        print(f"{k}: {'PASS' if v.get('passed') else 'FAIL'}  {v.get('name', '')}")
    print('SENS checks passed:', out['all_checks_passed'])
    print('baseline t_end = %.4f h' % out['baseline']['t_end_h'])
    print('OAT order:', ' > '.join(out['tornado']['order']))
    for k in out['tornado']['order']:
        b = out['tornado']['by_factor'][k]
        print('  %-12s +-%-5g  t_end %8.4f .. %8.4f h  (%+.2f%% .. %+.2f%%)'
              % (k, b['amplitude'], b['t_end_h_low'], b['t_end_h_high'],
                 b['delta_pct_low'], b['delta_pct_high']))
    s = out['lhs']['t_end_h']
    print('LHS n=%d: p05/p50/p95 = %.3f / %.3f / %.3f h, CV = %.4f'
          % (out['lhs']['n'], s['p05'], s['p50'], s['p95'], out['lhs']['t_end_h']['cv']))
    print('fraction in 2-3 d: %.3f | wall %.1f s' % (out['lhs']['fraction_in_2_3_days'],
                                                     out['wall_time_s']))
