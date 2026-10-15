# -*- coding: utf-8 -*-
"""生成问题2的全部交付物：result2.xlsx、表3/表4、图、全过程数据"""
import numpy as np, pandas as pd, os, sys, shutil, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_q2 import solve, TT, TA_TAB, XA_TAB, wet_bulb, DIF, RHO, CP, LAM, LAT, T_SWITCH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, '结果')
FIG = os.path.join(RES, 'figs_q2')
os.makedirs(FIG, exist_ok=True)

# ---------- 备份旧结果 ----------
bak = os.path.join(RES, '备份_问题2_未考虑潜热')
os.makedirs(bak, exist_ok=True)
for f in ['result2.xlsx', 'tab3.npy', 'tab4.npy']:
    p = os.path.join(RES, f)
    if os.path.exists(p) and not os.path.exists(os.path.join(bak, f)):
        shutil.copy2(p, os.path.join(bak, f))
print('备份完成 ->', bak)

DIST = [round(0.1 * k, 1) for k in range(21)]
OI = [0, 5, 10, 15, 20]          # r = 0, 0.5, 1.0, 1.5, 2.0 cm


def run_3h(dt=1.0, N=500):
    ts, Ts, Xs, _ = solve(N=N, dt=dt, tmax=10800.0, mode='limited', rec_dt=1.0)
    return ts, Ts, Xs


# ================= 1. 3 h 结果 -> result2.xlsx =================
print('计算 3 h (dt=1s) ...')
t0 = time.time()
ts, Ts, Xs = run_3h(dt=1.0, N=500)
print('  用时 %.1f s' % (time.time() - t0))

from openpyxl import Workbook
wb = Workbook(write_only=True)
for name, arr in [('温度', Ts), ('水分浓度', Xs)]:
    ws = wb.create_sheet(name)
    ws.append(['时间\\到药材中心的距离'] + DIST)
    for k in range(len(ts)):
        ws.append([int(ts[k])] + [round(float(v), 4) for v in arr[k]])
wb.save(os.path.join(RES, 'result2.xlsx'))
print('  result2.xlsx 写出：%d 行 × %d 列 × 2 表' % (len(ts), 21))

# ================= 2. 表3 / 表4 =================
hrs = [1800, 3600, 5400, 7200, 9000, 10800]
Ttab = np.array([[h] + list(Ts[np.where(ts == h)[0][0]][OI]) for h in hrs])
Xtab = np.array([[h] + list(Xs[np.where(ts == h)[0][0]][OI]) for h in hrs])
np.save(os.path.join(RES, 'tab3.npy'), Ttab)
np.save(os.path.join(RES, 'tab4.npy'), Xtab)
with pd.ExcelWriter(os.path.join(RES, '问题2_表3表4.xlsx')) as w:
    pd.DataFrame(np.round(Ttab, 4), columns=['时间/s'] + ['%g cm' % d for d in [0, .5, 1, 1.5, 2]]) \
        .to_excel(w, sheet_name='表3 温度(°C)', index=False)
    pd.DataFrame(np.round(Xtab, 4), columns=['时间/s'] + ['%g cm' % d for d in [0, .5, 1, 1.5, 2]]) \
        .to_excel(w, sheet_name='表4 水分浓度', index=False)
print('表3 =');print(np.round(Ttab, 4))
print('表4 =');print(np.round(Xtab, 4))

# ================= 3. 全过程 =================
print('计算全过程 ...')
t0 = time.time()
ts2, Ts2, Xs2, tend = solve(N=500, dt=1.0, tmax=345600.0, mode='limited', rec_dt=60.0)
tsn, Tsn, Xsn, tendn = solve(N=500, dt=2.0, tmax=345600.0, mode='none', rec_dt=60.0)
print('  用时 %.1f s' % (time.time() - t0))
print('  含潜热烘干时长 = %.2f h (%.0f s)' % (tend / 3600, tend))
print('  无潜热烘干时长 = %.2f h (%.0f s)' % (tendn / 3600, tendn))
np.savez_compressed(os.path.join(RES, 'q2_full.npz'),
                    t=ts2, T=Ts2, X=Xs2, t_none=tsn, T_none=Tsn, X_none=Xsn,
                    tend=tend, tend_none=tendn,
                    dist=np.array(DIST))

# 平均含水率
def xavg(Xp):
    r = np.array(DIST) / 100.0
    w = np.array([r[0] ** 2 / 2] + [(r[i] + 0.0005) ** 2 - (r[i] - 0.0005) ** 2 for i in range(1, 20)] +
                 [r[20] ** 2 - (r[20] - 0.0005) ** 2]) / 2
    return (Xp * w).sum() / w.sum()


Xavg = np.array([xavg(x) for x in Xs2])
Xavgn = np.array([xavg(x) for x in Xsn])

