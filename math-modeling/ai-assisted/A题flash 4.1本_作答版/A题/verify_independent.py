# -*- coding: utf-8 -*-
"""
独立交叉验证（与 solver.py 完全不同的离散路径）

独立性所在
----------
* 空间：**物理半径 r 坐标 + 单元中心有限体积**（solver.py 为归一化 xi + 顶点法）
* 界面系数：**调和平均**（solver.py 为算术平均）
* 近壁处理：**虚拟+半单元边界通量**，并用末两个单元中心**线性外推到 r=R0** 取表面值
  （solver.py 直接把表面节点放在 xi=1）
* 时间：BDF + 带状稀疏 Jacobian

用途
----
    python verify_independent.py            # 问题1 + 问题3 全套对照
    python verify_independent.py 3 400      # 只算问题3, M=400
"""
import sys
import os
import numpy as np
import openpyxl
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix

BASE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.join(BASE, "附件")

R0 = 0.02                     # m
T0, C0 = 28.0, 2.55
h, hm = 25.0, 8e-7

# ---------------- 环境（附件1） ----------------
_ws1 = openpyxl.load_workbook(os.path.join(ATT, "附件1.xlsx"), data_only=True)["Sheet1"]
_t = np.array([_ws1.cell(r, 1).value for r in range(2, _ws1.max_row + 1)], float)
_Ta = np.array([_ws1.cell(r, 2).value for r in range(2, _ws1.max_row + 1)], float)
_Ca = np.array([_ws1.cell(r, 3).value for r in range(2, _ws1.max_row + 1)], float)
T_SW, T_HOLD, C_HOLD = 14400.0, 50.0, 0.05


def Tair(t):
    return float(np.interp(t, _t, _Ta)) if t <= T_SW else T_HOLD


def Cair(t):
    return float(np.interp(t, _t, _Ca)) if t <= T_SW else C_HOLD


def props(mode, C, T_C):
    C = np.asarray(C, float)
    Tk = np.asarray(T_C, float) + 273.15
    if mode == 2:
        z = np.zeros_like(C)
        return 820.0 + z, 2600.0 + z, 0.36 + z, 7e-9 * np.exp(-0.89 / C)
    if mode == 3:
        return (650.0 + 128.0 * C,
                1450.0 + 2736.0 * C / (C + 1.0),
                0.21 + 0.38 * C / (C + 1.0),
                2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / Tk))
    raise ValueError(mode)


def _sparsity(M):
    n = 2 * M
    S = lil_matrix((n, n), dtype=float)
    for i in range(M):
        for d in (-1, 0, 1):
            j = i + d
            if 0 <= j < M:
                S[i, j] = 1; S[M + i, M + j] = 1
        S[i, M + i] = 1; S[M + i, i] = 1
    return S.tocsc()


def solve_physical(mode, t_end, M=400, t_eval=None, rtol=1e-7, atol=1e-9):
    """单元中心 FVM（物理坐标 r）"""
    rF = np.linspace(0.0, R0, M + 1)             # 面
    rc = 0.5 * (rF[:-1] + rF[1:])                # 单元中心
    dV = 0.5 * (rF[1:] ** 2 - rF[:-1] ** 2)      # ∫ r dr
    dr = rc[1:] - rc[:-1]

    def rhs(t, y):
        T = y[:M]; C = y[M:]
        Tai, Cai = Tair(t), Cair(t)
        rho, cp, kk, D = props(mode, C, T)
        # 界面系数：调和平均
        kf = 2.0 * kk[:-1] * kk[1:] / (kk[:-1] + kk[1:])
        Df = 2.0 * D[:-1] * D[1:] / (D[:-1] + D[1:])
        qT = kf * (T[1:] - T[:-1]) / dr          # 内部面 k dT/dr
        qC = Df * (C[1:] - C[:-1]) / dr          # 内部面 D dC/dr
        dT = np.empty(M); dC = np.empty(M)
        # 中心单元（r=rF[1]/2）：对称，只与东面交换
        dT[0] = rF[1] * qT[0] / dV[0] / (rho[0] * cp[0])
        dC[0] = rF[1] * qC[0] / dV[0]
        # 内部单元
        dT[1:M - 1] = (rF[2:M] * qT[1:] - rF[1:M - 1] * qT[:-1]) / dV[1:M - 1] \
            / (rho[1:M - 1] * cp[1:M - 1])
        dC[1:M - 1] = (rF[2:M] * qC[1:] - rF[1:M - 1] * qC[:-1]) / dV[1:M - 1]
        # 表面单元：东面取第三类边界（外法向 +r）
        i = M - 1
        qT_b = h * (Tai - T[i])                  # = k dT/dr |_{R0}
        qC_b = hm * (Cai - C[i])                 # = D dC/dr |_{R0}
        dT[i] = (rF[i + 1] * qT_b - rF[i] * qT[i - 1]) / dV[i] / (rho[i] * cp[i])
        dC[i] = (rF[i + 1] * qC_b - rF[i] * qC[i - 1]) / dV[i]
        return np.concatenate([dT, dC])

    y0 = np.concatenate([np.full(M, T0), np.full(M, C0)])
    if t_eval is None:
        t_eval = np.linspace(0, t_end, 2)
    kw = {"jac_sparsity": _sparsity(M)} if M >= 60 else {}
    sol = solve_ivp(rhs, (0.0, t_end), y0, method="BDF", t_eval=t_eval,
                    rtol=rtol, atol=atol, **kw)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol, rc


