# 图表生成步骤报告（数据图 · nature 风格）

**步骤**：10 步流程第 4 步「图表生成」中的**数据图**部分
**范围**：`PROBLEM_ANALYSIS.md` 的 `FIGURE_MANIFEST` 中 `DATA` 段 24 张
**不在本轮范围**：HTML 流程/架构图 5 张、TikZ 机理示意图 3 张（属下一步骤；`figure_check.sh`
的 5 条 `MISSING` 即指这 5 张流程图，为预期状态而非缺陷）

## 一、结论

| 项目 | 结果 |
| --- | --- |
| 规划数据图 | 24 张 |
| 已出脚本 / PNG | 24 / 24 |
| 规划外多余 PNG | 无 |
| panel 数对账（运行时实测） | 24/24 一致 |
| 闸门 `bash _utils/figure_check.sh` | **EXIT=0**（0 违规 + 1 可升级 + 0 配方问题） |
| 视觉复核（`MH_DATA_FIG_VISION=1`） | 24 张全部 passed，0 待修，0 跳过 |
| 交付物 `figures/latex_includes.tex` | 已生成，语法自检 0 issue |
| 交付物 `figures/figure_captions.md` | 已生成（Word 口径同源伴生件） |
| 分辨率 | 24 张全部 350 dpi，无任何 PDF 产物 |

## 二、交付物

### 1. `figures/latex_includes.tex`（声明的最低交付物）

24 个 `figure[H]` 块，每块含 `\includegraphics[width=<分数>\textwidth]`、短题注
`\caption[...]`（供图目录）、完整题注、`\label{fig:<名>}`。

`width` 分数不是估的，而是从每张图脚本里正则读出它实际调用的
`set_paper_placement(fig, X)`，避免题注宽度与出图宽度脱钩。

### 2. `figures/figure_captions.md`（同源伴生件）

`CLAUDE.md` 规定本流程导出 **Word（DOCX）**、写作步骤产出**纯 Markdown**、图片用
`![描述](figures/xxx.png)`。若只交 `.tex`，写作步骤仍需把 24 条题注里的几百个数字手抄一遍到
Markdown，这正是"数字漂移"最容易发生的地方。因此同一个生成器一并输出 Markdown 版：同一份
`CAP`/`SHORT` 字典、同一批现读数字，只把 `\,`→空格、`\%`→`%`、`--`→`–`、`\emph{}`→`*..*` 做记号降级。

写作步骤应直接引用本文件，不要另行手写数字。

> 附带发现（未擅自改动）：`CLAUDE.md:187` 写"按 `figures/latex_includes.tex` 里已生成的
> `fig_*.pdf` 直接引用"，但同一文件 195 行起明确本流程为 PNG-only Word 口径。已按 PNG 口径生成
> （`includegraphics{figures/*.png}`）。该行文字与实际口径不符，属流程模板遗留，留待模板维护者决定。

### 3. 生成脚本 `_tmp/gen_latex_includes.py`

题注里**每一个数字**都是生成时从 `figures/*.json` 现读的 `%` 槽位，没有一个是从
`RESULTS.md`、`MODELING_REPORT.md` 或对话记忆里抄的。生成前有两道硬闸：缺题注或缺 PNG 直接
`SystemExit`，不允许"少一张也照样出文件"。

## 三、本轮真正修掉的问题

### 3.1 题注数字：不抄结果，重放判据

写题注时最省事的做法是把报告里的结论数字搬过来。这条路会在"改了出图判据、题注还停在旧数"时
静默失真，而任何闸门都查不出来。所以凡是**图自己算出来的派生量**，生成器里都逐行重放该图的
判据，而不是抄它的输出。六处：

| 派生量 | 重放的判据 | 若直接抄会怎样 |
| --- | --- | --- |
| 恒温平台分界 | 尾段（$t\geq$150 min）均值 → 从末点回走至跳出 $\pm0.5$ °C | 我第一版写"3600 s 后进入 50.1 °C 平台"，实际是 **108.5 min / 50.017 °C** |
| 问题一四帧时刻 | 就近取 100/600/1200/1800 s | 我第一版用 `times_s[-4:]` = 900/1200/1500/1800 s，与图上四帧不符 |
| 问题四四帧时刻 | 就近取 12/24/36/48 h | 同类错误 |
| 四级模型阶梯取值 | L0 只有标量 `C_end`，其余三级取 `volavg_C_end` | 我第一版指向 `checks` 里的副本，与出图数据源脱钩 |
| 相对不均匀度峰值 | $(C_c-C_s)/\bar{C}$ 逐点取最大 | 我第一版把该插图说成"时刻标尺"，方向都写错了 |
| 基准网格 $N$ | 反查 `mesh_ladder` 中中心温度与 `summary` 完全相等的那一档 | 写死 120 会在阶梯改档后失真 |

