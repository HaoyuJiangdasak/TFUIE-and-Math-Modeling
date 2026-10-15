# code/utils.py — 守恒型有限体积核心、物性、驱动、事件、写盘与半解析解
import json

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
from scipy.sparse import lil_matrix
from scipy.special import j0, j1

import params as P

# ④M6：时间积分容差与格式定死，编码阶段不得再选
TOLERANCE_CONTRACT = dict(method='BDF', rtol=1e-8, atol=1e-10)
assert TOLERANCE_CONTRACT['rtol'] == P.RTOL and TOLERANCE_CONTRACT['atol'] == P.ATOL


# ---------------------------------------------------------------- 网格与权重
def make_grid(N):
    """无量纲径向坐标 eta = r/R 上的等宽有限体积网格。

    返回 eta_c（格心，N 个）、eta_f（界面，N+1 个，eta_f[0]=0）、
    V_cell（体积权 (eta_{i+1/2}^2-eta_{i-1/2}^2)/2）、A_face（面积权 eta_{i+1/2}）。
    A_face[0] = 0 使中心零通量由几何自动满足，不需额外施加对称条件。
    """
    deta = 1.0 / N
    eta_f = np.arange(N + 1) * deta
    eta_c = (np.arange(N) + 0.5) * deta
    V_cell = 0.5 * (eta_f[1:] ** 2 - eta_f[:-1] ** 2)
    A_face = eta_f.copy()
    return eta_c, eta_f, V_cell, A_face, deta


def flux_divergence(vals, coef_face, surf_F, A_face, V_cell, deta):
    """守恒型通量差分 (A_{i+1/2}F_{i+1/2} - A_{i-1/2}F_{i-1/2}) / V_i。

    coef_face 为 N-1 个内部界面的界面物性，surf_F 为表面处的（已含符号的）通量密度。
    """
    inner_F = coef_face * np.diff(vals) / deta
    full = np.concatenate(([0.0], A_face[1:] * np.append(inner_F, surf_F)))
    return np.diff(full) / V_cell


def face_harmonic(x):
    """界面物性取相邻格心的调和平均（④M1）：串联导纳的正确平均方式。"""
    a, b = x[:-1], x[1:]
    return 2.0 * a * b / (a + b)


def reconstruct_surface(val_N, D_N, h_m, C_a, R_m, deta):
    """M3 表面值代数反解：内侧离散扩散通量与外侧对流通量消元。

    记号按水分侧写出 (C_N, D_N, h_m, C_a)；温度侧完全同构，
    代入 (T_N, lam_N, h, T_a) 即得 T_s。这是 r=R 那一列的唯一合法来源。
    """
    conductance = 2 * D_N / (R_m * deta)
    return (conductance * val_N + h_m * C_a) / (conductance + h_m)


# ---------------------------------------------------------------- 物性（附录 2/3/4）
def props_appendix_2(C, T_C):
    """附录 2：rho/cp/lambda 为常数，D 仅依含水率（温度场因此线性且不受水分场反馈）。"""
    Cf = np.maximum(C, P.C_FLOOR)
    rho = np.full_like(Cf, P.RHO_A2)
    cp = np.full_like(Cf, P.CP_A2)
    lam = np.full_like(Cf, P.LAM_A2)
    D = P.D2_PREFACTOR * np.exp(-P.D2_MOIST_EXP / Cf)
    return rho, cp, lam, D


def props_appendix_3(C, T_C):
    """附录 3：四式逐点求值；D 的 Arrhenius 因子必须代开尔文。"""
    Cf = np.maximum(C, P.C_FLOOR)
    sat = Cf / (Cf + 1.0)
    rho = P.RHO3_A + P.RHO3_B * Cf
    cp = P.CP3_A + P.CP3_B * sat
    lam = P.LAM3_A + P.LAM3_B * sat
    T_K = T_C + P.KELVIN_OFFSET
    D = P.D3_PREFACTOR * np.exp(-P.D3_MOIST_EXP / Cf) * np.exp(-P.ACT_TEMP_K / T_K)
    return rho, cp, lam, D


