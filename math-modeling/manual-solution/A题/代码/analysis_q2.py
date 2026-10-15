# -*- coding: utf-8 -*-
"""
问题2 模型参数灵敏度分析：GRA(灰色关联) + FA(因子分析) + DEA(数据包络) + FCE(模糊综合评价)
输入：结果/q2_sensitivity.csv（25 个情景 × 6 个响应指标）
"""
import numpy as np, pandas as pd, os, sys
from scipy.optimize import linprog
from scipy.stats import rankdata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, '结果')
df = pd.read_csv(os.path.join(RES, 'q2_sensitivity.csv'))
df['U3'] = 1.0 - np.abs(df['Xs_3h'] - df['Xc_3h']) / 2.55      # 3h 内部含水率均匀度(越大越均匀)
df['dT3'] = df['Tc_3h'] - 28.0                                # 3h 预热升温幅度
IND = ['tend_h', 'Xc_3h', 'Xs_3h', 'Tc_3h', 'Ts_3h', 'v6', 'E', 'U3', 'dT3']
NAME = {'tend_h': '烘干时长 t_end/h', 'Xc_3h': '3h中心含水率', 'Xs_3h': '3h表面含水率',
        'Tc_3h': '3h中心温度/°C', 'Ts_3h': '3h表面温度/°C', 'v6': '前6h干燥速率/(kg·kg⁻¹·h⁻¹)',
        'E': '累计供热量/(MJ·m⁻¹)', 'U3': '3h水分均匀度', 'dT3': '3h预热升温/°C'}
FAC = ['烘房温度 T_a', '空气水分浓度 X_a', '对流换热系数 h', '对流传质系数 h_m',
       '初始含水率 X_0', '药材半径 R', '密度系数 ρ', '比热系数 c_p',
       '热导率系数 λ', '扩散系数前因子 D_0', '汽化潜热 L', '预热阶段时长 t_sw']

base = df.iloc[0]
Y = df[IND].to_numpy(float)
print('=' * 100)
print('情景-响应表（%d 个情景）' % len(df))
print(df[['情景'] + IND].round(4).to_string(index=False))

# ======================= 1. GRA 灰色关联分析 =======================
Ymean = Y / Y.mean(axis=0)                      # 均值化无量纲
x0 = Ymean[0]                                   # 参考序列 = 基准情景
D = np.abs(Ymean - x0)
dmin, dmax = D.min(), D.max()
xi = (dmin + 0.5 * dmax) / (D + 0.5 * dmax)
gamma = xi.mean(axis=1)
df['GRA关联度γ'] = gamma
# 每个因素：取 +扰动与-扰动的平均关联度；γ 越小说明该系统行为偏离基准越大 -> 越敏感
fac_g = []
for k, f in enumerate(FAC):
    g = gamma[1 + 2 * k: 3 + 2 * k].mean()
    fac_g.append((f, g, 1 - g))
gra = pd.DataFrame(fac_g, columns=['因素', '平均关联度γ', '灵敏度(1-γ)']).sort_values('灵敏度(1-γ)', ascending=False)
gra['排序'] = np.arange(1, len(gra) + 1)
print('\n' + '=' * 100)
print('【GRA 灰色关联分析】因素灵敏度排序（灵敏度=1-平均关联度，越大越敏感）')
print(gra.round(4).to_string(index=False))

# ======================= 2. FA 因子分析（主因子 + 方差最大旋转） =======================
Z = (Y - Y.mean(axis=0)) / Y.std(axis=0, ddof=1)
C = np.corrcoef(Z, rowvar=False)
w, V = np.linalg.eigh(C)
order = np.argsort(w)[::-1]
w, V = w[order], V[:, order]
cum = np.cumsum(w) / w.sum()
print('\n' + '=' * 100)
print('【FA 因子分析】相关系数矩阵特征值 / 方差贡献率')
print(pd.DataFrame({'因子': ['F%d' % (i + 1) for i in range(len(w))],
                    '特征值': np.round(w, 4), '方差贡献率': np.round(w / w.sum(), 4),
                    '累计贡献率': np.round(cum, 4)}).to_string(index=False))
m = int(np.searchsorted(cum, 0.85) + 1)
m = max(2, min(m, 4))
L0 = V[:, :m] * np.sqrt(w[:m])


