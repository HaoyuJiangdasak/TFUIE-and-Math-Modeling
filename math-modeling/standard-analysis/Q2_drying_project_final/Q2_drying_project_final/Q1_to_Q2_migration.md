# Q1 -> Q2 数值代码升级说明

本工程保持 Q1 的总体数值结构，不重新发明求解器。

## 直接继承的部分

- `EnvironmentData`：附件 1 读取与分段线性插值；
- 圆柱 `cell-centered FVM`；
- 中心面 `A(0)=0` 的轴对称零通量处理；
- 中心值二阶重构；
- 表面二阶 Robin 导数重构；
- Method of Lines；
- SciPy `solve_ivp(method="BDF")`；
- 求解网格与 `1 s x 0.1 cm` 输出网格分离；
- 网格收敛、Robin 残差、物理方向检查、Excel 输出的模块化组织。

## Q2 的核心升级

### 1. 联合状态

Q1 中温度、水分可以分别积分；Q2 改为

\[
y=[T_0,\ldots,T_{N-1},C_0,\ldots,C_{N-1}]^T
\]

统一交给 BDF。

### 2. 每次 RHS 调用都更新物性

\[
\rho(C),\quad c_p(C),\quad k(C),\quad D(C,T+273.15)
\]

全部由当前 BDF 状态实时计算，不做时间层参数冻结。

### 3. 内部面采用守恒通量

默认：

\[
k_f=\frac{2k_Lk_R}{k_L+k_R},
\qquad
D_f=\frac{2D_LD_R}{D_L+D_R}.
\]

同时保留 `midpoint_property` 和 `arithmetic` 用于离散敏感性分析。

### 4. 表面改为局部联立 Picard

在每次 RHS 计算中迭代

\[
C_s^{(m)}
\rightarrow
k(C_s^{(m)})
\rightarrow
T_s^{(m+1)}
\rightarrow
D(C_s^{(m)},T_s^{(m+1)})
\rightarrow
C_s^{(m+1)}.
\]

这是 Q2 相比 Q1 最重要的边界升级。

### 5. 主线 BDF，不引入人为 T->C 分裂

BDF 直接积分联合状态，因此正式结果不存在“每个时间层只做一次 T 后 C”的人为分裂误差。

### 6. 手工分块 Picard 作为独立误差分析

额外实现：

`Backward Euler + block Picard`

用途不是替代正式 BDF，而是：

- 检查固定时间步收敛；
- 验证其随 \(\Delta t\to0\) 向 BDF 结果靠近；
- 对比“充分迭代 Picard”和“只做一次滞后 T->C 扫描”，量化分裂/参数滞后误差。

### 7. Q2 热平衡验证与 Q1 不同

Q2 采用的模型是

\[
\rho(C)c_p(C)T_t=\nabla\cdot(k(C)\nabla T).
\]

因此不能照搬 Q1 的累计热能恒等式

\[
\Delta\int \rho c_pT\,dV=\int q\,dt.
\]

代码改为检查当前 PDE 真正要求的半离散瞬时平衡：

\[
\sum_i \rho_i c_{p,i}V_i\dot T_i+A_Rq_R\approx0.
\]

水分有效扩散方程仍检查 \(\int C\,dV\) 与累计表面通量的一致性。

## 当前建议

- 开发/调试：`N=320` 或 `N=640`；
- 正式生产：在收敛表复现后使用 `N=1280`；
- BDF 基线：`rtol=1e-9, atol=1e-11, max_step=5 s`；
- 严格时间复核：`rtol=2e-10, atol=2e-12, max_step=1 s`；
- 正式面系数：harmonic mean；
- 表面局部 Picard：默认无欠松弛，若未来参数区间导致收敛困难再启用欠松弛。