def props_appendix_4(C, T_C):
    """附录 4：结构同附录 3，前因子与水分抑制常数不同，活化温度相同。"""
    Cf = np.maximum(C, P.C_FLOOR)
    sat = Cf / (Cf + 1.0)
    rho = P.RHO4_A + P.RHO4_B * Cf
    cp = P.CP4_A + P.CP4_B * sat
    lam = P.LAM4_A + P.LAM4_B * sat
    T_K = T_C + P.KELVIN_OFFSET
    D = P.D4_PREFACTOR * np.exp(-P.D4_MOIST_EXP / Cf) * np.exp(-P.ACT_TEMP_K_A4 / T_K)
    return rho, cp, lam, D


PROPS_REGISTRY = {'appendix_2': props_appendix_2,
                  'appendix_3': props_appendix_3,
                  'appendix_4': props_appendix_4}


# ---------------------------------------------------------------- 烘房驱动（附件 1）
_A1 = pd.read_excel(P.ATT1_XLSX, sheet_name=0)
_A1.columns = ['t_s', 'Ta_C', 'Ca']
T_OBS = float(_A1['t_s'].iloc[-1])
_TA_OBS = _A1['Ta_C'].to_numpy(float)
_CA_OBS = _A1['Ca'].to_numpy(float)
_T_GRID = _A1['t_s'].to_numpy(float)
_PL = _T_GRID >= P.PLATEAU_WINDOW_START
TA_PLATEAU = float(_TA_OBS[_PL].mean())
CA_PLATEAU = float(_CA_OBS[_PL].mean())
TA_END = float(_TA_OBS[-1])
CA_END = float(_CA_OBS[-1])


def driver_Ta(t, plateau=None):
    """区内对附件 1 实测值线性插值；区外向平台均值指数松弛（tau=HOLD_RELAX_TAU）。

    松弛过渡使 t=T_OBS 处左右极限相等，避免零阶保持带来的 0.1965 °C 阶跃。
    """
    bar = TA_PLATEAU if plateau is None else plateau
    if t <= T_OBS:
        return float(np.interp(t, _T_GRID, _TA_OBS))
    decay = np.exp(-(t - T_OBS) / P.HOLD_RELAX_TAU)
    return float(bar + (TA_END - bar) * decay)


def driver_Ca(t, plateau=None):
    """水分侧同构：区内实测插值，区外平台均值指数松弛。"""
    bar = CA_PLATEAU if plateau is None else plateau
    if t <= T_OBS:
        return float(np.interp(t, _T_GRID, _CA_OBS))
    decay = np.exp(-(t - T_OBS) / P.HOLD_RELAX_TAU)
    return float(bar + (CA_END - bar) * decay)


# ---------------------------------------------------------------- 半径轨迹（附件 2）
_A2D = pd.read_excel(P.ATT2_XLSX, sheet_name=0)
_A2D.columns = ['t_s', 'R_cm']
R_T_GRID = _A2D['t_s'].to_numpy(float)
R_DATA_CM = _A2D['R_cm'].to_numpy(float)
R_MIN_CM = float(R_DATA_CM[-1])
R_T_LAST = float(R_T_GRID[-1])
_PCHIP_R = PchipInterpolator(R_T_GRID, R_DATA_CM, extrapolate=False)
_PCHIP_DR = _PCHIP_R.derivative()


def R_of_t(t):
    """保单调 PCHIP 插值的半径（m）；区外保持末点（E2），并显式钳制到实测区间。"""
    tc = min(max(float(t), 0.0), R_T_LAST)
    return float(np.clip(_PCHIP_R(tc), R_MIN_CM, P.R0_CM)) / P.CM_PER_M


def dRdt(t):
    """半径的时间导数（m/s）；区外为零（末点保持）。"""
    if t <= 0.0 or t >= R_T_LAST:
        return 0.0
    return float(_PCHIP_DR(float(t))) / P.CM_PER_M


RHO_D0 = (P.RHO4_A + P.RHO4_B * P.C0) / (1.0 + P.C0)


def rho_d_of_t(t, rho_d0=RHO_D0):
    """绝干密度记账：径向收缩下 rho_d(t) = rho_d0 * (R0/R)^2（单位长度绝干质量守恒）。"""
    R0 = P.R0_M
    return rho_d0 * (R0 / R_of_t(t)) ** 2