def varimax(L, tol=1e-8, it=500):
    p, k = L.shape
    R = np.eye(k); d = 0
    for _ in range(it):
        Lr = L @ R
        u, s, vt = np.linalg.svd(L.T @ (Lr ** 3 - (1.0 / p) * Lr @ np.diag(np.diag(Lr.T @ Lr))))
        R = u @ vt; dnew = s.sum()
        if dnew < d * (1 + tol):
            break
        d = dnew
    return L @ R


L = varimax(L0)
if L.sum(axis=0).mean() < 0:
    L = -L
load = pd.DataFrame(np.round(L, 3), index=[NAME[i] for i in IND], columns=['F%d' % (i + 1) for i in range(m)])
print('\n旋转后因子载荷矩阵：')
print(load.to_string())
sc = pd.DataFrame(np.round(Z @ np.linalg.pinv(C) @ L, 3),
                  columns=['F%d' % (i + 1) for i in range(m)])
df_fa = pd.concat([df[['情景']], sc], axis=1)
print('\n各情景因子得分（前 8 行）：')
print(df_fa.head(8).to_string(index=False))

# ======================= 3. DEA 数据包络分析（CCR-I / BCC-I） =======================
Xin = np.column_stack([df['tend_h'].to_numpy(), df['E'].to_numpy()])           # 投入
Yout = np.column_stack([df['v6'].to_numpy(), df['U3'].to_numpy(), df['dT3'].to_numpy()])  # 产出
n = len(df)


def dea(X, Y, rts='crs'):
    """投入导向 CCR(CRS)/BCC(VRS) 包络模型。X:(n,m) 投入, Y:(n,s) 产出"""
    n, m = X.shape
    s = Y.shape[1]
    eff = np.zeros(n)
    for o in range(n):
        c = np.concatenate([np.zeros(n), [1.0]])                 # min θ
        A_ub = np.vstack([np.hstack([X.T, -X[o].reshape(m, 1)]),   # Σλx - θx0 ≤ 0
                          np.hstack([-Y.T, np.zeros((s, 1))])])   # -Σλy ≤ -y0
        b_ub = np.concatenate([np.zeros(m), -Y[o]])
        A_eq = b_eq = None
        if rts == 'vrs':                                          # Σλ = 1
            A_eq = np.hstack([np.ones((1, n)), np.zeros((1, 1))])
            b_eq = np.array([1.0])
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                    bounds=[(0, None)] * n + [(0, None)], method='highs')
        eff[o] = r.fun if r.success else np.nan
    return eff


eff_crs = dea(Xin, Yout, 'crs')
eff_vrs = dea(Xin, Yout, 'vrs')
df['DEA_CCR'] = eff_crs
df['DEA_BCC'] = eff_vrs
df['规模效率'] = eff_crs / eff_vrs
print('\n' + '=' * 100)
print('【DEA 数据包络分析】投入=(t_end, E)，产出=(v6, U3, dT3)')
print(df[['情景', 'DEA_CCR', 'DEA_BCC', '规模效率']].round(4).to_string(index=False))

# ======================= 4. FCE 模糊综合评价（熵权法 + 梯形隶属度） =======================
CRIT = [('tend_h', 'cost'), ('E', 'cost'), ('v6', 'benefit'), ('U3', 'benefit'), ('dT3', 'benefit')]
cols = [c for c, _ in CRIT]
M = df[cols].to_numpy(float)
Mn = np.zeros_like(M)
for j, (c, d) in enumerate(CRIT):
    lo, hi = M[:, j].min(), M[:, j].max()
    Mn[:, j] = (M[:, j] - lo) / (hi - lo)
    if d == 'cost':
        Mn[:, j] = 1 - Mn[:, j]            # 归一化为"越大越好"
p = Mn / Mn.sum(axis=0, keepdims=True)
p = np.clip(p, 1e-12, None)
e = -np.sum(p * np.log(p), axis=0) / np.log(n)
wt = (1 - e) / (1 - e).sum()
print('\n' + '=' * 100)
print('【FCE 模糊综合评价】熵权法权重')
print(pd.DataFrame({'指标': [NAME[c] for c in cols], '信息熵e': np.round(e, 4),
                    '权重w': np.round(wt, 4)}).to_string(index=False))
