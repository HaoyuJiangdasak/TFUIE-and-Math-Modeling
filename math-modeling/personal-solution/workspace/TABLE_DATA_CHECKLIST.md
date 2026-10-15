# TABLE 数据真实性核对清单（paper-figure 步骤）

**JSON 源**: all_results.json, problem_1_results.json, problem_2_results.json, problem_3_results.json, problem_4_results.json, sensitivity_results.json
**JSON 数据条目**: 3253
**TABLE 文件**: 10 个

---

## 核心规则

**表格数字须能由结果数据复算；允许单位换算、舍入、差值、比值与统计区间，保留推导依据。**

paper-figure 步骤的设计是从 JSON 数据**渲染**出 TABLE 文件
（用 `_utils/stats_utils.py` 的 `regression_table()` / `descriptive_table()` 等函数，
或者读 JSON 后用 Python 脚本生成）。

**TABLE 中出现 JSON 没有的数字 = 编造**，必须用真实 JSON 数据重新生成对应表格。

---

## 自检步骤

1. **逐个打开 figures/TABLE_*.tex|md**，识别每个表格里的数字单元格
2. **对每个数字**，对照下方 JSON 数据清单：
   - ✅ 能精确匹配（含合理的精度截断如 `0.94` ↔ `0.93724`）→ 真实
   - 未直接匹配 JSON：先查推导、单位和舍入；仍无依据则标记待确认，不能直接认定编造或删除整张表，
     用真实 JSON 数据重新生成（推荐：`python3 -c "from _utils.stats_utils import descriptive_table; ..."`）
3. **跳过非数据型数字**：列号 `(1)(2)(3)`、列宽 `width=10cm`、LaTeX 字号 `\zihao{5}` 等格式标记中的数字
4. **修完所有 TABLE 后**，写自证标记：

   ```bash
   touch figures/TABLE_DATA_CHECK_PASSED.txt
   ```

   下一轮检查看到此标记会跳过自检循环。

**禁止**：禁止改 JSON 让数字"对得上"、禁止编造解释、禁止保留疑似编造的 TABLE。

**特别提示**：如果 JSON 中确实没有支撑某张表所需的数据（比如表格规划里有「数据集统计特征」但 JSON 只存了模型对比结果），说明 paper-analysis 步骤遗漏了该数据。应该：(a) 删除这张表 + 改写论文规划中关于这张表的引用；或 (b) 临时跑一段 Python 从原始数据重算并补到 JSON，再生成 TABLE。**不能**直接保留编造的数字。

---

## TABLE 文件全文

### `figures/TABLE_1.md` (661 字节)

```markdown
**表 1** 预热平衡阶段药材内部温度 / °C的时空分布（附录 2 常物性，r = 2 cm 列为边界条件重构的表面值）

| 时间 / s | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm |
|---|---|---|---|---|---|
| 100 | 28.0001 | 28.0003 | 28.0041 | 28.0327 | 28.1801 |
| 300 | 28.0408 | 28.0635 | 28.1514 | 28.3681 | 28.8489 |
| 600 | 28.4534 | 28.5361 | 28.8040 | 29.3160 | 30.1653 |
| 900 | 29.3243 | 29.4583 | 29.8755 | 30.6162 | 31.7304 |
| 1200 | 30.5427 | 30.7098 | 31.2224 | 32.1126 | 33.4277 |
| 1500 | 31.9957 | 32.1868 | 32.7661 | 33.7463 | 35.1203 |
| 1800 | 33.5753 | 33.7720 | 34.3642 | 35.3622 | 36.7856 |
```

### `figures/TABLE_10.md` (634 字节)

```markdown
**表 10** 物性与收缩的 2×2 归因分解（四次独立真实求解，链式闭合误差 0.0e+00 s）。加性框架在此失效：交互项占总效应 719.19%；改用乘性框架残差仅 10.34%，说明两种机理近似为乘性叠加

| 算例 | 烘干时长 / h | 烘干时长 / d | 相对问题三偏差 / % |
|---|---|---|---|
| 附录 3 物性 + 固定域（问题三基准） | 57.6251 | 2.4010 | +0.00 |
| 附录 4 物性 + 固定域 | 130.0577 | 5.4191 | +125.70 |
| 附录 3 物性 + 径向收缩 | 25.2786 | 1.0533 | -56.13 |
| 附录 4 物性 + 径向收缩（问题四） | 51.1511 | 2.1313 | -11.23 |
```

### `figures/TABLE_2.md` (633 字节)

```markdown
**表 2** 预热平衡阶段药材内部含水率 / (kg/kg)的时空分布（附录 2 常物性，r = 2 cm 列为边界条件重构的表面值）

| 时间 / s | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm |
|---|---|---|---|---|---|
| 100 | 2.5500 | 2.5500 | 2.5500 | 2.5500 | 2.2463 |
| 300 | 2.5500 | 2.5500 | 2.5500 | 2.5492 | 2.0505 |
| 600 | 2.5500 | 2.5500 | 2.5500 | 2.5352 | 1.8768 |
| 900 | 2.5500 | 2.5500 | 2.5497 | 2.5044 | 1.7546 |
| 1200 | 2.5500 | 2.5500 | 2.5482 | 2.4644 | 1.6585 |
| 1500 | 2.5500 | 2.5499 | 2.5445 | 2.4205 | 1.5787 |
| 1800 | 2.5500 | 2.5497 | 2.5383 | 2.3753 | 1.5102 |
```

### `figures/TABLE_3.md` (595 字节)

```markdown
**表 3** 全过程变物性双向强耦合下药材内部温度 / °C的时空分布（附录 3，空气侧取附件 1 实测驱动）

| 时间 / h | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm |
|---|---|---|---|---|---|
| 0.5 | 32.1892 | 32.3822 | 32.9660 | 33.9608 | 35.4130 |
| 1.0 | 40.3815 | 40.5536 | 41.0605 | 41.8782 | 42.9976 |
| 1.5 | 45.8467 | 45.9348 | 46.1929 | 46.6050 | 47.1400 |
| 2.0 | 48.4502 | 48.4880 | 48.5984 | 48.7735 | 49.0033 |
| 2.5 | 49.4670 | 49.4792 | 49.5136 | 49.5653 | 49.6609 |
| 3.0 | 49.8495 | 49.8553 | 49.8746 | 49.9101 | 49.9664 |
```

### `figures/TABLE_4.md` (572 字节)

```markdown
**表 4** 全过程变物性双向强耦合下药材内部含水率 / (kg/kg)的时空分布（附录 3，空气侧取附件 1 实测驱动）

| 时间 / h | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm |
|---|---|---|---|---|---|
| 0.5 | 2.5499 | 2.5489 | 2.5255 | 2.3256 | 1.6486 |
| 1.0 | 2.5257 | 2.4947 | 2.3578 | 2.0229 | 1.4711 |
| 1.5 | 2.3860 | 2.3256 | 2.1344 | 1.8020 | 1.3476 |
| 2.0 | 2.1708 | 2.1084 | 1.9236 | 1.6259 | 1.2311 |
| 2.5 | 1.9566 | 1.9006 | 1.7360 | 1.4720 | 1.1167 |
| 3.0 | 1.7662 | 1.7165 | 1.5702 | 1.3333 | 1.0081 |
```

### `figures/TABLE_5.md` (803 字节)

```markdown
**表 5** 全域最大含水率判据下的含水率分布与烘干结束时间（判据：各处含水率均降至 0.15 kg/kg 以下，首次满足于 t = 57.6251 h）

| 时间 / h | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm |
|---|---|---|---|---|---|
| 6 | 1.0172 | 0.9883 | 0.9016 | 0.7550 | 0.5326 |
| 12 | 0.4564 | 0.4433 | 0.4032 | 0.3298 | 0.1641 |
| 18 | 0.2990 | 0.2917 | 0.2688 | 0.2254 | 0.0843 |
| 24 | 0.2379 | 0.2329 | 0.2169 | 0.1857 | 0.0663 |
| 30 | 0.2060 | 0.2020 | 0.1893 | 0.1643 | 0.0597 |
| 36 | 0.1860 | 0.1827 | 0.1720 | 0.1506 | 0.0565 |
| 42 | 0.1722 | 0.1693 | 0.1599 | 0.1409 | 0.0547 |
| 48 | 0.1620 | 0.1594 | 0.1509 | 0.1337 | 0.0536 |
| 54 | 0.1540 | 0.1516 | 0.1438 | 0.1279 | 0.0529 |
| **烘干结束时间 57.6251 h** |  |  |  |  |  |
```

### `figures/TABLE_6.md` (927 字节)

```markdown
**表 6** 径向收缩条件下药材含水率分布与烘干结束时间（半径由 2 cm 收缩至 1.2000 cm；“—” 表示该固定距离已超出当时半径，物理上不存在该点）

| 时间 / h | 半径 R(t) / cm | r = 0 cm | r = 0.5 cm | r = 1 cm | r = 1.5 cm | r = 2 cm | 药材表面 |
|---|---|---|---|---|---|---|---|
| 6 | 1.3740 | 1.7191 | 1.5373 | 1.0222 | — | — | 0.4202 |
| 12 | 1.2480 | 0.7379 | 0.6548 | 0.4083 | — | — | 0.1668 |
| 18 | 1.2140 | 0.4090 | 0.3689 | 0.2398 | — | — | 0.0891 |
| 24 | 1.2040 | 0.2853 | 0.2612 | 0.1791 | — | — | 0.0672 |
| 30 | 1.2010 | 0.2265 | 0.2095 | 0.1494 | — | — | 0.0594 |
| 36 | 1.2000 | 0.1930 | 0.1798 | 0.1318 | — | — | 0.0558 |
| 42 | 1.2000 | 0.1714 | 0.1605 | 0.1201 | — | — | 0.0540 |
| 48 | 1.2000 | 0.1563 | 0.1469 | 0.1117 | — | — | 0.0529 |
| **烘干结束时间 51.1511 h** | 1.2000 |  |  |  |  |  |  |
```

### `figures/TABLE_7.md` (460 字节)

```markdown
**表 7** 四级模型阶梯在 t = 3 h 的体积平均含水率对比（每级均为独立真实求解，非近似换算）

| 模型层级 | 体积平均含水率 / (kg/kg) | 相对基准偏差 / % |
|---|---|---|
| L0 集中参数（Bi=O(1)，先验失效） | 1.1007 | -20.39 |
| L1 常物性（冻结在初值） | 1.4986 | +8.39 |
| L2 单向耦合（切断 T→C 反馈） | 1.5272 | +10.46 |
| L3 全耦合（本文基准） | 1.3825 | +0.00 |
```

### `figures/TABLE_8.md` (445 字节)

```markdown
**表 8** 三种终止判据口径对照（误读为体积平均将低估工期 37.27%，即 21.4752 h）

| 终止判据 | 烘干时长 / h | 烘干时长 / d | 相对题面判据偏差 / % |
|---|---|---|---|
| 表面含水率下穿（最松） | 12.5467 | 0.5228 | -78.23 |
| 体积平均含水率下穿（误读“各处”） | 36.1499 | 1.5062 | -37.27 |
| 全域最大含水率下穿（题面判据） | 57.6251 | 2.4010 | +0.00 |
```

### `figures/TABLE_9.md` (1007 字节)

```markdown
**表 9** 烘干时长的单因子敏感性排序与全局秩相关（基准 57.6251 h；弹性符号全部与机理一致；LHS n = 200 的秩相关首因子与单因子排序首位一致）

| 因子 | 扰动幅度 | 下界 t_end / h | 上界 t_end / h | 半极差 / h | 弹性 | Spearman |
|---|---|---|---|---|---|---|
| Arrhenius 活化温度 3850 K | ±5% | 35.0608 | 99.7772 | 32.3582 | +11.2306 | +0.8681 |
| 水分抑制常数 b | ±10% | 45.6516 | 73.7182 | 14.0333 | +2.4353 | +0.4118 |
| 扩散前因子 D0 | ±20% | 70.4561 | 49.1559 | 10.6501 | -0.9241 | -0.2079 |
| 对流传质系数 h_m | ±30% | 60.5794 | 56.2364 | 2.1715 | -0.1256 | -0.0183 |
| 平台热风温度 Ta | ±1 °C | 59.5012 | 55.8312 | 1.8350 | -0.0318 | -0.0429 |
| 初始含水率 C0 | ±5% | 57.3810 | 57.8565 | 0.2378 | +0.0825 | +0.0872 |
| 平台空气含湿量 Ca | ±20% | 57.5960 | 57.8068 | 0.1054 | +0.0091 | +0.0398 |
| 对流换热系数 h | ±30% | 57.6589 | 57.6071 | 0.0259 | -0.0015 | -0.0281 |
```

---

## JSON 真实数据完整清单

### `all_results.json`（692 条）