# ---------------------------------------------------------------- 求解器封装
def jacobian_sparsity(N):
    """块三对角结构：两场各自三对角，彼此通过逐点物性耦合（对角块）。"""
    S = lil_matrix((2 * N, 2 * N), dtype=np.int8)
    idx = np.arange(N)
    for off_r in (0, N):
        for off_c in (0, N):
            S[off_r + idx, off_c + idx] = 1
            S[off_r + idx[:-1], off_c + idx[1:]] = 1
            S[off_r + idx[1:], off_c + idx[:-1]] = 1
    return S.tocsr()


def integrate(rhs, t_span, y0, t_eval=None, N=None, events=None, max_step=np.inf, dense_output=False):
    """刚性隐式积分统一入口（④M6）：BDF + rtol=1e-8 + atol=1e-10 + 稀疏雅可比结构。"""
    n = N if N is not None else len(y0) // 2
    return solve_ivp(rhs, t_span, y0, method='BDF', rtol=1e-8, atol=1e-10,
                     jac_sparsity=jacobian_sparsity(n), t_eval=t_eval, events=events,
                     max_step=max_step, dense_output=dense_output)


def event_moisture_threshold(t, y, C_thr=P.C_THR):
    """事件函数 g(t) = max_r C(r,t) - C_thr：全域最大含水率的首次下穿。"""
    N = len(y) // 2
    return float(np.max(y[N:])) - C_thr


event_moisture_threshold.terminal = True
event_moisture_threshold.direction = -1


# ---------------------------------------------------------------- 输出插值（④M7）
def to_output_radii(vals, surf_val, eta_c, r_out_cm, R_cm):
    """格心值 -> 固定距离列：中心二阶外推 + 格心间线性插值 + 表面用 M3 重构值。"""
    center = (9.0 * vals[0] - vals[1]) / 8.0
    r_nodes = np.concatenate(([0.0], eta_c * R_cm, [R_cm]))
    v_nodes = np.concatenate(([center], vals, [surf_val]))
    out = np.interp(np.asarray(r_out_cm, float), r_nodes, v_nodes)
    return out


def fields_on_grid(sol, cfg, times, r_out_cm=None, R_cm=P.R0_CM):
    """把两场的格心解统一映射到固定距离列，并同时返回表面 (T_s, C_s) 序列。"""
    r_out_cm = P.OUT_R_CM if r_out_cm is None else r_out_cm
    N = cfg['N']
    Tg = np.empty((len(times), len(r_out_cm)))
    Cg = np.empty_like(Tg)
    surf = np.empty((len(times), 2))
    for k, t in enumerate(times):
        T, C = sol.y[:N, k], sol.y[N:, k]
        T_s, C_s = surface_pair(cfg, T, C, float(t))[:2]
        Tg[k] = to_output_radii(T, T_s, cfg['eta_c'], r_out_cm, R_cm)
        Cg[k] = to_output_radii(C, C_s, cfg['eta_c'], r_out_cm, R_cm)
        surf[k] = (T_s, C_s)
    return Tg, Cg, surf


def vol_average(vals, V_cell):
    """柱面体积权平均：sum(V_i x_i)/sum(V_i)，等价于 (2/R^2)*int_0^R x r dr。"""
    a = np.asarray(vals, float)
    w = np.asarray(V_cell, float)
    if a.ndim == 1:
        return float(a @ w / w.sum())
    return (a * w[:, None]).sum(axis=0) / w.sum()


# ---------------------------------------------------------------- 写盘与读回核验
CORNER = '时间\\到药材中心的距离'


def write_result_xlsx(path, sheets, times, columns):
    """按模板口径写 xlsx（四位小数），写完读回逐格核验（①-C16、MC18）。

    sheets: {工作表名: 二维数组}；columns: 列表头（数值或『药材表面』）。
    NaN 表示该格已超出当前药材外表面，写为空单元格（③-P09）。
    """
    rounded = {}
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        for name, arr in sheets.items():
            a = np.round(np.asarray(arr, float), P.DECIMALS)
            rounded[name] = a
            df = pd.DataFrame(a, index=pd.Index(list(times), name=CORNER), columns=list(columns))
            df.to_excel(writer, sheet_name=str(name), na_rep='')
    report = {}
    for name, a in rounded.items():
        back = pd.read_excel(path, sheet_name=str(name), index_col=0).to_numpy(float)
        nan_ok = bool(np.array_equal(np.isnan(a), np.isnan(back)))
        fin = ~np.isnan(a)
        max_gap = float(np.max(np.abs(a[fin] - back[fin]))) if fin.any() else 0.0
        assert nan_ok and max_gap == 0.0, f'{path.name}:{name} 读回不一致 max_gap={max_gap}'
        report[str(name)] = {'shape': list(a.shape), 'roundtrip_max_abs_diff': max_gap,
                            'blank_cells': int((~fin).sum())}
    return report