# 梯形隶属度：(差, 中, 良, 优)
GRADES = ['差', '中', '良', '优']
def memb(v):
    """v∈[0,1] -> 4 级隶属度"""
    a = [max(0.0, 1 - 3 * v), max(0.0, 1 - abs(3 * v - 1)), max(0.0, 1 - abs(3 * v - 2)), max(0.0, 1 - abs(3 * v - 3))]
    a = np.array(a)
    s = a.sum()
    return a / s if s > 0 else np.array([0, 0, 0, 1.0])


R = np.array([np.concatenate([memb(Mn[i, j]) * wt[j] for j in range(len(cols))]) for i in range(n)]
             ).reshape(n, len(cols), 4)
B = R.sum(axis=1)
score = B @ np.array([1.0, 2.0, 3.0, 4.0])
df['FCE得分'] = score
df['FCE等级'] = [GRADES[int(np.argmax(b))] for b in B]
for g, i in zip(GRADES, range(4)):
    df['μ' + g] = B[:, i]
print('\n各情景模糊综合评价结果：')
print(df[['情景', 'FCE得分', 'FCE等级'] + ['μ' + g for g in GRADES]].round(4).to_string(index=False))
dfd = df.copy()

# ======================= 汇总输出 =======================
out = os.path.join(RES, 'q2_sensitivity_result.xlsx')
with pd.ExcelWriter(out) as w:
    df[['情景'] + IND].round(4).to_excel(w, sheet_name='情景-响应', index=False)
    gra.round(4).to_excel(w, sheet_name='GRA灰色关联', index=False)
    load.to_excel(w, sheet_name='FA因子载荷')
    df_fa.to_excel(w, sheet_name='FA因子得分', index=False)
    df[['情景', 'DEA_CCR', 'DEA_BCC', '规模效率']].round(4).to_excel(w, sheet_name='DEA效率', index=False)
    pd.concat([df[['情景', 'FCE得分', 'FCE等级']].reset_index(drop=True),
               pd.DataFrame(np.round(B, 4), columns=['μ' + g for g in GRADES])], axis=1) \
        .to_excel(w, sheet_name='FCE模糊综合', index=False)
df.to_csv(os.path.join(RES, 'q2_sensitivity_analysis.csv'), index=False, encoding='utf-8-sig')
np.save(os.path.join(RES, 'q2_fa_scores.npy'), sc.to_numpy())
print('\n结果已保存 ->', out)

# ======================= 图 =======================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
FIG = os.path.join(RES, 'figs_q2')

fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
ax[0].barh(gra['因素'][::-1], gra['灵敏度(1-γ)'][::-1], color='#2e7d32')
ax[0].set_xlabel('灵敏度 1-γ（灰色关联度越小越敏感）')
ax[0].set_title('GRA 参数灵敏度排序'); ax[0].grid(alpha=.3, axis='x')
ax[1].scatter(df['DEA_CCR'], df['FCE得分'], c=df['tend_h'], cmap='RdYlGn_r', s=45, edgecolor='k', lw=.4)
for i in range(n):
    if df['DEA_CCR'][i] > 0.999 or df['FCE得分'][i] > df['FCE得分'].quantile(.9):
        ax[1].annotate(df['情景'][i], (df['DEA_CCR'][i], df['FCE得分'][i]), fontsize=6.5)
ax[1].set_xlabel('DEA-CCR 综合效率'); ax[1].set_ylabel('FCE 综合得分')
ax[1].set_title('DEA 效率 vs 模糊综合评价得分（颜色=烘干时长）'); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_q2_analysis.png'), dpi=140); plt.close()

fig, ax = plt.subplots(figsize=(6.4, 4.6))
k = len(load.columns)
for i in range(m):
    ax.scatter(load.iloc[:, 0], load.iloc[:, 1], s=0)
xs = np.zeros((len(IND), 2))
xs[:, 0] = load.iloc[:, 0]; xs[:, 1] = load.iloc[:, 1]
for i, nm in enumerate(load.index):
    ax.annotate('', xy=(xs[i]), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='#1565c0', lw=1.2))
    ax.text(xs[i, 0] * 1.06, xs[i, 1] * 1.06, nm, fontsize=8)
ax.axhline(0, color='gray', lw=.6); ax.axvline(0, color='gray', lw=.6)
ax.set_xlabel('因子 F1 载荷'); ax.set_ylabel('因子 F2 载荷')
ax.set_title('FA 因子载荷图（方差最大旋转）'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_q2_fa.png'), dpi=140); plt.close()
print('图已保存')