| 数据路径 | 数值 |
|---|---|
| `competition` | `cumcm` |
| `problem_id` | `A` |
| `title` | `药材的烘干问题` |
| `generated_by` | `code/main.py` |
| `seed` | 20260910 |
| `n_checks` | 64 |
| `n_checks_passed` | 64 |
| `all_checks_passed` | True |
| `timing_s.data_check` | 0.0370021 |
| `timing_s.problem1` | 2.33847 |
| `timing_s.problem2` | 13.856 |
| `timing_s.problem3` | 24.8499 |
| `timing_s.problem4` | 32.7964 |
| `timing_s.sensitivity` | 4.48297 |
| `wall_time_s` | 80.0971 |
| `headline.q1_T_center_1800s_C` | 33.5753 |
| `headline.q1_T_surface_1800s_C` | 36.7856 |
| `headline.q1_C_center_1800s` | 2.54999 |
| `headline.q1_C_surface_1800s` | 1.51023 |
| `headline.q1_semi_analytic_max_dev_C` | 6.164e-05 |
| `headline.q1_Bi_T` | 1.38889 |
| `headline.q1_Bi_m` | 3.2404 |
| `headline.q2_T_center_10800s_C` | 49.8495 |
| `headline.q2_T_surface_10800s_C` | 49.9664 |
| `headline.q2_C_center_10800s` | 1.76619 |
| `headline.q2_C_surface_10800s` | 1.00813 |
| `headline.q2_volavg_C_10800s` | 1.38255 |
| `headline.q3_t_end_h` | 57.6251 |
| `headline.q3_t_end_d` | 2.40105 |
| `headline.q4_t_end_h` | 51.1511 |
| `headline.q4_t_end_d` | 2.1313 |
| `headline.q4_R_at_t_end_cm` | 1.2 |
| `headline.q4_water_removed_pct` | 95.3564 |
| `headline.sens_baseline_t_end_h` | 57.6251 |
| `headline.sens_top_factor` | `act_scale` |
| `headline.sens_lhs_p05_p50_p95_h[0]` | 35.8451 |
| `headline.sens_lhs_p05_p50_p95_h[1]` | 57.5875 |
| `headline.sens_lhs_p05_p50_p95_h[2]` | 108.744 |
| `model_ladder.times_s[0]` | 1800 |
| `model_ladder.times_s[1]` | 3600 |
| `model_ladder.times_s[2]` | 5400 |
| `model_ladder.times_s[5]` | 10800 |
| `model_ladder.times_s[...]` | `<2 项省略>` |
| `model_ladder.paths.L1_const_prop.C_center_end` | 2.16423 |
| `model_ladder.paths.L1_const_prop.C_surface_end` | 0.865499 |
| `model_ladder.paths.L1_const_prop.T_center_end` | 49.7351 |
| `model_ladder.paths.L1_const_prop.volavg_C_end` | 1.49855 |
| `model_ladder.paths.L1_const_prop.C_center_series[0]` | 2.54997 |
| `model_ladder.paths.L1_const_prop.C_center_series[1]` | 2.54248 |
| `model_ladder.paths.L1_const_prop.C_center_series[2]` | 2.499 |
| `model_ladder.paths.L1_const_prop.C_center_series[5]` | 2.16423 |
| `model_ladder.paths.L1_const_prop.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L1_const_prop.volavg_C_series[0]` | 2.28543 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[1]` | 2.08219 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[2]` | 1.90951 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[5]` | 1.49855 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L2_oneway.C_center_end` | 2.19331 |
| `model_ladder.paths.L2_oneway.C_surface_end` | 0.816956 |
| `model_ladder.paths.L2_oneway.T_center_end` | 49.8306 |
| `model_ladder.paths.L2_oneway.volavg_C_end` | 1.52718 |
| `model_ladder.paths.L2_oneway.C_center_series[0]` | 2.54997 |
| `model_ladder.paths.L2_oneway.C_center_series[1]` | 2.54273 |
| `model_ladder.paths.L2_oneway.C_center_series[2]` | 2.50142 |
| `model_ladder.paths.L2_oneway.C_center_series[5]` | 2.19331 |
| `model_ladder.paths.L2_oneway.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L2_oneway.volavg_C_series[0]` | 2.28697 |
| `model_ladder.paths.L2_oneway.volavg_C_series[1]` | 2.08725 |
| `model_ladder.paths.L2_oneway.volavg_C_series[2]` | 1.91935 |
| `model_ladder.paths.L2_oneway.volavg_C_series[5]` | 1.52718 |
| `model_ladder.paths.L2_oneway.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L3_full.C_center_end` | 1.76619 |
| `model_ladder.paths.L3_full.C_surface_end` | 1.00813 |
| `model_ladder.paths.L3_full.T_center_end` | 49.8495 |
| `model_ladder.paths.L3_full.volavg_C_end` | 1.38255 |
| `model_ladder.paths.L3_full.C_center_series[0]` | 2.54993 |
| `model_ladder.paths.L3_full.C_center_series[1]` | 2.52571 |
| `model_ladder.paths.L3_full.C_center_series[2]` | 2.38604 |
| `model_ladder.paths.L3_full.C_center_series[5]` | 1.76619 |
| `model_ladder.paths.L3_full.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L3_full.volavg_C_series[0]` | 2.28267 |
| `model_ladder.paths.L3_full.volavg_C_series[1]` | 2.06499 |
| `model_ladder.paths.L3_full.volavg_C_series[2]` | 1.86877 |
| `model_ladder.paths.L3_full.volavg_C_series[5]` | 1.38255 |
| `model_ladder.paths.L3_full.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L0_lumped.C_end` | 1.1007 |
| `model_ladder.paths.L0_lumped.T_end` | 49.9978 |
| `model_ladder.paths.L0_lumped.note` | `Bi_T, Bi_m 均为 O(1)，集中参数假设不成立，此路径仅作错误极限对照` |
| `model_ladder.paths.L0_lumped.C_series[0]` | 2.21158 |
| `model_ladder.paths.L0_lumped.C_series[1]` | 1.92016 |
| `model_ladder.paths.L0_lumped.C_series[2]` | 1.66875 |
| `model_ladder.paths.L0_lumped.C_series[5]` | 1.1007 |
| `model_ladder.paths.L0_lumped.C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L0_lumped.T_series[0]` | 34.6992 |
| `model_ladder.paths.L0_lumped.T_series[1]` | 43.1844 |
| `model_ladder.paths.L0_lumped.T_series[2]` | 47.6086 |
| `model_ladder.paths.L0_lumped.T_series[5]` | 49.9978 |
| `model_ladder.paths.L0_lumped.T_series[...]` | `<2 项省略>` |
| `model_ladder.baseline_volavg_C_end` | 1.38255 |
| `criterion_comparison.max.t_end_s` | 2.075e+05 |
| `criterion_comparison.max.t_end_h` | 57.6251 |
| `criterion_comparison.max.nfev` | 21261 |
| `criterion_comparison.volavg.t_end_s` | 1.301e+05 |
| `criterion_comparison.volavg.t_end_h` | 36.1499 |
| `criterion_comparison.volavg.nfev` | 18628 |
| `criterion_comparison.surface.t_end_s` | 4.517e+04 |
| `criterion_comparison.surface.t_end_h` | 12.5467 |
| `criterion_comparison.surface.nfev` | 15221 |
| `q4_attribution.q3_baseline.props` | `appendix_3` |
| `q4_attribution.q3_baseline.shrink` | False |
| `q4_attribution.q3_baseline.t_end_s` | 2.075e+05 |
| `q4_attribution.q3_baseline.t_end_h` | 57.6251 |
| `q4_attribution.q3_baseline.nfev` | 21261 |
| `q4_attribution.app4_noshrink.props` | `appendix_4` |
| `q4_attribution.app4_noshrink.shrink` | False |
| `q4_attribution.app4_noshrink.t_end_s` | 4.682e+05 |
| `q4_attribution.app4_noshrink.t_end_h` | 130.058 |
| `q4_attribution.app4_noshrink.nfev` | 31717 |
| `q4_attribution.app3_shrink.props` | `appendix_3` |
| `q4_attribution.app3_shrink.shrink` | True |
| `q4_attribution.app3_shrink.t_end_s` | 9.1e+04 |
| `q4_attribution.app3_shrink.t_end_h` | 25.2786 |
| `q4_attribution.app3_shrink.nfev` | 17349 |
| `q4_attribution.app4_shrink.props` | `appendix_4` |
| `q4_attribution.app4_shrink.shrink` | True |
| `q4_attribution.app4_shrink.t_end_s` | 1.841e+05 |
| `q4_attribution.app4_shrink.t_end_h` | 51.1511 |
| `q4_attribution.app4_shrink.nfev` | 20764 |
| `cross_problem_ledger.n_items` | 9 |
| `cross_problem_ledger.items[0].id` | `XP1` |
| `cross_problem_ledger.items[0].quantity` | `问题一药材温度上界` |
| `cross_problem_ledger.items[0].unit` | `°C` |
| `cross_problem_ledger.items[0].bound.op` | `<=` |
| `cross_problem_ledger.items[0].bound.value` | 41.513 |
| `cross_problem_ledger.items[0].observed` | 36.7856 |
| `cross_problem_ledger.items[0].reason` | `1800 s 内热风由 28 °C 线性升至 41.5130 °C，药材温度不得超过同期热风温度` |
| `cross_problem_ledger.items[0].satisfied` | True |
| `cross_problem_ledger.items[1].id` | `XP2` |
| `cross_problem_ledger.items[1].quantity` | `问题一药材温度下界` |
| `cross_problem_ledger.items[1].unit` | `°C` |
| `cross_problem_ledger.items[1].bound.op` | `>=` |
| `cross_problem_ledger.items[1].bound.value` | 28 |
| `cross_problem_ledger.items[1].observed` | 28 |
| `cross_problem_ledger.items[1].reason` | `热风全程高于初温 28 °C，故药材只被加热` |
| `cross_problem_ledger.items[1].satisfied` | True |
| `cross_problem_ledger.items[2].id` | `XP3` |
| `cross_problem_ledger.items[2].quantity` | `问题一含水率上界` |
| `cross_problem_ledger.items[2].unit` | `kg/kg` |
| `cross_problem_ledger.items[2].bound.op` | `<=` |
| `cross_problem_ledger.items[2].bound.value` | 2.55 |
| `cross_problem_ledger.items[2].observed` | 2.55 |
| `cross_problem_ledger.items[2].reason` | `干燥过程只失水，任意点含水率不超过初值 C0` |
| `cross_problem_ledger.items[2].satisfied` | True |
| `cross_problem_ledger.items[8].id` | `XP9` |
| `cross_problem_ledger.items[8].quantity` | `问题三、四烘干时长量级` |
| `cross_problem_ledger.items[8].unit` | `d` |
| `cross_problem_ledger.items[8].bound.op` | `in` |
| `cross_problem_ledger.items[8].bound.value[0]` | 0.2 |
| `cross_problem_ledger.items[8].bound.value[1]` | 30 |
| `cross_problem_ledger.items[8].observed[0]` | 2.40105 |
| `cross_problem_ledger.items[8].observed[1]` | 2.1313 |
| `cross_problem_ledger.items[8].reason` | `题面「一般持续 2-3 天」是独立量级参照，允许同量级偏离，不作标定目标` |
| `cross_problem_ledger.items[8].satisfied` | True |
| `cross_problem_ledger.items[...]` | `<5 项省略>` |
| `cross_problem_ledger.all_satisfied` | True |
| `cross_problem_ledger.cross_problem_check_module` | `_utils/cross_problem_check.py` |
| `cross_problem_ledger.module_available` | False |
| `cross_problem_ledger.note` | `SKILL 第 7 步引用的 _utils/cross_problem_check.py 在本运行时不存在；按...` |
| `checks.problem1.C01.name` | `均匀场零通量` |
| `checks.problem1.C01.measured` | 0 |
| `checks.problem1.C01.tol` | 1e-08 |
| `checks.problem1.C01.passed` | True |
| `checks.problem1.C02.name` | `柱面通量正比于 r` |
| `checks.problem1.C02.measured` | 1.99e-13 |
| `checks.problem1.C02.tol` | 1e-08 |
| `checks.problem1.C02.passed` | True |
| `checks.problem1.C02.note` | `线性场下界面通量密度恒定，面积权 A_face=eta_{i+1/2} 使总流量正比于 r` |
| `checks.problem1.C03.name` | `双场独立` |
| `checks.problem1.C03.len_y` | 240 |
| `checks.problem1.C03.expect_len` | 240 |
| `checks.problem1.C03.dT_absmax` | 0.0309075 |
| `checks.problem1.C03.dC_absmax` | 0.0120326 |
| `checks.problem1.C03.slices_alias` | False |
| `checks.problem1.C03.passed` | True |
| `checks.problem1.C05.name` | `Robin 闭合一致` |
| `checks.problem1.C05.measured_C` | 1.653e-15 |
| `checks.problem1.C05.measured_T` | 2.811e-12 |
| `checks.problem1.C05.tol` | 1e-06 |
| `checks.problem1.C05.passed` | True |
| `checks.problem1.C10.name` | `问题一单向解耦` |
| `checks.problem1.C10.measured` | 0 |
| `checks.problem1.C10.tol` | 1e-14 |
| `checks.problem1.C10.passed` | True |
| `checks.problem1.C11.name` | `附录绑定` |
| `checks.problem1.C11.props_appendix` | `appendix_2` |
| `checks.problem1.C11.passed` | True |
| `checks.problem1.C14.name` | `低含水率下界保护` |
| `checks.problem1.C14.C_floor` | 1e-06 |
| `checks.problem1.C14.D_at_1e-18` | 0 |
| `checks.problem1.C14.finite` | True |
| `checks.problem1.C14.passed` | True |
| `checks.problem1.C09.name` | `半解析解对照 147 点` |
| `checks.problem1.C09.measured_max_abs_C` | 6.164e-05 |
| `checks.problem1.C09.tol` | 0.001 |
| `checks.problem1.C09.n_points` | 147 |
| `checks.problem1.C09.n_modes` | 200 |
| `checks.problem1.C09.passed` | True |
| `checks.problem1.V3.2.name` | `网格收敛阶梯（五档）` |
| `checks.problem1.V3.2.dT_center_seq[0]` | 0.0007018 |
| `checks.problem1.V3.2.dT_center_seq[1]` | 0.0001767 |
| `checks.problem1.V3.2.dT_center_seq[2]` | 4.225e-05 |
| `checks.problem1.V3.2.dT_center_seq[3]` | 1.337e-05 |
| `checks.problem1.V3.2.finest_pair_dT` | 1.337e-05 |
| `checks.problem1.V3.2.tol` | 0.0001 |
| `checks.problem1.V3.2.monotone_decreasing` | True |
| `checks.problem1.V3.2.passed` | True |
| `checks.problem1.C04.name` | `表面值网格无关性` |
| `checks.problem1.C04.measured` | 8.46e-08 |
| `checks.problem1.C04.tol` | 0.001 |
| `checks.problem1.C04.dC_surface_seq[0]` | 0.0002295 |
| `checks.problem1.C04.dC_surface_seq[1]` | 1.208e-05 |
| `checks.problem1.C04.dC_surface_seq[2]` | 3.168e-07 |
| `checks.problem1.C04.dC_surface_seq[3]` | 8.46e-08 |
| `checks.problem1.C04.passed` | True |
| `checks.problem1.C06.name` | `剖面单调（中心最湿/最冷）` |
| `checks.problem1.C06.C_worst_increase` | 8.882e-16 |
| `checks.problem1.C06.T_worst_decrease` | 7.105e-15 |
| `checks.problem1.C06.tol` | 1e-10 |
| `checks.problem1.C06.passed` | True |
| `checks.problem1.C07.name` | `全域最大含水率在中心` |
| `checks.problem1.C07.all_at_center` | True |
| `checks.problem1.C07.n_times_checked` | 1800 |
| `checks.problem1.C07.passed` | True |
| `checks.problem1.C13.name` | `干燥方向性` |
| `checks.problem1.C13.max_rise_of_Cmax` | 0 |
| `checks.problem1.C13.max_rise_of_volavg` | -0.0001182 |
| `checks.problem1.C13.tol` | 1e-12 |
| `checks.problem1.C13.passed` | True |
| `checks.problem1.V2.4.name` | `温度落在驱动包络内` |
| `checks.problem1.V2.4.T_min` | 28 |
| `checks.problem1.V2.4.T_max` | 36.7856 |
| `checks.problem1.V2.4.envelope[0]` | 28 |
| `checks.problem1.V2.4.envelope[1]` | 41.513 |
| `checks.problem1.V2.4.passed` | True |
| `checks.problem1.time_tol_layer.name` | `时间离散误差分层（收紧一档）` |
| `checks.problem1.time_tol_layer.measured_tighten_1e-10` | 4.928e-06 |
| `checks.problem1.time_tol_layer.tol` | 0.0001 |
| `checks.problem1.time_tol_layer.passed` | True |
| `checks.problem1.time_tol_layer.diagnostic_loosen_1e-6` | 0.0003328 |
| `checks.problem1.time_tol_layer.note` | `§4.4 判据为收紧容差后变化 <1e-4；放松到 1e-6 的偏差 3.328e-04 °C 一并记录，V3...` |
| `checks.problem1.C16.name` | `写盘-读回往返一致` |
| `checks.problem1.C16.measured` | 0 |
| `checks.problem1.C16.tol` | 0 |
| `checks.problem1.C16.per_sheet.温度.shape[0]` | 1800 |
| `checks.problem1.C16.per_sheet.温度.shape[1]` | 21 |
| `checks.problem1.C16.per_sheet.温度.roundtrip_max_abs_diff` | 0 |
| `checks.problem1.C16.per_sheet.温度.blank_cells` | 0 |
| `checks.problem1.C16.per_sheet.水分浓度.shape[0]` | 1800 |
| `checks.problem1.C16.per_sheet.水分浓度.shape[1]` | 21 |
| `checks.problem1.C16.per_sheet.水分浓度.roundtrip_max_abs_diff` | 0 |
| `checks.problem1.C16.per_sheet.水分浓度.blank_cells` | 0 |
| `checks.problem1.C16.passed` | True |
| `checks.problem2.C11.name` | `附录绑定` |
| `checks.problem2.C11.props_appendix` | `appendix_3` |
| `checks.problem2.C11.passed` | True |
| `checks.problem2.C12.name` | `五个物性偏导非零` |
| `checks.problem2.C12.partials.d_rho_dC` | 16.32 |
| `checks.problem2.C12.partials.d_cp_dC` | 26.7205 |
| `checks.problem2.C12.partials.d_lam_dC` | 0.003711 |
| `checks.problem2.C12.partials.d_D_dC` | 4.761e-11 |
| `checks.problem2.C12.partials.d_D_dT` | 1.31e-09 |
| `checks.problem2.C12.tol` | 1e-12 |
| `checks.problem2.C12.inert_partials_expected_zero.d_rho_dT` | 0 |
| `checks.problem2.C12.inert_partials_expected_zero.d_cp_dT` | 0 |
| `checks.problem2.C12.inert_partials_expected_zero.d_lam_dT` | 0 |
| `checks.problem2.C12.passed` | True |
| `checks.problem2.C08.name` | `附件 1 复现与衔接连续` |
| `checks.problem2.C08.sample_rel_err_Ta` | 0 |
| `checks.problem2.C08.sample_rel_err_Ca` | 0 |
| `checks.problem2.C08.tol_sample` | 1e-09 |
| `checks.problem2.C08.join_jump_Ta_C` | 5.35e-12 |
| `checks.problem2.C08.join_jump_Ca` | 1.478e-15 |
| `checks.problem2.C08.tol_join` | 1e-06 |
| `checks.problem2.C08.passed` | True |
| `checks.problem2.C14.name` | `低含水率下界保护` |
| `checks.problem2.C14.C_floor` | 1e-06 |
| `checks.problem2.C14.D_at_1e-18` | 0 |
| `checks.problem2.C14.passed` | True |
| `checks.problem2.C_kelvin.name` | `Arrhenius 用开尔文` |
| `checks.problem2.C_kelvin.measured_rel` | 1.86e-16 |
| `checks.problem2.C_kelvin.tol` | 1e-12 |
| `checks.problem2.C_kelvin.D_ratio_50_over_28` | 2.38776 |
| `checks.problem2.C_kelvin.passed` | True |
| `checks.problem2.C_no_plateau.name` | `问题二未进入外推段` |
| `checks.problem2.C_no_plateau.t_end_s` | 10800 |
| `checks.problem2.C_no_plateau.T_obs_s` | 1.44e+04 |
| `checks.problem2.C_no_plateau.passed` | True |
| `checks.problem2.C06.name` | `剖面单调（中心最湿；纯升温段中心最冷）` |
| `checks.problem2.C06.C_worst_increase` | 8.882e-16 |
| `checks.problem2.C06.tol_C` | 1e-10 |
| `checks.problem2.C06.T_inversion_rising_window` | 1.066e-14 |
| `checks.problem2.C06.tol_T_rising` | 1e-10 |
| `checks.problem2.C06.t_first_driver_dip_s` | 2940 |
| `checks.problem2.C06.n_times_rising` | 2940 |
| `checks.problem2.C06.T_inversion_after_first_dip` | 0.0007703 |
| `checks.problem2.C06.driver_worst_down_step_C` | 0.45 |
| `checks.problem2.C06.inversion_over_driver_step` | 0.001712 |
| `checks.problem2.C06.tol_ratio` | 0.05 |
| `checks.problem2.C06.driver_negative_increments` | 95 |
| `checks.problem2.C06.note` | `附件 1 平台段 Ta 有 95 次负增量（最大回落 0.45 °C）；热风回落时表面先冷于内部，该反转幅度仅...` |
| `checks.problem2.C06.passed` | True |
| `checks.problem2.C07.name` | `全域最大含水率在中心` |
| `checks.problem2.C07.max_minus_center` | 4.441e-16 |
| `checks.problem2.C07.tol` | 1e-12 |
| `checks.problem2.C07.n_times_checked` | 10800 |
| `checks.problem2.C07.n_times_strict_argmax_at_center` | 10794 |
| `checks.problem2.C07.note` | `早期中心与邻近若干格心在 1e-16 量级并列，故用 max-center 差值判定` |
| `checks.problem2.C07.passed` | True |
| `checks.problem2.C13.name` | `干燥方向性` |
| `checks.problem2.C13.max_rise_of_Cmax` | 0 |
| `checks.problem2.C13.max_rise_of_volavg` | -7.667e-05 |
| `checks.problem2.C13.tol` | 1e-12 |
| `checks.problem2.C13.passed` | True |
| `checks.problem2.V2.4.name` | `温度落在驱动包络内` |
| `checks.problem2.V2.4.T_min` | 28 |
| `checks.problem2.V2.4.T_max` | 49.9664 |
| `checks.problem2.V2.4.envelope[0]` | 28 |
| `checks.problem2.V2.4.envelope[1]` | 50.246 |
| `checks.problem2.V2.4.passed` | True |
| `checks.problem2.V3.2.name` | `网格收敛阶梯（四档）` |
| `checks.problem2.V3.2.dC_center_seq[0]` | 0.0001052 |
| `checks.problem2.V3.2.dC_center_seq[1]` | 2.632e-05 |
| `checks.problem2.V3.2.dC_center_seq[2]` | 6.56e-06 |
| `checks.problem2.V3.2.finest_pair` | 6.56e-06 |
| `checks.problem2.V3.2.tol` | 0.001 |
| `checks.problem2.V3.2.passed` | True |
| `checks.problem2.C04.name` | `表面值网格无关性` |
| `checks.problem2.C04.measured` | 2.968e-06 |
| `checks.problem2.C04.tol` | 0.001 |
| `checks.problem2.C04.dC_surface_seq[0]` | 4.738e-05 |
| `checks.problem2.C04.dC_surface_seq[1]` | 1.18e-05 |
| `checks.problem2.C04.dC_surface_seq[2]` | 2.968e-06 |
| `checks.problem2.C04.passed` | True |
| `checks.problem2.V3.6.name` | `四级模型阶梯真实独立运行` |
| `checks.problem2.V3.6.volavg_C_end_by_path.L0_lumped` | 1.1007 |
| `checks.problem2.V3.6.volavg_C_end_by_path.L1_const_prop` | 1.49855 |
| `checks.problem2.V3.6.volavg_C_end_by_path.L2_oneway` | 1.52718 |
| `checks.problem2.V3.6.volavg_C_end_by_path.L3_full` | 1.38255 |
| `checks.problem2.V3.6.min_pairwise_gap` | 0.0286287 |
| `checks.problem2.V3.6.tol` | 1e-06 |
| `checks.problem2.V3.6.passed` | True |
| `checks.problem2.C15.name` | `模型对比两两可分辨` |
| `checks.problem2.C15.measured_min_gap` | 0.0286287 |
| `checks.problem2.C15.tol` | 1e-06 |
| `checks.problem2.C15.n_pairs` | 6 |
| `checks.problem2.C15.passed` | True |
| `checks.problem2.C16.name` | `写盘-读回往返一致` |
| `checks.problem2.C16.measured` | 0 |
| `checks.problem2.C16.tol` | 0 |
| `checks.problem2.C16.per_sheet.温度.shape[0]` | 10800 |
| `checks.problem2.C16.per_sheet.温度.shape[1]` | 21 |
| `checks.problem2.C16.per_sheet.温度.roundtrip_max_abs_diff` | 0 |
| `checks.problem2.C16.per_sheet.温度.blank_cells` | 0 |
| `checks.problem2.C16.per_sheet.水分浓度.shape[0]` | 10800 |
| `checks.problem2.C16.per_sheet.水分浓度.shape[1]` | 21 |
| `checks.problem2.C16.per_sheet.水分浓度.roundtrip_max_abs_diff` | 0 |
| `checks.problem2.C16.per_sheet.水分浓度.blank_cells` | 0 |
| `checks.problem2.C16.passed` | True |
| `checks.problem3.C11.name` | `附录绑定（与问题二同源）` |
| `checks.problem3.C11.props_appendix` | `appendix_3` |
| `checks.problem3.C11.passed` | True |
| `checks.problem3.C19.name` | `首次下穿（密扫无更早穿越）` |
| `checks.problem3.C19.measured_endpoint_gap` | 0 |
| `checks.problem3.C19.tol` | 1e-05 |
| `checks.problem3.C19.n_scan_points` | 20000 |
| `checks.problem3.C19.n_points_below_thr` | 0 |
| `checks.problem3.C19.min_Cmax_before_t_end` | 0.15 |
| `checks.problem3.C19.passed` | True |
| `checks.problem3.C07.name` | `事件时刻最大值在中心` |
| `checks.problem3.C07.argmax_cell` | 0 |
| `checks.problem3.C07.C_center` | 0.15 |
| `checks.problem3.C07.C_surface_cell` | 0.0644202 |
| `checks.problem3.C07.passed` | True |
| `checks.problem3.C17.name` | `判据口径序关系` |
| `checks.problem3.C17.t_surface_h` | 12.5467 |
| `checks.problem3.C17.t_volavg_h` | 36.1499 |
| `checks.problem3.C17.t_max_h` | 57.6251 |
| `checks.problem3.C17.ordered` | True |
| `checks.problem3.C17.gap_max_minus_volavg_s` | 7.731e+04 |
| `checks.problem3.C17.tol_gap` | 60 |
| `checks.problem3.C17.underestimate_by_volavg_h` | 21.4752 |
| `checks.problem3.C17.underestimate_pct` | 37.267 |
| `checks.problem3.C17.passed` | True |
| `checks.problem3.V3.3.name` | `时间容差对照（t_end）` |
| `checks.problem3.V3.3.measured_dt_end_s` | 0.0284772 |
| `checks.problem3.V3.3.tol` | 60 |
| `checks.problem3.V3.3.t_end_rtol_1e_6_s` | 2.075e+05 |
| `checks.problem3.V3.3.t_end_rtol_1e_8_s` | 2.075e+05 |
| `checks.problem3.V3.3.passed` | True |
| `checks.problem3.V3.2.name` | `网格收敛阶梯（t_end，五档）` |
| `checks.problem3.V3.2.dt_end_seq_s[0]` | 1292 |
| `checks.problem3.V3.2.dt_end_seq_s[1]` | 572.164 |
| `checks.problem3.V3.2.dt_end_seq_s[2]` | 230.22 |
| `checks.problem3.V3.2.dt_end_seq_s[3]` | 84.048 |
| `checks.problem3.V3.2.dt_end_seq_rel[0]` | 0.006211 |
| `checks.problem3.V3.2.dt_end_seq_rel[1]` | 0.002758 |
| `checks.problem3.V3.2.dt_end_seq_rel[2]` | 0.001111 |
| `checks.problem3.V3.2.dt_end_seq_rel[3]` | 0.0004058 |
| `checks.problem3.V3.2.finest_pair_s` | 84.048 |
| `checks.problem3.V3.2.finest_pair_rel` | 0.0004058 |
| `checks.problem3.V3.2.tol_rel` | 0.002 |
| `checks.problem3.V3.2.observed_order` | 1.45373 |
| `checks.problem3.V3.2.richardson_limit_s` | 2.071e+05 |
| `checks.problem3.V3.2.richardson_limit_h` | 57.5244 |
| `checks.problem3.V3.2.baseline_minus_richardson_h` | 0.100721 |
| `checks.problem3.V3.2.monotone_decreasing` | True |
| `checks.problem3.V3.2.note` | `t_end 以约一阶精度收敛（表面重构与阈值定位均为一阶）；最细两档相对变化 0.041%，故用相对判据 0.2%` |
| `checks.problem3.V3.2.passed` | True |
| `checks.problem3.XA2.name` | `问题三与问题二逐格恒等（t<=10800 s）` |
| `checks.problem3.XA2.measured_max_abs_diff` | 0 |
| `checks.problem3.XA2.tol` | 1e-09 |
| `checks.problem3.XA2.n_times` | 6 |
| `checks.problem3.XA2.n_cells` | 240 |
| `checks.problem3.XA2.long_run_max_abs_dT_C` | 4.385e-06 |
| `checks.problem3.XA2.long_run_max_abs_dC` | 3.267e-08 |
| `checks.problem3.XA2.note` | `同一右端、同一 max_step 时逐位相同；长时程运行用 max_step=60 s（M6），其与问题二的差...` |
| `checks.problem3.XA2.passed` | True |
| `checks.problem3.V3.12.name` | `与题面 2-3 天量级对照` |
| `checks.problem3.V3.12.measured_days` | 2.40105 |
| `checks.problem3.V3.12.reference_range_days[0]` | 2 |
| `checks.problem3.V3.12.reference_range_days[1]` | 3 |
| `checks.problem3.V3.12.inside_range` | True |
| `checks.problem3.V3.12.same_order_of_magnitude` | True |
| `checks.problem3.V3.12.note` | `题面区间是独立于模型的量级参照，不是标定目标；未对任何物性做反向调参` |
| `checks.problem3.V3.12.passed` | True |
| `checks.problem3.C16.name` | `写盘-读回往返一致` |
| `checks.problem3.C16.measured` | 0 |
| `checks.problem3.C16.tol` | 0 |
| `checks.problem3.C16.per_sheet.Sheet1.shape[0]` | 3457 |
| `checks.problem3.C16.per_sheet.Sheet1.shape[1]` | 21 |
| `checks.problem3.C16.per_sheet.Sheet1.roundtrip_max_abs_diff` | 0 |
| `checks.problem3.C16.per_sheet.Sheet1.blank_cells` | 0 |
| `checks.problem3.C16.passed` | True |
| `checks.problem3.C13.name` | `干燥方向性（全程）` |
| `checks.problem3.C13.max_rise_of_Cmax` | 0 |
| `checks.problem3.C13.max_rise_of_volavg` | -1.274e-05 |
| `checks.problem3.C13.tol` | 1e-12 |
| `checks.problem3.C13.passed` | True |
| `checks.problem3.V2.4.name` | `温度落在驱动包络内` |
| `checks.problem3.V2.4.T_min` | 28 |
| `checks.problem3.V2.4.T_max` | 50.0399 |
| `checks.problem3.V2.4.envelope[0]` | 28 |
| `checks.problem3.V2.4.envelope[1]` | 50.246 |
| `checks.problem3.V2.4.passed` | True |
| `checks.problem4.C11.name` | `附录绑定（附录 4 物性 + 附件 2 半径）` |
| `checks.problem4.C11.props_appendix` | `appendix_4` |
| `checks.problem4.C11.shrink_mode` | `radial` |
| `checks.problem4.C11.passed` | True |
| `checks.problem4.C18.name` | `半径轨迹单调不增且复现附件 2` |
| `checks.problem4.C18.max_dR_over_scan_cm` | 0 |
| `checks.problem4.C18.max_dRdt_cm_per_s` | 0 |
| `checks.problem4.C18.min_dRdt_cm_per_s` | -8.359e-05 |
| `checks.problem4.C18.n_scan_points` | 10000 |
| `checks.problem4.C18.sample_repro_max_abs_cm` | 2.22e-16 |
| `checks.problem4.C18.tol_repro_cm` | 1e-12 |
| `checks.problem4.C18.R0_cm` | 2 |
| `checks.problem4.C18.R_end_cm` | 1.198 |
| `checks.problem4.C18.total_shrink_pct` | 40.1 |
| `checks.problem4.C18.passed` | True |
| `checks.problem4.C20.name` | `绝干骨架水量守恒（正向 + 三个反向变体）` |
| `checks.problem4.C20.forward_rel_drift` | 3.483e-16 |
| `checks.problem4.C20.tol_forward` | 1e-08 |
| `checks.problem4.C20.mass_kg_per_m_rel_drift_with_bookkeeping` | 3.331e-16 |
| `checks.problem4.C20.reverse_rel_drift.reverse_B_spurious_advection` | 0.109279 |
| `checks.problem4.C20.reverse_rel_drift.reverse_C_nonconservative` | 0.007219 |
| `checks.problem4.C20.reverse_rel_drift.reverse_A_drop_rho_d` | 0.610624 |
| `checks.problem4.C20.tol_reverse_min` | 0.0001 |
| `checks.problem4.C20.min_reverse_drift` | 0.007219 |
| `checks.problem4.C20.t_test_s` | 4.32e+04 |
| `checks.problem4.C20.R_cm_span[0]` | 2 |
| `checks.problem4.C20.R_cm_span[1]` | 1.248 |
| `checks.problem4.C20.rho_d_span[0]` | 278.732 |
| `checks.problem4.C20.rho_d_span[1]` | 715.844 |
| `checks.problem4.C20.note` | `反向 A 丢弃 rho_d(t) 记账、B 按 §7.5 再加 R*Rdot 对流通量、C 用非守恒 Lapl...` |
| `checks.problem4.C20.passed` | True |
| `checks.problem4.C22.name` | `t=0 收缩域退化为固定域` |
| `checks.problem4.C22.measured_max_abs_diff` | 0 |
| `checks.problem4.C22.tol` | 1e-12 |
| `checks.problem4.C22.R_at_0_cm` | 2 |
| `checks.problem4.C22.dRdt_at_0_cm_per_s` | 0 |
| `checks.problem4.C22.passed` | True |
| `checks.problem4.C_direction.name` | `收缩方向性判定（径向 vs 各向同性）` |
| `checks.problem4.C_direction.rho_d0` | 278.732 |
| `checks.problem4.C_direction.rho_d_end_radial` | 776.844 |
| `checks.problem4.C_direction.rho_d_end_isotropic` | 1297 |
| `checks.problem4.C_direction.reference_rho_zero_moisture` | 760 |
| `checks.problem4.C_direction.deviation_radial_pct` | 2.21631 |
| `checks.problem4.C_direction.deviation_isotropic_pct` | 70.6449 |
| `checks.problem4.C_direction.tol_accept_pct` | 5 |
| `checks.problem4.C_direction.tol_reject_pct` | 20 |
| `checks.problem4.C_direction.selected` | `radial` |
| `checks.problem4.C_direction.note` | `径向假设下末态绝干密度 776.84 kg/m^3 与附录 4 零含水率密度 760 相差 2.22%；各向同...` |
| `checks.problem4.C_direction.passed` | True |
| `checks.problem4.C_volume_consistency.name` | `收缩量自洽性（几何 vs 密度式反推）` |
| `checks.problem4.C_volume_consistency.volume_ratio_geometric` | 0.358801 |
| `checks.problem4.C_volume_consistency.volume_ratio_from_density` | 0.414405 |
| `checks.problem4.C_volume_consistency.relative_gap` | 0.134178 |
| `checks.problem4.C_volume_consistency.tol` | 0.2 |
| `checks.problem4.C_volume_consistency.rho_d_at_C_thr` | 672.609 |
| `checks.problem4.C_volume_consistency.note` | `附件 2 的几何收缩量 0.3588 与附录 4 密度式反推的 0.4144 差 13.42%；两者同阶但不完...` |
| `checks.problem4.C_volume_consistency.passed` | True |
| `checks.problem4.C19.name` | `首次下穿（密扫无更早穿越）` |
| `checks.problem4.C19.measured_endpoint_gap` | 0 |
| `checks.problem4.C19.tol` | 1e-05 |
| `checks.problem4.C19.n_scan_points` | 20000 |
| `checks.problem4.C19.n_points_below_thr` | 0 |
| `checks.problem4.C19.min_Cmax_before_t_end` | 0.15 |
| `checks.problem4.C19.passed` | True |
| `checks.problem4.C07.name` | `事件时刻最大值在中心` |
| `checks.problem4.C07.argmax_cell` | 0 |
| `checks.problem4.C07.C_center` | 0.15 |
| `checks.problem4.C07.C_outermost_cell` | 0.0586729 |
| `checks.problem4.C07.passed` | True |
| `checks.problem4.C21.name` | `归因分解闭合与交互项量化` |
| `checks.problem4.C21.chain_closure_s` | 0 |
| `checks.problem4.C21.tol_closure_s` | 1e-06 |
| `checks.problem4.C21.delta_props_s` | 2.608e+05 |
| `checks.problem4.C21.delta_shrink_s` | -2.841e+05 |
| `checks.problem4.C21.total_s` | -2.331e+04 |
| `checks.problem4.C21.interaction_s` | -1.676e+05 |
| `checks.problem4.C21.interaction_over_total_pct` | 719.19 |
| `checks.problem4.C21.mult_ratio_props` | 2.25696 |
| `checks.problem4.C21.mult_ratio_shrink` | 0.438674 |
| `checks.problem4.C21.mult_predicted_ratio` | 0.99007 |
| `checks.problem4.C21.mult_actual_ratio` | 0.887654 |
| `checks.problem4.C21.mult_residual_pct` | 10.3443 |
| `checks.problem4.C21.n_runs` | 4 |
| `checks.problem4.C21.note` | `附录 4 换物性使 t_end 增 72.43 h，径向收缩使其减 78.91 h，两者叠加只净减 6.47 ...` |
| `checks.problem4.C21.passed` | True |
| `checks.problem4.V3.2.name` | `网格收敛阶梯（t_end，五档）` |
| `checks.problem4.V3.2.dt_end_seq_s[0]` | 294.853 |
| `checks.problem4.V3.2.dt_end_seq_s[1]` | 122.438 |
| `checks.problem4.V3.2.dt_end_seq_s[2]` | 42.9203 |
| `checks.problem4.V3.2.dt_end_seq_s[3]` | 13.0635 |
| `checks.problem4.V3.2.dt_end_seq_rel[0]` | 0.0016 |
| `checks.problem4.V3.2.dt_end_seq_rel[1]` | 0.0006649 |
| `checks.problem4.V3.2.dt_end_seq_rel[2]` | 0.0002331 |
| `checks.problem4.V3.2.dt_end_seq_rel[3]` | 7.096e-05 |
| `checks.problem4.V3.2.finest_pair_s` | 13.0635 |
| `checks.problem4.V3.2.finest_pair_rel` | 7.096e-05 |
| `checks.problem4.V3.2.tol_rel` | 0.002 |
| `checks.problem4.V3.2.observed_order` | 1.71612 |
| `checks.problem4.V3.2.richardson_limit_s` | 1.841e+05 |
| `checks.problem4.V3.2.richardson_limit_h` | 51.134 |
| `checks.problem4.V3.2.baseline_minus_richardson_h` | 0.0171387 |
| `checks.problem4.V3.2.monotone_decreasing` | True |
| `checks.problem4.V3.2.note` | `与问题三同口径：表面重构与阈值定位均为一阶，故 t_end 用相对判据 0.2%，最细两档相对变化 0.007%` |
| `checks.problem4.V3.2.passed` | True |
| `checks.problem4.V3.3.name` | `时间容差对照（t_end）` |
| `checks.problem4.V3.3.measured_dt_end_s` | 0.0497595 |
| `checks.problem4.V3.3.tol` | 60 |
| `checks.problem4.V3.3.t_end_rtol_1e_6_s` | 1.841e+05 |
| `checks.problem4.V3.3.t_end_rtol_1e_8_s` | 1.841e+05 |
| `checks.problem4.V3.3.passed` | True |
| `checks.problem4.C16.name` | `写盘-读回往返一致（含空单元格掩码）` |
| `checks.problem4.C16.measured` | 0 |
| `checks.problem4.C16.tol` | 0 |
| `checks.problem4.C16.per_sheet.Sheet1.shape[0]` | 3069 |
| `checks.problem4.C16.per_sheet.Sheet1.shape[1]` | 21 |
| `checks.problem4.C16.per_sheet.Sheet1.roundtrip_max_abs_diff` | 0 |
| `checks.problem4.C16.per_sheet.Sheet1.blank_cells` | 20122 |
| `checks.problem4.C16.n_blank_cells` | 20122 |
| `checks.problem4.C16.blank_rule` | `r > R(t) 的格为空（药材已收缩到该位置以内）` |
| `checks.problem4.C16.passed` | True |
| `checks.problem4.C20_balance.name` | `全局水量平衡闭合（h_m 非零）` |
| `checks.problem4.C20_balance.measured_rel_gap` | 9.398e-05 |
| `checks.problem4.C20_balance.tol` | 0.001 |
| `checks.problem4.C20_balance.stored_drop_kg_per_m` | 0.851701 |
| `checks.problem4.C20_balance.cumulative_flux_kg_per_m` | 0.851781 |
| `checks.problem4.C20_balance.m_w_initial_kg_per_m` | 0.893177 |
| `checks.problem4.C20_balance.m_w_final_kg_per_m` | 0.0414757 |
| `checks.problem4.C20_balance.note` | `储量按 2*pi*rho_d(t)*R(t)^2*sum(V_i C_i) 记，失水按表面对流通量在 60 s...` |
| `checks.problem4.C20_balance.passed` | True |
| `checks.problem4.C13.name` | `干燥方向性（全程）` |
| `checks.problem4.C13.max_rise_of_Cmax` | 0 |
| `checks.problem4.C13.max_rise_of_volavg` | -2.094e-05 |
| `checks.problem4.C13.tol` | 1e-12 |
| `checks.problem4.C13.passed` | True |
| `checks.problem4.V2.4.name` | `温度落在驱动包络内` |
| `checks.problem4.V2.4.T_min` | 28 |
| `checks.problem4.V2.4.T_max` | 50.05 |
| `checks.problem4.V2.4.envelope[0]` | 28 |
| `checks.problem4.V2.4.envelope[1]` | 50.246 |
| `checks.problem4.V2.4.passed` | True |
| `checks.problem4.V3.12.name` | `与题面 2-3 天量级对照` |
| `checks.problem4.V3.12.measured_days` | 2.1313 |
| `checks.problem4.V3.12.reference_range_days[0]` | 2 |
| `checks.problem4.V3.12.reference_range_days[1]` | 3 |
| `checks.problem4.V3.12.inside_range` | True |
| `checks.problem4.V3.12.note` | `量级参照，非标定目标` |
| `checks.problem4.V3.12.passed` | True |
| `checks.sensitivity.C23.name` | `敏感性逐点真实重算` |
| `checks.sensitivity.C23.n_oat_points` | 16 |
| `checks.sensitivity.C23.n_lhs_points` | 200 |
| `checks.sensitivity.C23.n_lhs_q4_points` | 200 |
| `checks.sensitivity.C23.n_surface_points` | 49 |
| `checks.sensitivity.C23.min_abs_gap_to_baseline_s` | 64.7925 |
| `checks.sensitivity.C23.tol_gap_s` | 60 |
| `checks.sensitivity.C23.lhs_min_pairwise_gap_s` | 0.978556 |
| `checks.sensitivity.C23.lhs_q4_min_pairwise_gap_s` | 3.77704 |
| `checks.sensitivity.C23.n_distinct_lhs_t_end` | 200 |
| `checks.sensitivity.C23.n_distinct_lhs_q4_t_end` | 200 |
| `checks.sensitivity.C23.total_real_solves` | 471 |
| `checks.sensitivity.C23.checkpoint_hits.oat_latent` | True |
| `checks.sensitivity.C23.checkpoint_hits.surface` | True |
| `checks.sensitivity.C23.checkpoint_hits.lhs` | True |
| `checks.sensitivity.C23.checkpoint_hits.lhs_q4` | True |
| `checks.sensitivity.C23.passed` | True |
| `checks.sensitivity.V3.9.name` | `敏感性排序一致（OAT 首因子 = 秩相关首因子）` |
| `checks.sensitivity.V3.9.oat_rank[0]` | `act_scale` |
| `checks.sensitivity.V3.9.oat_rank[1]` | `moist_scale` |
| `checks.sensitivity.V3.9.oat_rank[2]` | `d_scale` |
| `checks.sensitivity.V3.9.oat_rank[7]` | `h` |
| `checks.sensitivity.V3.9.oat_rank[...]` | `<4 项省略>` |
| `checks.sensitivity.V3.9.top_oat` | `act_scale` |
| `checks.sensitivity.V3.9.top_spearman` | `act_scale` |
| `checks.sensitivity.V3.9.spearman.h_m` | -0.018254 |
| `checks.sensitivity.V3.9.spearman.h` | -0.0281152 |
| `checks.sensitivity.V3.9.spearman.ta_plateau` | -0.0428591 |
| `checks.sensitivity.V3.9.spearman.ca_plateau` | 0.0398185 |
| `checks.sensitivity.V3.9.spearman.d_scale` | -0.207934 |
| `checks.sensitivity.V3.9.spearman.act_scale` | 0.86807 |
| `checks.sensitivity.V3.9.spearman.C0` | 0.0871567 |
| `checks.sensitivity.V3.9.spearman.moist_scale` | 0.411757 |
| `checks.sensitivity.V3.9.passed` | True |
| `checks.sensitivity.V3.10.name` | `单因子弹性符号与机理一致` |
| `checks.sensitivity.V3.10.expected.h_m` | -1 |
| `checks.sensitivity.V3.10.expected.h` | -1 |
| `checks.sensitivity.V3.10.expected.ta_plateau` | -1 |
| `checks.sensitivity.V3.10.expected.ca_plateau` | 1 |
| `checks.sensitivity.V3.10.expected.d_scale` | -1 |
| `checks.sensitivity.V3.10.expected.act_scale` | 1 |
| `checks.sensitivity.V3.10.expected.C0` | 1 |
| `checks.sensitivity.V3.10.expected.moist_scale` | 1 |
| `checks.sensitivity.V3.10.observed.h_m` | -1 |
| `checks.sensitivity.V3.10.observed.h` | -1 |
| `checks.sensitivity.V3.10.observed.ta_plateau` | -1 |
| `checks.sensitivity.V3.10.observed.ca_plateau` | 1 |
| `checks.sensitivity.V3.10.observed.d_scale` | -1 |
| `checks.sensitivity.V3.10.observed.act_scale` | 1 |
| `checks.sensitivity.V3.10.observed.C0` | 1 |
| `checks.sensitivity.V3.10.observed.moist_scale` | 1 |
| `checks.sensitivity.V3.10.note` | `h_m/h/Ta/D0 增大加快干燥（t_end 下降），Ca/活化温度/C0/水分抑制常数 b 增大延长干燥...` |
| `checks.sensitivity.V3.10.passed` | True |
| `checks.sensitivity.V3.11.name` | `响应面双向单调` |
| `checks.sensitivity.V3.11.monotone_along_D0` | True |
| `checks.sensitivity.V3.11.monotone_along_hm` | True |
| `checks.sensitivity.V3.11.span_h[0]` | 47.6546 |
| `checks.sensitivity.V3.11.span_h[1]` | 73.1618 |
| `checks.sensitivity.V3.11.corner_ratio` | 1.53525 |
| `checks.sensitivity.V3.11.passed` | True |
| `checks.sensitivity.V3.4.name` | `潜热方向探针（t_end 随 chi 单调增大）` |
| `checks.sensitivity.V3.4.chi_values[0]` | 0 |
| `checks.sensitivity.V3.4.chi_values[1]` | 0.1 |
| `checks.sensitivity.V3.4.chi_values[2]` | 0.25 |
| `checks.sensitivity.V3.4.chi_values[3]` | 0.5 |
| `checks.sensitivity.V3.4.n_fired` | 4 |
| `checks.sensitivity.V3.4.n_scanned` | 4 |
| `checks.sensitivity.V3.4.t_end_h_by_chi[0]` | 57.6251 |
| `checks.sensitivity.V3.4.t_end_h_by_chi[1]` | 58.1745 |
| `checks.sensitivity.V3.4.t_end_h_by_chi[2]` | 59.0274 |
| `checks.sensitivity.V3.4.t_end_h_by_chi[3]` | 60.5067 |
| `checks.sensitivity.V3.4.T_field_min_C_by_chi[0]` | 28 |
| `checks.sensitivity.V3.4.T_field_min_C_by_chi[1]` | 27.1048 |
| `checks.sensitivity.V3.4.T_field_min_C_by_chi[2]` | 24.7062 |
| `checks.sensitivity.V3.4.T_field_min_C_by_chi[3]` | 19.1837 |
| `checks.sensitivity.V3.4.monotone_increasing` | True |
| `checks.sensitivity.V3.4.note` | `chi=0 为基准；未触发的 chi 说明其 t_end 超出保护上限 1.2e+06 s，方向同样成立` |
| `checks.sensitivity.V3.4.passed` | True |
| `checks.sensitivity.V3.13.name` | `问题三/四鲁棒性配对同源（同一 LHS 矩阵）` |
| `checks.sensitivity.V3.13.n_pairs` | 200 |
| `checks.sensitivity.V3.13.multipliers_identical` | True |
| `checks.sensitivity.V3.13.q4_shorter_fraction` | 1 |
| `checks.sensitivity.V3.13.ratio_q4_over_q3.mean` | 0.884924 |
| `checks.sensitivity.V3.13.ratio_q4_over_q3.min` | 0.794432 |
| `checks.sensitivity.V3.13.ratio_q4_over_q3.max` | 0.983037 |
| `checks.sensitivity.V3.13.note` | `两条分布共用同一组因子取值，故雨云图是配对对比；q4/q3 比值恒小于 1 即收缩缩短工期这一结论在全分布上稳健` |
| `checks.sensitivity.V3.13.passed` | True |
| `result_files.1` | `result1.xlsx` |
| `result_files.2` | `result2.xlsx` |
| `result_files.3` | `result3.xlsx` |
| `result_files.4` | `result4.xlsx` |

