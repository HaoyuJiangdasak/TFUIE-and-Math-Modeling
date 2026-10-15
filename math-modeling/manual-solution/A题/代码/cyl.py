# -*- coding: utf-8 -*-
"""
药材烘干 A 题：轴对称圆柱一维传热-传质耦合求解器
  - 有限体积离散，节点沿半径 r_i = i*dr (i=0..N)，r=0 用 L'Hopital 处理
  - 时间方向：向后欧拉（隐式），三对角用 scipy.linalg.solve_banded 求解
  - 变系数：rho(X)、cp(X)、lam(X)、D(X,T) 由经验公式给出，系数取上一时刻值（半隐式/Picard 线性化）
  - 传质边界：-D dX/dr|_R = h_m (X_s - X_a)          （X 均为干基含水率 kg/kg）
  - 传热边界：-lam dT/dr|_R = h (T_s - T_a)
  - 潜热项：  rho_d * L * dX/dt,  rho_d = rho_app/(1+X)
              -> dT/dt = div(lam grad T)/(rho cp) + L*dX/dt/((1+X) cp)
"""
import numpy as np
from scipy.linalg import solve_banded


class Cyl1D:
    def __init__(self, N=500, R=0.02, n_out=21, out_step=0.001):
        self.N = N
        self.R = R
        self.dr = R / N
        dr = self.dr
        Nn = N
        ii = np.arange(1, Nn)
        self.api = np.zeros(Nn + 1)
        self.ami = np.zeros(Nn + 1)
        self.api[ii] = (ii + 0.5) / (ii * dr * dr)
        self.ami[ii] = (ii - 0.5) / (ii * dr * dr)
        den = dr * dr * (Nn - 0.25)
        self.coef_in = 2.0 * (Nn - 0.5) / den
        self.coef_out = 2.0 * Nn * dr / den
        self.c0 = 4.0 / (dr * dr)
        self.out_idx = [min(Nn, int(round(k * out_step / dr))) for k in range(n_out)]
        self.ii = ii
        self.r = np.arange(Nn + 1) * dr

    # ---------------- 水分的隐式步 ----------------
    def moisture_step(self, X, D, hm, Xa, dt):
        N = self.N
        Df0 = 0.5 * (D[0] + D[1])
        a = np.zeros(N + 1)
        b = np.zeros(N + 1)
        c = np.zeros(N + 1)
        b[0] = 1.0 + dt * self.c0 * Df0
        c[0] = -dt * self.c0 * Df0
        ii = self.ii
        Dfp = 0.5 * (D[ii - 1] + D[ii])
        Dfm = 0.5 * (D[ii] + D[ii + 1])
        a[ii] = -dt * self.ami[ii] * Dfp
        b[ii] = 1.0 + dt * (self.ami[ii] * Dfp + self.api[ii] * Dfm)
        c[ii] = -dt * self.api[ii] * Dfm
        DfpN = 0.5 * (D[N - 1] + D[N])
        a[N] = -dt * self.coef_in * DfpN
        b[N] = 1.0 + dt * (self.coef_in * DfpN + self.coef_out * hm)
        rhs = X.copy()
        rhs[N] = X[N] + dt * self.coef_out * hm * Xa
        ab = np.zeros((3, N + 1))
        ab[0, 1:] = c[:N]
        ab[1, :] = b
        ab[2, :N] = a[1:]
        return solve_banded((1, 1), ab, rhs)

    # ---------------- 温度的隐式步 ----------------
    def heat_step(self, T, lam, rc, h, Ta, dT_latent, dt):
        """dT_latent[i] = L*dX_i/((1+X_i)*cp_i) 为潜热引起的温升增量（负值）"""
        N = self.N
        lf0 = 0.5 * (lam[0] + lam[1])
        a = np.zeros(N + 1)
        b = np.zeros(N + 1)
        c = np.zeros(N + 1)
        k0 = dt * self.c0 * lf0 / rc[0]
        b[0] = 1.0 + k0
        c[0] = -k0
        ii = self.ii
        lfp = 0.5 * (lam[ii - 1] + lam[ii])
        lfm = 0.5 * (lam[ii] + lam[ii + 1])
        kp = dt * self.ami[ii] * lfp / rc[ii]
        km = dt * self.api[ii] * lfm / rc[ii]
        a[ii] = -kp
        b[ii] = 1.0 + kp + km
        c[ii] = -km
        lfpN = 0.5 * (lam[N - 1] + lam[N])
        kn = dt * self.coef_in * lfpN / rc[N]
        ko = dt * self.coef_out * h / rc[N]
        a[N] = -kn
        b[N] = 1.0 + kn + ko
        rhs = T.copy() + dT_latent
        rhs[N] = T[N] + dT_latent[N] + ko * Ta
        ab = np.zeros((3, N + 1))
        ab[0, 1:] = c[:N]
        ab[1, :] = b
        ab[2, :N] = a[1:]
        return solve_banded((1, 1), ab, rhs)