另外两处纯口径错误：响应面网格**本就是小时**，我却又除了 3600；雨云图 q3 在 `k=0`、y 轴向上，
所以 q3 是**下行**不是上行，我第一版写反了。

### 3.2 LaTeX 记号

- Python `repr` 指数（`6.164e-05`、`1e-09`、`0.00e+00`）会原样漏进正文。加 `sci()` 转成
  `$6.16\times10^{-5}$`，尾数恰为 1 时省掉 `1\times`。
- `$<$10^{-9}$` 这类**相邻数学环境** 3 处，由 `_tmp/check_tex.py` 抓出。修法是把比较号收进
  同一个数学组：`$<10^{-9}$`。
- `\textmu` / `\textdegree` 需要 `textcomp`。换成 `$\mu$m`、`$90^{\circ}$`，不对模板附加包做假设。

### 3.3 规划=产物一致：`fig_q2_stage_compare`

对账发现该图规划 `[single]`、实际 2 panel。闸门对这种不一致给的处理是"若该图型确实不适合本题
数据，请先改规划文档里的图型，再改图（保持规划=产物一致）"。

判断：温度量程 30–52.5 °C、含水率量程 0.9–2.65 kg/kg，单位与量纲都不同，**无法诚实地共用一根
哑铃轴**（强行共轴只能靠归一化，那就不再是"温升/失水量"的原始读数）。所以移动的是规划标注，
已改为 `[2-panel]` 并写明分板理由。图型仍是 advanced #2 Dumbbell，未降级。

### 3.4 panel 数改为运行时实测

正则数 `add_subplot` 在两种写法上必然失真：**循环里一次 `add_subplot` 画四帧**会少数，
**colorbar 专用轴**会多数。`fig_q4_3d_cylinder` 就是被正则数成 3/4 的假警报。

改成 `_tmp/count_panels.py`：monkeypatch `Figure.savefig`，问 figure 自己有几个数据轴，
剔除 colorbar 轴、极端窄高比轴、与主轴位置重合的 twin 轴，inset 另计。实测结果：

```
4 panel: q1_profiles_frames, q1_validate_analytic, q4_3d_cylinder, q4_moving_boundary_frames
2 panel: q1_air_input, q1_temp_field_3d, q2_spacetime_heatmap, q2_stage_compare,
         q2_coupling_flux, q4_radius_fit
1 panel + inset: q1_moisture_bl, q3_drying_curve, q3_uniformity, q34_robustness,
                 q4_mass_balance, q4_shrink_consistency
```

`_tmp/reconcile_manifest.py` 已改为读这份实测结果而非自己正则，对账不通过项 **0**。

## 四、闸门残留项：两处检测器盲区（非缺陷）

两条提示复查到源码级，确认是检测器自身的匹配问题，**不是图的质量问题**。均未改动共享检测器
（它对全部论文生效，不属本步骤职责），只在此记录定位证据。

### 4.1 `errorbar\(` 的未闭合括号（`_utils/figure_check.sh:180`）

```bash
! echo "$_SRC_ALL" | grep -q 'uncertainty_band\|fill_between\|errorbar\(' 2>/dev/null
```

BRE 里 `\(` 是**分组起始**，不是字面括号，整个模式因括号未闭合而非法。实测：

```
$ grep -q '...\|errorbar\(' file      → grep: Unmatched ( or \(   exit=2
$ grep -q '...\|errorbar('  file      → exit=0
```

`grep` 退出 2（报错），`2>/dev/null` 把报错吞掉，`!` 取反后条件**恒为真**。后果：任何同时含
随机数与 `.plot(` 的脚本都会被误报"只画了单条曲线"，无论它有没有画不确定性。
`fig_q34_robustness.py:35` 明确有 `ax.fill_between(...)`，仍被误报，即此因。把 `\(` 写成 `(`
即可修复。