### `problem_1_results.json`（636 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 1 |
| `props_appendix` | `appendix_2` |
| `characteristics.alpha_m2_s` | 1.689e-07 |
| `characteristics.Bi_T` | 1.38889 |
| `characteristics.Bi_m` | 3.2404 |
| `characteristics.R0_sq_over_alpha_s` | 2369 |
| `characteristics.D_at_C0_m2_s` | 4.938e-09 |
| `characteristics.Fo_T_1800s` | 0.75985 |
| `characteristics.penetration_depth_cm` | 0.298124 |
| `fields.n_times` | 1800 |
| `fields.n_radii` | 21 |
| `semi_analytic.beta_first6[0]` | 1.41847 |
| `semi_analytic.beta_first6[1]` | 4.16647 |
| `semi_analytic.beta_first6[2]` | 7.20848 |
| `semi_analytic.beta_first6[5]` | 16.5545 |
| `semi_analytic.beta_first6[...]` | `<2 项省略>` |
| `semi_analytic.A_first6[0]` | 1.26582 |
| `semi_analytic.A_first6[1]` | -0.377974 |
| `semi_analytic.A_first6[2]` | 0.174964 |
| `semi_analytic.A_first6[5]` | -0.0514114 |
| `semi_analytic.A_first6[...]` | `<2 项省略>` |
| `semi_analytic.tau_first3_s[0]` | 1177 |
| `semi_analytic.tau_first3_s[1]` | 136.461 |
| `semi_analytic.tau_first3_s[2]` | 45.5887 |
| `semi_analytic.max_abs_dev_C` | 6.164e-05 |
| `semi_analytic.mean_abs_dev_C` | 3.868e-05 |
| `semi_analytic.per_time_max_dev_C[0]` | 4.281e-05 |
| `semi_analytic.per_time_max_dev_C[1]` | 5.566e-05 |
| `semi_analytic.per_time_max_dev_C[2]` | 5.088e-05 |
| `semi_analytic.per_time_max_dev_C[6]` | 3.853e-05 |
| `semi_analytic.per_time_max_dev_C[...]` | `<3 项省略>` |
| `semi_analytic.T_analytic_table[0][0]` | 28.0001 |
| `semi_analytic.T_analytic_table[0][1]` | 28.0003 |
| `semi_analytic.T_analytic_table[0][2]` | 28.004 |
| `semi_analytic.T_analytic_table[0][3]` | 28.0327 |
| `semi_analytic.T_analytic_table[0][4]` | 28.1801 |
| `semi_analytic.T_analytic_table[1][0]` | 28.0408 |
| `semi_analytic.T_analytic_table[1][1]` | 28.0635 |
| `semi_analytic.T_analytic_table[1][2]` | 28.1514 |
| `semi_analytic.T_analytic_table[1][3]` | 28.3681 |
| `semi_analytic.T_analytic_table[1][4]` | 28.8489 |
| `semi_analytic.T_analytic_table[2][0]` | 28.4533 |
| `semi_analytic.T_analytic_table[2][1]` | 28.536 |
| `semi_analytic.T_analytic_table[2][2]` | 28.8039 |
| `semi_analytic.T_analytic_table[2][3]` | 29.3159 |
| `semi_analytic.T_analytic_table[2][4]` | 30.1652 |
| `semi_analytic.T_analytic_table[6][0]` | 33.5753 |
| `semi_analytic.T_analytic_table[6][1]` | 33.772 |
| `semi_analytic.T_analytic_table[6][2]` | 34.3642 |
| `semi_analytic.T_analytic_table[6][3]` | 35.3621 |
| `semi_analytic.T_analytic_table[6][4]` | 36.7856 |
| `semi_analytic.T_analytic_table[...]` | `<3 项省略>` |
| `semi_analytic.times_s[0]` | 100 |
| `semi_analytic.times_s[1]` | 300 |
| `semi_analytic.times_s[2]` | 600 |
| `semi_analytic.times_s[6]` | 1800 |
| `semi_analytic.times_s[...]` | `<3 项省略>` |
| `semi_analytic.r_cm[0]` | 0 |
| `semi_analytic.r_cm[1]` | 0.1 |
| `semi_analytic.r_cm[2]` | 0.2 |
| `semi_analytic.r_cm[20]` | 2 |
| `semi_analytic.r_cm[...]` | `<17 项省略>` |
| `semi_analytic.T_analytic_full[0][0]` | 28.0001 |
| `semi_analytic.T_analytic_full[0][1]` | 28.0001 |
| `semi_analytic.T_analytic_full[0][2]` | 28.0001 |
| `semi_analytic.T_analytic_full[0][20]` | 28.1801 |
| `semi_analytic.T_analytic_full[0][...]` | `<17 项省略>` |
| `semi_analytic.T_analytic_full[1][0]` | 28.0408 |
| `semi_analytic.T_analytic_full[1][1]` | 28.0416 |
| `semi_analytic.T_analytic_full[1][2]` | 28.0442 |
| `semi_analytic.T_analytic_full[1][20]` | 28.8489 |
| `semi_analytic.T_analytic_full[1][...]` | `<17 项省略>` |
| `semi_analytic.T_analytic_full[2][0]` | 28.4533 |
| `semi_analytic.T_analytic_full[2][1]` | 28.4566 |
| `semi_analytic.T_analytic_full[2][2]` | 28.4663 |
| `semi_analytic.T_analytic_full[2][20]` | 30.1652 |
| `semi_analytic.T_analytic_full[2][...]` | `<17 项省略>` |
| `semi_analytic.T_analytic_full[6][0]` | 33.5753 |
| `semi_analytic.T_analytic_full[6][1]` | 33.5832 |
| `semi_analytic.T_analytic_full[6][2]` | 33.6068 |
| `semi_analytic.T_analytic_full[6][20]` | 36.7856 |
| `semi_analytic.T_analytic_full[6][...]` | `<17 项省略>` |
| `semi_analytic.T_analytic_full[...]` | `<3 项省略>` |
| `semi_analytic.T_numeric_full[0][0]` | 28.0001 |
| `semi_analytic.T_numeric_full[0][1]` | 28.0001 |
| `semi_analytic.T_numeric_full[0][2]` | 28.0001 |
| `semi_analytic.T_numeric_full[0][20]` | 28.1801 |
| `semi_analytic.T_numeric_full[0][...]` | `<17 项省略>` |
| `semi_analytic.T_numeric_full[1][0]` | 28.0408 |
| `semi_analytic.T_numeric_full[1][1]` | 28.0417 |
| `semi_analytic.T_numeric_full[1][2]` | 28.0442 |
| `semi_analytic.T_numeric_full[1][20]` | 28.8489 |
| `semi_analytic.T_numeric_full[1][...]` | `<17 项省略>` |
| `semi_analytic.T_numeric_full[2][0]` | 28.4534 |
| `semi_analytic.T_numeric_full[2][1]` | 28.4566 |
| `semi_analytic.T_numeric_full[2][2]` | 28.4664 |
| `semi_analytic.T_numeric_full[2][20]` | 30.1653 |
| `semi_analytic.T_numeric_full[2][...]` | `<17 项省略>` |
| `semi_analytic.T_numeric_full[6][0]` | 33.5753 |
| `semi_analytic.T_numeric_full[6][1]` | 33.5832 |
| `semi_analytic.T_numeric_full[6][2]` | 33.6068 |
| `semi_analytic.T_numeric_full[6][20]` | 36.7856 |
| `semi_analytic.T_numeric_full[6][...]` | `<17 项省略>` |
| `semi_analytic.T_numeric_full[...]` | `<3 项省略>` |
| `semi_analytic.residual_C[0][0]` | 3.996e-07 |
| `semi_analytic.residual_C[0][1]` | 4.871e-07 |
| `semi_analytic.residual_C[0][2]` | 5.943e-07 |
| `semi_analytic.residual_C[0][20]` | 4.281e-05 |
| `semi_analytic.residual_C[0][...]` | `<17 项省略>` |
| `semi_analytic.residual_C[1][0]` | 1.691e-05 |
| `semi_analytic.residual_C[1][1]` | 2.288e-05 |
| `semi_analytic.residual_C[1][2]` | 2.32e-05 |
| `semi_analytic.residual_C[1][20]` | 5.47e-05 |
| `semi_analytic.residual_C[1][...]` | `<17 项省略>` |
| `semi_analytic.residual_C[2][0]` | 2.838e-05 |
| `semi_analytic.residual_C[2][1]` | 5.088e-05 |
| `semi_analytic.residual_C[2][2]` | 5.084e-05 |
| `semi_analytic.residual_C[2][20]` | 4.974e-05 |
| `semi_analytic.residual_C[2][...]` | `<17 项省略>` |
| `semi_analytic.residual_C[6][0]` | -1.603e-05 |
| `semi_analytic.residual_C[6][1]` | 3.853e-05 |
| `semi_analytic.residual_C[6][2]` | 3.844e-05 |
| `semi_analytic.residual_C[6][20]` | 2.565e-05 |
| `semi_analytic.residual_C[6][...]` | `<17 项省略>` |
| `semi_analytic.residual_C[...]` | `<3 项省略>` |
| `semi_analytic.n_points` | 147 |
| `mesh_ladder[0].N` | 15 |
| `mesh_ladder[0].T_center_1800s` | 33.5744 |
| `mesh_ladder[0].C_surface_1800s` | 1.50999 |
| `mesh_ladder[0].T_surface_1800s` | 36.7872 |
| `mesh_ladder[0].nfev` | 1737 |
| `mesh_ladder[1].N` | 30 |
| `mesh_ladder[1].T_center_1800s` | 33.5751 |
| `mesh_ladder[1].C_surface_1800s` | 1.51022 |
| `mesh_ladder[1].T_surface_1800s` | 36.786 |
| `mesh_ladder[1].nfev` | 1848 |
| `mesh_ladder[1].dT_center_vs_prev` | 0.0007018 |
| `mesh_ladder[1].dC_surface_vs_prev` | 0.0002295 |
| `mesh_ladder[2].N` | 60 |
| `mesh_ladder[2].T_center_1800s` | 33.5753 |
| `mesh_ladder[2].C_surface_1800s` | 1.51023 |
| `mesh_ladder[2].T_surface_1800s` | 36.7857 |
| `mesh_ladder[2].nfev` | 1894 |
| `mesh_ladder[2].dT_center_vs_prev` | 0.0001767 |
| `mesh_ladder[2].dC_surface_vs_prev` | 1.208e-05 |
| `mesh_ladder[3].N` | 120 |
| `mesh_ladder[3].T_center_1800s` | 33.5753 |
| `mesh_ladder[3].C_surface_1800s` | 1.51023 |
| `mesh_ladder[3].T_surface_1800s` | 36.7856 |
| `mesh_ladder[3].nfev` | 1978 |
| `mesh_ladder[3].dT_center_vs_prev` | 4.225e-05 |
| `mesh_ladder[3].dC_surface_vs_prev` | 3.168e-07 |
| `mesh_ladder[4].N` | 240 |
| `mesh_ladder[4].T_center_1800s` | 33.5753 |
| `mesh_ladder[4].C_surface_1800s` | 1.51023 |
| `mesh_ladder[4].T_surface_1800s` | 36.7856 |
| `mesh_ladder[4].nfev` | 1961 |
| `mesh_ladder[4].dT_center_vs_prev` | 1.337e-05 |
| `mesh_ladder[4].dC_surface_vs_prev` | 8.46e-08 |
| `table_1_temperature.times_s[0]` | 100 |
| `table_1_temperature.times_s[1]` | 300 |
| `table_1_temperature.times_s[2]` | 600 |
| `table_1_temperature.times_s[6]` | 1800 |
| `table_1_temperature.times_s[...]` | `<3 项省略>` |
| `table_1_temperature.radii_cm[0]` | 0 |
| `table_1_temperature.radii_cm[1]` | 0.5 |
| `table_1_temperature.radii_cm[2]` | 1 |
| `table_1_temperature.radii_cm[3]` | 1.5 |
| `table_1_temperature.radii_cm[4]` | 2 |
| `table_1_temperature.values[0][0]` | 28.0001 |
| `table_1_temperature.values[0][1]` | 28.0003 |
| `table_1_temperature.values[0][2]` | 28.0041 |
| `table_1_temperature.values[0][3]` | 28.0327 |
| `table_1_temperature.values[0][4]` | 28.1801 |
| `table_1_temperature.values[1][0]` | 28.0408 |
| `table_1_temperature.values[1][1]` | 28.0635 |
| `table_1_temperature.values[1][2]` | 28.1514 |
| `table_1_temperature.values[1][3]` | 28.3681 |
| `table_1_temperature.values[1][4]` | 28.8489 |
| `table_1_temperature.values[2][0]` | 28.4534 |
| `table_1_temperature.values[2][1]` | 28.5361 |
| `table_1_temperature.values[2][2]` | 28.804 |
| `table_1_temperature.values[2][3]` | 29.316 |
| `table_1_temperature.values[2][4]` | 30.1653 |
| `table_1_temperature.values[6][0]` | 33.5753 |
| `table_1_temperature.values[6][1]` | 33.772 |
| `table_1_temperature.values[6][2]` | 34.3642 |
| `table_1_temperature.values[6][3]` | 35.3622 |
| `table_1_temperature.values[6][4]` | 36.7856 |
| `table_1_temperature.values[...]` | `<3 项省略>` |
| `table_2_moisture.times_s[0]` | 100 |
| `table_2_moisture.times_s[1]` | 300 |
| `table_2_moisture.times_s[2]` | 600 |
| `table_2_moisture.times_s[6]` | 1800 |
| `table_2_moisture.times_s[...]` | `<3 项省略>` |
| `table_2_moisture.radii_cm[0]` | 0 |
| `table_2_moisture.radii_cm[1]` | 0.5 |
| `table_2_moisture.radii_cm[2]` | 1 |
| `table_2_moisture.radii_cm[3]` | 1.5 |
| `table_2_moisture.radii_cm[4]` | 2 |
| `table_2_moisture.values[0][0]` | 2.55 |
| `table_2_moisture.values[0][1]` | 2.55 |
| `table_2_moisture.values[0][2]` | 2.55 |
| `table_2_moisture.values[0][3]` | 2.55 |
| `table_2_moisture.values[0][4]` | 2.2463 |
| `table_2_moisture.values[1][0]` | 2.55 |
| `table_2_moisture.values[1][1]` | 2.55 |
| `table_2_moisture.values[1][2]` | 2.55 |
| `table_2_moisture.values[1][3]` | 2.5492 |
| `table_2_moisture.values[1][4]` | 2.0505 |
| `table_2_moisture.values[2][0]` | 2.55 |
| `table_2_moisture.values[2][1]` | 2.55 |
| `table_2_moisture.values[2][2]` | 2.55 |
| `table_2_moisture.values[2][3]` | 2.5352 |
| `table_2_moisture.values[2][4]` | 1.8768 |
| `table_2_moisture.values[6][0]` | 2.55 |
| `table_2_moisture.values[6][1]` | 2.5497 |
| `table_2_moisture.values[6][2]` | 2.5383 |
| `table_2_moisture.values[6][3]` | 2.3753 |
| `table_2_moisture.values[6][4]` | 1.5102 |
| `table_2_moisture.values[...]` | `<3 项省略>` |
| `summary.T_center_1800s` | 33.5753 |
| `summary.T_surface_1800s` | 36.7856 |
| `summary.T_gap_center_surface_1800s` | 3.21026 |
| `summary.C_center_1800s` | 2.54999 |
| `summary.C_surface_1800s` | 1.51023 |
| `summary.C_center_deviation_from_C0` | 7.856e-06 |
| `summary.herb_T_max` | 36.7856 |
| `summary.herb_T_min` | 28 |
| `summary.herb_C_max` | 2.55 |
| `summary.herb_C_min` | 1.51023 |
| `summary.volavg_C_1800s` | 2.29359 |
| `profiles.times_s[0]` | 100 |
| `profiles.times_s[1]` | 300 |
| `profiles.times_s[2]` | 600 |
| `profiles.times_s[6]` | 1800 |
| `profiles.times_s[...]` | `<3 项省略>` |
| `profiles.r_cm[0]` | 0 |
| `profiles.r_cm[1]` | 0.1 |
| `profiles.r_cm[2]` | 0.2 |
| `profiles.r_cm[20]` | 2 |
| `profiles.r_cm[...]` | `<17 项省略>` |
| `profiles.T[0][0]` | 28.0001 |
| `profiles.T[0][1]` | 28.0001 |
| `profiles.T[0][2]` | 28.0001 |
| `profiles.T[0][20]` | 28.1801 |
| `profiles.T[0][...]` | `<17 项省略>` |
| `profiles.T[1][0]` | 28.0408 |
| `profiles.T[1][1]` | 28.0417 |
| `profiles.T[1][2]` | 28.0442 |
| `profiles.T[1][20]` | 28.8489 |
| `profiles.T[1][...]` | `<17 项省略>` |
| `profiles.T[2][0]` | 28.4534 |
| `profiles.T[2][1]` | 28.4566 |
| `profiles.T[2][2]` | 28.4664 |
| `profiles.T[2][20]` | 30.1653 |
| `profiles.T[2][...]` | `<17 项省略>` |
| `profiles.T[6][0]` | 33.5753 |
| `profiles.T[6][1]` | 33.5832 |
| `profiles.T[6][2]` | 33.6068 |
| `profiles.T[6][20]` | 36.7856 |
| `profiles.T[6][...]` | `<17 项省略>` |
| `profiles.T[...]` | `<3 项省略>` |
| `profiles.C[0][0]` | 2.55 |
| `profiles.C[0][1]` | 2.55 |
| `profiles.C[0][2]` | 2.55 |
| `profiles.C[0][20]` | 2.24629 |
| `profiles.C[0][...]` | `<17 项省略>` |
| `profiles.C[1][0]` | 2.55 |
| `profiles.C[1][1]` | 2.55 |
| `profiles.C[1][2]` | 2.55 |
| `profiles.C[1][20]` | 2.05054 |
| `profiles.C[1][...]` | `<17 项省略>` |
| `profiles.C[2][0]` | 2.55 |
| `profiles.C[2][1]` | 2.55 |
| `profiles.C[2][2]` | 2.55 |
| `profiles.C[2][20]` | 1.87683 |
| `profiles.C[2][...]` | `<17 项省略>` |
| `profiles.C[6][0]` | 2.54999 |
| `profiles.C[6][1]` | 2.54999 |
| `profiles.C[6][2]` | 2.54998 |
| `profiles.C[6][20]` | 1.51023 |
| `profiles.C[6][...]` | `<17 项省略>` |
| `profiles.C[...]` | `<3 项省略>` |
| `timeseries.t_s[0]` | 1 |
| `timeseries.t_s[1]` | 11 |
| `timeseries.t_s[2]` | 21 |
| `timeseries.t_s[179]` | 1791 |
| `timeseries.t_s[...]` | `<176 项省略>` |
| `timeseries.T_center[0]` | 28 |
| `timeseries.T_center[1]` | 28 |
| `timeseries.T_center[2]` | 28 |
| `timeseries.T_center[179]` | 33.5276 |
| `timeseries.T_center[...]` | `<176 项省略>` |
| `timeseries.T_surface[0]` | 28.0002 |
| `timeseries.T_surface[1]` | 28.0066 |
| `timeseries.T_surface[2]` | 28.0172 |
| `timeseries.T_surface[179]` | 36.734 |
| `timeseries.T_surface[...]` | `<176 项省略>` |
| `timeseries.C_center[0]` | 2.55 |
| `timeseries.C_center[1]` | 2.55 |
| `timeseries.C_center[2]` | 2.55 |
| `timeseries.C_center[179]` | 2.54999 |
| `timeseries.C_center[...]` | `<176 项省略>` |
| `timeseries.C_surface[0]` | 2.50533 |
| `timeseries.C_surface[1]` | 2.44163 |
| `timeseries.C_surface[2]` | 2.40372 |
| `timeseries.C_surface[179]` | 1.51215 |
| `timeseries.C_surface[...]` | `<176 项省略>` |
| `timeseries.Ta[0]` | 28.0088 |
| `timeseries.Ta[1]` | 28.0968 |
| `timeseries.Ta[2]` | 28.1848 |
| `timeseries.Ta[179]` | 41.4609 |
| `timeseries.Ta[...]` | `<176 项省略>` |
| `timeseries.Ca[0]` | 0.0196365 |
| `timeseries.Ca[1]` | 0.0197015 |
| `timeseries.Ca[2]` | 0.0197665 |
| `timeseries.Ca[179]` | 0.0330025 |
| `timeseries.Ca[...]` | `<176 项省略>` |
| `heatmap.t_s[0]` | 1 |
| `heatmap.t_s[1]` | 21 |
| `heatmap.t_s[2]` | 41 |
| `heatmap.t_s[89]` | 1781 |
| `heatmap.t_s[...]` | `<86 项省略>` |
| `heatmap.r_cm[0]` | 0 |
| `heatmap.r_cm[1]` | 0.1 |
| `heatmap.r_cm[2]` | 0.2 |
| `heatmap.r_cm[20]` | 2 |
| `heatmap.r_cm[...]` | `<17 项省略>` |
| `heatmap.T[0][0]` | 28 |
| `heatmap.T[0][1]` | 28 |
| `heatmap.T[0][2]` | 28 |
| `heatmap.T[0][20]` | 28.0002 |
| `heatmap.T[0][...]` | `<17 项省略>` |
| `heatmap.T[1][0]` | 28 |
| `heatmap.T[1][1]` | 28 |
| `heatmap.T[1][2]` | 28 |
| `heatmap.T[1][20]` | 28.0172 |
| `heatmap.T[1][...]` | `<17 项省略>` |
| `heatmap.T[2][0]` | 28 |
| `heatmap.T[2][1]` | 28 |
| `heatmap.T[2][2]` | 28 |
| `heatmap.T[2][20]` | 28.0461 |
| `heatmap.T[2][...]` | `<17 项省略>` |
| `heatmap.T[89][0]` | 33.4745 |
| `heatmap.T[89][1]` | 33.4824 |
| `heatmap.T[89][2]` | 33.506 |
| `heatmap.T[89][20]` | 36.6765 |
| `heatmap.T[89][...]` | `<17 项省略>` |
| `heatmap.T[...]` | `<86 项省略>` |
| `heatmap.C[0][0]` | 2.55 |
| `heatmap.C[0][1]` | 2.55 |
| `heatmap.C[0][2]` | 2.55 |
| `heatmap.C[0][20]` | 2.5053 |
| `heatmap.C[0][...]` | `<17 项省略>` |
| `heatmap.C[1][0]` | 2.55 |
| `heatmap.C[1][1]` | 2.55 |
| `heatmap.C[1][2]` | 2.55 |
| `heatmap.C[1][20]` | 2.4037 |
| `heatmap.C[1][...]` | `<17 项省略>` |
| `heatmap.C[2][0]` | 2.55 |
| `heatmap.C[2][1]` | 2.55 |
| `heatmap.C[2][2]` | 2.55 |
| `heatmap.C[2][20]` | 2.3497 |
| `heatmap.C[2][...]` | `<17 项省略>` |
| `heatmap.C[89][0]` | 2.55 |
| `heatmap.C[89][1]` | 2.55 |
| `heatmap.C[89][2]` | 2.55 |
| `heatmap.C[89][20]` | 1.5143 |
| `heatmap.C[89][...]` | `<17 项省略>` |
| `heatmap.C[...]` | `<86 项省略>` |
| `air_input.t_obs_s[0]` | 0 |
| `air_input.t_obs_s[1]` | 60 |
| `air_input.t_obs_s[2]` | 120 |
| `air_input.t_obs_s[30]` | 1800 |
| `air_input.t_obs_s[...]` | `<27 项省略>` |
| `air_input.Ta_obs_C[0]` | 28 |
| `air_input.Ta_obs_C[1]` | 28.528 |
| `air_input.Ta_obs_C[2]` | 29.192 |
| `air_input.Ta_obs_C[30]` | 41.513 |
| `air_input.Ta_obs_C[...]` | `<27 项省略>` |
| `air_input.Ca_obs[0]` | 0.01963 |
| `air_input.Ca_obs[1]` | 0.02002 |
| `air_input.Ca_obs[2]` | 0.02053 |
| `air_input.Ca_obs[30]` | 0.03307 |
| `air_input.Ca_obs[...]` | `<27 项省略>` |
| `air_input.t_interp_s[0]` | 1 |
| `air_input.t_interp_s[1]` | 11 |
| `air_input.t_interp_s[2]` | 21 |
| `air_input.t_interp_s[179]` | 1791 |
| `air_input.t_interp_s[...]` | `<176 项省略>` |
| `air_input.Ta_interp_C[0]` | 28.0088 |
| `air_input.Ta_interp_C[1]` | 28.0968 |
| `air_input.Ta_interp_C[2]` | 28.1848 |
| `air_input.Ta_interp_C[179]` | 41.4609 |
| `air_input.Ta_interp_C[...]` | `<176 项省略>` |
| `air_input.Ca_interp[0]` | 0.0196365 |
| `air_input.Ca_interp[1]` | 0.0197015 |
| `air_input.Ca_interp[2]` | 0.0197665 |
| `air_input.Ca_interp[179]` | 0.0330025 |
| `air_input.Ca_interp[...]` | `<176 项省略>` |
| `air_input.Ta_range_C[0]` | 28.0088 |
| `air_input.Ta_range_C[1]` | 41.513 |
| `air_input.n_obs_points` | 31 |
| `air_input.note` | `问题一时段内热风温度由 28 °C 近线性升至 41.5130 °C；空气含湿量同步上行` |
| `temp_field_3d.t_s[0]` | 30 |
| `temp_field_3d.t_s[1]` | 60 |
| `temp_field_3d.t_s[2]` | 90 |
| `temp_field_3d.t_s[59]` | 1800 |
| `temp_field_3d.t_s[...]` | `<56 项省略>` |
| `temp_field_3d.r_cm[0]` | 0 |
| `temp_field_3d.r_cm[1]` | 0.1 |
| `temp_field_3d.r_cm[2]` | 0.2 |
| `temp_field_3d.r_cm[20]` | 2 |
| `temp_field_3d.r_cm[...]` | `<17 项省略>` |
| `temp_field_3d.T[0][0]` | 28 |
| `temp_field_3d.T[0][1]` | 28 |
| `temp_field_3d.T[0][2]` | 28 |
| `temp_field_3d.T[0][20]` | 28.0291 |
| `temp_field_3d.T[0][...]` | `<17 项省略>` |
| `temp_field_3d.T[1][0]` | 28 |
| `temp_field_3d.T[1][1]` | 28 |
| `temp_field_3d.T[1][2]` | 28 |
| `temp_field_3d.T[1][20]` | 28.0803 |
| `temp_field_3d.T[1][...]` | `<17 项省略>` |
| `temp_field_3d.T[2][0]` | 28 |
| `temp_field_3d.T[2][1]` | 28 |
| `temp_field_3d.T[2][2]` | 28 |
| `temp_field_3d.T[2][20]` | 28.1523 |
| `temp_field_3d.T[2][...]` | `<17 项省略>` |
| `temp_field_3d.T[59][0]` | 33.5753 |
| `temp_field_3d.T[59][1]` | 33.5832 |
| `temp_field_3d.T[59][2]` | 33.6068 |
| `temp_field_3d.T[59][20]` | 36.7856 |
| `temp_field_3d.T[59][...]` | `<17 项省略>` |
| `temp_field_3d.T[...]` | `<56 项省略>` |
| `temp_field_3d.C[0][0]` | 2.55 |
| `temp_field_3d.C[0][1]` | 2.55 |
| `temp_field_3d.C[0][2]` | 2.55 |
| `temp_field_3d.C[0][20]` | 2.3771 |
| `temp_field_3d.C[0][...]` | `<17 项省略>` |
| `temp_field_3d.C[1][0]` | 2.55 |
| `temp_field_3d.C[1][1]` | 2.55 |
| `temp_field_3d.C[1][2]` | 2.55 |
| `temp_field_3d.C[1][20]` | 2.3106 |
| `temp_field_3d.C[1][...]` | `<17 项省略>` |
| `temp_field_3d.C[2][0]` | 2.55 |
| `temp_field_3d.C[2][1]` | 2.55 |
| `temp_field_3d.C[2][2]` | 2.55 |
| `temp_field_3d.C[2][20]` | 2.2608 |
| `temp_field_3d.C[2][...]` | `<17 项省略>` |
| `temp_field_3d.C[59][0]` | 2.55 |
| `temp_field_3d.C[59][1]` | 2.55 |
| `temp_field_3d.C[59][2]` | 2.55 |
| `temp_field_3d.C[59][20]` | 1.5102 |
| `temp_field_3d.C[59][...]` | `<17 项省略>` |
| `temp_field_3d.C[...]` | `<56 项省略>` |
| `temp_field_3d.T_span_C[0]` | 28 |
| `temp_field_3d.T_span_C[1]` | 36.7856 |
| `temp_field_3d.C_span[0]` | 1.51023 |
| `temp_field_3d.C_span[1]` | 2.55 |
| `moisture_bl.times_s[0]` | 100 |
| `moisture_bl.times_s[1]` | 300 |
| `moisture_bl.times_s[2]` | 600 |
| `moisture_bl.times_s[6]` | 1800 |
| `moisture_bl.times_s[...]` | `<3 项省略>` |
| `moisture_bl.depth_from_surface_cm[0]` | 1.99167 |
| `moisture_bl.depth_from_surface_cm[1]` | 1.975 |
| `moisture_bl.depth_from_surface_cm[2]` | 1.95833 |
| `moisture_bl.depth_from_surface_cm[119]` | 0.008333 |
| `moisture_bl.depth_from_surface_cm[...]` | `<116 项省略>` |
| `moisture_bl.C_cells[0][0]` | 2.55 |
| `moisture_bl.C_cells[0][1]` | 2.55 |
| `moisture_bl.C_cells[0][2]` | 2.55 |
| `moisture_bl.C_cells[0][119]` | 2.27763 |
| `moisture_bl.C_cells[0][...]` | `<116 项省略>` |
| `moisture_bl.C_cells[1][0]` | 2.55 |
| `moisture_bl.C_cells[1][1]` | 2.55 |
| `moisture_bl.C_cells[1][2]` | 2.55 |
| `moisture_bl.C_cells[1][119]` | 2.08017 |
| `moisture_bl.C_cells[1][...]` | `<116 项省略>` |
| `moisture_bl.C_cells[2][0]` | 2.55 |
| `moisture_bl.C_cells[2][1]` | 2.55 |
| `moisture_bl.C_cells[2][2]` | 2.55 |
| `moisture_bl.C_cells[2][119]` | 1.90498 |
| `moisture_bl.C_cells[2][...]` | `<116 项省略>` |
| `moisture_bl.C_cells[6][0]` | 2.54999 |
| `moisture_bl.C_cells[6][1]` | 2.54999 |
| `moisture_bl.C_cells[6][2]` | 2.54999 |
| `moisture_bl.C_cells[6][119]` | 1.53535 |
| `moisture_bl.C_cells[6][...]` | `<116 项省略>` |
| `moisture_bl.C_cells[...]` | `<3 项省略>` |
| `moisture_bl.deficit_from_C0[0][0]` | 0 |
| `moisture_bl.deficit_from_C0[0][1]` | 0 |
| `moisture_bl.deficit_from_C0[0][2]` | 0 |
| `moisture_bl.deficit_from_C0[0][119]` | 0.27237 |
| `moisture_bl.deficit_from_C0[0][...]` | `<116 项省略>` |
| `moisture_bl.deficit_from_C0[1][0]` | 0 |
| `moisture_bl.deficit_from_C0[1][1]` | 0 |
| `moisture_bl.deficit_from_C0[1][2]` | 0 |
| `moisture_bl.deficit_from_C0[1][119]` | 0.469827 |
| `moisture_bl.deficit_from_C0[1][...]` | `<116 项省略>` |
| `moisture_bl.deficit_from_C0[2][0]` | 0 |
| `moisture_bl.deficit_from_C0[2][1]` | 0 |
| `moisture_bl.deficit_from_C0[2][2]` | 0 |
| `moisture_bl.deficit_from_C0[2][119]` | 0.645024 |
| `moisture_bl.deficit_from_C0[2][...]` | `<116 项省略>` |
| `moisture_bl.deficit_from_C0[6][0]` | 7.87e-06 |
| `moisture_bl.deficit_from_C0[6][1]` | 8.02e-06 |
| `moisture_bl.deficit_from_C0[6][2]` | 8.32e-06 |
| `moisture_bl.deficit_from_C0[6][119]` | 1.01465 |
| `moisture_bl.deficit_from_C0[6][...]` | `<116 项省略>` |
| `moisture_bl.deficit_from_C0[...]` | `<3 项省略>` |
| `moisture_bl.C_surface_recon[0]` | 2.24629 |
| `moisture_bl.C_surface_recon[1]` | 2.05054 |
| `moisture_bl.C_surface_recon[2]` | 1.87683 |
| `moisture_bl.C_surface_recon[6]` | 1.51023 |
| `moisture_bl.C_surface_recon[...]` | `<3 项省略>` |
| `moisture_bl.C_center[0]` | 2.55 |
| `moisture_bl.C_center[1]` | 2.55 |
| `moisture_bl.C_center[2]` | 2.55 |
| `moisture_bl.C_center[6]` | 2.54999 |
| `moisture_bl.C_center[...]` | `<3 项省略>` |
| `moisture_bl.penetration_depth_cm` | 0.298124 |
| `moisture_bl.bl_thickness_cm[0]` | 0.325 |
| `moisture_bl.bl_thickness_cm[1]` | 0.591667 |
| `moisture_bl.bl_thickness_cm[2]` | 0.875 |
| `moisture_bl.bl_thickness_cm[6]` | 1.60833 |
| `moisture_bl.bl_thickness_cm[...]` | `<3 项省略>` |
| `moisture_bl.deficit_tol` | 0.0001 |
| `moisture_bl.C0` | 2.55 |
| `moisture_bl.R0_cm` | 2 |
| `moisture_bl.note` | `失水层厚度 1.6083 cm（1800 s，判据 C0-C>1e-4），与尺度估计 sqrt(D t)=0....` |
| `xlsx_report.温度.shape[0]` | 1800 |
| `xlsx_report.温度.shape[1]` | 21 |
| `xlsx_report.温度.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.温度.blank_cells` | 0 |
| `xlsx_report.水分浓度.shape[0]` | 1800 |
| `xlsx_report.水分浓度.shape[1]` | 21 |
| `xlsx_report.水分浓度.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.水分浓度.blank_cells` | 0 |
| `checks.C01.name` | `均匀场零通量` |
| `checks.C01.measured` | 0 |
| `checks.C01.tol` | 1e-08 |
| `checks.C01.passed` | True |
| `checks.C02.name` | `柱面通量正比于 r` |
| `checks.C02.measured` | 1.99e-13 |
| `checks.C02.tol` | 1e-08 |
| `checks.C02.passed` | True |
| `checks.C02.note` | `线性场下界面通量密度恒定，面积权 A_face=eta_{i+1/2} 使总流量正比于 r` |
| `checks.C03.name` | `双场独立` |
| `checks.C03.len_y` | 240 |
| `checks.C03.expect_len` | 240 |
| `checks.C03.dT_absmax` | 0.0309075 |
| `checks.C03.dC_absmax` | 0.0120326 |
| `checks.C03.slices_alias` | False |
| `checks.C03.passed` | True |
| `checks.C05.name` | `Robin 闭合一致` |
| `checks.C05.measured_C` | 1.653e-15 |
| `checks.C05.measured_T` | 2.811e-12 |
| `checks.C05.tol` | 1e-06 |
| `checks.C05.passed` | True |
| `checks.C10.name` | `问题一单向解耦` |
| `checks.C10.measured` | 0 |
| `checks.C10.tol` | 1e-14 |
| `checks.C10.passed` | True |
| `checks.C11.name` | `附录绑定` |
| `checks.C11.props_appendix` | `appendix_2` |
| `checks.C11.passed` | True |
| `checks.C14.name` | `低含水率下界保护` |
| `checks.C14.C_floor` | 1e-06 |
| `checks.C14.D_at_1e-18` | 0 |
| `checks.C14.finite` | True |
| `checks.C14.passed` | True |
| `checks.C09.name` | `半解析解对照 147 点` |
| `checks.C09.measured_max_abs_C` | 6.164e-05 |
| `checks.C09.tol` | 0.001 |
| `checks.C09.n_points` | 147 |
| `checks.C09.n_modes` | 200 |
| `checks.C09.passed` | True |
| `checks.V3.2.name` | `网格收敛阶梯（五档）` |
| `checks.V3.2.dT_center_seq[0]` | 0.0007018 |
| `checks.V3.2.dT_center_seq[1]` | 0.0001767 |
| `checks.V3.2.dT_center_seq[2]` | 4.225e-05 |
| `checks.V3.2.dT_center_seq[3]` | 1.337e-05 |
| `checks.V3.2.finest_pair_dT` | 1.337e-05 |
| `checks.V3.2.tol` | 0.0001 |
| `checks.V3.2.monotone_decreasing` | True |
| `checks.V3.2.passed` | True |
| `checks.C04.name` | `表面值网格无关性` |
| `checks.C04.measured` | 8.46e-08 |
| `checks.C04.tol` | 0.001 |
| `checks.C04.dC_surface_seq[0]` | 0.0002295 |
| `checks.C04.dC_surface_seq[1]` | 1.208e-05 |
| `checks.C04.dC_surface_seq[2]` | 3.168e-07 |
| `checks.C04.dC_surface_seq[3]` | 8.46e-08 |
| `checks.C04.passed` | True |
| `checks.C06.name` | `剖面单调（中心最湿/最冷）` |
| `checks.C06.C_worst_increase` | 8.882e-16 |
| `checks.C06.T_worst_decrease` | 7.105e-15 |
| `checks.C06.tol` | 1e-10 |
| `checks.C06.passed` | True |
| `checks.C07.name` | `全域最大含水率在中心` |
| `checks.C07.all_at_center` | True |
| `checks.C07.n_times_checked` | 1800 |
| `checks.C07.passed` | True |
| `checks.C13.name` | `干燥方向性` |
| `checks.C13.max_rise_of_Cmax` | 0 |
| `checks.C13.max_rise_of_volavg` | -0.0001182 |
| `checks.C13.tol` | 1e-12 |
| `checks.C13.passed` | True |
| `checks.V2.4.name` | `温度落在驱动包络内` |
| `checks.V2.4.T_min` | 28 |
| `checks.V2.4.T_max` | 36.7856 |
| `checks.V2.4.envelope[0]` | 28 |
| `checks.V2.4.envelope[1]` | 41.513 |
| `checks.V2.4.passed` | True |
| `checks.time_tol_layer.name` | `时间离散误差分层（收紧一档）` |
| `checks.time_tol_layer.measured_tighten_1e-10` | 4.928e-06 |
| `checks.time_tol_layer.tol` | 0.0001 |
| `checks.time_tol_layer.passed` | True |
| `checks.time_tol_layer.diagnostic_loosen_1e-6` | 0.0003328 |
| `checks.time_tol_layer.note` | `§4.4 判据为收紧容差后变化 <1e-4；放松到 1e-6 的偏差 3.328e-04 °C 一并记录，V3...` |
| `checks.C16.name` | `写盘-读回往返一致` |
| `checks.C16.measured` | 0 |
| `checks.C16.tol` | 0 |
| `checks.C16.per_sheet.温度.shape[0]` | 1800 |
| `checks.C16.per_sheet.温度.shape[1]` | 21 |
| `checks.C16.per_sheet.温度.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.温度.blank_cells` | 0 |
| `checks.C16.per_sheet.水分浓度.shape[0]` | 1800 |
| `checks.C16.per_sheet.水分浓度.shape[1]` | 21 |
| `checks.C16.per_sheet.水分浓度.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.水分浓度.blank_cells` | 0 |
| `checks.C16.passed` | True |
| `all_checks_passed` | True |