# ---------------------------------------------------------------- 固定域右端（问题一至三共用骨架）
# 每个附录各自的水分抑制常数 b 与活化温度：扰动必须作用在本附录的常数上，不能串用附录 3 的
MOIST_EXP_BY_APPENDIX = {'appendix_2': P.D2_MOIST_EXP, 'appendix_3': P.D3_MOIST_EXP,
                         'appendix_4': P.D4_MOIST_EXP}
ACT_TEMP_BY_APPENDIX = {'appendix_2': 0.0, 'appendix_3': P.ACT_TEMP_K,
                        'appendix_4': P.ACT_TEMP_K_A4}   # 附录 2 无 Arrhenius，故取 0 使扰动成空操作


def make_config(props_key, N=P.N_CELLS, freeze_props=False, d_temp_frozen=False,
                h=None, h_m=None, ta_plateau=None, ca_plateau=None, chi=0.0,
                d_scale=1.0, act_scale=1.0, moist_scale=1.0):
    eta_c, eta_f, V_cell, A_face, deta = make_grid(N)
    return {'N': N, 'props_key': props_key, 'eta_c': eta_c, 'eta_f': eta_f, 'V_cell': V_cell,
            'A_face': A_face, 'deta': deta, 'R_m': P.R0_M,
            'h': P.H_CONV if h is None else h, 'h_m': P.HM_MASS if h_m is None else h_m,
            'freeze_props': freeze_props, 'd_temp_frozen': d_temp_frozen,
            'ta_plateau': ta_plateau, 'ca_plateau': ca_plateau, 'chi': chi,
            'd_scale': d_scale, 'act_scale': act_scale, 'moist_scale': moist_scale}


def eval_props(cfg, C, T_C):
    fn = PROPS_REGISTRY[cfg['props_key']]
    if cfg['freeze_props']:
        rho, cp, lam, D = fn(np.full_like(C, P.C0), np.full_like(C, P.T0_C))
    elif cfg['d_temp_frozen']:
        rho, cp, lam, _ = fn(C, T_C)
        _, _, _, D = fn(C, np.full_like(C, P.T0_C))
    else:
        rho, cp, lam, D = fn(C, T_C)
    if cfg['d_scale'] != 1.0 or cfg['act_scale'] != 1.0 or cfg['moist_scale'] != 1.0:
        # 三个扰动都以「相对基准的比值」施加，等价于把 act/b 换成 act*s、b*s，不必先除再乘
        Cf = np.maximum(C, P.C_FLOOR)
        act = ACT_TEMP_BY_APPENDIX[cfg['props_key']]
        b = MOIST_EXP_BY_APPENDIX[cfg['props_key']]
        D = (D * cfg['d_scale']
             * np.exp(-act * (cfg['act_scale'] - 1.0) / (T_C + P.KELVIN_OFFSET))
             * np.exp(-b * (cfg['moist_scale'] - 1.0) / Cf))
    return rho, cp, lam, D


def fixed_domain_rhs(t, y, cfg):
    """固定半径下的耦合右端：两个独立分布场，守恒型通量差分 + Robin 表面重构。"""
    N = cfg['N']
    T, C = y[:N], y[N:]
    rho, cp, lam, D = eval_props(cfg, C, T)
    Ta = driver_Ta(t, cfg['ta_plateau'])
    Ca = driver_Ca(t, cfg['ca_plateau'])
    R_m, deta = cfg['R_m'], cfg['deta']
    T_s = reconstruct_surface(T[-1], lam[-1], cfg['h'], Ta, R_m, deta)
    C_s = reconstruct_surface(C[-1], D[-1], cfg['h_m'], Ca, R_m, deta)
    surf_G = -R_m * cfg['h'] * (T_s - Ta)
    surf_F = -R_m * cfg['h_m'] * (C_s - Ca)
    dC = flux_divergence(C, face_harmonic(D), surf_F, cfg['A_face'], cfg['V_cell'], deta) / R_m ** 2
    dT = flux_divergence(T, face_harmonic(lam), surf_G, cfg['A_face'], cfg['V_cell'], deta) / (rho * cp * R_m ** 2)
    if cfg['chi']:
        dT = dT + latent_sink(cfg['chi'], rho, cp, C, dC)
    return np.concatenate((dT, dC))


