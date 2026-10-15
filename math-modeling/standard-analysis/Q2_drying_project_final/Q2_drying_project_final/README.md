# Q2 药材烘干：联合 BDF 数值求解工程

本工程在第一问已经验证过的圆柱径向有限体积框架上升级得到，用于第二问 0–3 h 的变物性、非线性热湿耦合计算。

## 已确认的正式数值路线

正式结果：

\[
\boxed{
\text{cylindrical cell-centered FVM}
\rightarrow
\text{joint state } y=[T,C]
\rightarrow
\text{local coupled Picard for }(T_s,C_s)
\rightarrow
\text{Method of Lines}
\rightarrow
\text{SciPy BDF}
}
\]

辅助分析：

\[
\boxed{
\text{Backward Euler}
+
\text{block Picard}
}
\]

分块 Picard **不作为正式结果源**，只用于：
- 固定步长收敛分析；
- 与联合 BDF 交叉验证；
- 比较“充分 Picard 迭代”与“每步只做一次滞后 \(T\to C\) 扫描”，量化参数滞后/分裂误差。

## 与 Q1 相比的核心升级

1. Q2 从 `t=0` 重新计算，不接 Q1 的 1800 s 状态。
2. 全过程调用附录 3：
   - `rho(C)`
   - `cp(C)`
   - `k(C)`
   - `D(C,T_K)`
3. `D` 内部自动执行 `T_K = T_C + 273.15`。
4. 温度和水分不再分别积分，而是联合状态交给 BDF。
5. 表面 `Ts` 与 `Cs` 存在局部相互依赖，使用联立 Picard。
6. 内部 `k_face`、`D_face` 默认采用调和平均，并保留其它面系数方案用于敏感性检查。
7. Q2 热验证使用半离散瞬时平衡，不照搬 Q1 的累计热量恒等式。

## 工程结构

```text
Q2_drying_project_final/
├─ src/
│  └─ q2_solver.py
├─ notebooks/
│  └─ Q2_analysis.ipynb
├─ data/
│  └─ 附件1.xlsx
├─ docs/
│  └─ Q2_完整建模与数值求解交接文档.md
├─ outputs/
├─ Q1_to_Q2_migration.md
├─ SMOKE_TEST_REPORT.md
├─ requirements.txt
├─ environment.yml
└─ README.md
```

## Conda 环境

```bash
conda env create -f environment.yml
conda activate q2_drying
python -m ipykernel install --user --name q2_drying --display-name "Python (q2_drying)"
```

## pip / venv

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 建议使用顺序

先打开：

```text
notebooks/Q2_analysis.ipynb
```

建议依次运行：

1. 附件 1 数据检查；
2. 附录 3 物性尺度检查；
3. `N=320` 联合 BDF 基准解；
4. 论文要求的 0.5–3 h 表格；
5. 径向温度、水分剖面；
6. 中心/中部/表面时间历程；
7. `D(C,T)` 等物性变化；
8. 正值性、通量方向与局部表面 Picard 迭代次数；
9. 独立 Robin 残差；
10. 半离散热平衡和水分积分平衡；
11. `N=320,640,1280` 网格收敛；
12. BDF 容差 / `max_step` 敏感性；
13. 面系数敏感性；
14. Backward Euler + 分块 Picard 对照；
15. 单次滞后扫描的分裂误差；
16. 可选 Q1–Q2 前 1800 s 公平对比；
17. `N=1280` 正式生产解；
18. 生成 `result2.xlsx`。

## 开发运行

```bash
python src/q2_solver.py \
  --env data/附件1.xlsx \
  --output outputs/result2_N640.xlsx \
  --N 640 \
  --rtol 1e-9 \
  --atol 1e-11 \
  --max-step 5
```

## 正式生产建议

完成 Notebook 中的收敛验证后：

```bash
python src/q2_solver.py \
  --env data/附件1.xlsx \
  --output outputs/result2.xlsx \
  --N 1280 \
  --rtol 1e-9 \
  --atol 1e-11 \
  --max-step 5
```

如官方提供 `result2.xlsx` 模板：

```bash
python src/q2_solver.py \
  --env data/附件1.xlsx \
  --output outputs/result2.xlsx \
  --template data/result2_template.xlsx \
  --N 1280 \
  --rtol 1e-9 \
  --atol 1e-11 \
  --max-step 5
```

## 重要说明

- `1 s` 是结果输出间隔，不是 BDF 固定时间步。
- `0.1 cm` 是结果输出空间间隔，不是有限体积求解网格宽度。
- `h=25 W/(m^2 K)` 与 `hm=8e-7 m/s` 是从 Q1 在同一设备条件下继承的闭合假设。
- `C` 不允许通过 `clip()` 人工修正；若出现非正值，程序直接报错。
- 最终收敛、平衡、残差分析必须使用未四舍五入的内部数值。