### `problem_2_results.json`（493 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 2 |
| `props_appendix` | `appendix_3` |
| `mesh_ladder[0].N` | 30 |
| `mesh_ladder[0].C_center_end` | 1.76632 |
| `mesh_ladder[0].C_surface_end` | 1.00819 |
| `mesh_ladder[0].T_center_end` | 49.8494 |
| `mesh_ladder[0].nfev` | 9912 |
| `mesh_ladder[1].N` | 60 |
| `mesh_ladder[1].C_center_end` | 1.76621 |
| `mesh_ladder[1].C_surface_end` | 1.00814 |
| `mesh_ladder[1].T_center_end` | 49.8495 |
| `mesh_ladder[1].nfev` | 10257 |
| `mesh_ladder[1].dC_center_vs_prev` | 0.0001052 |
| `mesh_ladder[1].dC_surface_vs_prev` | 4.738e-05 |
| `mesh_ladder[2].N` | 120 |
| `mesh_ladder[2].C_center_end` | 1.76619 |
| `mesh_ladder[2].C_surface_end` | 1.00813 |
| `mesh_ladder[2].T_center_end` | 49.8495 |
| `mesh_ladder[2].nfev` | 10286 |
| `mesh_ladder[2].dC_center_vs_prev` | 2.632e-05 |
| `mesh_ladder[2].dC_surface_vs_prev` | 1.18e-05 |
| `mesh_ladder[3].N` | 240 |
| `mesh_ladder[3].C_center_end` | 1.76618 |
| `mesh_ladder[3].C_surface_end` | 1.00812 |
| `mesh_ladder[3].T_center_end` | 49.8495 |
| `mesh_ladder[3].nfev` | 10393 |
| `mesh_ladder[3].dC_center_vs_prev` | 6.56e-06 |
| `mesh_ladder[3].dC_surface_vs_prev` | 2.968e-06 |
| `model_ladder.times_s[0]` | 1800 |
| `model_ladder.times_s[1]` | 3600 |
| `model_ladder.times_s[2]` | 5400 |
| `model_ladder.times_s[5]` | 10800 |
| `model_ladder.times_s[...]` | `<2 项省略>` |
| `model_ladder.paths.L1_const_prop.C_center_end` | 2.16423 |
| `model_ladder.paths.L1_const_prop.C_surface_end` | 0.865499 |
| `model_ladder.paths.L1_const_prop.T_center_end` | 49.7351 |
| `model_ladder.paths.L1_const_prop.volavg_C_end` | 1.49855 |
| `model_ladder.paths.L1_const_prop.C_center_series[0]` | 2.54997 |
| `model_ladder.paths.L1_const_prop.C_center_series[1]` | 2.54248 |
| `model_ladder.paths.L1_const_prop.C_center_series[2]` | 2.499 |
| `model_ladder.paths.L1_const_prop.C_center_series[5]` | 2.16423 |
| `model_ladder.paths.L1_const_prop.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L1_const_prop.volavg_C_series[0]` | 2.28543 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[1]` | 2.08219 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[2]` | 1.90951 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[5]` | 1.49855 |
| `model_ladder.paths.L1_const_prop.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L2_oneway.C_center_end` | 2.19331 |
| `model_ladder.paths.L2_oneway.C_surface_end` | 0.816956 |
| `model_ladder.paths.L2_oneway.T_center_end` | 49.8306 |
| `model_ladder.paths.L2_oneway.volavg_C_end` | 1.52718 |
| `model_ladder.paths.L2_oneway.C_center_series[0]` | 2.54997 |
| `model_ladder.paths.L2_oneway.C_center_series[1]` | 2.54273 |
| `model_ladder.paths.L2_oneway.C_center_series[2]` | 2.50142 |
| `model_ladder.paths.L2_oneway.C_center_series[5]` | 2.19331 |
| `model_ladder.paths.L2_oneway.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L2_oneway.volavg_C_series[0]` | 2.28697 |
| `model_ladder.paths.L2_oneway.volavg_C_series[1]` | 2.08725 |
| `model_ladder.paths.L2_oneway.volavg_C_series[2]` | 1.91935 |
| `model_ladder.paths.L2_oneway.volavg_C_series[5]` | 1.52718 |
| `model_ladder.paths.L2_oneway.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L3_full.C_center_end` | 1.76619 |
| `model_ladder.paths.L3_full.C_surface_end` | 1.00813 |
| `model_ladder.paths.L3_full.T_center_end` | 49.8495 |
| `model_ladder.paths.L3_full.volavg_C_end` | 1.38255 |
| `model_ladder.paths.L3_full.C_center_series[0]` | 2.54993 |
| `model_ladder.paths.L3_full.C_center_series[1]` | 2.52571 |
| `model_ladder.paths.L3_full.C_center_series[2]` | 2.38604 |
| `model_ladder.paths.L3_full.C_center_series[5]` | 1.76619 |
| `model_ladder.paths.L3_full.C_center_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L3_full.volavg_C_series[0]` | 2.28267 |
| `model_ladder.paths.L3_full.volavg_C_series[1]` | 2.06499 |
| `model_ladder.paths.L3_full.volavg_C_series[2]` | 1.86877 |
| `model_ladder.paths.L3_full.volavg_C_series[5]` | 1.38255 |
| `model_ladder.paths.L3_full.volavg_C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L0_lumped.C_end` | 1.1007 |
| `model_ladder.paths.L0_lumped.T_end` | 49.9978 |
| `model_ladder.paths.L0_lumped.note` | `Bi_T, Bi_m 均为 O(1)，集中参数假设不成立，此路径仅作错误极限对照` |
| `model_ladder.paths.L0_lumped.C_series[0]` | 2.21158 |
| `model_ladder.paths.L0_lumped.C_series[1]` | 1.92016 |
| `model_ladder.paths.L0_lumped.C_series[2]` | 1.66875 |
| `model_ladder.paths.L0_lumped.C_series[5]` | 1.1007 |
| `model_ladder.paths.L0_lumped.C_series[...]` | `<2 项省略>` |
| `model_ladder.paths.L0_lumped.T_series[0]` | 34.6992 |
| `model_ladder.paths.L0_lumped.T_series[1]` | 43.1844 |
| `model_ladder.paths.L0_lumped.T_series[2]` | 47.6086 |
| `model_ladder.paths.L0_lumped.T_series[5]` | 49.9978 |
| `model_ladder.paths.L0_lumped.T_series[...]` | `<2 项省略>` |
| `model_ladder.baseline_volavg_C_end` | 1.38255 |
| `table_3_temperature.times_s[0]` | 1800 |
| `table_3_temperature.times_s[1]` | 3600 |
| `table_3_temperature.times_s[2]` | 5400 |
| `table_3_temperature.times_s[5]` | 10800 |
| `table_3_temperature.times_s[...]` | `<2 项省略>` |
| `table_3_temperature.radii_cm[0]` | 0 |
| `table_3_temperature.radii_cm[1]` | 0.5 |
| `table_3_temperature.radii_cm[2]` | 1 |
| `table_3_temperature.radii_cm[3]` | 1.5 |
| `table_3_temperature.radii_cm[4]` | 2 |
| `table_3_temperature.values[0][0]` | 32.1892 |
| `table_3_temperature.values[0][1]` | 32.3822 |
| `table_3_temperature.values[0][2]` | 32.966 |
| `table_3_temperature.values[0][3]` | 33.9608 |
| `table_3_temperature.values[0][4]` | 35.413 |
| `table_3_temperature.values[1][0]` | 40.3815 |
| `table_3_temperature.values[1][1]` | 40.5536 |
| `table_3_temperature.values[1][2]` | 41.0605 |
| `table_3_temperature.values[1][3]` | 41.8782 |
| `table_3_temperature.values[1][4]` | 42.9976 |
| `table_3_temperature.values[2][0]` | 45.8467 |
| `table_3_temperature.values[2][1]` | 45.9348 |
| `table_3_temperature.values[2][2]` | 46.1929 |
| `table_3_temperature.values[2][3]` | 46.605 |
| `table_3_temperature.values[2][4]` | 47.14 |
| `table_3_temperature.values[5][0]` | 49.8495 |
| `table_3_temperature.values[5][1]` | 49.8553 |
| `table_3_temperature.values[5][2]` | 49.8746 |
| `table_3_temperature.values[5][3]` | 49.9101 |
| `table_3_temperature.values[5][4]` | 49.9664 |
| `table_3_temperature.values[...]` | `<2 项省略>` |
| `table_4_moisture.times_s[0]` | 1800 |
| `table_4_moisture.times_s[1]` | 3600 |
| `table_4_moisture.times_s[2]` | 5400 |
| `table_4_moisture.times_s[5]` | 10800 |
| `table_4_moisture.times_s[...]` | `<2 项省略>` |
| `table_4_moisture.radii_cm[0]` | 0 |
| `table_4_moisture.radii_cm[1]` | 0.5 |
| `table_4_moisture.radii_cm[2]` | 1 |
| `table_4_moisture.radii_cm[3]` | 1.5 |
| `table_4_moisture.radii_cm[4]` | 2 |
| `table_4_moisture.values[0][0]` | 2.5499 |
| `table_4_moisture.values[0][1]` | 2.5489 |
| `table_4_moisture.values[0][2]` | 2.5255 |
| `table_4_moisture.values[0][3]` | 2.3256 |
| `table_4_moisture.values[0][4]` | 1.6486 |
| `table_4_moisture.values[1][0]` | 2.5257 |
| `table_4_moisture.values[1][1]` | 2.4947 |
| `table_4_moisture.values[1][2]` | 2.3578 |
| `table_4_moisture.values[1][3]` | 2.0229 |
| `table_4_moisture.values[1][4]` | 1.4711 |
| `table_4_moisture.values[2][0]` | 2.386 |
| `table_4_moisture.values[2][1]` | 2.3256 |
| `table_4_moisture.values[2][2]` | 2.1344 |
| `table_4_moisture.values[2][3]` | 1.802 |
| `table_4_moisture.values[2][4]` | 1.3476 |
| `table_4_moisture.values[5][0]` | 1.7662 |
| `table_4_moisture.values[5][1]` | 1.7165 |
| `table_4_moisture.values[5][2]` | 1.5702 |
| `table_4_moisture.values[5][3]` | 1.3333 |
| `table_4_moisture.values[5][4]` | 1.0081 |
| `table_4_moisture.values[...]` | `<2 项省略>` |
| `summary.T_center_end` | 49.8495 |
| `summary.T_surface_end` | 49.9664 |
| `summary.C_center_end` | 1.76619 |
| `summary.C_surface_end` | 1.00813 |
| `summary.volavg_C_end` | 1.38255 |
| `summary.C_center_at_1800s` | 2.54993 |
| `summary.C_surface_at_1800s` | 1.64862 |
| `summary.T_center_at_1800s` | 32.1892 |
| `summary.herb_T_max` | 49.9664 |
| `summary.herb_T_min` | 28 |
| `summary.herb_C_max` | 2.55 |
| `summary.herb_C_min` | 1.00813 |
| `summary.D_at_center_end_m2_s` | 1.239e-08 |
| `summary.D_at_t0_m2_s` | 5.642e-09 |
| `profiles.times_s[0]` | 1800 |
| `profiles.times_s[1]` | 3600 |
| `profiles.times_s[2]` | 5400 |
| `profiles.times_s[5]` | 10800 |
| `profiles.times_s[...]` | `<2 项省略>` |
| `profiles.r_cm[0]` | 0 |
| `profiles.r_cm[1]` | 0.1 |
| `profiles.r_cm[2]` | 0.2 |
| `profiles.r_cm[20]` | 2 |
| `profiles.r_cm[...]` | `<17 项省略>` |
| `profiles.T[0][0]` | 32.1892 |
| `profiles.T[0][1]` | 32.197 |
| `profiles.T[0][2]` | 32.2201 |
| `profiles.T[0][20]` | 35.413 |
| `profiles.T[0][...]` | `<17 项省略>` |
| `profiles.T[1][0]` | 40.3815 |
| `profiles.T[1][1]` | 40.3885 |
| `profiles.T[1][2]` | 40.4092 |
| `profiles.T[1][20]` | 42.9976 |
| `profiles.T[1][...]` | `<17 项省略>` |
| `profiles.T[2][0]` | 45.8467 |
| `profiles.T[2][1]` | 45.8503 |
| `profiles.T[2][2]` | 45.8609 |
| `profiles.T[2][20]` | 47.14 |
| `profiles.T[2][...]` | `<17 项省略>` |
| `profiles.T[5][0]` | 49.8495 |
| `profiles.T[5][1]` | 49.8497 |
| `profiles.T[5][2]` | 49.8504 |
| `profiles.T[5][20]` | 49.9664 |
| `profiles.T[5][...]` | `<17 项省略>` |
| `profiles.T[...]` | `<2 项省略>` |
| `profiles.C[0][0]` | 2.54993 |
| `profiles.C[0][1]` | 2.54992 |
| `profiles.C[0][2]` | 2.54986 |
| `profiles.C[0][20]` | 1.64862 |
| `profiles.C[0][...]` | `<17 项省略>` |
| `profiles.C[1][0]` | 2.52571 |
| `profiles.C[1][1]` | 2.52462 |
| `profiles.C[1][2]` | 2.52129 |
| `profiles.C[1][20]` | 1.47111 |
| `profiles.C[1][...]` | `<17 项省略>` |
| `profiles.C[2][0]` | 2.38604 |
| `profiles.C[2][1]` | 2.38365 |
| `profiles.C[2][2]` | 2.3765 |
| `profiles.C[2][20]` | 1.34758 |
| `profiles.C[2][...]` | `<17 项省略>` |
| `profiles.C[5][0]` | 1.76619 |
| `profiles.C[5][1]` | 1.76418 |
| `profiles.C[5][2]` | 1.7582 |
| `profiles.C[5][20]` | 1.00813 |
| `profiles.C[5][...]` | `<17 项省略>` |
| `profiles.C[...]` | `<2 项省略>` |
| `D_response_surface.C_axis[0]` | 0.15 |
| `D_response_surface.C_axis[1]` | 0.25 |
| `D_response_surface.C_axis[2]` | 0.35 |
| `D_response_surface.C_axis[24]` | 2.55 |
| `D_response_surface.C_axis[...]` | `<21 项省略>` |
| `D_response_surface.T_axis_C[0]` | 28 |
| `D_response_surface.T_axis_C[1]` | 28.9269 |
| `D_response_surface.T_axis_C[2]` | 29.8538 |
| `D_response_surface.T_axis_C[24]` | 50.246 |
| `D_response_surface.T_axis_C[...]` | `<21 项省略>` |
| `D_response_surface.D_m2_s[0][0]` | 3.351e-10 |
| `D_response_surface.D_m2_s[0][1]` | 1.113e-09 |
| `D_response_surface.D_m2_s[0][2]` | 1.861e-09 |
| `D_response_surface.D_m2_s[0][24]` | 5.642e-09 |
| `D_response_surface.D_m2_s[0][...]` | `<21 项省略>` |
| `D_response_surface.D_m2_s[1][0]` | 3.485e-10 |
| `D_response_surface.D_m2_s[1][1]` | 1.157e-09 |
| `D_response_surface.D_m2_s[1][2]` | 1.935e-09 |
| `D_response_surface.D_m2_s[1][24]` | 5.867e-09 |
| `D_response_surface.D_m2_s[1][...]` | `<21 项省略>` |
| `D_response_surface.D_m2_s[2][0]` | 3.624e-10 |
| `D_response_surface.D_m2_s[2][1]` | 1.203e-09 |
| `D_response_surface.D_m2_s[2][2]` | 2.012e-09 |
| `D_response_surface.D_m2_s[2][24]` | 6.101e-09 |
| `D_response_surface.D_m2_s[2][...]` | `<21 项省略>` |
| `D_response_surface.D_m2_s[24][0]` | 8.074e-10 |
| `D_response_surface.D_m2_s[24][1]` | 2.681e-09 |
| `D_response_surface.D_m2_s[24][2]` | 4.483e-09 |
| `D_response_surface.D_m2_s[24][24]` | 1.359e-08 |
| `D_response_surface.D_m2_s[24][...]` | `<21 项省略>` |
| `D_response_surface.D_m2_s[...]` | `<21 项省略>` |
| `D_response_surface.D_min` | 3.351e-10 |
| `D_response_surface.D_max` | 1.359e-08 |
| `D_response_surface.ratio_max_over_min` | 40.5667 |
| `D_response_surface.trajectory_C_T[0][0]` | 2.5499 |
| `D_response_surface.trajectory_C_T[0][1]` | 28 |
| `D_response_surface.trajectory_C_T[1][0]` | 2.54407 |
| `D_response_surface.trajectory_C_T[1][1]` | 28.0062 |
| `D_response_surface.trajectory_C_T[2][0]` | 2.53841 |
| `D_response_surface.trajectory_C_T[2][1]` | 28.0263 |
| `D_response_surface.trajectory_C_T[179][0]` | 1.51451 |
| `D_response_surface.trajectory_C_T[179][1]` | 49.8746 |
| `D_response_surface.trajectory_C_T[...]` | `<176 项省略>` |
| `D_response_surface.trajectory_t_s[0]` | 1 |
| `D_response_surface.trajectory_t_s[1]` | 61 |
| `D_response_surface.trajectory_t_s[2]` | 121 |
| `D_response_surface.trajectory_t_s[179]` | 10741 |
| `D_response_surface.trajectory_t_s[...]` | `<176 项省略>` |
| `D_response_surface.note` | `D 随温度升高而增大、随含水率下降而减小，两者在烘干过程中反向抵消` |
| `timeseries.t_s[0]` | 1 |
| `timeseries.t_s[1]` | 31 |
| `timeseries.t_s[2]` | 61 |
| `timeseries.t_s[359]` | 10771 |
| `timeseries.t_s[...]` | `<356 项省略>` |
| `timeseries.T_center[0]` | 28 |
| `timeseries.T_center[1]` | 28 |
| `timeseries.T_center[2]` | 28 |
| `timeseries.T_center[359]` | 49.8455 |
| `timeseries.T_center[...]` | `<356 项省略>` |
| `timeseries.T_surface[0]` | 28.0001 |
| `timeseries.T_surface[1]` | 28.0218 |
| `timeseries.T_surface[2]` | 28.0596 |
| `timeseries.T_surface[359]` | 49.9567 |
| `timeseries.T_surface[...]` | `<356 项省略>` |
| `timeseries.C_center[0]` | 2.55 |
| `timeseries.C_center[1]` | 2.55 |
| `timeseries.C_center[2]` | 2.55 |
| `timeseries.C_center[359]` | 1.76906 |
| `timeseries.C_center[...]` | `<356 项省略>` |
| `timeseries.C_surface[0]` | 2.5096 |
| `timeseries.C_surface[1]` | 2.38588 |
| `timeseries.C_surface[2]` | 2.32445 |
| `timeseries.C_surface[359]` | 1.00981 |
| `timeseries.C_surface[...]` | `<356 项省略>` |
| `timeseries.C_volavg[0]` | 2.5498 |
| `timeseries.C_volavg[1]` | 2.544 |
| `timeseries.C_volavg[2]` | 2.5384 |
| `timeseries.C_volavg[359]` | 1.38477 |
| `timeseries.C_volavg[...]` | `<356 项省略>` |
| `timeseries.Ta[0]` | 28.0088 |
| `timeseries.Ta[1]` | 28.2728 |
| `timeseries.Ta[2]` | 28.5391 |
| `timeseries.Ta[359]` | 50.1607 |
| `timeseries.Ta[...]` | `<356 项省略>` |
| `timeseries.Ca[0]` | 0.0196365 |
| `timeseries.Ca[1]` | 0.0198315 |
| `timeseries.Ca[2]` | 0.0200285 |
| `timeseries.Ca[359]` | 0.0499198 |
| `timeseries.Ca[...]` | `<356 项省略>` |
| `timeseries.T_surf_recon[0]` | 28.0001 |
| `timeseries.T_surf_recon[1]` | 28.0218 |
| `timeseries.T_surf_recon[2]` | 28.0596 |
| `timeseries.T_surf_recon[359]` | 49.9567 |
| `timeseries.T_surf_recon[...]` | `<356 项省略>` |
| `timeseries.C_surf_recon[0]` | 2.5096 |
| `timeseries.C_surf_recon[1]` | 2.38588 |
| `timeseries.C_surf_recon[2]` | 2.32445 |
| `timeseries.C_surf_recon[359]` | 1.00981 |
| `timeseries.C_surf_recon[...]` | `<356 项省略>` |
| `timeseries.q_conv_W_m2[0]` | 0.216647 |
| `timeseries.q_conv_W_m2[1]` | 6.27398 |
| `timeseries.q_conv_W_m2[2]` | 11.9872 |
| `timeseries.q_conv_W_m2[359]` | 5.10037 |
| `timeseries.q_conv_W_m2[...]` | `<356 项省略>` |
| `timeseries.j_mass_kg_m2_s[0]` | 1.992e-06 |
| `timeseries.j_mass_kg_m2_s[1]` | 1.893e-06 |
| `timeseries.j_mass_kg_m2_s[2]` | 1.844e-06 |
| `timeseries.j_mass_kg_m2_s[359]` | 7.679e-07 |
| `timeseries.j_mass_kg_m2_s[...]` | `<356 项省略>` |
| `heatmap.t_s[0]` | 1 |
| `heatmap.t_s[1]` | 121 |
| `heatmap.t_s[2]` | 241 |
| `heatmap.t_s[89]` | 10681 |
| `heatmap.t_s[...]` | `<86 项省略>` |
| `heatmap.r_cm[0]` | 0 |
| `heatmap.r_cm[1]` | 0.1 |
| `heatmap.r_cm[2]` | 0.2 |
| `heatmap.r_cm[20]` | 2 |
| `heatmap.r_cm[...]` | `<17 项省略>` |
| `heatmap.T[0][0]` | 28 |
| `heatmap.T[0][1]` | 28 |
| `heatmap.T[0][2]` | 28 |
| `heatmap.T[0][20]` | 28.0001 |
| `heatmap.T[0][...]` | `<17 项省略>` |
| `heatmap.T[1][0]` | 28.0001 |
| `heatmap.T[1][1]` | 28.0001 |
| `heatmap.T[1][2]` | 28.0001 |
| `heatmap.T[1][20]` | 28.1789 |
| `heatmap.T[1][...]` | `<17 项省略>` |
| `heatmap.T[2][0]` | 28.0064 |
| `heatmap.T[2][1]` | 28.0067 |
| `heatmap.T[2][2]` | 28.0074 |
| `heatmap.T[2][20]` | 28.4561 |
| `heatmap.T[2][...]` | `<17 项省略>` |
| `heatmap.T[89][0]` | 49.8365 |
| `heatmap.T[89][1]` | 49.8366 |
| `heatmap.T[89][2]` | 49.837 |
| `heatmap.T[89][20]` | 49.944 |
| `heatmap.T[89][...]` | `<17 项省略>` |
| `heatmap.T[...]` | `<86 项省略>` |
| `heatmap.C[0][0]` | 2.55 |
| `heatmap.C[0][1]` | 2.55 |
| `heatmap.C[0][2]` | 2.55 |
| `heatmap.C[0][20]` | 2.5096 |
| `heatmap.C[0][...]` | `<17 项省略>` |
| `heatmap.C[1][0]` | 2.55 |
| `heatmap.C[1][1]` | 2.55 |
| `heatmap.C[1][2]` | 2.55 |
| `heatmap.C[1][20]` | 2.2404 |
| `heatmap.C[1][...]` | `<17 项省略>` |
| `heatmap.C[2][0]` | 2.55 |
| `heatmap.C[2][1]` | 2.55 |
| `heatmap.C[2][2]` | 2.55 |
| `heatmap.C[2][20]` | 2.1282 |
| `heatmap.C[2][...]` | `<17 项省略>` |
| `heatmap.C[89][0]` | 1.778 |
| `heatmap.C[89][1]` | 1.776 |
| `heatmap.C[89][2]` | 1.77 |
| `heatmap.C[89][20]` | 1.015 |
| `heatmap.C[89][...]` | `<17 项省略>` |
| `heatmap.C[...]` | `<86 项省略>` |
| `xlsx_report.温度.shape[0]` | 10800 |
| `xlsx_report.温度.shape[1]` | 21 |
| `xlsx_report.温度.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.温度.blank_cells` | 0 |
| `xlsx_report.水分浓度.shape[0]` | 10800 |
| `xlsx_report.水分浓度.shape[1]` | 21 |
| `xlsx_report.水分浓度.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.水分浓度.blank_cells` | 0 |
| `checks.C11.name` | `附录绑定` |
| `checks.C11.props_appendix` | `appendix_3` |
| `checks.C11.passed` | True |
| `checks.C12.name` | `五个物性偏导非零` |
| `checks.C12.partials.d_rho_dC` | 16.32 |
| `checks.C12.partials.d_cp_dC` | 26.7205 |
| `checks.C12.partials.d_lam_dC` | 0.003711 |
| `checks.C12.partials.d_D_dC` | 4.761e-11 |
| `checks.C12.partials.d_D_dT` | 1.31e-09 |
| `checks.C12.tol` | 1e-12 |
| `checks.C12.inert_partials_expected_zero.d_rho_dT` | 0 |
| `checks.C12.inert_partials_expected_zero.d_cp_dT` | 0 |
| `checks.C12.inert_partials_expected_zero.d_lam_dT` | 0 |
| `checks.C12.passed` | True |
| `checks.C08.name` | `附件 1 复现与衔接连续` |
| `checks.C08.sample_rel_err_Ta` | 0 |
| `checks.C08.sample_rel_err_Ca` | 0 |
| `checks.C08.tol_sample` | 1e-09 |
| `checks.C08.join_jump_Ta_C` | 5.35e-12 |
| `checks.C08.join_jump_Ca` | 1.478e-15 |
| `checks.C08.tol_join` | 1e-06 |
| `checks.C08.passed` | True |
| `checks.C14.name` | `低含水率下界保护` |
| `checks.C14.C_floor` | 1e-06 |
| `checks.C14.D_at_1e-18` | 0 |
| `checks.C14.passed` | True |
| `checks.C_kelvin.name` | `Arrhenius 用开尔文` |
| `checks.C_kelvin.measured_rel` | 1.86e-16 |
| `checks.C_kelvin.tol` | 1e-12 |
| `checks.C_kelvin.D_ratio_50_over_28` | 2.38776 |
| `checks.C_kelvin.passed` | True |
| `checks.C_no_plateau.name` | `问题二未进入外推段` |
| `checks.C_no_plateau.t_end_s` | 10800 |
| `checks.C_no_plateau.T_obs_s` | 1.44e+04 |
| `checks.C_no_plateau.passed` | True |
| `checks.C06.name` | `剖面单调（中心最湿；纯升温段中心最冷）` |
| `checks.C06.C_worst_increase` | 8.882e-16 |
| `checks.C06.tol_C` | 1e-10 |
| `checks.C06.T_inversion_rising_window` | 1.066e-14 |
| `checks.C06.tol_T_rising` | 1e-10 |
| `checks.C06.t_first_driver_dip_s` | 2940 |
| `checks.C06.n_times_rising` | 2940 |
| `checks.C06.T_inversion_after_first_dip` | 0.0007703 |
| `checks.C06.driver_worst_down_step_C` | 0.45 |
| `checks.C06.inversion_over_driver_step` | 0.001712 |
| `checks.C06.tol_ratio` | 0.05 |
| `checks.C06.driver_negative_increments` | 95 |
| `checks.C06.note` | `附件 1 平台段 Ta 有 95 次负增量（最大回落 0.45 °C）；热风回落时表面先冷于内部，该反转幅度仅...` |
| `checks.C06.passed` | True |
| `checks.C07.name` | `全域最大含水率在中心` |
| `checks.C07.max_minus_center` | 4.441e-16 |
| `checks.C07.tol` | 1e-12 |
| `checks.C07.n_times_checked` | 10800 |
| `checks.C07.n_times_strict_argmax_at_center` | 10794 |
| `checks.C07.note` | `早期中心与邻近若干格心在 1e-16 量级并列，故用 max-center 差值判定` |
| `checks.C07.passed` | True |
| `checks.C13.name` | `干燥方向性` |
| `checks.C13.max_rise_of_Cmax` | 0 |
| `checks.C13.max_rise_of_volavg` | -7.667e-05 |
| `checks.C13.tol` | 1e-12 |
| `checks.C13.passed` | True |
| `checks.V2.4.name` | `温度落在驱动包络内` |
| `checks.V2.4.T_min` | 28 |
| `checks.V2.4.T_max` | 49.9664 |
| `checks.V2.4.envelope[0]` | 28 |
| `checks.V2.4.envelope[1]` | 50.246 |
| `checks.V2.4.passed` | True |
| `checks.V3.2.name` | `网格收敛阶梯（四档）` |
| `checks.V3.2.dC_center_seq[0]` | 0.0001052 |
| `checks.V3.2.dC_center_seq[1]` | 2.632e-05 |
| `checks.V3.2.dC_center_seq[2]` | 6.56e-06 |
| `checks.V3.2.finest_pair` | 6.56e-06 |
| `checks.V3.2.tol` | 0.001 |
| `checks.V3.2.passed` | True |
| `checks.C04.name` | `表面值网格无关性` |
| `checks.C04.measured` | 2.968e-06 |
| `checks.C04.tol` | 0.001 |
| `checks.C04.dC_surface_seq[0]` | 4.738e-05 |
| `checks.C04.dC_surface_seq[1]` | 1.18e-05 |
| `checks.C04.dC_surface_seq[2]` | 2.968e-06 |
| `checks.C04.passed` | True |
| `checks.V3.6.name` | `四级模型阶梯真实独立运行` |
| `checks.V3.6.volavg_C_end_by_path.L0_lumped` | 1.1007 |
| `checks.V3.6.volavg_C_end_by_path.L1_const_prop` | 1.49855 |
| `checks.V3.6.volavg_C_end_by_path.L2_oneway` | 1.52718 |
| `checks.V3.6.volavg_C_end_by_path.L3_full` | 1.38255 |
| `checks.V3.6.min_pairwise_gap` | 0.0286287 |
| `checks.V3.6.tol` | 1e-06 |
| `checks.V3.6.passed` | True |
| `checks.C15.name` | `模型对比两两可分辨` |
| `checks.C15.measured_min_gap` | 0.0286287 |
| `checks.C15.tol` | 1e-06 |
| `checks.C15.n_pairs` | 6 |
| `checks.C15.passed` | True |
| `checks.C16.name` | `写盘-读回往返一致` |
| `checks.C16.measured` | 0 |
| `checks.C16.tol` | 0 |
| `checks.C16.per_sheet.温度.shape[0]` | 10800 |
| `checks.C16.per_sheet.温度.shape[1]` | 21 |
| `checks.C16.per_sheet.温度.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.温度.blank_cells` | 0 |
| `checks.C16.per_sheet.水分浓度.shape[0]` | 10800 |
| `checks.C16.per_sheet.水分浓度.shape[1]` | 21 |
| `checks.C16.per_sheet.水分浓度.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.水分浓度.blank_cells` | 0 |
| `checks.C16.passed` | True |
| `all_checks_passed` | True |

### `problem_3_results.json`（305 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 3 |
| `props_appendix` | `appendix_3` |
| `t_end.seconds` | 2.075e+05 |
| `t_end.hours` | 57.6251 |
| `t_end.days` | 2.40105 |
| `t_end.nfev` | 21261 |
| `t_end.n_solver_steps` | 8869 |
| `criterion_comparison.max.t_end_s` | 2.075e+05 |
| `criterion_comparison.max.t_end_h` | 57.6251 |
| `criterion_comparison.max.nfev` | 21261 |
| `criterion_comparison.volavg.t_end_s` | 1.301e+05 |
| `criterion_comparison.volavg.t_end_h` | 36.1499 |
| `criterion_comparison.volavg.nfev` | 18628 |
| `criterion_comparison.surface.t_end_s` | 4.517e+04 |
| `criterion_comparison.surface.t_end_h` | 12.5467 |
| `criterion_comparison.surface.nfev` | 15221 |
| `mesh_ladder[0].N` | 30 |
| `mesh_ladder[0].t_end_s` | 2.093e+05 |
| `mesh_ladder[0].t_end_h` | 58.1429 |
| `mesh_ladder[1].N` | 60 |
| `mesh_ladder[1].t_end_s` | 2.08e+05 |
| `mesh_ladder[1].t_end_h` | 57.784 |
| `mesh_ladder[1].dt_end_vs_prev_s` | 1292 |
| `mesh_ladder[1].dt_end_vs_prev_rel` | 0.006211 |
| `mesh_ladder[2].N` | 120 |
| `mesh_ladder[2].t_end_s` | 2.075e+05 |
| `mesh_ladder[2].t_end_h` | 57.6251 |
| `mesh_ladder[2].dt_end_vs_prev_s` | 572.164 |
| `mesh_ladder[2].dt_end_vs_prev_rel` | 0.002758 |
| `mesh_ladder[3].N` | 240 |
| `mesh_ladder[3].t_end_s` | 2.072e+05 |
| `mesh_ladder[3].t_end_h` | 57.5611 |
| `mesh_ladder[3].dt_end_vs_prev_s` | 230.22 |
| `mesh_ladder[3].dt_end_vs_prev_rel` | 0.001111 |
| `mesh_ladder[4].N` | 480 |
| `mesh_ladder[4].t_end_s` | 2.071e+05 |
| `mesh_ladder[4].t_end_h` | 57.5378 |
| `mesh_ladder[4].dt_end_vs_prev_s` | 84.048 |
| `mesh_ladder[4].dt_end_vs_prev_rel` | 0.0004058 |
| `table_5_moisture.times_s[0]` | 21600 |
| `table_5_moisture.times_s[1]` | 43200 |
| `table_5_moisture.times_s[2]` | 64800 |
| `table_5_moisture.times_s[8]` | 194400 |
| `table_5_moisture.times_s[...]` | `<5 项省略>` |
| `table_5_moisture.times_h[0]` | 6 |
| `table_5_moisture.times_h[1]` | 12 |
| `table_5_moisture.times_h[2]` | 18 |
| `table_5_moisture.times_h[8]` | 54 |
| `table_5_moisture.times_h[...]` | `<5 项省略>` |
| `table_5_moisture.radii_cm[0]` | 0 |
| `table_5_moisture.radii_cm[1]` | 0.5 |
| `table_5_moisture.radii_cm[2]` | 1 |
| `table_5_moisture.radii_cm[3]` | 1.5 |
| `table_5_moisture.radii_cm[4]` | 2 |
| `table_5_moisture.values[0][0]` | 1.0172 |
| `table_5_moisture.values[0][1]` | 0.9883 |
| `table_5_moisture.values[0][2]` | 0.9016 |
| `table_5_moisture.values[0][3]` | 0.755 |
| `table_5_moisture.values[0][4]` | 0.5326 |
| `table_5_moisture.values[1][0]` | 0.4564 |
| `table_5_moisture.values[1][1]` | 0.4433 |
| `table_5_moisture.values[1][2]` | 0.4032 |
| `table_5_moisture.values[1][3]` | 0.3298 |
| `table_5_moisture.values[1][4]` | 0.1641 |
| `table_5_moisture.values[2][0]` | 0.299 |
| `table_5_moisture.values[2][1]` | 0.2917 |
| `table_5_moisture.values[2][2]` | 0.2688 |
| `table_5_moisture.values[2][3]` | 0.2254 |
| `table_5_moisture.values[2][4]` | 0.0843 |
| `table_5_moisture.values[8][0]` | 0.154 |
| `table_5_moisture.values[8][1]` | 0.1516 |
| `table_5_moisture.values[8][2]` | 0.1438 |
| `table_5_moisture.values[8][3]` | 0.1279 |
| `table_5_moisture.values[8][4]` | 0.0529 |
| `table_5_moisture.values[...]` | `<5 项省略>` |
| `table_5_moisture.t_end_row.label` | `烘干结束时间` |
| `table_5_moisture.t_end_row.hours` | 57.6251 |
| `table_5_moisture.t_end_row.seconds` | 2.075e+05 |
| `summary.t_end_h` | 57.6251 |
| `summary.t_end_days` | 2.40105 |
| `summary.C_max_at_t_end` | 0.15 |
| `summary.C_center_at_t_end` | 0.15 |
| `summary.C_surface_at_t_end` | 0.0525172 |
| `summary.volavg_C_at_t_end` | 0.124418 |
| `summary.T_center_at_t_end` | 49.9685 |
| `summary.herb_T_max` | 50.0399 |
| `summary.herb_T_min` | 28 |
| `summary.herb_C_max` | 2.55 |
| `summary.herb_C_min` | 0.0525179 |
| `summary.n_output_rows` | 3457 |
| `drying_curve.t_s[0]` | 60 |
| `drying_curve.t_s[1]` | 660 |
| `drying_curve.t_s[2]` | 1260 |
| `drying_curve.t_s[345]` | 207060 |
| `drying_curve.t_s[...]` | `<342 项省略>` |
| `drying_curve.t_h[0]` | 0.0166667 |
| `drying_curve.t_h[1]` | 0.183333 |
| `drying_curve.t_h[2]` | 0.35 |
| `drying_curve.t_h[345]` | 57.5167 |
| `drying_curve.t_h[...]` | `<342 项省略>` |
| `drying_curve.C_max[0]` | 2.55 |
| `drying_curve.C_max[1]` | 2.55 |
| `drying_curve.C_max[2]` | 2.55 |
| `drying_curve.C_max[345]` | 0.150113 |
| `drying_curve.C_max[...]` | `<342 项省略>` |
| `drying_curve.C_volavg[0]` | 2.53859 |
| `drying_curve.C_volavg[1]` | 2.44037 |
| `drying_curve.C_volavg[2]` | 2.35443 |
| `drying_curve.C_volavg[345]` | 0.124501 |
| `drying_curve.C_volavg[...]` | `<342 项省略>` |
| `drying_curve.C_center[0]` | 2.55 |
| `drying_curve.C_center[1]` | 2.55 |
| `drying_curve.C_center[2]` | 2.55 |
| `drying_curve.C_center[345]` | 0.150114 |
| `drying_curve.C_center[...]` | `<342 项省略>` |
| `drying_curve.C_surface[0]` | 2.32619 |
| `drying_curve.C_surface[1]` | 1.9089 |
| `drying_curve.C_surface[2]` | 1.74195 |
| `drying_curve.C_surface[345]` | 0.052526 |
| `drying_curve.C_surface[...]` | `<342 项省略>` |
| `drying_curve.T_center[0]` | 28 |
| `drying_curve.T_center[1]` | 28.3597 |
| `drying_curve.T_center[2]` | 29.9722 |
| `drying_curve.T_center[345]` | 49.9685 |
| `drying_curve.T_center[...]` | `<342 项省略>` |
| `drying_curve.threshold` | 0.15 |
| `heatmap.t_s[0]` | 60 |
| `heatmap.t_s[1]` | 1260 |
| `heatmap.t_s[2]` | 2460 |
| `heatmap.t_s[172]` | 206460 |
| `heatmap.t_s[...]` | `<169 项省略>` |
| `heatmap.t_h[0]` | 0.0166667 |
| `heatmap.t_h[1]` | 0.35 |
| `heatmap.t_h[2]` | 0.683333 |
| `heatmap.t_h[172]` | 57.35 |
| `heatmap.t_h[...]` | `<169 项省略>` |
| `heatmap.r_cm[0]` | 0 |
| `heatmap.r_cm[1]` | 0.1 |
| `heatmap.r_cm[2]` | 0.2 |
| `heatmap.r_cm[20]` | 2 |
| `heatmap.r_cm[...]` | `<17 项省略>` |
| `heatmap.C[0][0]` | 2.55 |
| `heatmap.C[0][1]` | 2.55 |
| `heatmap.C[0][2]` | 2.55 |
| `heatmap.C[0][20]` | 2.3262 |
| `heatmap.C[0][...]` | `<17 项省略>` |
| `heatmap.C[1][0]` | 2.55 |
| `heatmap.C[1][1]` | 2.55 |
| `heatmap.C[1][2]` | 2.55 |
| `heatmap.C[1][20]` | 1.742 |
| `heatmap.C[1][...]` | `<17 项省略>` |
| `heatmap.C[2][0]` | 2.5485 |
| `heatmap.C[2][1]` | 2.5483 |
| `heatmap.C[2][2]` | 2.5477 |
| `heatmap.C[2][20]` | 1.569 |
| `heatmap.C[2][...]` | `<17 项省略>` |
| `heatmap.C[172][0]` | 0.1503 |
| `heatmap.C[172][1]` | 0.1502 |
| `heatmap.C[172][2]` | 0.1499 |
| `heatmap.C[172][20]` | 0.0525 |
| `heatmap.C[172][...]` | `<17 项省略>` |
| `heatmap.C[...]` | `<169 项省略>` |
| `heatmap.T[0][0]` | 28 |
| `heatmap.T[0][1]` | 28 |
| `heatmap.T[0][2]` | 28 |
| `heatmap.T[0][20]` | 28.0581 |
| `heatmap.T[0][...]` | `<17 项省略>` |
| `heatmap.T[1][0]` | 29.9722 |
| `heatmap.T[1][1]` | 29.9784 |
| `heatmap.T[1][2]` | 29.9969 |
| `heatmap.T[1][20]` | 32.7159 |
| `heatmap.T[1][...]` | `<17 项省略>` |
| `heatmap.T[2][0]` | 35.2768 |
| `heatmap.T[2][1]` | 35.2851 |
| `heatmap.T[2][2]` | 35.3096 |
| `heatmap.T[2][20]` | 38.5642 |
| `heatmap.T[2][...]` | `<17 项省略>` |
| `heatmap.T[172][0]` | 49.9685 |
| `heatmap.T[172][1]` | 49.9685 |
| `heatmap.T[172][2]` | 49.9685 |
| `heatmap.T[172][20]` | 49.9685 |
| `heatmap.T[172][...]` | `<17 项省略>` |
| `heatmap.T[...]` | `<169 项省略>` |
| `profiles.times_s[0]` | 21600 |
| `profiles.times_s[1]` | 43200 |
| `profiles.times_s[2]` | 64800 |
| `profiles.times_s[8]` | 194400 |
| `profiles.times_s[...]` | `<5 项省略>` |
| `profiles.r_cm[0]` | 0 |
| `profiles.r_cm[1]` | 0.1 |
| `profiles.r_cm[2]` | 0.2 |
| `profiles.r_cm[20]` | 2 |
| `profiles.r_cm[...]` | `<17 项省略>` |
| `profiles.C[0][0]` | 1.01716 |
| `profiles.C[0][1]` | 1.016 |
| `profiles.C[0][2]` | 1.01254 |
| `profiles.C[0][20]` | 0.53256 |
| `profiles.C[0][...]` | `<17 项省略>` |
| `profiles.C[1][0]` | 0.456351 |
| `profiles.C[1][1]` | 0.45583 |
| `profiles.C[1][2]` | 0.454278 |
| `profiles.C[1][20]` | 0.164057 |
| `profiles.C[1][...]` | `<17 项省略>` |
| `profiles.C[2][0]` | 0.298993 |
| `profiles.C[2][1]` | 0.298702 |
| `profiles.C[2][2]` | 0.297833 |
| `profiles.C[2][20]` | 0.08431 |
| `profiles.C[2][...]` | `<17 项省略>` |
| `profiles.C[8][0]` | 0.154027 |
| `profiles.C[8][1]` | 0.153932 |
| `profiles.C[8][2]` | 0.153646 |
| `profiles.C[8][20]` | 0.052856 |
| `profiles.C[8][...]` | `<17 项省略>` |
| `profiles.C[...]` | `<5 项省略>` |
| `xlsx_report.Sheet1.shape[0]` | 3457 |
| `xlsx_report.Sheet1.shape[1]` | 21 |
| `xlsx_report.Sheet1.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.Sheet1.blank_cells` | 0 |
| `checks.C11.name` | `附录绑定（与问题二同源）` |
| `checks.C11.props_appendix` | `appendix_3` |
| `checks.C11.passed` | True |
| `checks.C19.name` | `首次下穿（密扫无更早穿越）` |
| `checks.C19.measured_endpoint_gap` | 0 |
| `checks.C19.tol` | 1e-05 |
| `checks.C19.n_scan_points` | 20000 |
| `checks.C19.n_points_below_thr` | 0 |
| `checks.C19.min_Cmax_before_t_end` | 0.15 |
| `checks.C19.passed` | True |
| `checks.C07.name` | `事件时刻最大值在中心` |
| `checks.C07.argmax_cell` | 0 |
| `checks.C07.C_center` | 0.15 |
| `checks.C07.C_surface_cell` | 0.0644202 |
| `checks.C07.passed` | True |
| `checks.C17.name` | `判据口径序关系` |
| `checks.C17.t_surface_h` | 12.5467 |
| `checks.C17.t_volavg_h` | 36.1499 |
| `checks.C17.t_max_h` | 57.6251 |
| `checks.C17.ordered` | True |
| `checks.C17.gap_max_minus_volavg_s` | 7.731e+04 |
| `checks.C17.tol_gap` | 60 |
| `checks.C17.underestimate_by_volavg_h` | 21.4752 |
| `checks.C17.underestimate_pct` | 37.267 |
| `checks.C17.passed` | True |
| `checks.V3.3.name` | `时间容差对照（t_end）` |
| `checks.V3.3.measured_dt_end_s` | 0.0284772 |
| `checks.V3.3.tol` | 60 |
| `checks.V3.3.t_end_rtol_1e_6_s` | 2.075e+05 |
| `checks.V3.3.t_end_rtol_1e_8_s` | 2.075e+05 |
| `checks.V3.3.passed` | True |
| `checks.V3.2.name` | `网格收敛阶梯（t_end，五档）` |
| `checks.V3.2.dt_end_seq_s[0]` | 1292 |
| `checks.V3.2.dt_end_seq_s[1]` | 572.164 |
| `checks.V3.2.dt_end_seq_s[2]` | 230.22 |
| `checks.V3.2.dt_end_seq_s[3]` | 84.048 |
| `checks.V3.2.dt_end_seq_rel[0]` | 0.006211 |
| `checks.V3.2.dt_end_seq_rel[1]` | 0.002758 |
| `checks.V3.2.dt_end_seq_rel[2]` | 0.001111 |
| `checks.V3.2.dt_end_seq_rel[3]` | 0.0004058 |
| `checks.V3.2.finest_pair_s` | 84.048 |
| `checks.V3.2.finest_pair_rel` | 0.0004058 |
| `checks.V3.2.tol_rel` | 0.002 |
| `checks.V3.2.observed_order` | 1.45373 |
| `checks.V3.2.richardson_limit_s` | 2.071e+05 |
| `checks.V3.2.richardson_limit_h` | 57.5244 |
| `checks.V3.2.baseline_minus_richardson_h` | 0.100721 |
| `checks.V3.2.monotone_decreasing` | True |
| `checks.V3.2.note` | `t_end 以约一阶精度收敛（表面重构与阈值定位均为一阶）；最细两档相对变化 0.041%，故用相对判据 0.2%` |
| `checks.V3.2.passed` | True |
| `checks.XA2.name` | `问题三与问题二逐格恒等（t<=10800 s）` |
| `checks.XA2.measured_max_abs_diff` | 0 |
| `checks.XA2.tol` | 1e-09 |
| `checks.XA2.n_times` | 6 |
| `checks.XA2.n_cells` | 240 |
| `checks.XA2.long_run_max_abs_dT_C` | 4.385e-06 |
| `checks.XA2.long_run_max_abs_dC` | 3.267e-08 |
| `checks.XA2.note` | `同一右端、同一 max_step 时逐位相同；长时程运行用 max_step=60 s（M6），其与问题二的差...` |
| `checks.XA2.passed` | True |
| `checks.V3.12.name` | `与题面 2-3 天量级对照` |
| `checks.V3.12.measured_days` | 2.40105 |
| `checks.V3.12.reference_range_days[0]` | 2 |
| `checks.V3.12.reference_range_days[1]` | 3 |
| `checks.V3.12.inside_range` | True |
| `checks.V3.12.same_order_of_magnitude` | True |
| `checks.V3.12.note` | `题面区间是独立于模型的量级参照，不是标定目标；未对任何物性做反向调参` |
| `checks.V3.12.passed` | True |
| `checks.C16.name` | `写盘-读回往返一致` |
| `checks.C16.measured` | 0 |
| `checks.C16.tol` | 0 |
| `checks.C16.per_sheet.Sheet1.shape[0]` | 3457 |
| `checks.C16.per_sheet.Sheet1.shape[1]` | 21 |
| `checks.C16.per_sheet.Sheet1.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.Sheet1.blank_cells` | 0 |
| `checks.C16.passed` | True |
| `checks.C13.name` | `干燥方向性（全程）` |
| `checks.C13.max_rise_of_Cmax` | 0 |
| `checks.C13.max_rise_of_volavg` | -1.274e-05 |
| `checks.C13.tol` | 1e-12 |
| `checks.C13.passed` | True |
| `checks.V2.4.name` | `温度落在驱动包络内` |
| `checks.V2.4.T_min` | 28 |
| `checks.V2.4.T_max` | 50.0399 |
| `checks.V2.4.envelope[0]` | 28 |
| `checks.V2.4.envelope[1]` | 50.246 |
| `checks.V2.4.passed` | True |
| `all_checks_passed` | True |

### `problem_4_results.json`（623 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 4 |
| `props_appendix` | `appendix_4` |
| `shrink_mode` | `radial` |
| `t_end.seconds` | 1.841e+05 |
| `t_end.hours` | 51.1511 |
| `t_end.days` | 2.1313 |
| `t_end.nfev` | 20764 |
| `t_end.n_solver_steps` | 8791 |
| `t_end.R_at_t_end_cm` | 1.2 |
| `attribution.q3_baseline.props` | `appendix_3` |
| `attribution.q3_baseline.shrink` | False |
| `attribution.q3_baseline.t_end_s` | 2.075e+05 |
| `attribution.q3_baseline.t_end_h` | 57.6251 |
| `attribution.q3_baseline.nfev` | 21261 |
| `attribution.app4_noshrink.props` | `appendix_4` |
| `attribution.app4_noshrink.shrink` | False |
| `attribution.app4_noshrink.t_end_s` | 4.682e+05 |
| `attribution.app4_noshrink.t_end_h` | 130.058 |
| `attribution.app4_noshrink.nfev` | 31717 |
| `attribution.app3_shrink.props` | `appendix_3` |
| `attribution.app3_shrink.shrink` | True |
| `attribution.app3_shrink.t_end_s` | 9.1e+04 |
| `attribution.app3_shrink.t_end_h` | 25.2786 |
| `attribution.app3_shrink.nfev` | 17349 |
| `attribution.app4_shrink.props` | `appendix_4` |
| `attribution.app4_shrink.shrink` | True |
| `attribution.app4_shrink.t_end_s` | 1.841e+05 |
| `attribution.app4_shrink.t_end_h` | 51.1511 |
| `attribution.app4_shrink.nfev` | 20764 |
| `mesh_ladder[0].N` | 30 |
| `mesh_ladder[0].t_end_s` | 1.846e+05 |
| `mesh_ladder[0].t_end_h` | 51.2671 |
| `mesh_ladder[1].N` | 60 |
| `mesh_ladder[1].t_end_s` | 1.843e+05 |
| `mesh_ladder[1].t_end_h` | 51.1851 |
| `mesh_ladder[1].dt_end_vs_prev_s` | 294.853 |
| `mesh_ladder[1].dt_end_vs_prev_rel` | 0.0016 |
| `mesh_ladder[2].N` | 120 |
| `mesh_ladder[2].t_end_s` | 1.841e+05 |
| `mesh_ladder[2].t_end_h` | 51.1511 |
| `mesh_ladder[2].dt_end_vs_prev_s` | 122.438 |
| `mesh_ladder[2].dt_end_vs_prev_rel` | 0.0006649 |
| `mesh_ladder[3].N` | 240 |
| `mesh_ladder[3].t_end_s` | 1.841e+05 |
| `mesh_ladder[3].t_end_h` | 51.1392 |
| `mesh_ladder[3].dt_end_vs_prev_s` | 42.9203 |
| `mesh_ladder[3].dt_end_vs_prev_rel` | 0.0002331 |
| `mesh_ladder[4].N` | 480 |
| `mesh_ladder[4].t_end_s` | 1.841e+05 |
| `mesh_ladder[4].t_end_h` | 51.1356 |
| `mesh_ladder[4].dt_end_vs_prev_s` | 13.0635 |
| `mesh_ladder[4].dt_end_vs_prev_rel` | 7.096e-05 |
| `table_6_moisture.radii_cm[0]` | 0 |
| `table_6_moisture.radii_cm[1]` | 0.5 |
| `table_6_moisture.radii_cm[2]` | 1 |
| `table_6_moisture.radii_cm[3]` | 1.5 |
| `table_6_moisture.radii_cm[4]` | 2 |
| `table_6_moisture.rows[0].t_s` | 21600 |
| `table_6_moisture.rows[0].t_h` | 6 |
| `table_6_moisture.rows[0].R_cm` | 1.374 |
| `table_6_moisture.rows[0].C[0]` | 1.7191 |
| `table_6_moisture.rows[0].C[1]` | 1.5373 |
| `table_6_moisture.rows[0].C[2]` | 1.0222 |
| `table_6_moisture.rows[0].C_surface` | 0.4202 |
| `table_6_moisture.rows[1].t_s` | 43200 |
| `table_6_moisture.rows[1].t_h` | 12 |
| `table_6_moisture.rows[1].R_cm` | 1.248 |
| `table_6_moisture.rows[1].C[0]` | 0.7379 |
| `table_6_moisture.rows[1].C[1]` | 0.6548 |
| `table_6_moisture.rows[1].C[2]` | 0.4083 |
| `table_6_moisture.rows[1].C_surface` | 0.1668 |
| `table_6_moisture.rows[2].t_s` | 64800 |
| `table_6_moisture.rows[2].t_h` | 18 |
| `table_6_moisture.rows[2].R_cm` | 1.214 |
| `table_6_moisture.rows[2].C[0]` | 0.409 |
| `table_6_moisture.rows[2].C[1]` | 0.3689 |
| `table_6_moisture.rows[2].C[2]` | 0.2398 |
| `table_6_moisture.rows[2].C_surface` | 0.0891 |
| `table_6_moisture.rows[7].t_s` | 172800 |
| `table_6_moisture.rows[7].t_h` | 48 |
| `table_6_moisture.rows[7].R_cm` | 1.2 |
| `table_6_moisture.rows[7].C[0]` | 0.1563 |
| `table_6_moisture.rows[7].C[1]` | 0.1469 |
| `table_6_moisture.rows[7].C[2]` | 0.1117 |
| `table_6_moisture.rows[7].C_surface` | 0.0529 |
| `table_6_moisture.rows[...]` | `<4 项省略>` |
| `table_6_moisture.surface_label` | `药材表面` |
| `table_6_moisture.t_end_row.label` | `烘干结束时间` |
| `table_6_moisture.t_end_row.hours` | 51.1511 |
| `table_6_moisture.t_end_row.seconds` | 1.841e+05 |
| `table_6_moisture.t_end_row.R_cm` | 1.2 |
| `radius_curve.t_data_s[0]` | 0 |
| `radius_curve.t_data_s[1]` | 1800 |
| `radius_curve.t_data_s[2]` | 3600 |
| `radius_curve.t_data_s[144]` | 2.592e+05 |
| `radius_curve.t_data_s[...]` | `<141 项省略>` |
| `radius_curve.R_data_cm[0]` | 2 |
| `radius_curve.R_data_cm[1]` | 1.873 |
| `radius_curve.R_data_cm[2]` | 1.794 |
| `radius_curve.R_data_cm[144]` | 1.198 |
| `radius_curve.R_data_cm[...]` | `<141 项省略>` |
| `radius_curve.t_dense_s[0]` | 0 |
| `radius_curve.t_dense_s[1]` | 432 |
| `radius_curve.t_dense_s[2]` | 864 |
| `radius_curve.t_dense_s[600]` | 2.592e+05 |
| `radius_curve.t_dense_s[...]` | `<597 项省略>` |
| `radius_curve.R_pchip_cm[0]` | 2 |
| `radius_curve.R_pchip_cm[1]` | 1.9649 |
| `radius_curve.R_pchip_cm[2]` | 1.93238 |
| `radius_curve.R_pchip_cm[600]` | 1.198 |
| `radius_curve.R_pchip_cm[...]` | `<597 项省略>` |
| `radius_curve.R_weibull_cm[0]` | 2 |
| `radius_curve.R_weibull_cm[1]` | 1.9606 |
| `radius_curve.R_weibull_cm[2]` | 1.9294 |
| `radius_curve.R_weibull_cm[600]` | 1.19941 |
| `radius_curve.R_weibull_cm[...]` | `<597 项省略>` |
| `radius_curve.dRdt_cm_per_s[0]` | 0 |
| `radius_curve.dRdt_cm_per_s[1]` | -7.844e-05 |
| `radius_curve.dRdt_cm_per_s[2]` | -7.192e-05 |
| `radius_curve.dRdt_cm_per_s[600]` | 0 |
| `radius_curve.dRdt_cm_per_s[...]` | `<597 项省略>` |
| `radius_curve.t_end_s` | 1.841e+05 |
| `radius_curve.R_at_t_end_cm` | 1.2 |
| `radius_curve.weibull_params.R_inf_cm` | 1.19941 |
| `radius_curve.weibull_params.tau_s` | 1.331e+04 |
| `radius_curve.weibull_params.k` | 0.871345 |
| `radius_curve.weibull_rmse_cm` | 0.002329 |
| `radius_curve.weibull_max_abs_cm` | 0.020148 |
| `radius_curve.note` | `Weibull 只作描述性参考；PDE 中的 R(t) 一律取附件 2 的保单调 PCHIP 插值` |
| `shrink_consistency.volume_ratio_geometric` | 0.358801 |
| `shrink_consistency.volume_ratio_from_density` | 0.414405 |
| `shrink_consistency.relative_gap` | 0.134178 |
| `shrink_consistency.rho_d_at_C_thr` | 672.609 |
| `shrink_consistency.rho_d0` | 278.732 |
| `shrink_consistency.rho_d_end_radial` | 776.844 |
| `shrink_consistency.rho_d_end_isotropic` | 1297 |
| `shrink_consistency.reference_rho_zero_moisture` | 760 |
| `shrink_consistency.bland_altman.t_s[0]` | 0 |
| `shrink_consistency.bland_altman.t_s[1]` | 1800 |
| `shrink_consistency.bland_altman.t_s[2]` | 3600 |
| `shrink_consistency.bland_altman.t_s[102]` | 1.836e+05 |
| `shrink_consistency.bland_altman.t_s[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.t_h[0]` | 0 |
| `shrink_consistency.bland_altman.t_h[1]` | 0.5 |
| `shrink_consistency.bland_altman.t_h[2]` | 1 |
| `shrink_consistency.bland_altman.t_h[102]` | 51 |
| `shrink_consistency.bland_altman.t_h[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.volume_ratio_geometric[0]` | 1 |
| `shrink_consistency.bland_altman.volume_ratio_geometric[1]` | 0.877032 |
| `shrink_consistency.bland_altman.volume_ratio_geometric[2]` | 0.804609 |
| `shrink_consistency.bland_altman.volume_ratio_geometric[102]` | 0.36 |
| `shrink_consistency.bland_altman.volume_ratio_geometric[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.volume_ratio_from_density[0]` | 1 |
| `shrink_consistency.bland_altman.volume_ratio_from_density[1]` | 0.960006 |
| `shrink_consistency.bland_altman.volume_ratio_from_density[2]` | 0.928177 |
| `shrink_consistency.bland_altman.volume_ratio_from_density[102]` | 0.404568 |
| `shrink_consistency.bland_altman.volume_ratio_from_density[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.volavg_C[0]` | 2.55 |
| `shrink_consistency.bland_altman.volavg_C[1]` | 2.34424 |
| `shrink_consistency.bland_altman.volavg_C[2]` | 2.18591 |
| `shrink_consistency.bland_altman.volavg_C[102]` | 0.118601 |
| `shrink_consistency.bland_altman.volavg_C[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.mean[0]` | 1 |
| `shrink_consistency.bland_altman.mean[1]` | 0.918519 |
| `shrink_consistency.bland_altman.mean[2]` | 0.866393 |
| `shrink_consistency.bland_altman.mean[102]` | 0.382284 |
| `shrink_consistency.bland_altman.mean[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.diff[0]` | 0 |
| `shrink_consistency.bland_altman.diff[1]` | 0.0829742 |
| `shrink_consistency.bland_altman.diff[2]` | 0.123568 |
| `shrink_consistency.bland_altman.diff[102]` | 0.0445684 |
| `shrink_consistency.bland_altman.diff[...]` | `<99 项省略>` |
| `shrink_consistency.bland_altman.bias` | 0.0886474 |
| `shrink_consistency.bland_altman.sd_diff` | 0.0526812 |
| `shrink_consistency.bland_altman.loa_lower` | -0.0146078 |
| `shrink_consistency.bland_altman.loa_upper` | 0.191902 |
| `shrink_consistency.bland_altman.n_pairs` | 103 |
| `shrink_consistency.bland_altman.n_outside_loa` | 10 |
| `shrink_consistency.bland_altman.note` | `几何路径只用附件 2 半径，密度路径只用附录 4 密度式 + 本解体积平均含水率；两者独立，故偏差即两套数据源...` |
| `moving_boundary_frames[0].t_s` | 21600 |
| `moving_boundary_frames[0].t_h` | 6 |
| `moving_boundary_frames[0].R_cm` | 1.374 |
| `moving_boundary_frames[0].r_cm[0]` | 0.005725 |
| `moving_boundary_frames[0].r_cm[1]` | 0.017175 |
| `moving_boundary_frames[0].r_cm[2]` | 0.028625 |
| `moving_boundary_frames[0].r_cm[120]` | 1.374 |
| `moving_boundary_frames[0].r_cm[...]` | `<117 项省略>` |
| `moving_boundary_frames[0].C[0]` | 1.7191 |
| `moving_boundary_frames[0].C[1]` | 1.7189 |
| `moving_boundary_frames[0].C[2]` | 1.71852 |
| `moving_boundary_frames[0].C[120]` | 0.420197 |
| `moving_boundary_frames[0].C[...]` | `<117 项省略>` |
| `moving_boundary_frames[0].T[0]` | 49.9687 |
| `moving_boundary_frames[0].T[1]` | 49.9687 |
| `moving_boundary_frames[0].T[2]` | 49.9687 |
| `moving_boundary_frames[0].T[120]` | 49.9686 |
| `moving_boundary_frames[0].T[...]` | `<117 项省略>` |
| `moving_boundary_frames[1].t_s` | 43200 |
| `moving_boundary_frames[1].t_h` | 12 |
| `moving_boundary_frames[1].R_cm` | 1.248 |
| `moving_boundary_frames[1].r_cm[0]` | 0.0052 |
| `moving_boundary_frames[1].r_cm[1]` | 0.0156 |
| `moving_boundary_frames[1].r_cm[2]` | 0.026 |
| `moving_boundary_frames[1].r_cm[120]` | 1.248 |
| `moving_boundary_frames[1].r_cm[...]` | `<117 项省略>` |
| `moving_boundary_frames[1].C[0]` | 0.737909 |
| `moving_boundary_frames[1].C[1]` | 0.737836 |
| `moving_boundary_frames[1].C[2]` | 0.737691 |
| `moving_boundary_frames[1].C[120]` | 0.166766 |
| `moving_boundary_frames[1].C[...]` | `<117 项省略>` |
| `moving_boundary_frames[1].T[0]` | 49.9685 |
| `moving_boundary_frames[1].T[1]` | 49.9685 |
| `moving_boundary_frames[1].T[2]` | 49.9685 |
| `moving_boundary_frames[1].T[120]` | 49.9685 |
| `moving_boundary_frames[1].T[...]` | `<117 项省略>` |
| `moving_boundary_frames[2].t_s` | 64800 |
| `moving_boundary_frames[2].t_h` | 18 |
| `moving_boundary_frames[2].R_cm` | 1.214 |
| `moving_boundary_frames[2].r_cm[0]` | 0.005058 |
| `moving_boundary_frames[2].r_cm[1]` | 0.015175 |
| `moving_boundary_frames[2].r_cm[2]` | 0.025292 |
| `moving_boundary_frames[2].r_cm[120]` | 1.214 |
| `moving_boundary_frames[2].r_cm[...]` | `<117 项省略>` |
| `moving_boundary_frames[2].C[0]` | 0.408992 |
| `moving_boundary_frames[2].C[1]` | 0.408959 |
| `moving_boundary_frames[2].C[2]` | 0.408893 |
| `moving_boundary_frames[2].C[120]` | 0.089051 |
| `moving_boundary_frames[2].C[...]` | `<117 项省略>` |
| `moving_boundary_frames[2].T[0]` | 49.9685 |
| `moving_boundary_frames[2].T[1]` | 49.9685 |
| `moving_boundary_frames[2].T[2]` | 49.9685 |
| `moving_boundary_frames[2].T[120]` | 49.9685 |
| `moving_boundary_frames[2].T[...]` | `<117 项省略>` |
| `moving_boundary_frames[7].t_s` | 172800 |
| `moving_boundary_frames[7].t_h` | 48 |
| `moving_boundary_frames[7].R_cm` | 1.2 |
| `moving_boundary_frames[7].r_cm[0]` | 0.005 |
| `moving_boundary_frames[7].r_cm[1]` | 0.015 |
| `moving_boundary_frames[7].r_cm[2]` | 0.025 |
| `moving_boundary_frames[7].r_cm[120]` | 1.2 |
| `moving_boundary_frames[7].r_cm[...]` | `<117 项省略>` |
| `moving_boundary_frames[7].C[0]` | 0.156264 |
| `moving_boundary_frames[7].C[1]` | 0.156257 |
| `moving_boundary_frames[7].C[2]` | 0.156243 |
| `moving_boundary_frames[7].C[120]` | 0.052883 |
| `moving_boundary_frames[7].C[...]` | `<117 项省略>` |
| `moving_boundary_frames[7].T[0]` | 49.9685 |
| `moving_boundary_frames[7].T[1]` | 49.9685 |
| `moving_boundary_frames[7].T[2]` | 49.9685 |
| `moving_boundary_frames[7].T[120]` | 49.9685 |
| `moving_boundary_frames[7].T[...]` | `<117 项省略>` |
| `moving_boundary_frames[...]` | `<4 项省略>` |
| `compare_q3.t_s[0]` | 0 |
| `compare_q3.t_s[1]` | 519.926 |
| `compare_q3.t_s[2]` | 1040 |
| `compare_q3.t_s[399]` | 2.075e+05 |
| `compare_q3.t_s[...]` | `<396 项省略>` |
| `compare_q3.t_h[0]` | 0 |
| `compare_q3.t_h[1]` | 0.144424 |
| `compare_q3.t_h[2]` | 0.288848 |
| `compare_q3.t_h[399]` | 57.6251 |
| `compare_q3.t_h[...]` | `<396 项省略>` |
| `compare_q3.C_max_q4_shrink[0]` | 2.55 |
| `compare_q3.C_max_q4_shrink[1]` | 2.55 |
| `compare_q3.C_max_q4_shrink[2]` | 2.55 |
| `compare_q3.C_max_q4_shrink[...]` | `<396 项省略>` |
| `compare_q3.C_max_q3_fixed[0]` | 2.55 |
| `compare_q3.C_max_q3_fixed[1]` | 2.55 |
| `compare_q3.C_max_q3_fixed[2]` | 2.55 |
| `compare_q3.C_max_q3_fixed[399]` | 0.15 |
| `compare_q3.C_max_q3_fixed[...]` | `<396 项省略>` |
| `compare_q3.t_end_q4_h` | 51.1511 |
| `compare_q3.t_end_q3_h` | 57.6251 |
| `compare_q3.delta_h` | -6.47395 |
| `compare_q3.delta_pct` | -11.2346 |
| `compare_q3.threshold` | 0.15 |
| `compare_q3.probe_eta[0]` | 0 |
| `compare_q3.probe_eta[1]` | 0.25 |
| `compare_q3.probe_eta[2]` | 0.5 |
| `compare_q3.probe_eta[3]` | 0.75 |
| `compare_q3.probe_eta[4]` | 1 |
| `compare_q3.probe_r_cm_q3[0]` | 0 |
| `compare_q3.probe_r_cm_q3[1]` | 0.5 |
| `compare_q3.probe_r_cm_q3[2]` | 1 |
| `compare_q3.probe_r_cm_q3[3]` | 1.5 |
| `compare_q3.probe_r_cm_q3[4]` | 2 |
| `compare_q3.probe_r_cm_q4_at_t_end[0]` | 0 |
| `compare_q3.probe_r_cm_q4_at_t_end[1]` | 0.3 |
| `compare_q3.probe_r_cm_q4_at_t_end[2]` | 0.6 |
| `compare_q3.probe_r_cm_q4_at_t_end[3]` | 0.9 |
| `compare_q3.probe_r_cm_q4_at_t_end[4]` | 1.2 |
| `compare_q3.probe_cross_h_q4[0]` | 51.1511 |
| `compare_q3.probe_cross_h_q4[1]` | 49.4368 |
| `compare_q3.probe_cross_h_q4[2]` | 44.1932 |
| `compare_q3.probe_cross_h_q4[3]` | 34.8364 |
| `compare_q3.probe_cross_h_q4[4]` | 13.3058 |
| `compare_q3.probe_cross_h_q3[0]` | 57.6251 |
| `compare_q3.probe_cross_h_q3[1]` | 55.3644 |
| `compare_q3.probe_cross_h_q3[2]` | 48.5134 |
| `compare_q3.probe_cross_h_q3[3]` | 36.5953 |
| `compare_q3.probe_cross_h_q3[4]` | 12.8858 |
| `compare_q3.attribution_runs_h.q3_baseline` | 57.6251 |
| `compare_q3.attribution_runs_h.app4_noshrink` | 130.058 |
| `compare_q3.attribution_runs_h.app3_shrink` | 25.2786 |
| `compare_q3.attribution_runs_h.app4_shrink` | 51.1511 |
| `compare_q3.probe_note` | `测点取物质坐标 eta=r/R(t)；问题三 R 恒为 2 cm，故 eta 与固定物理半径一一对应。归因三次...` |
| `mass_balance.t_s[0]` | 0 |
| `mass_balance.t_s[1]` | 600 |
| `mass_balance.t_s[2]` | 1200 |
| `mass_balance.t_s[306]` | 1.836e+05 |
| `mass_balance.t_s[...]` | `<303 项省略>` |
| `mass_balance.t_h[0]` | 0 |
| `mass_balance.t_h[1]` | 0.166667 |
| `mass_balance.t_h[2]` | 0.333333 |
| `mass_balance.t_h[306]` | 51 |
| `mass_balance.t_h[...]` | `<303 项省略>` |
| `mass_balance.m_w_kg_per_m[0]` | 0.893177 |
| `mass_balance.m_w_kg_per_m[1]` | 0.864211 |
| `mass_balance.m_w_kg_per_m[2]` | 0.841532 |
| `mass_balance.m_w_kg_per_m[306]` | 0.0415419 |
| `mass_balance.m_w_kg_per_m[...]` | `<303 项省略>` |
| `mass_balance.cumulative_loss_kg_per_m[0]` | 0 |
| `mass_balance.cumulative_loss_kg_per_m[1]` | 0.0290415 |
| `mass_balance.cumulative_loss_kg_per_m[2]` | 0.0517232 |
| `mass_balance.cumulative_loss_kg_per_m[306]` | 0.851715 |
| `mass_balance.cumulative_loss_kg_per_m[...]` | `<303 项省略>` |
| `mass_balance.flux_rate_kg_per_m_s[0]` | 6.666e-05 |
| `mass_balance.flux_rate_kg_per_m_s[1]` | 4.087e-05 |
| `mass_balance.flux_rate_kg_per_m_s[2]` | 3.548e-05 |
| `mass_balance.flux_rate_kg_per_m_s[306]` | 1.23e-07 |
| `mass_balance.flux_rate_kg_per_m_s[...]` | `<303 项省略>` |
| `mass_balance.stored_drop_kg_per_m` | 0.851701 |
| `mass_balance.closure_rel_gap` | 9.398e-05 |
| `drying_curve.t_s[0]` | 60 |
| `drying_curve.t_s[1]` | 660 |
| `drying_curve.t_s[2]` | 1260 |
| `drying_curve.t_s[306]` | 183660 |
| `drying_curve.t_s[...]` | `<303 项省略>` |
| `drying_curve.t_h[0]` | 0.0166667 |
| `drying_curve.t_h[1]` | 0.183333 |
| `drying_curve.t_h[2]` | 0.35 |
| `drying_curve.t_h[306]` | 51.0167 |
| `drying_curve.t_h[...]` | `<303 项省略>` |
| `drying_curve.C_max[0]` | 2.55 |
| `drying_curve.C_max[1]` | 2.55 |
| `drying_curve.C_max[2]` | 2.55 |
| `drying_curve.C_max[306]` | 0.150249 |
| `drying_curve.C_max[...]` | `<303 项省略>` |
| `drying_curve.C_volavg[0]` | 2.53951 |
| `drying_curve.C_volavg[1]` | 2.46037 |
| `drying_curve.C_volavg[2]` | 2.39651 |
| `drying_curve.C_volavg[306]` | 0.11858 |
| `drying_curve.C_volavg[...]` | `<303 项省略>` |
| `drying_curve.C_center[0]` | 2.55 |
| `drying_curve.C_center[1]` | 2.55 |
| `drying_curve.C_center[2]` | 2.55 |
| `drying_curve.C_center[306]` | 0.15025 |
| `drying_curve.C_center[...]` | `<303 项省略>` |
| `drying_curve.C_surface[0]` | 2.07191 |
| `drying_curve.C_surface[1]` | 1.41788 |
| `drying_curve.C_surface[2]` | 1.2238 |
| `drying_curve.C_surface[306]` | 0.052497 |
| `drying_curve.C_surface[...]` | `<303 项省略>` |
| `drying_curve.T_center[0]` | 28 |
| `drying_curve.T_center[1]` | 28.1328 |
| `drying_curve.T_center[2]` | 29.208 |
| `drying_curve.T_center[306]` | 49.9685 |
| `drying_curve.T_center[...]` | `<303 项省略>` |
| `drying_curve.T_surface[0]` | 28.0749 |
| `drying_curve.T_surface[1]` | 30.2891 |
| `drying_curve.T_surface[2]` | 33.2074 |
| `drying_curve.T_surface[306]` | 49.9685 |
| `drying_curve.T_surface[...]` | `<303 项省略>` |
| `drying_curve.R_cm[0]` | 1.99499 |
| `drying_curve.R_cm[1]` | 1.94738 |
| `drying_curve.R_cm[2]` | 1.90524 |
| `drying_curve.R_cm[306]` | 1.2 |
| `drying_curve.R_cm[...]` | `<303 项省略>` |
| `drying_curve.threshold` | 0.15 |
| `heatmap.t_s[0]` | 60 |
| `heatmap.t_s[1]` | 1260 |
| `heatmap.t_s[2]` | 2460 |
| `heatmap.t_s[153]` | 183660 |
| `heatmap.t_s[...]` | `<150 项省略>` |
| `heatmap.t_h[0]` | 0.0166667 |
| `heatmap.t_h[1]` | 0.35 |
| `heatmap.t_h[2]` | 0.683333 |
| `heatmap.t_h[153]` | 51.0167 |
| `heatmap.t_h[...]` | `<150 项省略>` |
| `heatmap.r_cm[0]` | 0 |
| `heatmap.r_cm[1]` | 0.1 |
| `heatmap.r_cm[2]` | 0.2 |
| `heatmap.r_cm[19]` | 1.9 |
| `heatmap.r_cm[...]` | `<16 项省略>` |
| `heatmap.surface_label` | `药材表面` |
| `heatmap.R_cm[0]` | 1.99499 |
| `heatmap.R_cm[1]` | 1.90524 |
| `heatmap.R_cm[2]` | 1.8418 |
| `heatmap.R_cm[153]` | 1.2 |
| `heatmap.R_cm[...]` | `<150 项省略>` |
| `heatmap.C[0][0]` | 2.55 |
| `heatmap.C[0][1]` | 2.55 |
| `heatmap.C[0][2]` | 2.55 |
| `heatmap.C[0][19]` | 2.5475 |
| `heatmap.C[0][...]` | `<16 项省略>` |
| `heatmap.C[1][0]` | 2.55 |
| `heatmap.C[1][1]` | 2.55 |
| `heatmap.C[1][2]` | 2.55 |
| `heatmap.C[1][19]` | 1.267 |
| `heatmap.C[1][...]` | `<16 项省略>` |
| `heatmap.C[2][0]` | 2.55 |
| `heatmap.C[2][1]` | 2.55 |
| `heatmap.C[2][2]` | 2.55 |
| `heatmap.C[2][...]` | `<16 项省略>` |
| `heatmap.C[153][0]` | 0.1502 |
| `heatmap.C[153][1]` | 0.1499 |
| `heatmap.C[153][2]` | 0.1489 |
| `heatmap.C[153][...]` | `<16 项省略>` |
| `heatmap.C[...]` | `<150 项省略>` |
| `heatmap.T[0][0]` | 28 |
| `heatmap.T[0][1]` | 28 |
| `heatmap.T[0][2]` | 28 |
| `heatmap.T[0][19]` | 28.0419 |
| `heatmap.T[0][...]` | `<16 项省略>` |
| `heatmap.T[1][0]` | 29.208 |
| `heatmap.T[1][1]` | 29.2167 |
| `heatmap.T[1][2]` | 29.2429 |
| `heatmap.T[1][19]` | 33.1797 |
| `heatmap.T[1][...]` | `<16 项省略>` |
| `heatmap.T[2][0]` | 33.9249 |
| `heatmap.T[2][1]` | 33.9395 |
| `heatmap.T[2][2]` | 33.9833 |
| `heatmap.T[2][...]` | `<16 项省略>` |
| `heatmap.T[153][0]` | 49.9685 |
| `heatmap.T[153][1]` | 49.9685 |
| `heatmap.T[153][2]` | 49.9685 |
| `heatmap.T[153][...]` | `<16 项省略>` |
| `heatmap.T[...]` | `<150 项省略>` |
| `heatmap.C_surface[0]` | 2.0719 |
| `heatmap.C_surface[1]` | 1.2238 |
| `heatmap.C_surface[2]` | 1.0605 |
| `heatmap.C_surface[153]` | 0.0525 |
| `heatmap.C_surface[...]` | `<150 项省略>` |
| `heatmap.T_surface[0]` | 28.0749 |
| `heatmap.T_surface[1]` | 33.2074 |
| `heatmap.T_surface[2]` | 38.9806 |
| `heatmap.T_surface[153]` | 49.9685 |
| `heatmap.T_surface[...]` | `<150 项省略>` |
| `summary.t_end_h` | 51.1511 |
| `summary.t_end_days` | 2.1313 |
| `summary.R_min_cm` | 1.2 |
| `summary.R_max_cm` | 1.99499 |
| `summary.R_at_t_end_cm` | 1.2 |
| `summary.C_max_at_t_end` | 0.15 |
| `summary.C_center_at_t_end` | 0.15 |
| `summary.C_surface_at_t_end` | 0.0524816 |
| `summary.volavg_C_at_t_end` | 0.118411 |
| `summary.T_center_at_t_end` | 49.9685 |
| `summary.herb_T_max` | 50.05 |
| `summary.herb_T_min` | 28 |
| `summary.herb_C_max` | 2.55 |
| `summary.herb_C_min` | 0.0524818 |
| `summary.m_w_initial_kg_per_m` | 0.893177 |
| `summary.m_w_final_kg_per_m` | 0.0414757 |
| `summary.water_removed_pct` | 95.3564 |
| `summary.rho_d0` | 278.732 |
| `summary.rho_d_at_t_end` | 774.257 |
| `summary.n_output_rows` | 3069 |
| `summary.n_blank_cells` | 20122 |
| `summary.D_at_center_t_end_m2_s` | 3.802e-10 |
| `summary.D_at_t0_m2_s` | 1.047e-09 |
| `xlsx_report.Sheet1.shape[0]` | 3069 |
| `xlsx_report.Sheet1.shape[1]` | 21 |
| `xlsx_report.Sheet1.roundtrip_max_abs_diff` | 0 |
| `xlsx_report.Sheet1.blank_cells` | 20122 |
| `checks.C11.name` | `附录绑定（附录 4 物性 + 附件 2 半径）` |
| `checks.C11.props_appendix` | `appendix_4` |
| `checks.C11.shrink_mode` | `radial` |
| `checks.C11.passed` | True |
| `checks.C18.name` | `半径轨迹单调不增且复现附件 2` |
| `checks.C18.max_dR_over_scan_cm` | 0 |
| `checks.C18.max_dRdt_cm_per_s` | 0 |
| `checks.C18.min_dRdt_cm_per_s` | -8.359e-05 |
| `checks.C18.n_scan_points` | 10000 |
| `checks.C18.sample_repro_max_abs_cm` | 2.22e-16 |
| `checks.C18.tol_repro_cm` | 1e-12 |
| `checks.C18.R0_cm` | 2 |
| `checks.C18.R_end_cm` | 1.198 |
| `checks.C18.total_shrink_pct` | 40.1 |
| `checks.C18.passed` | True |
| `checks.C20.name` | `绝干骨架水量守恒（正向 + 三个反向变体）` |
| `checks.C20.forward_rel_drift` | 3.483e-16 |
| `checks.C20.tol_forward` | 1e-08 |
| `checks.C20.mass_kg_per_m_rel_drift_with_bookkeeping` | 3.331e-16 |
| `checks.C20.reverse_rel_drift.reverse_B_spurious_advection` | 0.109279 |
| `checks.C20.reverse_rel_drift.reverse_C_nonconservative` | 0.007219 |
| `checks.C20.reverse_rel_drift.reverse_A_drop_rho_d` | 0.610624 |
| `checks.C20.tol_reverse_min` | 0.0001 |
| `checks.C20.min_reverse_drift` | 0.007219 |
| `checks.C20.t_test_s` | 4.32e+04 |
| `checks.C20.R_cm_span[0]` | 2 |
| `checks.C20.R_cm_span[1]` | 1.248 |
| `checks.C20.rho_d_span[0]` | 278.732 |
| `checks.C20.rho_d_span[1]` | 715.844 |
| `checks.C20.note` | `反向 A 丢弃 rho_d(t) 记账、B 按 §7.5 再加 R*Rdot 对流通量、C 用非守恒 Lapl...` |
| `checks.C20.passed` | True |
| `checks.C22.name` | `t=0 收缩域退化为固定域` |
| `checks.C22.measured_max_abs_diff` | 0 |
| `checks.C22.tol` | 1e-12 |
| `checks.C22.R_at_0_cm` | 2 |
| `checks.C22.dRdt_at_0_cm_per_s` | 0 |
| `checks.C22.passed` | True |
| `checks.C_direction.name` | `收缩方向性判定（径向 vs 各向同性）` |
| `checks.C_direction.rho_d0` | 278.732 |
| `checks.C_direction.rho_d_end_radial` | 776.844 |
| `checks.C_direction.rho_d_end_isotropic` | 1297 |
| `checks.C_direction.reference_rho_zero_moisture` | 760 |
| `checks.C_direction.deviation_radial_pct` | 2.21631 |
| `checks.C_direction.deviation_isotropic_pct` | 70.6449 |
| `checks.C_direction.tol_accept_pct` | 5 |
| `checks.C_direction.tol_reject_pct` | 20 |
| `checks.C_direction.selected` | `radial` |
| `checks.C_direction.note` | `径向假设下末态绝干密度 776.84 kg/m^3 与附录 4 零含水率密度 760 相差 2.22%；各向同...` |
| `checks.C_direction.passed` | True |
| `checks.C_volume_consistency.name` | `收缩量自洽性（几何 vs 密度式反推）` |
| `checks.C_volume_consistency.volume_ratio_geometric` | 0.358801 |
| `checks.C_volume_consistency.volume_ratio_from_density` | 0.414405 |
| `checks.C_volume_consistency.relative_gap` | 0.134178 |
| `checks.C_volume_consistency.tol` | 0.2 |
| `checks.C_volume_consistency.rho_d_at_C_thr` | 672.609 |
| `checks.C_volume_consistency.note` | `附件 2 的几何收缩量 0.3588 与附录 4 密度式反推的 0.4144 差 13.42%；两者同阶但不完...` |
| `checks.C_volume_consistency.passed` | True |
| `checks.C19.name` | `首次下穿（密扫无更早穿越）` |
| `checks.C19.measured_endpoint_gap` | 0 |
| `checks.C19.tol` | 1e-05 |
| `checks.C19.n_scan_points` | 20000 |
| `checks.C19.n_points_below_thr` | 0 |
| `checks.C19.min_Cmax_before_t_end` | 0.15 |
| `checks.C19.passed` | True |
| `checks.C07.name` | `事件时刻最大值在中心` |
| `checks.C07.argmax_cell` | 0 |
| `checks.C07.C_center` | 0.15 |
| `checks.C07.C_outermost_cell` | 0.0586729 |
| `checks.C07.passed` | True |
| `checks.C21.name` | `归因分解闭合与交互项量化` |
| `checks.C21.chain_closure_s` | 0 |
| `checks.C21.tol_closure_s` | 1e-06 |
| `checks.C21.delta_props_s` | 2.608e+05 |
| `checks.C21.delta_shrink_s` | -2.841e+05 |
| `checks.C21.total_s` | -2.331e+04 |
| `checks.C21.interaction_s` | -1.676e+05 |
| `checks.C21.interaction_over_total_pct` | 719.19 |
| `checks.C21.mult_ratio_props` | 2.25696 |
| `checks.C21.mult_ratio_shrink` | 0.438674 |
| `checks.C21.mult_predicted_ratio` | 0.99007 |
| `checks.C21.mult_actual_ratio` | 0.887654 |
| `checks.C21.mult_residual_pct` | 10.3443 |
| `checks.C21.n_runs` | 4 |
| `checks.C21.note` | `附录 4 换物性使 t_end 增 72.43 h，径向收缩使其减 78.91 h，两者叠加只净减 6.47 ...` |
| `checks.C21.passed` | True |
| `checks.V3.2.name` | `网格收敛阶梯（t_end，五档）` |
| `checks.V3.2.dt_end_seq_s[0]` | 294.853 |
| `checks.V3.2.dt_end_seq_s[1]` | 122.438 |
| `checks.V3.2.dt_end_seq_s[2]` | 42.9203 |
| `checks.V3.2.dt_end_seq_s[3]` | 13.0635 |
| `checks.V3.2.dt_end_seq_rel[0]` | 0.0016 |
| `checks.V3.2.dt_end_seq_rel[1]` | 0.0006649 |
| `checks.V3.2.dt_end_seq_rel[2]` | 0.0002331 |
| `checks.V3.2.dt_end_seq_rel[3]` | 7.096e-05 |
| `checks.V3.2.finest_pair_s` | 13.0635 |
| `checks.V3.2.finest_pair_rel` | 7.096e-05 |
| `checks.V3.2.tol_rel` | 0.002 |
| `checks.V3.2.observed_order` | 1.71612 |
| `checks.V3.2.richardson_limit_s` | 1.841e+05 |
| `checks.V3.2.richardson_limit_h` | 51.134 |
| `checks.V3.2.baseline_minus_richardson_h` | 0.0171387 |
| `checks.V3.2.monotone_decreasing` | True |
| `checks.V3.2.note` | `与问题三同口径：表面重构与阈值定位均为一阶，故 t_end 用相对判据 0.2%，最细两档相对变化 0.007%` |
| `checks.V3.2.passed` | True |
| `checks.V3.3.name` | `时间容差对照（t_end）` |
| `checks.V3.3.measured_dt_end_s` | 0.0497595 |
| `checks.V3.3.tol` | 60 |
| `checks.V3.3.t_end_rtol_1e_6_s` | 1.841e+05 |
| `checks.V3.3.t_end_rtol_1e_8_s` | 1.841e+05 |
| `checks.V3.3.passed` | True |
| `checks.C16.name` | `写盘-读回往返一致（含空单元格掩码）` |
| `checks.C16.measured` | 0 |
| `checks.C16.tol` | 0 |
| `checks.C16.per_sheet.Sheet1.shape[0]` | 3069 |
| `checks.C16.per_sheet.Sheet1.shape[1]` | 21 |
| `checks.C16.per_sheet.Sheet1.roundtrip_max_abs_diff` | 0 |
| `checks.C16.per_sheet.Sheet1.blank_cells` | 20122 |
| `checks.C16.n_blank_cells` | 20122 |
| `checks.C16.blank_rule` | `r > R(t) 的格为空（药材已收缩到该位置以内）` |
| `checks.C16.passed` | True |
| `checks.C20_balance.name` | `全局水量平衡闭合（h_m 非零）` |
| `checks.C20_balance.measured_rel_gap` | 9.398e-05 |
| `checks.C20_balance.tol` | 0.001 |
| `checks.C20_balance.stored_drop_kg_per_m` | 0.851701 |
| `checks.C20_balance.cumulative_flux_kg_per_m` | 0.851781 |
| `checks.C20_balance.m_w_initial_kg_per_m` | 0.893177 |
| `checks.C20_balance.m_w_final_kg_per_m` | 0.0414757 |
| `checks.C20_balance.note` | `储量按 2*pi*rho_d(t)*R(t)^2*sum(V_i C_i) 记，失水按表面对流通量在 60 s...` |
| `checks.C20_balance.passed` | True |
| `checks.C13.name` | `干燥方向性（全程）` |
| `checks.C13.max_rise_of_Cmax` | 0 |
| `checks.C13.max_rise_of_volavg` | -2.094e-05 |
| `checks.C13.tol` | 1e-12 |
| `checks.C13.passed` | True |
| `checks.V2.4.name` | `温度落在驱动包络内` |
| `checks.V2.4.T_min` | 28 |
| `checks.V2.4.T_max` | 50.05 |
| `checks.V2.4.envelope[0]` | 28 |
| `checks.V2.4.envelope[1]` | 50.246 |
| `checks.V2.4.passed` | True |
| `checks.V3.12.name` | `与题面 2-3 天量级对照` |
| `checks.V3.12.measured_days` | 2.1313 |
| `checks.V3.12.reference_range_days[0]` | 2 |
| `checks.V3.12.reference_range_days[1]` | 3 |
| `checks.V3.12.inside_range` | True |
| `checks.V3.12.note` | `量级参照，非标定目标` |
| `checks.V3.12.passed` | True |
| `all_checks_passed` | True |

### `sensitivity_results.json`（504 条）

| 数据路径 | 数值 |
|---|---|
| `base_appendix` | `appendix_3` |
| `seed` | 20260910 |
| `n_lhs` | 200 |
| `factors[0].name` | `h_m` |
| `factors[0].kind` | `h_m` |
| `factors[0].amplitude` | 0.3 |
| `factors[0].label` | `对流传质系数 h_m` |
| `factors[1].name` | `h` |
| `factors[1].kind` | `h` |
| `factors[1].amplitude` | 0.3 |
| `factors[1].label` | `对流换热系数 h` |
| `factors[2].name` | `ta_plateau` |
| `factors[2].kind` | `abs` |
| `factors[2].amplitude` | 1 |
| `factors[2].label` | `平台热风温度 Ta` |
| `factors[7].name` | `moist_scale` |
| `factors[7].kind` | `moist_scale` |
| `factors[7].amplitude` | 0.1 |
| `factors[7].label` | `水分抑制常数 b` |
| `factors[...]` | `<4 项省略>` |
| `baseline.t_end_s` | 2.075e+05 |
| `baseline.t_end_h` | 57.6251 |
| `baseline.nfev` | 21261 |
| `baseline_q4.t_end_s` | 1.841e+05 |
| `baseline_q4.t_end_h` | 51.1511 |
| `baseline_q4.nfev` | 20764 |
| `baseline_q4.appendix` | `appendix_4` |
| `baseline_q4.moving_boundary` | True |
| `oat[0].amplitude` | 0.3 |
| `oat[0].delta_h` | 2.95427 |
| `oat[0].delta_pct` | 5.12671 |
| `oat[0].factor` | `h_m` |
| `oat[0].kind` | `h_m` |
| `oat[0].label` | `对流传质系数 h_m` |
| `oat[0].multiplier` | 0.7 |
| `oat[0].nfev` | 20840 |
| `oat[0].sign` | -1 |
| `oat[0].t_end_h` | 60.5794 |
| `oat[0].t_end_s` | 2.181e+05 |
| `oat[1].amplitude` | 0.3 |
| `oat[1].delta_h` | -1.38871 |
| `oat[1].delta_pct` | -2.40991 |
| `oat[1].factor` | `h_m` |
| `oat[1].kind` | `h_m` |
| `oat[1].label` | `对流传质系数 h_m` |
| `oat[1].multiplier` | 1.3 |
| `oat[1].nfev` | 21387 |
| `oat[1].sign` | 1 |
| `oat[1].t_end_h` | 56.2364 |
| `oat[1].t_end_s` | 2.025e+05 |
| `oat[2].amplitude` | 0.3 |
| `oat[2].delta_h` | 0.0338513 |
| `oat[2].delta_pct` | 0.058744 |
| `oat[2].factor` | `h` |
| `oat[2].kind` | `h` |
| `oat[2].label` | `对流换热系数 h` |
| `oat[2].multiplier` | 0.7 |
| `oat[2].nfev` | 20355 |
| `oat[2].sign` | -1 |
| `oat[2].t_end_h` | 57.6589 |
| `oat[2].t_end_s` | 2.076e+05 |
| `oat[15].amplitude` | 0.1 |
| `oat[15].delta_h` | 16.0931 |
| `oat[15].delta_pct` | 27.9273 |
| `oat[15].factor` | `moist_scale` |
| `oat[15].kind` | `moist_scale` |
| `oat[15].label` | `水分抑制常数 b` |
| `oat[15].multiplier` | 1.1 |
| `oat[15].nfev` | 23142 |
| `oat[15].sign` | 1 |
| `oat[15].t_end_h` | 73.7182 |
| `oat[15].t_end_s` | 2.654e+05 |
| `oat[...]` | `<12 项省略>` |
| `tornado.order[0]` | `act_scale` |
| `tornado.order[1]` | `moist_scale` |
| `tornado.order[2]` | `d_scale` |
| `tornado.order[7]` | `h` |
| `tornado.order[...]` | `<4 项省略>` |
| `tornado.by_factor.h_m.label` | `对流传质系数 h_m` |
| `tornado.by_factor.h_m.amplitude` | 0.3 |
| `tornado.by_factor.h_m.kind` | `h_m` |
| `tornado.by_factor.h_m.t_end_h_low` | 60.5794 |
| `tornado.by_factor.h_m.t_end_h_high` | 56.2364 |
| `tornado.by_factor.h_m.delta_pct_low` | 5.12671 |
| `tornado.by_factor.h_m.delta_pct_high` | -2.40991 |
| `tornado.by_factor.h_m.half_range_h` | 2.17149 |
| `tornado.by_factor.h_m.elasticity` | -0.12561 |
| `tornado.by_factor.h.label` | `对流换热系数 h` |
| `tornado.by_factor.h.amplitude` | 0.3 |
| `tornado.by_factor.h.kind` | `h` |
| `tornado.by_factor.h.t_end_h_low` | 57.6589 |
| `tornado.by_factor.h.t_end_h_high` | 57.6071 |
| `tornado.by_factor.h.delta_pct_low` | 0.058744 |
| `tornado.by_factor.h.delta_pct_high` | -0.0312328 |
| `tornado.by_factor.h.half_range_h` | 0.0259246 |
| `tornado.by_factor.h.elasticity` | -0.0015 |
| `tornado.by_factor.ta_plateau.label` | `平台热风温度 Ta` |
| `tornado.by_factor.ta_plateau.amplitude` | 1 |
| `tornado.by_factor.ta_plateau.kind` | `abs` |
| `tornado.by_factor.ta_plateau.t_end_h_low` | 59.5012 |
| `tornado.by_factor.ta_plateau.t_end_h_high` | 55.8312 |
| `tornado.by_factor.ta_plateau.delta_pct_low` | 3.25565 |
| `tornado.by_factor.ta_plateau.delta_pct_high` | -3.11307 |
| `tornado.by_factor.ta_plateau.half_range_h` | 1.83499 |
| `tornado.by_factor.ta_plateau.elasticity` | -0.0318436 |
| `tornado.by_factor.ca_plateau.label` | `平台空气含湿量 Ca` |
| `tornado.by_factor.ca_plateau.amplitude` | 0.2 |
| `tornado.by_factor.ca_plateau.kind` | `ca_plateau` |
| `tornado.by_factor.ca_plateau.t_end_h_low` | 57.596 |
| `tornado.by_factor.ca_plateau.t_end_h_high` | 57.8068 |
| `tornado.by_factor.ca_plateau.delta_pct_low` | -0.0504927 |
| `tornado.by_factor.ca_plateau.delta_pct_high` | 0.315312 |
| `tornado.by_factor.ca_plateau.half_range_h` | 0.105398 |
| `tornado.by_factor.ca_plateau.elasticity` | 0.009145 |
| `tornado.by_factor.d_scale.label` | `扩散前因子 D0` |
| `tornado.by_factor.d_scale.amplitude` | 0.2 |
| `tornado.by_factor.d_scale.kind` | `d_scale` |
| `tornado.by_factor.d_scale.t_end_h_low` | 70.4561 |
| `tornado.by_factor.d_scale.t_end_h_high` | 49.1559 |
| `tornado.by_factor.d_scale.delta_pct_low` | 22.2664 |
| `tornado.by_factor.d_scale.delta_pct_high` | -14.697 |
| `tornado.by_factor.d_scale.half_range_h` | 10.6501 |
| `tornado.by_factor.d_scale.elasticity` | -0.924085 |
| `tornado.by_factor.act_scale.label` | `Arrhenius 活化温度 3850 K` |
| `tornado.by_factor.act_scale.amplitude` | 0.05 |
| `tornado.by_factor.act_scale.kind` | `act` |
| `tornado.by_factor.act_scale.t_end_h_low` | 35.0608 |
| `tornado.by_factor.act_scale.t_end_h_high` | 99.7772 |
| `tornado.by_factor.act_scale.delta_pct_low` | -39.157 |
| `tornado.by_factor.act_scale.delta_pct_high` | 73.1489 |
| `tornado.by_factor.act_scale.half_range_h` | 32.3582 |
| `tornado.by_factor.act_scale.elasticity` | 11.2306 |
| `tornado.by_factor.C0.label` | `初始含水率 C0` |
| `tornado.by_factor.C0.amplitude` | 0.05 |
| `tornado.by_factor.C0.kind` | `C0` |
| `tornado.by_factor.C0.t_end_h_low` | 57.381 |
| `tornado.by_factor.C0.t_end_h_high` | 57.8565 |
| `tornado.by_factor.C0.delta_pct_low` | -0.423642 |
| `tornado.by_factor.C0.delta_pct_high` | 0.401543 |
| `tornado.by_factor.C0.half_range_h` | 0.237757 |
| `tornado.by_factor.C0.elasticity` | 0.0825185 |
| `tornado.by_factor.moist_scale.label` | `水分抑制常数 b` |
| `tornado.by_factor.moist_scale.amplitude` | 0.1 |
| `tornado.by_factor.moist_scale.kind` | `moist_scale` |
| `tornado.by_factor.moist_scale.t_end_h_low` | 45.6516 |
| `tornado.by_factor.moist_scale.t_end_h_high` | 73.7182 |
| `tornado.by_factor.moist_scale.delta_pct_low` | -20.7782 |
| `tornado.by_factor.moist_scale.delta_pct_high` | 27.9273 |
| `tornado.by_factor.moist_scale.half_range_h` | 14.0333 |
| `tornado.by_factor.moist_scale.elasticity` | 2.43527 |
| `tornado.baseline_h` | 57.6251 |
| `latent_scan.chi_values[0]` | 0 |
| `latent_scan.chi_values[1]` | 0.1 |
| `latent_scan.chi_values[2]` | 0.25 |
| `latent_scan.chi_values[3]` | 0.5 |
| `latent_scan.rows[0].T_center_at_1800s_C` | 32.1893 |
| `latent_scan.rows[0].T_center_min_C` | 28 |
| `latent_scan.rows[0].T_field_min_C` | 28 |
| `latent_scan.rows[0].chi` | 0 |
| `latent_scan.rows[0].delta_pct` | 0 |
| `latent_scan.rows[0].fired` | True |
| `latent_scan.rows[0].nfev` | 21261 |
| `latent_scan.rows[0].t_end_h` | 57.6251 |
| `latent_scan.rows[0].t_end_s` | 2.075e+05 |
| `latent_scan.rows[1].T_center_at_1800s_C` | 29.3773 |
| `latent_scan.rows[1].T_center_min_C` | 27.3847 |
| `latent_scan.rows[1].T_field_min_C` | 27.1048 |
| `latent_scan.rows[1].chi` | 0.1 |
| `latent_scan.rows[1].delta_pct` | 0.953503 |
| `latent_scan.rows[1].fired` | True |
| `latent_scan.rows[1].nfev` | 21629 |
| `latent_scan.rows[1].t_end_h` | 58.1745 |
| `latent_scan.rows[1].t_end_s` | 2.094e+05 |
| `latent_scan.rows[2].T_center_at_1800s_C` | 25.3742 |
| `latent_scan.rows[2].T_center_min_C` | 24.8588 |
| `latent_scan.rows[2].T_field_min_C` | 24.7062 |
| `latent_scan.rows[2].chi` | 0.25 |
| `latent_scan.rows[2].delta_pct` | 2.43346 |
| `latent_scan.rows[2].fired` | True |
| `latent_scan.rows[2].nfev` | 21927 |
| `latent_scan.rows[2].t_end_h` | 59.0274 |
| `latent_scan.rows[2].t_end_s` | 2.125e+05 |
| `latent_scan.rows[3].T_center_at_1800s_C` | 19.2176 |
| `latent_scan.rows[3].T_center_min_C` | 19.2141 |
| `latent_scan.rows[3].T_field_min_C` | 19.1837 |
| `latent_scan.rows[3].chi` | 0.5 |
| `latent_scan.rows[3].delta_pct` | 5.00064 |
| `latent_scan.rows[3].fired` | True |
| `latent_scan.rows[3].nfev` | 22665 |
| `latent_scan.rows[3].t_end_h` | 60.5067 |
| `latent_scan.rows[3].t_end_s` | 2.178e+05 |
| `latent_scan.note` | `chi=0 为本文基准：题面未给潜热与相变速率数据，故不引入未给定参数；chi>0 只作情景界定` |
| `response_surface.d0_mult[0]` | 0.8 |
| `response_surface.d0_mult[1]` | 0.866667 |
| `response_surface.d0_mult[2]` | 0.933333 |
| `response_surface.d0_mult[6]` | 1.2 |
| `response_surface.d0_mult[...]` | `<3 项省略>` |
| `response_surface.grid[0][0]` | 73.1618 |
| `response_surface.grid[0][1]` | 68.3023 |
| `response_surface.grid[0][2]` | 64.1562 |
| `response_surface.grid[0][6]` | 52.3046 |
| `response_surface.grid[0][...]` | `<3 项省略>` |
| `response_surface.grid[1][0]` | 71.9834 |
| `response_surface.grid[1][1]` | 67.0871 |
| `response_surface.grid[1][2]` | 62.9074 |
| `response_surface.grid[1][6]` | 50.9462 |
| `response_surface.grid[1][...]` | `<3 项省略>` |
| `response_surface.grid[2][0]` | 71.1153 |
| `response_surface.grid[2][1]` | 66.1894 |
| `response_surface.grid[2][2]` | 61.9829 |
| `response_surface.grid[2][6]` | 49.9336 |
| `response_surface.grid[2][...]` | `<3 项省略>` |
| `response_surface.grid[6][0]` | 69.209 |
| `response_surface.grid[6][1]` | 64.2079 |
| `response_surface.grid[6][2]` | 59.9324 |
| `response_surface.grid[6][6]` | 47.6546 |
| `response_surface.grid[6][...]` | `<3 项省略>` |
| `response_surface.grid[...]` | `<3 项省略>` |
| `response_surface.hm_mult[0]` | 0.7 |
| `response_surface.hm_mult[1]` | 0.8 |
| `response_surface.hm_mult[2]` | 0.9 |
| `response_surface.hm_mult[6]` | 1.3 |
| `response_surface.hm_mult[...]` | `<3 项省略>` |
| `lhs.n` | 200 |
| `lhs.seed` | 20260910 |
| `lhs.rows[0].delta_pct` | -22.2494 |
| `lhs.rows[0].i` | 0 |
| `lhs.rows[0].multipliers.C0` | 1.03611 |
| `lhs.rows[0].multipliers.act_scale` | 1.00957 |
| `lhs.rows[0].multipliers.ca_plateau` | 1.04871 |
| `lhs.rows[0].multipliers.d_scale` | 1.19724 |
| `lhs.rows[0].multipliers.h` | 0.972036 |
| `lhs.rows[0].multipliers.h_m` | 1.02501 |
| `lhs.rows[0].multipliers.moist_scale` | 0.925065 |
| `lhs.rows[0].multipliers.ta_plateau` | 1.68125 |
| `lhs.rows[0].nfev` | 19673 |
| `lhs.rows[0].t_end_h` | 44.8038 |
| `lhs.rows[0].t_end_s` | 1.613e+05 |
| `lhs.rows[1].delta_pct` | -11.6407 |
| `lhs.rows[1].i` | 1 |
| `lhs.rows[1].multipliers.C0` | 0.965248 |
| `lhs.rows[1].multipliers.act_scale` | 0.977057 |
| `lhs.rows[1].multipliers.ca_plateau` | 0.834438 |
| `lhs.rows[1].multipliers.d_scale` | 1.09318 |
| `lhs.rows[1].multipliers.h` | 0.92597 |
| `lhs.rows[1].multipliers.h_m` | 1.10482 |
| `lhs.rows[1].multipliers.moist_scale` | 1.09233 |
| `lhs.rows[1].multipliers.ta_plateau` | 1.40428 |
| `lhs.rows[1].nfev` | 20362 |
| `lhs.rows[1].t_end_h` | 50.9171 |
| `lhs.rows[1].t_end_s` | 1.833e+05 |
| `lhs.rows[2].delta_pct` | -22.8448 |
| `lhs.rows[2].i` | 2 |
| `lhs.rows[2].multipliers.C0` | 0.981392 |
| `lhs.rows[2].multipliers.act_scale` | 0.962313 |
| `lhs.rows[2].multipliers.ca_plateau` | 1.11678 |
| `lhs.rows[2].multipliers.d_scale` | 1.06677 |
| `lhs.rows[2].multipliers.h` | 1.2237 |
| `lhs.rows[2].multipliers.h_m` | 1.17818 |
| `lhs.rows[2].multipliers.moist_scale` | 1.09827 |
| `lhs.rows[2].multipliers.ta_plateau` | 1.79849 |
| `lhs.rows[2].nfev` | 20284 |
| `lhs.rows[2].t_end_h` | 44.4608 |
| `lhs.rows[2].t_end_s` | 1.601e+05 |
| `lhs.rows[199].delta_pct` | -18.1535 |
| `lhs.rows[199].i` | 199 |
| `lhs.rows[199].multipliers.C0` | 1.0249 |
| `lhs.rows[199].multipliers.act_scale` | 0.974598 |
| `lhs.rows[199].multipliers.ca_plateau` | 1.14086 |
| `lhs.rows[199].multipliers.d_scale` | 0.876879 |
| `lhs.rows[199].multipliers.h` | 1.14804 |
| `lhs.rows[199].multipliers.h_m` | 0.762365 |
| `lhs.rows[199].multipliers.moist_scale` | 0.950449 |
| `lhs.rows[199].multipliers.ta_plateau` | 0.875218 |
| `lhs.rows[199].nfev` | 19943 |
| `lhs.rows[199].t_end_h` | 47.1641 |
| `lhs.rows[199].t_end_s` | 1.698e+05 |
| `lhs.rows[...]` | `<196 项省略>` |
| `lhs.t_end_h.mean` | 62.6117 |
| `lhs.t_end_h.std` | 22.4426 |
| `lhs.t_end_h.cv` | 0.358441 |
| `lhs.t_end_h.p05` | 35.8451 |
| `lhs.t_end_h.p50` | 57.5875 |
| `lhs.t_end_h.p95` | 108.744 |
| `lhs.t_end_h.min` | 26.1045 |
| `lhs.t_end_h.max` | 128.003 |
| `lhs.fraction_in_2_3_days` | 0.395 |
| `lhs.fraction_below_2_days` | 0.32 |
| `lhs.fraction_above_3_days` | 0.285 |
| `lhs.spearman.h_m` | -0.018254 |
| `lhs.spearman.h` | -0.0281152 |
| `lhs.spearman.ta_plateau` | -0.0428591 |
| `lhs.spearman.ca_plateau` | 0.0398185 |
| `lhs.spearman.d_scale` | -0.207934 |
| `lhs.spearman.act_scale` | 0.86807 |
| `lhs.spearman.C0` | 0.0871567 |
| `lhs.spearman.moist_scale` | 0.411757 |
| `lhs.histogram.counts[0]` | 3 |
| `lhs.histogram.counts[1]` | 5 |
| `lhs.histogram.counts[2]` | 16 |
| `lhs.histogram.counts[23]` | 4 |
| `lhs.histogram.counts[...]` | `<20 项省略>` |
| `lhs.histogram.edges_h[0]` | 26.1045 |
| `lhs.histogram.edges_h[1]` | 30.3503 |
| `lhs.histogram.edges_h[2]` | 34.5961 |
| `lhs.histogram.edges_h[24]` | 128.003 |
| `lhs.histogram.edges_h[...]` | `<21 项省略>` |
| `lhs_q4.n` | 200 |
| `lhs_q4.seed` | 20260910 |
| `lhs_q4.appendix` | `appendix_4` |
| `lhs_q4.moving_boundary` | True |
| `lhs_q4.rows[0].delta_pct` | -16.7048 |
| `lhs_q4.rows[0].i` | 0 |
| `lhs_q4.rows[0].multipliers.C0` | 1.03611 |
| `lhs_q4.rows[0].multipliers.act_scale` | 1.00957 |
| `lhs_q4.rows[0].multipliers.ca_plateau` | 1.04871 |
| `lhs_q4.rows[0].multipliers.d_scale` | 1.19724 |
| `lhs_q4.rows[0].multipliers.h` | 0.972036 |
| `lhs_q4.rows[0].multipliers.h_m` | 1.02501 |
| `lhs_q4.rows[0].multipliers.moist_scale` | 0.925065 |
| `lhs_q4.rows[0].multipliers.ta_plateau` | 1.68125 |
| `lhs_q4.rows[0].nfev` | 19587 |
| `lhs_q4.rows[0].t_end_h` | 42.6064 |
| `lhs_q4.rows[0].t_end_s` | 1.534e+05 |
| `lhs_q4.rows[1].delta_pct` | -18.2664 |
| `lhs_q4.rows[1].i` | 1 |
| `lhs_q4.rows[1].multipliers.C0` | 0.965248 |
| `lhs_q4.rows[1].multipliers.act_scale` | 0.977057 |
| `lhs_q4.rows[1].multipliers.ca_plateau` | 0.834438 |
| `lhs_q4.rows[1].multipliers.d_scale` | 1.09318 |
| `lhs_q4.rows[1].multipliers.h` | 0.92597 |
| `lhs_q4.rows[1].multipliers.h_m` | 1.10482 |
| `lhs_q4.rows[1].multipliers.moist_scale` | 1.09233 |
| `lhs_q4.rows[1].multipliers.ta_plateau` | 1.40428 |
| `lhs_q4.rows[1].nfev` | 19319 |
| `lhs_q4.rows[1].t_end_h` | 41.8077 |
| `lhs_q4.rows[1].t_end_s` | 1.505e+05 |
| `lhs_q4.rows[2].delta_pct` | -28.1601 |
| `lhs_q4.rows[2].i` | 2 |
| `lhs_q4.rows[2].multipliers.C0` | 0.981392 |
| `lhs_q4.rows[2].multipliers.act_scale` | 0.962313 |
| `lhs_q4.rows[2].multipliers.ca_plateau` | 1.11678 |
| `lhs_q4.rows[2].multipliers.d_scale` | 1.06677 |
| `lhs_q4.rows[2].multipliers.h` | 1.2237 |
| `lhs_q4.rows[2].multipliers.h_m` | 1.17818 |
| `lhs_q4.rows[2].multipliers.moist_scale` | 1.09827 |
| `lhs_q4.rows[2].multipliers.ta_plateau` | 1.79849 |
| `lhs_q4.rows[2].nfev` | 19442 |
| `lhs_q4.rows[2].t_end_h` | 36.7469 |
| `lhs_q4.rows[2].t_end_s` | 1.323e+05 |
| `lhs_q4.rows[199].delta_pct` | -16.7415 |
| `lhs_q4.rows[199].i` | 199 |
| `lhs_q4.rows[199].multipliers.C0` | 1.0249 |
| `lhs_q4.rows[199].multipliers.act_scale` | 0.974598 |
| `lhs_q4.rows[199].multipliers.ca_plateau` | 1.14086 |
| `lhs_q4.rows[199].multipliers.d_scale` | 0.876879 |
| `lhs_q4.rows[199].multipliers.h` | 1.14804 |
| `lhs_q4.rows[199].multipliers.h_m` | 0.762365 |
| `lhs_q4.rows[199].multipliers.moist_scale` | 0.950449 |
| `lhs_q4.rows[199].multipliers.ta_plateau` | 0.875218 |
| `lhs_q4.rows[199].nfev` | 19802 |
| `lhs_q4.rows[199].t_end_h` | 42.5877 |
| `lhs_q4.rows[199].t_end_s` | 1.533e+05 |
| `lhs_q4.rows[...]` | `<196 项省略>` |
| `lhs_q4.t_end_h.mean` | 54.9284 |
| `lhs_q4.t_end_h.std` | 18.3611 |
| `lhs_q4.t_end_h.cv` | 0.334273 |
| `lhs_q4.t_end_h.p05` | 32.1911 |
| `lhs_q4.t_end_h.p50` | 51.8475 |
| `lhs_q4.t_end_h.p95` | 91.5737 |
| `lhs_q4.t_end_h.min` | 25.638 |
| `lhs_q4.t_end_h.max` | 108.217 |
| `lhs_q4.fraction_in_2_3_days` | 0.4 |
| `lhs_q4.fraction_below_2_days` | 0.425 |
| `lhs_q4.fraction_above_3_days` | 0.175 |
| `lhs_q4.spearman.h_m` | 0.0228621 |
| `lhs_q4.spearman.h` | -0.040381 |
| `lhs_q4.spearman.ta_plateau` | -0.0455561 |
| `lhs_q4.spearman.ca_plateau` | 0.0379074 |
| `lhs_q4.spearman.d_scale` | -0.22123 |
| `lhs_q4.spearman.act_scale` | 0.917391 |
| `lhs_q4.spearman.C0` | 0.0934433 |
| `lhs_q4.spearman.moist_scale` | 0.270643 |
| `lhs_q4.histogram.counts[0]` | 4 |
| `lhs_q4.histogram.counts[1]` | 9 |
| `lhs_q4.histogram.counts[2]` | 15 |
| `lhs_q4.histogram.counts[23]` | 2 |
| `lhs_q4.histogram.counts[...]` | `<20 项省略>` |
| `lhs_q4.histogram.edges_h[0]` | 25.638 |
| `lhs_q4.histogram.edges_h[1]` | 29.0788 |
| `lhs_q4.histogram.edges_h[2]` | 32.5196 |
| `lhs_q4.histogram.edges_h[24]` | 108.217 |
| `lhs_q4.histogram.edges_h[...]` | `<21 项省略>` |
| `robustness_pair.label_q3` | `问题三口径（附录 3 + 固定域）` |
| `robustness_pair.label_q4` | `问题四口径（附录 4 + 径向收缩）` |
| `robustness_pair.n` | 200 |
| `robustness_pair.baseline_q3_h` | 57.6251 |
| `robustness_pair.baseline_q4_h` | 51.1511 |
| `robustness_pair.t_end_h_q3[0]` | 44.8038 |
| `robustness_pair.t_end_h_q3[1]` | 50.9171 |
| `robustness_pair.t_end_h_q3[2]` | 44.4608 |
| `robustness_pair.t_end_h_q3[199]` | 47.1641 |
| `robustness_pair.t_end_h_q3[...]` | `<196 项省略>` |
| `robustness_pair.t_end_h_q4[0]` | 42.6064 |
| `robustness_pair.t_end_h_q4[1]` | 41.8077 |
| `robustness_pair.t_end_h_q4[2]` | 36.7469 |
| `robustness_pair.t_end_h_q4[199]` | 42.5877 |
| `robustness_pair.t_end_h_q4[...]` | `<196 项省略>` |
| `robustness_pair.ratio_q4_over_q3[0]` | 0.950955 |
| `robustness_pair.ratio_q4_over_q3[1]` | 0.821093 |
| `robustness_pair.ratio_q4_over_q3[2]` | 0.826503 |
| `robustness_pair.ratio_q4_over_q3[199]` | 0.902968 |
| `robustness_pair.ratio_q4_over_q3[...]` | `<196 项省略>` |
| `robustness_pair.q4_shorter_fraction` | 1 |
| `robustness_pair.note` | `同一 LHS 矩阵驱动两种口径，逐样本配对；雨云图左右两半即这两列` |
| `checks.C23.name` | `敏感性逐点真实重算` |
| `checks.C23.n_oat_points` | 16 |
| `checks.C23.n_lhs_points` | 200 |
| `checks.C23.n_lhs_q4_points` | 200 |
| `checks.C23.n_surface_points` | 49 |
| `checks.C23.min_abs_gap_to_baseline_s` | 64.7925 |
| `checks.C23.tol_gap_s` | 60 |
| `checks.C23.lhs_min_pairwise_gap_s` | 0.978556 |
| `checks.C23.lhs_q4_min_pairwise_gap_s` | 3.77704 |
| `checks.C23.n_distinct_lhs_t_end` | 200 |
| `checks.C23.n_distinct_lhs_q4_t_end` | 200 |
| `checks.C23.total_real_solves` | 471 |
| `checks.C23.checkpoint_hits.oat_latent` | True |
| `checks.C23.checkpoint_hits.surface` | True |
| `checks.C23.checkpoint_hits.lhs` | True |
| `checks.C23.checkpoint_hits.lhs_q4` | True |
| `checks.C23.passed` | True |
| `checks.V3.9.name` | `敏感性排序一致（OAT 首因子 = 秩相关首因子）` |
| `checks.V3.9.oat_rank[0]` | `act_scale` |
| `checks.V3.9.oat_rank[1]` | `moist_scale` |
| `checks.V3.9.oat_rank[2]` | `d_scale` |
| `checks.V3.9.oat_rank[7]` | `h` |
| `checks.V3.9.oat_rank[...]` | `<4 项省略>` |
| `checks.V3.9.top_oat` | `act_scale` |
| `checks.V3.9.top_spearman` | `act_scale` |
| `checks.V3.9.spearman.h_m` | -0.018254 |
| `checks.V3.9.spearman.h` | -0.0281152 |
| `checks.V3.9.spearman.ta_plateau` | -0.0428591 |
| `checks.V3.9.spearman.ca_plateau` | 0.0398185 |
| `checks.V3.9.spearman.d_scale` | -0.207934 |
| `checks.V3.9.spearman.act_scale` | 0.86807 |
| `checks.V3.9.spearman.C0` | 0.0871567 |
| `checks.V3.9.spearman.moist_scale` | 0.411757 |
| `checks.V3.9.passed` | True |
| `checks.V3.10.name` | `单因子弹性符号与机理一致` |
| `checks.V3.10.expected.h_m` | -1 |
| `checks.V3.10.expected.h` | -1 |
| `checks.V3.10.expected.ta_plateau` | -1 |
| `checks.V3.10.expected.ca_plateau` | 1 |
| `checks.V3.10.expected.d_scale` | -1 |
| `checks.V3.10.expected.act_scale` | 1 |
| `checks.V3.10.expected.C0` | 1 |
| `checks.V3.10.expected.moist_scale` | 1 |
| `checks.V3.10.observed.h_m` | -1 |
| `checks.V3.10.observed.h` | -1 |
| `checks.V3.10.observed.ta_plateau` | -1 |
| `checks.V3.10.observed.ca_plateau` | 1 |
| `checks.V3.10.observed.d_scale` | -1 |
| `checks.V3.10.observed.act_scale` | 1 |
| `checks.V3.10.observed.C0` | 1 |
| `checks.V3.10.observed.moist_scale` | 1 |
| `checks.V3.10.note` | `h_m/h/Ta/D0 增大加快干燥（t_end 下降），Ca/活化温度/C0/水分抑制常数 b 增大延长干燥...` |
| `checks.V3.10.passed` | True |
| `checks.V3.11.name` | `响应面双向单调` |
| `checks.V3.11.monotone_along_D0` | True |
| `checks.V3.11.monotone_along_hm` | True |
| `checks.V3.11.span_h[0]` | 47.6546 |
| `checks.V3.11.span_h[1]` | 73.1618 |
| `checks.V3.11.corner_ratio` | 1.53525 |
| `checks.V3.11.passed` | True |
| `checks.V3.4.name` | `潜热方向探针（t_end 随 chi 单调增大）` |
| `checks.V3.4.chi_values[0]` | 0 |
| `checks.V3.4.chi_values[1]` | 0.1 |
| `checks.V3.4.chi_values[2]` | 0.25 |
| `checks.V3.4.chi_values[3]` | 0.5 |
| `checks.V3.4.n_fired` | 4 |
| `checks.V3.4.n_scanned` | 4 |
| `checks.V3.4.t_end_h_by_chi[0]` | 57.6251 |
| `checks.V3.4.t_end_h_by_chi[1]` | 58.1745 |
| `checks.V3.4.t_end_h_by_chi[2]` | 59.0274 |
| `checks.V3.4.t_end_h_by_chi[3]` | 60.5067 |
| `checks.V3.4.T_field_min_C_by_chi[0]` | 28 |
| `checks.V3.4.T_field_min_C_by_chi[1]` | 27.1048 |
| `checks.V3.4.T_field_min_C_by_chi[2]` | 24.7062 |
| `checks.V3.4.T_field_min_C_by_chi[3]` | 19.1837 |
| `checks.V3.4.monotone_increasing` | True |
| `checks.V3.4.note` | `chi=0 为基准；未触发的 chi 说明其 t_end 超出保护上限 1.2e+06 s，方向同样成立` |
| `checks.V3.4.passed` | True |
| `checks.V3.13.name` | `问题三/四鲁棒性配对同源（同一 LHS 矩阵）` |
| `checks.V3.13.n_pairs` | 200 |
| `checks.V3.13.multipliers_identical` | True |
| `checks.V3.13.q4_shorter_fraction` | 1 |
| `checks.V3.13.ratio_q4_over_q3.mean` | 0.884924 |
| `checks.V3.13.ratio_q4_over_q3.min` | 0.794432 |
| `checks.V3.13.ratio_q4_over_q3.max` | 0.983037 |
| `checks.V3.13.note` | `两条分布共用同一组因子取值，故雨云图是配对对比；q4/q3 比值恒小于 1 即收缩缩短工期这一结论在全分布上稳健` |
| `checks.V3.13.passed` | True |
| `all_checks_passed` | True |
| `wall_time_s` | 4.48297 |