# ================= 4. 图 =================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 图1：3h 内温度/水分 剖面演化
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
snap = [600, 1800, 3600, 5400, 7200, 9000, 10800]
cmap = plt.cm.viridis
for i, tt_ in enumerate(snap):
    k = np.where(ts == tt_)[0][0]
    c = cmap(i / (len(snap) - 1))
    axes[0].plot(DIST, Ts[k], color=c, label='%.1f h' % (tt_ / 3600))
    axes[1].plot(DIST, Xs[k], color=c, label='%.1f h' % (tt_ / 3600))
axes[0].set_xlabel('到药材中心距离 / cm'); axes[0].set_ylabel('温度 / °C')
axes[0].set_title('问题2：前3 h 温度剖面（含潜热）'); axes[0].grid(alpha=.3); axes[0].legend(fontsize=8)
axes[1].set_xlabel('到药材中心距离 / cm'); axes[1].set_ylabel('水分浓度 / (kg/kg)')
axes[1].set_title('问题2：前3 h 水分浓度剖面（含潜热）'); axes[1].grid(alpha=.3); axes[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_q2_3h.png'), dpi=140); plt.close()

# 图2：全过程
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].plot(ts2 / 3600, Ts2[:, 0], label='中心 r=0')
axes[0].plot(ts2 / 3600, Ts2[:, 10], label='r=1.0 cm')
axes[0].plot(ts2 / 3600, Ts2[:, 20], label='表面 r=2.0 cm')
ta_curve = [np.interp(t, TT, TA_TAB) if t <= T_SWITCH else 50.0 for t in ts2]
twb_curve = [wet_bulb(np.interp(t, TT, TA_TAB) if t <= T_SWITCH else 50.0,
                      np.interp(t, TT, XA_TAB) if t <= T_SWITCH else 0.05) for t in ts2]
axes[0].plot(ts2 / 3600, ta_curve, 'r--', lw=1, label='烘房空气')
axes[0].plot(ts2 / 3600, twb_curve, 'c:', lw=1.3, label='空气湿球温度')
axes[0].axvline(tend / 3600, color='k', ls=':', alpha=.6)
axes[0].set_xlabel('时间 / h'); axes[0].set_ylabel('温度 / °C')
axes[0].set_title('含潜热模型：全过程温度'); axes[0].grid(alpha=.3); axes[0].legend(fontsize=8)
axes[1].plot(ts2 / 3600, Xs2[:, 0], label='中心 r=0')
axes[1].plot(ts2 / 3600, Xs2[:, 10], label='r=1.0 cm')
axes[1].plot(ts2 / 3600, Xs2[:, 20], label='表面 r=2.0 cm')
axes[1].plot(ts2 / 3600, Xavg, 'k--', label='平均')
axes[1].plot(tsn / 3600, Xsn[:, 0], color='gray', ls='-.', lw=1, label='无潜热(中心)')
axes[1].axhline(0.15, color='r', ls='--', lw=1); axes[1].text(1, 0.18, '0.15 kg/kg 判据', color='r', fontsize=8)
axes[1].axvline(tend / 3600, color='k', ls=':', alpha=.6)
axes[1].text(tend / 3600 - 18, 2.2, '烘干结束 %.1f h' % (tend / 3600), fontsize=9)
axes[1].set_xlabel('时间 / h'); axes[1].set_ylabel('水分浓度 / (kg/kg)')
axes[1].set_title('含潜热模型：全过程水分浓度'); axes[1].grid(alpha=.3); axes[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_q2_full.png'), dpi=140); plt.close()

# 图3：三种潜热处理对比
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for mode, st, nm in [('none', '-', '不计潜热'), ('full', ':', '计潜热·无供热限制'), ('limited', '-', '计潜热·供热限制(本文)')]:
    _, Tm, Xm, _ = solve(N=500, dt=1.0, tmax=10800.0, mode=mode, rec_dt=300.0)
    tm = np.arange(1, len(Tm) + 1) * 300.0
    axes[0].plot(tm / 3600, Tm[:, 10], st, label=nm + ' (r=1cm)')
    axes[1].plot(tm / 3600, Xm[:, 20], st, label=nm + ' (表面)')
tb = [wet_bulb(np.interp(t, TT, TA_TAB), np.interp(t, TT, XA_TAB)) for t in tm]
axes[0].plot(tm / 3600, tb, 'r--', lw=1, label='空气湿球温度')
axes[0].set_xlabel('时间 / h'); axes[0].set_ylabel('温度 / °C')
axes[0].set_title('潜热处理方式对温度的影响'); axes[0].grid(alpha=.3); axes[0].legend(fontsize=8)
axes[1].set_xlabel('时间 / h'); axes[1].set_ylabel('水分浓度 / (kg/kg)')
axes[1].set_title('潜热处理方式对干燥速率的影响'); axes[1].grid(alpha=.3); axes[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_q2_latent_cmp.png'), dpi=140); plt.close()
print('图已保存 ->', FIG)
