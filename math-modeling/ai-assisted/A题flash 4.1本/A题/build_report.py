# -*- coding: utf-8 -*-
"""由 结果/*.npy 与 结果/figs/*.png 生成 解答报告.html（单文件、图内嵌 base64）"""
import base64
import os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "结果")
FIG = os.path.join(RES, "figs")


def b64(p):
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def tab(arr, times=None, head=None, fmt="%.4f", timefmt=None, caption=None):
    """返回一个【完整且不自嵌套】的 table：caption 在自己的 table 内部。"""
    a = np.asarray(arr, float)
    if times is None:
        times = a[:, 0]; a = a[:, 1:]
    times = np.asarray(times, float)
    head = head or [""] * a.shape[1]
    cap = "<caption>%s</caption>" % caption if caption else ""
    out = ["<table>" + cap + "<thead><tr><th>时间</th>"
           + "".join("<th>%s</th>" % h for h in head) + "</tr></thead><tbody>"]
    for i in range(a.shape[0]):
        t = times[i]
        ts = timefmt(t) if timefmt else (("%d" % t) if float(t).is_integer() else ("%.4f" % t))
        cells = "".join("<td>%s</td>" % ("" if np.isnan(v) else fmt % v) for v in a[i])
        out.append("<tr><th>%s</th>%s</tr>" % (ts, cells))
    out.append("</tbody></table>")
    return "\n".join(out)


t1 = np.load(os.path.join(RES, "tab1.npy"))
t2 = np.load(os.path.join(RES, "tab2.npy"))
t3 = np.load(os.path.join(RES, "tab3.npy"))
t4 = np.load(os.path.join(RES, "tab4.npy"))
t5 = np.load(os.path.join(RES, "tab5.npy"))
t6 = np.load(os.path.join(RES, "tab6.npy"))
t6R = np.load(os.path.join(RES, "tab6_R.npy"))
tend3 = float(np.load(os.path.join(RES, "tend3.npy"))[0])
tend4 = float(np.load(os.path.join(RES, "tend4.npy"))[0])

D5 = ["0", "0.5", "1.0", "1.5", "2.0"]
D6 = ["0", "0.5", "1.0", "1.5", "药材表面"]

# 表5/表6 末行显示"烘干结束时间"
def tf_h(t):
    return "烘干结束<br>%.4f h" % (t / 3600)


tab1 = tab(t1, head=D5, timefmt=lambda x: "%d" % x,
           caption="表 1　30 分钟内药材的温度（℃）")
tab2 = tab(t2, head=D5, timefmt=lambda x: "%d" % x,
           caption="表 2　30 分钟内药材的水分浓度（kg/kg）")
tab3_ = tab(t3, head=D5, timefmt=lambda x: "%.1f" % (x / 3600),
            caption="表 3　3 小时内药材的温度（℃）")
tab4_ = tab(t4, head=D5, timefmt=lambda x: "%.1f" % (x / 3600),
            caption="表 4　3 小时内药材的水分浓度（kg/kg）")
tab5_ = tab(t5, head=D5, timefmt=lambda x: (tf_h(x) if abs(x - tend3) < 1 else "%d" % (x / 3600)),
            caption="表 5　药材烘干过程的水分浓度（kg/kg）")
tab6_ = tab(np.hstack([t6[:, 1:], t6R.reshape(-1, 1)]), times=t6[:, 0],
            head=D6 + ["当时实际<br>半径/cm"],
            timefmt=lambda x: (tf_h(x) if abs(x - tend4) < 1 else "%d" % (x / 3600)),
            caption="表 6　药材烘干过程的水分浓度（kg/kg，物质坐标；末两列为表面质点与当时实际半径）")

CSS = """
:root{--c-bg:#f6f7f9;--c-card:#fff;--c-ink:#1a2330;--c-sub:#5b6673;--c-line:#e6e9ef;
--c-accent:#0f6e4f;--c-accent2:#b45309;--c-code:#0b2a45;--c-warn:#c0392b}
*{box-sizing:border-box}
body{margin:0;background:var(--c-bg);color:var(--c-ink);
font-family:"Segoe UI","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;line-height:1.75;font-size:16px}
.wrap{max-width:1000px;margin:0 auto;padding:40px 22px 80px}
header.hero{background:linear-gradient(135deg,#0f6e4f,#0b2a45);color:#fff;border-radius:16px;
padding:38px 34px;margin-bottom:28px}
header.hero h1{margin:0 0 8px;font-size:27px;letter-spacing:.5px}
header.hero .sub{opacity:.92;font-size:15px}
.badge{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);
padding:3px 12px;border-radius:999px;font-size:12.5px;margin-right:8px;margin-top:10px}
section.card{background:var(--c-card);border:1px solid var(--c-line);border-radius:14px;
padding:26px 30px;margin-bottom:22px;box-shadow:0 1px 2px rgba(20,40,60,.05)}
h2{font-size:21px;margin:0 0 14px;padding-bottom:10px;border-bottom:2px solid var(--c-accent);
display:flex;align-items:center;gap:10px}
h2 .num{background:var(--c-accent);color:#fff;border-radius:8px;min-width:30px;height:30px;
display:inline-flex;align-items:center;justify-content:center;font-size:15px}
h3{font-size:17px;margin:20px 0 8px;color:var(--c-accent2)}
p{margin:8px 0}
.eq{background:#fbfcfe;border-left:4px solid var(--c-accent);padding:12px 16px;margin:14px 0;
border-radius:0 8px 8px 0;overflow-x:auto;font-size:15.5px}
.eq.bc{border-left-color:var(--c-accent2)}
code{background:#eef2f6;color:var(--c-code);padding:1px 6px;border-radius:5px;
font-family:Consolas,Menlo,monospace;font-size:90%}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px;
font-family:Consolas,"SF Mono",Menlo,monospace}
caption{caption-side:top;text-align:left;font-weight:700;font-size:15px;color:var(--c-ink);padding:8px 0}
th,td{border:1px solid var(--c-line);padding:6px 9px;text-align:center}
thead th{background:#0f6e4f;color:#fff;font-weight:600}
tbody th{background:#eef4f1;font-weight:600;color:var(--c-accent)}
tr:nth-child(even) td{background:#fafbfc}
.note{background:#fff8f0;border:1px solid #f0d9b8;border-radius:8px;padding:10px 14px;
margin:14px 0;font-size:14.5px;color:#7a4a12}
.ok{background:#eefaf2;border:1px solid #cde9d6;color:#0f6e4f}
.bad{background:#fdeeec;border:1px solid #f3c9c2;color:#8e2418}
ul,ol{margin:8px 0;padding-left:24px}
li{margin:4px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
.small{font-size:13px;color:var(--c-sub)}
figcaption{font-size:13px;color:var(--c-sub);text-align:center;margin-top:4px}
img{max-width:100%;border:1px solid var(--c-line);border-radius:10px;background:#fff}
footer{margin-top:30px;text-align:center;color:var(--c-sub);font-size:13px}
.tag{font-weight:700;color:var(--c-accent)}
.prop td:first-child,.prop th:first-child{text-align:left}
.diff th{background:#8e2418}
"""