def value_at(sol, rc, field, rq_m):
    """把单元中心解插值到给定物理半径(米)；表面 r=R0 用末两个单元中心线性外推。"""
    M = len(rc)
    y = sol.y[:M] if field == 'T' else sol.y[M:]
    out = np.empty((len(sol.t), len(rq_m)))
    Re = rc[-1] + 1e-12
    for j in range(len(sol.t)):
        yj = y[:, j].copy()
        slope = (yj[-1] - yj[-2]) / (rc[-1] - rc[-2])
        ysurf = yj[-1] + slope * (R0 - rc[-1])
        xs = np.append(rc, R0); ys = np.append(yj, ysurf)
        out[j] = np.interp(rq_m, xs, ys)
    return out


def crossing_time(sol, rc, thresh=0.15):
    M = len(rc)
    Cmax = sol.y[M:, :].max(axis=0)
    idx = np.where(Cmax < thresh)[0]
    if len(idx) == 0:
        return np.inf
    i1 = int(idx[0])
    if i1 == 0:
        return float(sol.t[0])
    t0, t1_ = sol.t[i1 - 1], sol.t[i1]
    c0, c1 = Cmax[i1 - 1], Cmax[i1]
    return float(t0 + (thresh - c0) * (t1_ - t0) / (c1 - c0))


# ---------------- 对照基准（来自 solver.py / 解答报告） ----------------
REF = {
    # t=1800 s 处 T(℃)、C(kg/kg) 在 r=0/0.5/1.0/1.5/2.0 cm
    2: {"T": [33.5754, 33.7720, 34.3642, 35.3621, 36.7856],
        "C": [2.5500, 2.5497, 2.5383, 2.3755, 1.5102]},
    3: {"dry_h": 57.4742},
}


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    M = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    rq = np.array([0.0, 0.005, 0.010, 0.015, 0.020])   # 米

    if what in ("all", "2", "1"):
        sol, rc = solve_physical(2, 1800.0, M=M, t_eval=np.arange(1.0, 1801.0))
        Tp = value_at(sol, rc, 'T', rq); Cp = value_at(sol, rc, 'C', rq)
        j = len(sol.t) - 1
        print("== 问题1 (独立: 物理坐标 FVM + 调和平均 + BDF, M=%d) ==" % M)
        print("  t=1800s  T:", " ".join("%.4f" % v for v in Tp[j]),
              " | 参考:", " ".join("%.4f" % v for v in REF[2]["T"]))
        print("  t=1800s  C:", " ".join("%.4f" % v for v in Cp[j]),
              " | 参考:", " ".join("%.4f" % v for v in REF[2]["C"]))
        print("  最大偏差  ΔT=%.4f ℃   ΔC=%.4f kg/kg"
              % (np.abs(Tp[j] - REF[2]["T"]).max(), np.abs(Cp[j] - REF[2]["C"]).max()))

    if what in ("all", "3"):
        sol, rc = solve_physical(3, 120 * 3600.0, M=M,
                                 t_eval=np.arange(60.0, 120 * 3600.0 + 1, 60.0))
        tc = crossing_time(sol, rc)
        print("== 问题3 (独立, M=%d) ==" % M)
        print("  烘干时长 = %.1f s = %.4f h   | 参考 206907 s = 57.4742 h   偏差 %.1f s"
              % (tc, tc / 3600, tc - REF[3]["dry_h"] * 3600))


if __name__ == "__main__":
    main()