def latent_sink(chi, rho, cp, C, dC):
    """④M9 蒸发潜热汇：+chi*rho_d*h_fg*(dC/dt)/(rho*cp)，dC<0 故该项为负（降温）。

    报告 §7.3/§13-④M9 把汇项写作 -chi*rho_d*h_fg*dC/dt，那里的 dC/dt 指失水速率的
    正量值；按状态量 C 的时间导数（干燥时为负）书写时符号为正号，才与报告三处明写的
    方向一致：计入潜热 -> 药材降温 -> Arrhenius 因子使 D 减小 -> t_end 随 chi 单调增大。
    """
    rho_dry = rho / (1.0 + np.maximum(C, P.C_FLOOR))
    return chi * rho_dry * P.H_FG_SCAN * dC / (rho * cp)


def surface_pair(cfg, T, C, t, R_m=None):
    """给定时刻的表面温度与表面含水率（M3 重构值）；R_m 缺省用固定半径。"""
    rho, cp, lam, D = eval_props(cfg, C, T)
    Ta, Ca = driver_Ta(t, cfg['ta_plateau']), driver_Ca(t, cfg['ca_plateau'])
    Rm = cfg['R_m'] if R_m is None else float(R_m)
    T_s = reconstruct_surface(T[-1], lam[-1], cfg['h'], Ta, Rm, cfg['deta'])
    C_s = reconstruct_surface(C[-1], D[-1], cfg['h_m'], Ca, Rm, cfg['deta'])
    return T_s, C_s, Ta, Ca, lam[-1], D[-1]


def initial_state(N):
    return np.concatenate((np.full(N, P.T0_C), np.full(N, P.C0)))


# ---------------------------------------------------------------- 材料坐标（收缩域）右端
def nonconservative_div(vals, coef_c, ghost_outer, eta_c, deta):
    """C20 反向对照：教科书式非守恒展开 coef*(d2/deta2 + (1/eta) d/deta)。

    界面物性与面积权都被丢掉，离散通量不再逐面抵消，故 sum(V_i x_i) 不再守恒。
    """
    ext = np.concatenate(([vals[0]], vals, [ghost_outer]))
    d2 = (ext[:-2] - 2.0 * vals + ext[2:]) / deta ** 2
    d1 = (ext[2:] - ext[:-2]) / (2.0 * deta)
    return coef_c * (d2 + d1 / eta_c)


def moving_domain_rhs(t, y, cfg, variant=None):
    """径向收缩下的材料坐标右端（④M11）：固定 eta = r/R(t) 即骨架物质点。

    骨架速度 u = (Rdot/R) r 与绝干骨架质量守恒 d(rho_d)/dt + rho_d*div(u) = 0 联立后，
    对流项与体积膨胀项精确抵消，收缩只通过 1/R(t)**2 进入方程；绝干密度记账
    rho_d(t) = rho_d0 (R0/R)**2 只出现在总水量换算里（见问题四 C20）。
    variant 用于 C20 的反向对照：'spurious_advection' 按 §7.5 再加一遍
    R*Rdot*eta^2*C 通量与 -2*R*Rdot*C 源；'nonconservative' 用非守恒展开替换通量差分。
    """
    N = cfg['N']
    T, C = y[:N], y[N:]
    rho, cp, lam, D = eval_props(cfg, C, T)
    R_m = R_of_t(t)
    deta, A_face, V_cell = cfg['deta'], cfg['A_face'], cfg['V_cell']
    Ta = driver_Ta(t, cfg['ta_plateau'])
    Ca = driver_Ca(t, cfg['ca_plateau'])
    T_s = reconstruct_surface(T[-1], lam[-1], cfg['h'], Ta, R_m, deta)
    C_s = reconstruct_surface(C[-1], D[-1], cfg['h_m'], Ca, R_m, deta)
    surf_G = -R_m * cfg['h'] * (T_s - Ta)
    surf_F = -R_m * cfg['h_m'] * (C_s - Ca)
    if variant == 'nonconservative':
        dT = nonconservative_div(T, lam, 2.0 * T_s - T[-1], cfg['eta_c'], deta) / (rho * cp * R_m ** 2)
        dC = nonconservative_div(C, D, 2.0 * C_s - C[-1], cfg['eta_c'], deta) / R_m ** 2
    else:
        dT = flux_divergence(T, face_harmonic(lam), surf_G, A_face, V_cell, deta) / (rho * cp * R_m ** 2)
        dC = flux_divergence(C, face_harmonic(D), surf_F, A_face, V_cell, deta) / R_m ** 2
    if variant == 'spurious_advection':
        Rd = dRdt(t)
        C_f = 0.5 * (C[:-1] + C[1:])
        adv = R_m * Rd * np.concatenate(([0.0], cfg['eta_f'][1:-1] ** 2 * C_f, [C[-1]]))
        dC = dC + (np.diff(adv) / V_cell - 2.0 * R_m * Rd * C) / R_m ** 2
    if cfg['chi']:
        dT = dT + latent_sink(cfg['chi'], rho, cp, C, dC)
    return np.concatenate((dT, dC))