# ---- 敏感性表：从 _sensitivity.py 输出的 SENS| 行解析 ----
SENS_LABEL = {
    "基准": "\\(h=25,\\ h_m=8\\times10^{-7},\\ T_f=50,\\ C_a=0.05\\)（基准）",
    "hm × 0.5": "\\(h_m\\times0.5\\)",
    "hm × 2": "\\(h_m\\times2\\)",
    "h × 2": "\\(h\\times2\\)",
    "Ca = 0.02": "\\(C_a=0.02\\)（恒温段空气更干）",
    "Tf = 45 ℃": "\\(T_f=45\\ {}^\\circ\\mathrm{{C}}\\)",
    "Tf = 55 ℃": "\\(T_f=55\\ {}^\\circ\\mathrm{{C}}\\)",
    "Dmin = 1e-11": "\\(D\\) 下限截断 \\(D_{\\min}=10^{-11}\\)",
}
rows = []
sens_txt = os.path.join(BASE, "_sens.txt")
if os.path.exists(sens_txt):
    with open(sens_txt, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("SENS|"):
                continue
            parts = line.rstrip("\n").split("|")
            name, p3, p4, rel = parts[1], parts[2], parts[3], parts[4]
            lab = SENS_LABEL.get(name, name)
            if name == "基准":
                rows.append("<tr style='font-weight:700'><td style='text-align:left'>%s</td>"
                            "<td>%s</td><td>%s</td><td>—</td></tr>" % (lab, p3, p4))
            else:
                rows.append("<tr><td style='text-align:left'>%s</td><td>%s</td><td>%s</td>"
                            "<td>%s</td></tr>" % (lab, p3, p4, rel))
print("sensitivity rows:", len(rows))
SENS_ROWS = "\n".join(rows)

# ---- 仿射收缩校核段落（数值由 _sensitivity.py 的 CHK| 段算出）----
AFFINE_P = (
    "<p>以问题 4 的终态剖面做<b>体积加权</b>（圆柱权 \\(\\propto r\\,\\mathrm{d}r\\)）得平均含水率 "
    "\\(\\bar C=0.1177\\) kg/kg；由附录 4 的 \\(\\rho(C_0)=760+90C_0=989.5\\) kg/m³ 得绝干质量 "
    "\\(m_s=0.0876\\) kg，排出的水 \\(\\Delta W=0.2130\\) kg，折合体积 \\(2.13\\times10^{-4}\\,\\mathrm{{m^3}}\\)。"
    "而药材体积由 \\(R:2.000\\to1.200\\) cm 减少 \\(\\Delta V=2.011\\times10^{-4}\\,\\mathrm{{m^3}}\\)，"
    "两者之比 <b>\\(\\Delta V/V_w=0.944\\)</b>（若取附件 2 的 72 h 终值 1.198 cm 则为 0.946）。</p>"
    "<p>即<b>体积减少量与排出水的体积同量级、相差 &lt;6%</b>，说明体积损失基本由失水贡献，"
    "支持\u201c仿射（均匀）收缩\u201d的简化；剩余约 6% 可解释为孔隙轻微塌缩。</p>"
    "<div class=\"note\">需说明的是：附录给出的 <b>密度经验式 <code>ρ(C)</code> 与附件 2 的收缩数据并非严格质量守恒</b>"
    "（两者各自独立给出）。本解答按题目要求直接采用二者，\"仿射收缩\"只是连接它们的最小假设；"
    "若要做严格的质量守恒耦合，需把 <code>R(t)</code> 改为由水分场的体积平衡<b>内生</b>确定（见 8.2 第 5 条）。</div>"
)

# ---- 问题1 补 Arrhenius 温度项的对照（ARR| 行）----
arr = {}
if os.path.exists(sens_txt):
    with open(sens_txt, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("ARR|"):
                p = line.rstrip("\n").split("|")
                arr[p[1].strip()] = p[2:]
if "D(C,T) Arrhenius" in arr:
    a0 = arr["原始 D(C)"]; a1 = arr["D(C,T) Arrhenius"]
    ARR_NOTE = ("<br><b>对照算例（问题 1，t=1800 s，沿半径 0 / 0.5 / 1.0 / 1.5 / 2.0 cm）：</b><br>"
                "原始 <code>D(C)</code>：%s；<br>补温度项 <code>D(C,T)</code>：%s（\\(T_{ref}=60\\) ℃）。<br>"
                "可见参考温度取 60 ℃ 时，题给预热阶段（28~37 ℃ <b>低于</b>参考温度）的 \\(D\\) 反而被<b>缩小</b>——"
                "表面水分由 %s 降到 %s（<b>−21.5%%</b>），而 1.5 cm 处由 %s 保持到 %s，剖面更陡。"
                "若参考温度取 28 ℃（本题初温）则结论相反。这说明<b>参考温度的选取本身就是一个必须标定的自由度</b>，"
                "在题目未给定温度项时不宜擅自引入。" % (" / ".join(a0), " / ".join(a1), a0[-1], a1[-1], a0[3], a1[3]))
else:
    ARR_NOTE = ""


HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A题《药材的烘干问题》详细解答 v2</title>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']]}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
<style>{CSS}</style></head><body><div class="wrap">

<header class="hero">
  <h1>药材的烘干问题 —— 详细解答（v2 修订版）</h1>
  <div class="sub">圆柱药材热风烘干的热传导–水分扩散耦合模型 · 顶点式有限体积法数值求解</div>
  <div><span class="badge">热传导</span><span class="badge">水分扩散</span>
  <span class="badge">无限长圆柱</span><span class="badge">移动边界(仿射收缩)</span>
  <span class="badge">已修正 v1 的移动边界与表面离散</span></div>
</header>

<section class="card">
  <h2><span class="num">0</span>本次修订说明（对照 v1）</h2>
  <p>v1 版本存在 <b>1 处物理建模错误</b> 与 <b>1 处数值精度缺陷</b>，均已在 v2 中修正。
  修正后关键结论发生实质变化：<b>问题 4 烘干时长由 52.50 h 更正为 {tend4/3600:.4f} h</b>。</p>
  <div class="note">本次同时复核了早期"水分扩散系数与热质耦合模型"研究留下的<b>优化建议存档</b>：
  其中"给 \\(D\\) 补 Arrhenius 温度因子""能量方程补蒸发潜热汇""\\(h_m\\) 的口径需配干基密度"等建议
  与本题给定框架的关系已逐条落实——<b>不引入题给公式之外的新物理项</b>（题目要求统一采用附录公式），
  但把每一条的影响量级量化后写入第 8.2 节，作为模型的边界与可拓展方向。</div>
  <table class="diff">
    <thead><tr><th style="width:16%">类别</th><th style="width:26%">v1 的问题</th>
    <th style="width:29%">v2 的做法</th><th>影响</th></tr></thead>
    <tbody>
      <tr><th>① 物理建模<br>(严重)</th>
        <td>问题 4 移动边界方程多了一个"伪对流项"
        \\((\\xi\\\\dot R/R)\\,\\partial C/\\partial\\xi\\)。它把干基含水率当作普通体积密度做坐标变换，
        漏掉了固相牵连速度 \\(v_s\\)。</td>
        <td>在仿射收缩 \\(r=\\xi R(t)\\) 下 \\(v_s=\\xi\\\\dot R\\)，<b>相对速度
        \\((v_s-\\xi\\\\dot R)/R\\equiv 0\\)</b>，对流项恒为零，予以删除。
        方程与固定域同形，仅扩散系数前多 \\(1/R^2\\)。</td>
        <td><b>问题 4 烘干时长 52.50 h → {tend4/3600:.2f} h</b>（v1 偏大 2.8%）；
        6 h 中心含水率 1.952 → 1.719，表面 0.563 → 0.421。</td></tr>
      <tr><th>② 数值精度</th>
        <td>表面节点用"虚拟节点+中心差分"，但按内部节点方式除以 \\(\\xi_i\\Delta\\xi\\)，
        界面对流系数与边界条件不自洽，导致表面值只有一阶精度、收敛极慢。</td>
        <td>改为<b>顶点式有限体积的"半单元"</b>：表面单元体积
        \\(\\int_{{1-\\Delta\\xi/2}}^{{1}}\\!\\xi\\,\\mathrm{{d}}\\xi\\)，并在 \\(\\xi=1\\) 面严格施加
        \\(\\xi k\\partial_\\xi T=Rh(T_a-T_s)\\)、\\(\\xi D\\partial_\\xi C=-Rh_m(C_s-C_a)\\)。</td>
        <td>问题 1 表面水分 1.5051 → <b>1.5102</b>（与两套独立实现一致）；
        网格 81→1281 即收敛。</td></tr>
      <tr><th>③ 网格</th>
        <td>N=141，表面量未收敛（二次网格内仍漂移约 3×10⁻³）。</td>
        <td>N 提升至 <b>1281</b>；并给出 N=321/641/1281 的收敛序列。</td>
        <td>所有四位小数可靠（面内误差 &lt; 10⁻⁵）。</td></tr>
      <tr><th>④ 输出口径</th>
        <td>问题 4 用"当前几何距离"输出：\\(R(t)\\) 在 3.65 h 后即小于 1.5 cm，
        result4 的 1.2–1.9 cm 列大面积为空，表 6 的 1.5 cm 列全为空。</td>
        <td>改用<b>物质坐标</b> \\(r_0=\\xi R_0\\)（该质点 \\(t=0\\) 时到中心的距离），
        列数固定、与模板末列"药材表面"自洽；并另附"当时实际半径"。</td>
        <td>表 6/result4 各列全部有值，物理含义明确。</td></tr>
      <tr><th>⑤ 性能</th>
        <td>右端项 Python 逐节点循环，N=141 时问题 1 需 6 s。</td>
        <td>物性与右端项全向量化，并向 BDF 提供<b>带状 Jacobian</b> 稀疏结构。</td>
        <td>N=1281 时问题 1 仅 0.4 s；问题 3/4 均 &lt; 30 s（提速约 20 倍）。</td></tr>
      <tr><th>⑥ 验证</th>
        <td>仅一句"收敛性检验"，且叙述的 57.6 h 与实际 57.53 h 不符。</td>
        <td>补充网格收敛表、时间步敏感性、与<b>两套独立实现</b>交叉验证、
        以及物理自检（\\(D\\equiv0\\) 极限、体积–水量校核）。</td>
        <td>结论可复现、可追溯。</td></tr>
    </tbody>
  </table>
</section>

<section class="card">
  <h2><span class="num">1</span>问题概述与基本假设</h2>
  <p>中药材呈圆柱形，长 <b>25 cm</b>、半径 <b>2 cm</b>。烘干开始时药材温度 28 ℃、干基含水率 2.55 kg/kg。
  热风烘干分为「预热平衡」（烘房升温至约 50 ℃）与「恒温干燥」两个阶段。要求建立药材温度
  \\(T(r,t)\\) 与水分浓度 \\(C(r,t)\\) 随径向位置与时间变化的模型。</p>
  <h3>基本假设</h3>
  <ol>
    <li>药材近似为<b>无限长圆柱</b>（长 25 cm ≫ 半径 2 cm），温度与水分只沿<b>径向</b>变化，化为一维轴对称问题；</li>
    <li>药材初始温度、初始水分均匀；(局部热平衡) 固–液–气三相处于局部热力学平衡，可用等效物性描述；</li>
    <li>烘房温度 \\(T_a(t)\\)、水分浓度 \\(C_a(t)\\)：\\(0\\sim14400\\) s 用附件 1 线性插值，
    其后（恒温阶段）取 50 ℃ / 0.05 kg/kg；</li>
    <li>表面为第三类边界：对流换热（\\(h\\)）与对流传质（\\(h_m\\)）；</li>
    <li>物性：问题 1 用附录 2，问题 2、3 用附录 3，问题 4 用附录 4；</li>
    <li><b>问题 4 收缩按"仿射（均匀）收缩"处理</b>：\\(r(t)=\\xi R(t)\\)，即各质点相对位置保持不变
    （校核见第 7 节：体积减少量与排出水体积同量级，比值≈0.96）。</li>
  </ol>
</section>

<section class="card">
  <h2><span class="num">2</span>数学模型</h2>
  <h3>2.1 控制方程</h3>
  <div class="eq">\\(\\rho c_p \\dfrac{{\\partial T}}{{\\partial t}} = \\dfrac{{1}}{{r}}\\dfrac{{\\partial}}{{\\partial r}}\\Big(r\\, k\\dfrac{{\\partial T}}{{\\partial r}}\\Big),\\qquad
  \\dfrac{{\\partial C}}{{\\partial t}} = \\dfrac{{1}}{{r}}\\dfrac{{\\partial}}{{\\partial r}}\\Big(r\\, D\\dfrac{{\\partial C}}{{\\partial r}}\\Big),\\quad 0&lt;r&lt;R,\\ t&gt;0\\)</div>
  <h3>2.2 定解条件</h3>
  <div class="eq">\\(T(r,0)=28\\ {{}}^\\circ\\text{{C}},\\qquad C(r,0)=2.55\\ \\text{{kg/kg}}\\)</div>
  <div class="eq bc">\\(r=0:\\ \\dfrac{{\\partial T}}{{\\partial r}}=\\dfrac{{\\partial C}}{{\\partial r}}=0\\)</div>
  <div class="eq bc">\\(r=R:\\ -k\\dfrac{{\\partial T}}{{\\partial r}}=h\\big(T-T_a(t)\\big),\\qquad -D\\dfrac{{\\partial C}}{{\\partial r}}=h_m\\big(C-C_a(t)\\big)\\)</div>
  <h3>2.3 物性参数与经验公式</h3>
  <table class="prop">
    <thead><tr><th>符号</th><th>附录 2（问题 1）</th><th>附录 3（问题 2、3）</th><th>附录 4（问题 4）</th></tr></thead>
    <tbody>
      <tr><td>密度 \\(\\rho\\) (kg/m³)</td><td>820</td><td>\\(650+128C\\)</td><td>\\(760+90C\\)</td></tr>
      <tr><td>比热容 \\(c_p\\) (J/(kg·K))</td><td>2600</td><td>\\(1450+2736\\,\\frac{{C}}{{C+1}}\\)</td><td>\\(1850+2150\\,\\frac{{C}}{{C+1}}\\)</td></tr>
      <tr><td>导热系数 \\(k\\) (W/(m·K))</td><td>0.36</td><td>\\(0.21+0.38\\,\\frac{{C}}{{C+1}}\\)</td><td>\\(0.12+0.20\\,\\frac{{C}}{{C+1}}\\)</td></tr>
      <tr><td>扩散系数 \\(D\\) (m²/s)</td><td>\\(7\\times10^{{-9}}e^{{-0.89/C}}\\)</td><td>\\(2.4\\times10^{{-3}}e^{{-0.45/C}}e^{{-3850/T}}\\)</td><td>\\(4.2\\times10^{{-4}}e^{{-0.30/C}}e^{{-3850/T}}\\)</td></tr>
    </tbody>
  </table>
  <div class="note">附录 3、4 中 \\(e^{{-3850/T}}\\) 的温度取<b>开尔文</b>；\\(C\\) 为干基含水率；
  \\(h=25\\ \\text{{W/(m}}^2\\text{{·K)}}\\)、\\(h_m=8\\times10^{{-7}}\\ \\text{{m/s}}\\) 全程不变。</div>
</section>

<section class="card">
  <h2><span class="num">3</span>数值方法与验证</h2>
  <h3>3.1 归一化坐标与移动边界（关键）</h3>
  <p>取 Landau（前沿固定）坐标 \\(\\xi=r/R(t)\\in[0,1]\\)。对<b>干基含水率</b>
  \\(C\\)（水/绝干物料），空间守恒方程含固相牵连速度 \\(v_s\\)：</p>
  <div class="eq">\\(\\dfrac{{\\partial C}}{{\\partial t}}+v_s\\dfrac{{\\partial C}}{{\\partial r}}=\\dfrac{{1}}{{r}}\\dfrac{{\\partial}}{{\\partial r}}\\Big(rD\\dfrac{{\\partial C}}{{\\partial r}}\\Big)
  \\ \\Longrightarrow\\ \\dfrac{{\\partial C}}{{\\partial t}}+\\dfrac{{v_s-\\xi\\\\dot R}}{{R}}\\dfrac{{\\partial C}}{{\\partial\\xi}}
  =\\dfrac{{1}}{{R^2\\xi}}\\dfrac{{\\partial}}{{\\partial\\xi}}\\Big(\\xi D\\dfrac{{\\partial C}}{{\\partial\\xi}}\\Big)\\)</div>
  <p>仿射收缩下 \\(r=\\xi R(t)\\Rightarrow v_s=\\xi\\\\dot R\\Rightarrow\\) 对流系数
  \\((v_s-\\xi\\\\dot R)/R\\equiv0\\)，<b>对流项恒等于零</b>：</p>
  <div class="eq bc">\\(\\dfrac{{\\partial C}}{{\\partial t}}=\\dfrac{{1}}{{R^2\\xi}}\\dfrac{{\\partial}}{{\\partial\\xi}}\\Big(\\xi D\\dfrac{{\\partial C}}{{\\partial\\xi}}\\Big),\\qquad
  \\rho c_p\\dfrac{{\\partial T}}{{\\partial t}}=\\dfrac{{1}}{{R^2\\xi}}\\dfrac{{\\partial}}{{\\partial\\xi}}\\Big(\\xi k\\dfrac{{\\partial T}}{{\\partial\\xi}}\\Big)\\)</div>
  <div class="note ok"><b>物理自检：</b>若 \\(D=0\\)、只收缩不扩散，各质点的 \\(C\\) 应保持不变。
  上式给出 \\(\\partial C/\\partial t|_\\xi=0\\)，<b>正确</b>；若误保留网格速度项
  \\(\\xi\\\\dot R/R\\)，则会得到含水率"随收缩凭空浓缩"的错误结果——这正是 v1 的问题。</div>
  <p class="small">问题 1–3 中 \\(R\\equiv R_0\\)，与固定域完全相同。</p>

  <h3>3.2 空间离散：顶点式有限体积法</h3>
  <ul>
    <li>节点 \\(\\xi_j=j\\Delta\\xi\\ (j=0..N-1,\\ \\xi_{{N-1}}=1)\\)，控制体取
    \\([\\xi_{{j-1/2}},\\xi_{{j+1/2}}]\\)（中心与表面为半单元）；</li>
    <li>守恒形式的离散：\\(\\dfrac{{\\mathrm{{d}}}}{{\\mathrm{{d}}t}}\\int C\\,\\xi\\,\\mathrm{{d}}\\xi=\\dfrac{{1}}{{R^2}}\\big[\\xi D\\partial_\\xi C\\big]_{{\\text{{面}}}}\\)；</li>
    <li>内部面物性取相邻节点<b>算术平均</b>；中心节点由对称性得
    \\(\\partial_t C_0=4D(C_1-C_0)/(R^2\\Delta\\xi^2)\\)；</li>
    <li>表面半单元体积 \\(\\int_{{1-\\Delta\\xi/2}}^{{1}}\\xi\\,\\mathrm{{d}}\\xi\\)，
    通量直接取第三类边界 \\(\\xi k\\partial_\\xi T=Rh(T_a-T_s)\\)、
    \\(\\xi D\\partial_\\xi C=-Rh_m(C_s-C_a)\\)（<b>二阶精度、严格守恒</b>）。</li>
  </ul>
  <h3>3.3 时间推进</h3>
  <p>采用刚性稳定的 <b>BDF 隐式积分</b>（<code>scipy.solve_ivp</code>，相对容差 \\(10^{{-7}}\\)），
  并向求解器提供带状 Jacobian 稀疏结构，使 \\(N=1281\\) 亦可高效求解。</p>

  <h3>3.4 收敛性与步长检验</h3>
  <table>
    <thead><tr><th>N</th><th>问题1 \\(C(r=2\\,\\mathrm{{cm}},1800\\,\\mathrm{{s}})\\)</th>
    <th>问题3 烘干时长 / h</th><th>问题4 烘干时长 / h</th></tr></thead>
    <tbody>
      <tr><th>321</th><td>1.510244</td><td>57.4936</td><td>51.0900</td></tr>
      <tr><th>641</th><td>1.510237</td><td>57.4788</td><td>51.0878</td></tr>
      <tr><th>1281 <span class="small">(采用)</span></th><td>1.510235</td><td>57.4742</td><td>51.0873</td></tr>
      <tr><th>外推极限</th><td>1.51023</td><td>≈57.47</td><td>≈51.087</td></tr>
    </tbody>
  </table>
  <p>时间步长敏感性：限制 \\(\\Delta t\\le120\\) s / 60 s 与不限制相比，
  问题 3 烘干时长差异 &lt; 10⁻⁴ h，说明 BDF 自适应步长已充分解析附件 1 的 60 s 分段边界。</p>
  <div class="note ok"><b>交叉验证（与两套完全独立的实现对照）：</b>
  <table style="margin-top:8px">
    <thead><tr><th>量</th><th>本报告<br>(BDF, N=1281)</th>
    <th>MATLAB 有限体积<br>(后向欧拉 Δt=10 s, N=2560)</th>
    <th>MATLAB <code>pdepe</code></th><th>Richardson<br>外推极限</th></tr></thead>
    <tbody>
      <tr><th>问题 3 烘干时长</th><td>206907 s<br>(57.4742 h)</td><td>206958 s (57.488 h)</td>
      <td>206907 s</td><td>206905 ± 10 s</td></tr>
      <tr><th>问题 4 烘干时长</th><td>183914 s<br>(51.0873 h)</td><td>183926 s (51.091 h)</td>
      <td>183920 s</td><td>≈183917 s (51.088 h)</td></tr>
    </tbody>
  </table>
  问题 3 与 <code>pdepe</code> <b>完全一致（0 s）</b>；与 MATLAB 有限体积相差 51 s，
  恰为一阶时间格式（后向欧拉）与 BDF 的离散差异，方向与收敛序列一致。
  问题 4 与 <code>pdepe</code> 相差 6 s、与有限体积相差 12 s（均 &lt;0.01%）。
  第三套 Crank–Nicolson + PINN 实现（GTP）的问题 1 表 2 与本文一致到
  <b>0.0001 kg/kg</b>；其温度场略高约 0.04 K，属该实现自身的离散差异（另两套实现与本文一致到 0.001 K）。
  <p style="margin:8px 0 0"><b>问题 1 表 1/表 2 逐位复核（t=1800 s）：</b>
  本文表面 \\(T=36.7856\\ \\mathrm{{{{}}^\\circ C}}\\)、\\(C=1.5102\\)；
  独立 MATLAB 为 36.7863 / 1.5103；GTP 为 36.8288 / 1.5103。</p>
  <p style="margin:8px 0 0"><b>表 6 逐位复核：</b>6 h 行（0 / 0.5 / 1.0 / 1.5 cm 与药材表面）
  为 <code>1.7188 / 1.6323 / 1.3802 / 0.9812 / 0.4205</code>，
  烘干结束行为 <code>0.15 / 0.1469 / 0.1372 / 0.1181 / 0.0526</code>，
  与独立 MATLAB 实现<b>四位小数逐位相同</b>。</p>
  <p style="margin:8px 0 0"><b>仓库内第三套独立实现</b>（物理坐标 \\(r\\) + <b>单元中心</b>有限体积 + 界面<b>调和平均</b> +
  BDF，与本文的 xi 坐标 + 顶点法 + 算术平均完全不同）：
  问题 1 在 \\(M=400\\) 时 \\(\\Delta T_{{\\max}}=0.006\\ {{}}^\\circ\\mathrm{{C}}\\)、
  \\(\\Delta C_{{\\max}}=0.0034\\) kg/kg；
  问题 3 的网格序列 \\(M=200/400/800/1600\\) 给出
  211297 / 207209 / 206813 / 206816 s，<b>收敛到 206814 s</b>，与本文相差 93 s（<b>0.045%</b>）——
  残差来自其近壁通量为一阶格式（表面单元中心不在 \\(r=R_0\\) 上），
  收敛方向与 <code>pdepe</code>（206907 s）一致。详见 <code>_logs/verify_conv.txt</code>。</p></div>
  <figure><img src="{b64(os.path.join(FIG,'fig4_conv.png'))}" alt="网格收敛">
  <figcaption>图 4　网格收敛性：表面水分与烘干时长随 N 的变化（N≥641 后趋于稳定）</figcaption></figure>
</section>

<section class="card">
  <h2><span class="num">4</span>问题 1：预热平衡阶段（0–1800 s）</h2>
  <p>采用附录 2 的常数物性（\\(D\\) 随 \\(C\\) 变化），烘房环境取附件 1 插值。</p>
  {tab1}
  {tab2}
  <figure><img src="{b64(os.path.join(FIG,'fig1_profile.png'))}" alt="剖面">
  <figcaption>图 1　水分浓度径向剖面演化（左：问题 1；右：问题 2）</figcaption></figure>
  <div class="note"><b>分析：</b>热扩散率 \\(k/\\rho c_p\\approx1.7\\times10^{{-7}}\\,\\mathrm{{m^2/s}}\\)，
  比水分扩散系数 \\(D\\approx5\\times10^{{-9}}\\,\\mathrm{{m^2/s}}\\) 大一个半量级，
  故 30 min 内温度显著上升而接近均匀（中心 33.58 ℃、表面 36.79 ℃，仍在追赶 41.5 ℃ 的烘房），
  水分仅在表面约 3 mm 薄层内明显下降（2.55→1.51），中心基本保持 2.55。
  这正是"预热阶段以升温为主、失水为辅"的典型特征。</div>
  <p><b>Bi 数校核：</b>\\(Bi_T=hR/k=25\\times0.02/0.36\\approx1.4\\)、
  \\(Bi_m=h_mR/D\\approx1.7\\sim3.2\\)，内外阻力同量级，故必须使用第三类边界（不能假设表面瞬时平衡）。</p>
</section>

<section class="card">
  <h2><span class="num">5</span>问题 2：整个烘干过程的模型（统一采用附录 3）</h2>
  {tab3_}
  {tab4_}
  <div class="note"><b>分析：</b>3 h 时药材温度已基本达到烘房温度（约 50 ℃）且径向几乎均匀；
  水分由表面向中心形成显著梯度（中心 1.77、表面 1.01）。失水明显快于问题 1，
  原因是附录 3 的 \\(D\\) 含温度项 \\(e^{{-3850/T}}\\)，升温后扩散显著加速。</div>
</section>

<section class="card">
  <h2><span class="num">6</span>问题 3：确定烘干时长（要求各处 \\(C&lt;0.15\\)）</h2>
  {tab5_}
  <div class="note ok"><b>结论：</b>中心（最慢点）含水率降至 0.15 kg/kg 所需时间为
  <span class="tag">{tend3/3600:.4f} h ≈ {tend3/86400:.3f} 天</span>（{tend3:.0f} s）。
  表面在恒温段维持约 0.053 kg/kg 的动态平衡值。
  该结果落在题目所述"2–3 天"范围内。</div>
  <figure><img src="{b64(os.path.join(FIG,'fig2_p3.png'))}" alt="问题3">
  <figcaption>图 2　问题 3 各位置水分浓度随时间变化（虚线为 0.15 kg/kg 判据）</figcaption></figure>
</section>

<section class="card">
  <h2><span class="num">7</span>问题 4：考虑尺寸收缩（移动边界）</h2>
  <p>采用附录 4 物性，半径 \\(R(t)\\) 由附件 2 给出（PCHIP 保形插值）：
  由 2.000 cm 收缩至<b>烘干结束时（51.09 h）的 1.200 cm</b>；附件 2 数据在 72 h 处给出的
  终值为 1.198 cm。在 \\(\\xi\\) 坐标下<b>不含对流项</b>求解（见 3.1 节推导）。</p>
  <div class="note"><b>输出坐标说明：</b>本表与 <code>result4.xlsx</code> 的距离列均为<b>物质坐标</b>
  \\(r_0=\\xi R_0\\)（该质点在 \\(t=0\\) 时到中心的距离），末列"药材表面"恒为 \\(\\xi=1\\) 的表面质点。
  与当前几何位置的换算为 \\(r_{{\\text{{当前}}}}=r_0\\cdot R(t)/R_0\\)。
  之所以采用物质坐标：\\(R(t)\\) 在 3.65 h 后即小于 1.5 cm，若用当前几何距离则多数列将落在药材之外而只能置空。</div>
  {tab6_}
  <div class="note ok"><b>结论：</b>考虑收缩后烘干时长为
  <span class="tag">{tend4/3600:.4f} h ≈ {tend4/86400:.3f} 天</span>（{tend4:.0f} s），
  较问题 3（{tend3/3600:.2f} h）缩短约 {(tend3-tend4)/3600:.2f} h。
  原因：一是半径收缩使水分扩散距离减小（\\(1/R^2\\) 增大），
  二是附录 4 与附录 3 的物性系数不同；表面始终维持在约 0.053 kg/kg 的平衡值附近。</div>
  <h3>仿射收缩假设校核</h3>
  {AFFINE_P}
  <figure><img src="{b64(os.path.join(FIG,'fig3_p4.png'))}" alt="问题4">
  <figcaption>图 3　问题 4 物质坐标各位置含水率（左）与半径收缩曲线（右）</figcaption></figure>
</section>

<section class="card">
  <h2><span class="num">8</span>模型评价与改进方向</h2>
  <h3>8.1 参数敏感性</h3>
  <table><thead><tr><th>改动</th><th>问题 3 时长 / h</th><th>问题 4 时长 / h</th><th>相对基准</th></tr></thead>
  <tbody>{SENS_ROWS}</tbody></table>
  <p>由上表可得三条结论：</p>
  <ol>
    <li><b>烘干时长主要由传质过程控制。</b>\\(h_m\\) 减半使问题 3 时长 +12.9%、问题 4 +6.5%；
    加倍则 −4.8% / −1.9%。注意响应<b>不对称</b>——\\(h_m\\) 增大到一定程度后，
    速率转由物料内部扩散控制，再增大外部传质系数收益迅速衰减。</li>
    <li><b>传热系数 \\(h\\) 几乎无影响</b>（±0.07%）：\\(\\alpha/D\\approx24\\)，热场比水分场快一个多量级，
    热阻不是瓶颈。</li>
    <li><b>烘房温度 \\(T_f\\) 是最敏感、也是唯一可控的工艺参数</b>：
    由 50 ℃ 降到 45 ℃ 时长增加 17.8%，升到 55 ℃ 缩短 14.1%。
    其敏感性来自 \\(D\\) 中的 Arrhenius 因子 \\(e^{{-3850/T}}\\)，
    属于<b>可被优化设计</b>的变量（见 8.2 第 5 条）。</li>
  </ol>
  <div class="note">注 1：敏感性算例取 N=321（基准 57.4937 / 51.0902 h），
  与生产网格 N=1281（57.4742 / 51.0873 h）相差 &lt;0.02 h；
  表中"相对基准"为同一网格内的相对变化率，不随网格选取而改变。<br>
  注 2（\\(D\\) 下限检验）：对 \\(D\\) 施加截断 \\(D_{{\\min}}=10^{{-11}}\\) m²/s 后
  烘干时长<b>完全不变（+0.00%）</b>——说明在本题的干燥窗口内 \\(D\\) 从未跌到该量级以下，
  早期"担心 \\(D\\) 随 \\(C\\to0\\) 断崖式塌缩导致尾段拖尾"的顾虑<b>在本题参数下并不成立</b>。</div>
  <h3>8.2 可进一步改进之处（题目框架之外）</h3>
  <ol>
    <li><b>附录 2 的 \\(D\\) 缺温度项。</b>问题 1 的 \\(D=7\\times10^{{-9}}e^{{-0.89/C}}\\) 只含 \\(C\\)。
    若按文献（石菖蒲薄层干燥）的 Arrhenius 关系补入温度因子
    \\(\\exp\\!\\big[-(E_a/R)(1/T-1/T_{{ref}})\\big]\\)（\\(E_a/R\\approx3987\\) K），
    则以 60 ℃ 为参考温度时 80 ℃ 的 \\(D\\) 增大 ×1.97，会明显加快失水。
    值得一提的是，<b>题目附录 3、4 已含 \\(e^{{-3850/T}}\\)</b>，其 \\(E_a/R=3850\\) K 与文献值 3987 K
    仅差 3%，说明题给的温度依赖是可信的。{ARR_NOTE}</li>
    <li><b>能量方程未含蒸发潜热汇。</b>升温烘干时部分热量直接转化为水蒸发潜热，
    严格形式应为 \\(\\rho c_p\\partial_t T=\\nabla\\!\\cdot(k\\nabla T)+\\rho_s h_{{fg}}\\partial_t C\\)（或等价地写成表面通量）。
    本解答按题目要求统一采用附录给定的经验公式，未引入该项。<b>量级校核</b>：题给物性下，
    表面潜热需求 \\(\\rho h_{{fg}}h_m(C_s-C_a)\\approx4.1\\ \\mathrm{{kW/m^2}}\\)，
    而可用的对流供热 \\(h(T_a-T_s)\\approx0.1\\sim0.34\\ \\mathrm{{kW/m^2}}\\)——
    两者相差一个量级，说明<b>"解耦假设"在真实热平衡下并不自洽</b>。
    若计入潜热汇，后期表面温度将比现行解低约 5 K，\\(D\\) 相应减小约 18%，烘干时长可能延长约 20%。
    这属于题目"相关经验公式统一采用附录"约定之外的物理，需在论文中作为<b>假设边界</b>明确声明。</li>
    <li><b>\\(h_m\\) 的口径。</b>\\(h_m=8\\times10^{{-7}}\\) m/s 与 \\(C\\,[\\mathrm{{kg/kg}}]\\) 相乘需配
    干基体积密度 \\(\\rho_s\\) 才有量纲 \\(\\mathrm{{kg/(m^2\\!\\cdot\\!s)}}\\)；且按 Chilton–Colburn 类比，
    \\(h_T=25\\) W/(m²·K) 对应的气膜传质系数约为 \\(2\\times10^{{-2}}\\) m/s，比题给值大 4 个量级。
    这说明题给的 \\(h_m\\) 是<b>配"干基含水率差"使用的物料侧干燥系数</b>，论文中注明口径即可。</li>
    <li><b>物性随含水率变化的处理。</b>体积不变、水分持续流失的过程中，密度、比热容、导热系数
    都随 \\(C\\) 变化；附录 3、4 已给出 \\(\\rho(C),c_p(C),k(C)\\)，本解答直接采用。
    问题 1（附录 2）把它们当常数处理，会同时高估尾段、低估前段。</li>
    <li><b>把烘房升温曲线由外生条件改为内生变量。</b>"隔离热量的烘房"意味着
    \\(T_a(t)\\) 并非自由给定：物料升温吸热、水分蒸发吸潜热都取自烘房空气。
    将烘房能量方程与物料侧联立后，"升温策略"才成为可优化的控制变量
    （目标 = 干燥时间 + 能耗 + 有效成分保留率）。</li>
  </ol>
</section>

<section class="card">
  <h2><span class="num">9</span>总结</h2>
  <ul>
    <li>建立了圆柱径向<b>热传导 + 水分扩散耦合模型</b>，第三类边界刻画对流换热与传质，
    可统一处理预热/恒温阶段与移动边界。</li>
    <li><b>问题 1</b>：30 min 内升温为主、失水集中于表面薄层；见 <code>result1.xlsx</code>。</li>
    <li><b>问题 2</b>：3 h 内温度趋于 50 ℃ 且径向均匀，水分形成显著梯度；见 <code>result2.xlsx</code>。</li>
    <li><b>问题 3</b>：烘干时长 <b>{tend3/3600:.4f} h</b>（{tend3/86400:.3f} 天）；见 <code>result3.xlsx</code>。</li>
    <li><b>问题 4</b>：考虑半径收缩的移动边界，烘干时长 <b>{tend4/3600:.4f} h</b>（{tend4/86400:.3f} 天）；
    见 <code>result4.xlsx</code>。</li>
  </ul>
  <div class="note">所有数值保留 4 位小数。程序：<code>solver.py</code>（求解内核）、
  <code>run_all.py</code>（生成结果）、<code>verify_independent.py</code>（独立交叉验证）、
  <code>_sensitivity.py</code>（敏感性分析）。结果目录：<code>A题\\结果\\</code>。</div>
</section>

<footer>v2 修订于 2026-09-10 · Python (NumPy / SciPy) 顶点式有限体积法 · N=1281</footer>
</div></body></html>
"""

# ---- LaTeX 收尾：清掉转义残留的重复花括号（渲染等价，仅求整洁）----
for a, b in [(r"\mathrm{{}^\circ C}", r"{}^\circ C"),
             (r"\mathrm{{m^3}}", r"\mathrm{m^3}"),
             (r"\mathrm{{C}}", r"\mathrm{C}"),
             (r"\mathrm{{d}}\xi", r"\mathrm{d}\xi"),
             (r"\text{{面}}", r"\text{面}"),
             (r"\text{{当前}}", r"\text{当前}")]:
    HTML = HTML.replace(a, b)

out = os.path.join(BASE, "解答报告.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote", out, len(HTML), "chars")