### 4.2 `boxplot` 行内关键词过滤（`_utils/figure_check.sh:213`）

```bash
grep -n 'boxplot\|box_plot' "$script" | grep -v 'rain\|violin\|strip\|swarm'
```

第二段 `grep -v` 过滤的是**命中行自身**的文字。手画雨云图的三件套分散在不同行：半小提琴在
`gaussian_kde` + `fill_between`（31/35 行）、抖动散点在 `ax.plot(..., marker='.')`（46/47 行）、
箱线在 `ax.boxplot(...)`（39 行）。箱线那一行不含 violin/strip 字样，于是被判"plain box plot"。
只有把 `violin` 字样写到 `boxplot` 同一行才能骗过它——那属于为通过检测而写无意义代码。
该图三件套齐备，判定为盲区。

> 注：`_utils/recipe_audit.py:49` 的注释明确承认"Rain Cloud 常见三种实现：violinplot /
> 半小提琴手画(fill_betweenx+KDE) / 只画KDE+散点"，即 audit 认这种手画写法，
> 是 `figure_check.sh` 的行内过滤没跟上。

### 4.3 `fig_q2_model_compare` 的"没画出规划图型"

规划要求方法对比热图，audit 期望 `\.imshow\(|\.pcolormesh\(|sns\.heatmap`
（`_utils/recipe_audit.py:39`）。该图用的是 `_utils/plot_utils.py:5692` 的
`draw_vector_heatmap`，其 docstring 写明"Unlike `imshow`, every cell is a vector rectangle"，
实现是 `ax.add_patch(Rectangle(...))`（5756 行）逐格画矢量方块。

即热图**画了**，只是引擎是矢量方块而非栅格图像，`imshow` 的正则**结构上不可能匹配**。同一份
`figure_check.sh:174` 还反向要求"带文字热力图改用 `draw_vector_heatmap`"——两条规则互相矛盾，
遵守其一必被另一条误报。本图遵守的是更严的那条（矢量 + 背景对比检测），故保留现状。

## 五、其他

- **`figure_pdf_quality_check.py` 在本流程是空转**：它 glob `*.pdf`，而本流程 PNG-only，
  0 个输入。不是"跑过了"，是无对象可查。真正起作用的是 `plot_utils` 的 savefig 钩子
  （autofit → 重叠修复 → 图例修复 → 刻度溢出修复，未解决则 **raise**）与视觉复核。
- **字号放大机制**：`_display_width_in()`（`_utils/plot_utils.py:381`）取"落地宽"=
  `min(PAGE_MAX_W_IN=5.5, 画布宽)`，再按长宽比分档与 LaTeX 链路的 `6.5×系数` 取**更窄的那个**；
  画时字号 = 目标落地字号 × 画布宽 ÷ 落地宽。本篇最宽 7.30 in、落地 5.5 in，字号被乘约 1.33。
  布局引擎却是在**放大前**的字号上预留空间——两者顺序相反，是 compaction 前几乎所有版面失败的
  根因。闸门的"原生画布尺寸体检"已确认 24 张缩放比都在 ~0.9–1.1 档内。
- 清理了 3 处死代码：`gen_fig_q4_compare_q3.py` 的 `allr` 绑定（归因插图已删）、
  `gen_fig_q1_grid_conv.py` 的 `N_used`、`gen_fig_q2_stage_compare.py` 的 `i_mid`；
  并修正 `gen_fig_q4_compare_q3.py` 仍在宣传已删插图的过期 docstring。
- 全部 24 张 PNG 的 mtime 均新于其脚本，无待重跑项。

## 六、遗留给后续步骤

1. HTML 流程/架构图 5 张（`fig_roadmap`、`fig_flow_q1..q4`）、TikZ 机理图 3 张
   （`tikz_mechanism_heatmass`、`tikz_derive_fvm`、`tikz_q4_moving_boundary`）。
   完成后 `figure_check.sh` 的 5 条 `MISSING` 自然消解。
2. 写作步骤请直接 `cat figures/figure_captions.md` 取图与题注，**不要重新手打数字**。
3. `CLAUDE.md:187` 的 `fig_*.pdf` 措辞与 PNG-only 口径不符，建议模板维护者更正。
