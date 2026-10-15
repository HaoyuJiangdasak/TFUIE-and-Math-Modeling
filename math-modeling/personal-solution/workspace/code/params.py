# code/params.py — 参数唯一来源：PROBLEM_FACTS.json（自动派生，禁止手改数值）
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_FACTS = json.loads((ROOT / 'PROBLEM_FACTS.json').read_text(encoding='utf-8'))


def _sci(node, key_pre='prefactor'):
    """把 facts 里 prefactor + power_of_ten_* 的编码还原为浮点。"""
    mag = node['power_of_ten_magnitude']
    sign = -1 if node['power_of_ten_sign'] == 'negative' else 1
    return float(node[key_pre]) * 10.0 ** (sign * mag)


_GEO = _FACTS['geometry']
_IC = _FACTS['initial_conditions']
_BC = _FACTS['boundary_coefficients']
_A2 = _FACTS['material_appendix2']
_A3 = _FACTS['material_appendix3']
_A4 = _FACTS['material_appendix4']

CM_PER_M = 100.0
KELVIN_OFFSET = 273.15

# ---------- 几何与初始条件 ----------
R0_CM = float(_GEO['radius_cm'])
L_CM = float(_GEO['length_cm'])
R0_M = R0_CM / CM_PER_M
L_M = L_CM / CM_PER_M
T0_C = float(_IC['T0_celsius'])
C0 = float(_IC['C0_kg_per_kg'])

# ---------- 表面传递系数（附录 2 给出，附录 3/4 未重给，四问沿用）----------
H_CONV = float(_BC['h_convective_heat']['value'])
HM_MASS = _sci(_BC['hm_convective_mass'])

# ---------- 附录 2：常物性 + D 仅依含水率 ----------
RHO_A2 = float(_A2['rho']['value'])
CP_A2 = float(_A2['cp']['value'])
LAM_A2 = float(_A2['lambda']['value'])
D2_PREFACTOR = _sci(_A2['D'])
D2_MOIST_EXP = float(_A2['moisture_exponent_constant']) if 'moisture_exponent_constant' in _A2 \
    else float(_A2['D']['moisture_exponent_constant'])
assert abs(D2_PREFACTOR - 7.0e-9) < 1e-20, 'appendix-2 prefactor mismatch'
assert abs(D2_MOIST_EXP - 0.89) < 1e-12

# ---------- 附录 3：变物性 + Arrhenius（问题二、三）----------
RHO3_A = float(_A3['rho']['intercept'])
RHO3_B = float(_A3['rho']['slope'])
CP3_A = float(_A3['cp']['intercept'])
CP3_B = float(_A3['cp']['coefficient'])
LAM3_A = float(_A3['lambda']['intercept'])
LAM3_B = float(_A3['lambda']['coefficient'])
D3_PREFACTOR = _sci(_A3['D'])
D3_MOIST_EXP = float(_A3['D']['moisture_exponent_constant'])
ACT_TEMP_K = float(_A3['D']['activation_temperature_K'])
assert (CP3_A, CP3_B) == (1450.0, 2736.0), 'appendix-3 cp mismatch'
assert ACT_TEMP_K == 3850.0, 'activation temperature mismatch'

# ---------- 附录 4：变物性 + Arrhenius（问题四）----------
RHO4_A = float(_A4['rho']['intercept'])
RHO4_B = float(_A4['rho']['slope'])
CP4_A = float(_A4['cp']['intercept'])
CP4_B = float(_A4['cp']['coefficient'])
LAM4_A = float(_A4['lambda']['intercept'])
LAM4_B = float(_A4['lambda']['coefficient'])
D4_PREFACTOR = _sci(_A4['D'])
D4_MOIST_EXP = float(_A4['D']['moisture_exponent_constant'])
ACT_TEMP_K_A4 = float(_A4['D']['activation_temperature_K'])
assert ACT_TEMP_K_A4 == ACT_TEMP_K, 'appendix-4 activation temperature must equal appendix-3'

# ---------- 阈值 ----------
C_THR = float(_FACTS['thresholds']['moisture_limit_kg_per_kg'])
DUR_DAYS_LOW = float(_FACTS['process_facts']['typical_duration_days_low'])
DUR_DAYS_HIGH = float(_FACTS['process_facts']['typical_duration_days_high'])

# ---------- 数值方案（§13-④，编码阶段不得再选）----------
N_CELLS = 120
MESH_LADDER = (15, 30, 60, 120, 240)
RTOL = 1e-8
ATOL = 1e-10
MAX_STEP_SHORT = 10.0        # 问题一、二（M6）
MAX_STEP_LONG = 60.0         # 问题三、四（M6）
T_INTEGRATION_CAP = 1.2e6    # 事件未触发的保护上限（③-P05）
C_FLOOR = 1e-6               # 仅用于物性求值的下界保护（①-C14）
N_MODES = 200                # 贝塞尔-杜阿梅尔级数模态数（MC5）
SEED = 20260910
HOLD_RELAX_TAU = 300.0       # 平台衔接指数松弛时间常数（④M2）
PLATEAU_WINDOW_START = 7200.0
LATENT_HEAT_FACTOR = 0.0     # 基准不引入潜热汇（假设 A1）
H_FG_SCAN = 2.4e6            # 仅供 §13-④M9 的假设代价扫描使用
DECIMALS = 4

# ---------- 输出口径（§13-⓪(c)）----------
SEC_PER_HOUR = 3600.0
OUT_R_CM = [round(0.1 * k, 1) for k in range(21)]          # 0, 0.1, ..., 2.0
Q4_FIXED_R_CM = [round(0.1 * k, 1) for k in range(20)]     # 0, ..., 1.9 + 「药材表面」
SURFACE_LABEL = '药材表面'
TABLE_R_CM = [0.0, 0.5, 1.0, 1.5, 2.0]
Q1_TABLE_TIMES = [100, 300, 600, 900, 1200, 1500, 1800]
Q1_T_END = 1800
Q2_T_END = 10800
Q2_TABLE_TIMES = [1800, 3600, 5400, 7200, 9000, 10800]
Q1_OUT_TIMES = list(range(1, Q1_T_END + 1))                # result1：1..1800 s 步长 1 s
Q2_OUT_TIMES = list(range(1, Q2_T_END + 1))                # result2：1..10800 s 步长 1 s
OUT_STEP_LONG = 60                                         # result3/4：60,120,... s

# ---------- 路径 ----------
DATA_DIR = ROOT / 'user_data'
FIG_DIR = ROOT / 'figures'
TMP_DIR = ROOT / '_tmp'
ATT1_XLSX = DATA_DIR / '附件1.xlsx'
ATT2_XLSX = DATA_DIR / '附件2.xlsx'
TEMPLATES = {k: DATA_DIR / f'result{k}.xlsx' for k in (1, 2, 3, 4)}
RESULT_FILES = {k: ROOT / f'result{k}.xlsx' for k in (1, 2, 3, 4)}