# ---------------------------------------------------------------- 贝塞尔-杜阿梅尔半解析解
def bessel_eigenvalues(Bi, n_modes=P.N_MODES):
    """解特征方程 beta*J1(beta) = Bi*J0(beta) 的前 n_modes 个正根。"""
    f = lambda b: b * j1(b) - Bi * j0(b)
    grid = np.arange(1e-6, 3.3 * n_modes + 10.0, 1e-3)
    fv = f(grid)
    sign_change = np.nonzero(np.sign(fv[:-1]) * np.sign(fv[1:]) < 0)[0]
    roots = [brentq(f, grid[k], grid[k + 1], xtol=1e-14, rtol=8.9e-16) for k in sign_change[:n_modes]]
    return np.array(roots)


def semi_analytic_temperature(t_list, r_cm_list, alpha, Bi, T0, ta_times, ta_vals, n_modes=P.N_MODES):
    """问题一温度场的贝塞尔-杜阿梅尔半解析解。

    附录 2 下 rho/cp/lambda 为常数且 D 不含 T，温度场是带时变第三类边界的线性问题，
    故有严格级数解。对分段线性的 T_a(t) 逐段做解析卷积（不做数值积分）。
    单位阶跃响应 S(eta,t) = 1 - sum_n A_n J0(beta_n eta) exp(-t/tau_n)。
    """
    t_arr = np.asarray(t_list, float)
    assert t_arr.max() <= ta_times[-1] + 1e-9, '半解析对照只在附件 1 覆盖区内有效'
    beta = bessel_eigenvalues(Bi, n_modes)
    A_n = 2.0 * j1(beta) / (beta * (j0(beta) ** 2 + j1(beta) ** 2))
    tau = P.R0_M ** 2 / (alpha * beta ** 2)
    eta = np.asarray(r_cm_list, float) / P.R0_CM
    basis = j0(np.outer(eta, beta))                       # (n_r, n_modes)

    seg_t0, seg_t1 = ta_times[:-1], ta_times[1:]
    slope = np.diff(ta_vals) / np.diff(ta_times)          # 分段线性驱动的逐段斜率
    step0 = ta_vals[0] - T0                               # t=0 处驱动与初温之差（本题为 0）

    out = np.zeros((len(t_arr), len(eta)))
    for k, t in enumerate(t_arr):
        w = -A_n * np.exp(-t / tau) * step0               # 初始阶跃项的模态权重
        act = seg_t0 < t
        a = seg_t0[act]
        b = np.minimum(seg_t1[act], t)
        m = slope[act]
        # int_a^b m*S(t-s) ds 的解析式：ramp 部分 + 指数记忆部分
        ramp = float(np.dot(m, b - a))
        e_a = np.exp(-(t - a)[:, None] / tau[None, :])
        e_b = np.exp(-(t - b)[:, None] / tau[None, :])
        w = w - (A_n * tau) * np.dot(m, e_b - e_a)
        out[k] = T0 + step0 + ramp + basis @ w
    return out, beta, A_n, tau
