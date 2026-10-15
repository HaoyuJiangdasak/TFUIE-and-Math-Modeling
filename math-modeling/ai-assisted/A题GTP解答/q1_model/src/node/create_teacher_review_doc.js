const fs = require("fs");
const path = require("path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  Footer,
  HeadingLevel,
  ImageRun,
  PageBreak,
  PageNumber,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} = require("docx");

const modelDir = path.resolve(__dirname, "..", "..");
const assetDir = path.join(modelDir, "output", "teacher_doc_assets");
const manifest = JSON.parse(fs.readFileSync(path.join(assetDir, "manifest.json"), "utf8"));
const outputFile = path.join(modelDir, "00_请老师先看_第一问模型检查版_修正版.docx");

const PAGE_WIDTH = 11906;
const MARGIN = 900;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN;
const thin = { style: BorderStyle.SINGLE, size: 1, color: "9CA3AF" };
const borders = { top: thin, bottom: thin, left: thin, right: thin };

const table1 = [
  ["100", "28.0001", "28.0003", "28.0040", "28.0327", "28.1800"],
  ["300", "28.0408", "28.0635", "28.1514", "28.3681", "28.8488"],
  ["600", "28.4533", "28.5360", "28.8039", "29.3159", "30.1652"],
  ["900", "29.3243", "29.4583", "29.8755", "30.6161", "31.7304"],
  ["1200", "30.5427", "30.7098", "31.2223", "32.1126", "33.4276"],
  ["1500", "31.9957", "32.1867", "32.7660", "33.7463", "35.1203"],
  ["1800", "33.5753", "33.7720", "34.3642", "35.3621", "36.7856"],
];

const table2 = [
  ["100", "2.5500", "2.5500", "2.5500", "2.5500", "2.2475"],
  ["300", "2.5500", "2.5500", "2.5500", "2.5492", "2.0510"],
  ["600", "2.5500", "2.5500", "2.5500", "2.5353", "1.8770"],
  ["900", "2.5500", "2.5500", "2.5497", "2.5045", "1.7547"],
  ["1200", "2.5500", "2.5500", "2.5482", "2.4646", "1.6586"],
  ["1500", "2.5500", "2.5499", "2.5445", "2.4206", "1.5787"],
  ["1800", "2.5500", "2.5497", "2.5383", "2.3755", "1.5103"],
];

function textParagraph(text, options = {}) {
  return new Paragraph({
    alignment: options.alignment || AlignmentType.JUSTIFIED,
    spacing: { after: options.after ?? 120, line: options.line ?? 320 },
    children: [
      new TextRun({
        text,
        font: "Microsoft YaHei",
        size: options.size || 22,
        bold: options.bold || false,
        color: options.color || "111827",
        highlight: options.highlight,
      }),
    ],
  });
}

function heading(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({
    heading: level,
    spacing: { before: 220, after: 120 },
    children: [new TextRun({ text, font: "Microsoft YaHei", bold: true })],
  });
}

function equation(name, label) {
  const item = manifest[name];
  const width = Math.min(650, item.width * 0.42);
  const height = item.height * (width / item.width);
  return [
    textParagraph(label, { bold: true, after: 50, color: "1F4E78" }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
      children: [
        new ImageRun({
          type: "png",
          data: fs.readFileSync(item.path),
          transformation: { width, height },
          altText: { title: label, description: label, name },
        }),
      ],
    }),
  ];
}

function cell(text, width, options = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    shading: options.fill
      ? { fill: options.fill, type: ShadingType.CLEAR }
      : undefined,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [
      new Paragraph({
        alignment: options.alignment || AlignmentType.CENTER,
        children: [
          new TextRun({
            text: String(text),
            font: "Microsoft YaHei",
            size: options.size || 19,
            bold: options.bold || false,
            color: options.color || "111827",
          }),
        ],
      }),
    ],
  });
}

function makeTable(headers, rows, widths, options = {}) {
  const allRows = [];
  allRows.push(
    new TableRow({
      tableHeader: true,
      children: headers.map((value, index) =>
        cell(value, widths[index], { fill: options.headerFill || "D9EAF7", bold: true })
      ),
    })
  );
  for (const row of rows) {
    allRows.push(
      new TableRow({
        children: row.map((value, index) =>
          cell(value, widths[index], {
            alignment: index === 0 && options.leftFirst ? AlignmentType.LEFT : AlignmentType.CENTER,
            fill: options.bodyFill,
            size: options.size || 18,
          })
        ),
      })
    );
  }
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: allRows,
  });
}

function callout(title, lines, fill = "FFF2CC") {
  const children = [textParagraph(title, { bold: true, color: "9C5700", after: 80 })];
  lines.forEach((line, index) => {
    children.push(textParagraph(`${index + 1}. ${line}`, { size: 20, after: 50 }));
  });
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [CONTENT_WIDTH],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            borders,
            shading: { fill, type: ShadingType.CLEAR },
            margins: { top: 140, bottom: 140, left: 180, right: 180 },
            children,
          }),
        ],
      }),
    ],
  });
}

function figureParagraph(fileName, width, height, description) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 140 },
    children: [
      new ImageRun({
        type: "png",
        data: fs.readFileSync(path.join(modelDir, "output", "figures", fileName)),
        transformation: { width, height },
        altText: { title: description, description, name: fileName },
      }),
    ],
  });
}

const children = [];
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 280, after: 180 },
    children: [
      new TextRun({
        text: "A题第一问模型——教师检查版",
        font: "Microsoft YaHei",
        size: 38,
        bold: true,
        color: "17365D",
      }),
    ],
  }),
  textParagraph("本文件专门用于教师审阅。核心模型、关键假设和代码入口已经单独标出；公式均以高清图片嵌入，避免 Word/WPS 公式乱码。", {
    alignment: AlignmentType.CENTER,
    size: 22,
    color: "374151",
  }),
  callout("先看这里：四个最重要的文件", [
    "主控制模型：src\\matlab\\solve_q1_cn.m",
    "边界数据处理：src\\matlab\\fit_boundary_curves.m",
    "PINN 模型：src\\python\\train_q1_pinn.py",
    "一键运行入口：run_q1_all.m",
  ], "E2F0D9"),
  heading("一、模型文件与作用"),
  makeTable(
    ["优先级", "文件", "教师检查内容"],
    [
      ["核心", "src\\matlab\\solve_q1_cn.m", "控制方程、Robin 边界、CN/FVM、Picard 迭代"],
      ["核心", "src\\matlab\\run_q1_cn_fit.m", "参数、网格、时间步、收敛与守恒验证"],
      ["边界", "src\\matlab\\fit_boundary_curves.m", "温度采用附件1线性插值；非线性拟合作辅助对照"],
      ["验证", "src\\python\\train_q1_pinn.py", "PINN 方程残差、初边界损失、CN 对比"],
      ["入口", "run_q1_all.m", "按顺序运行 MATLAB 主解和 PyTorch PINN"],
    ],
    [1200, 3600, 5200],
    { leftFirst: true, size: 18 }
  ),
  heading("二、请老师重点检查的六个判断"),
  callout("这些不是计算错误，而是需要确认的建模假设", [
    "圆柱长25 cm、半径2 cm，主模型按一维径向处理并忽略端面；端面面积约占总表面积7.4%。",
    "补充公式文档是平板直角坐标方程，本模型已改为圆柱径向算子。",
    "题目没有给汽化潜热和相变源项，因此热方程不加入蒸发潜热项。",
    "空气含水率与固体干基含水率直接组成 Robin 传质边界，被视为题目给出的等效经验关系。",
    "附件1温度每60 s有观测值，表1主模型使用分段线性插值；全时段非线性拟合仅作辅助。",
    "PINN 是同一 PDE 的交叉数值验证，不是独立实验验证。",
  ]),
  new Paragraph({ children: [new PageBreak()] }),
  heading("三、核心控制模型——请重点检查"),
  textParagraph("变量：T(r,t) 为药材温度，X(r,t) 为干基含水率，R=0.02 m。采用轴对称一维圆柱径向模型。"),
  ...equation("heat_pde", "模型1：圆柱径向非稳态热传导方程"),
  ...equation("moisture_pde", "模型2：含水率非线性扩散方程"),
  ...equation("diffusivity", "题设扩散系数"),
  ...equation("initial_center", "初始条件与中心对称条件"),
  ...equation("surface_robin", "表面 Robin 换热与传质条件"),
  heading("四、参数表"),
  makeTable(
    ["参数", "数值", "单位", "来源/作用"],
    [
      ["R", "0.02", "m", "题目给定半径2 cm"],
      ["ρ", "820", "kg/m³", "题目附录2"],
      ["cp", "2600", "J/(kg·K)", "题目附录2"],
      ["k", "0.36", "W/(m·K)", "题目附录2"],
      ["hT", "25", "W/(m²·K)", "表面对流换热"],
      ["hm", "8×10⁻⁷", "m/s", "表面对流传质"],
      ["T0", "28", "°C", "初始温度"],
      ["X0", "2.55", "kg/kg", "初始干基含水率"],
    ],
    [1500, 1900, 2200, 4500],
    { size: 18 }
  ),
  heading("五、边界数据处理与辅助非线性拟合"),
  textParagraph("表1的烘房温度边界直接对附件1做分段线性插值，以避免全时段单曲线拟合带来的系统偏差。下表的拉伸指数拟合保留用于参数化分析；烘房含水率仍使用该非线性拟合。"),
  ...equation("boundary_fit", "边界拟合模型"),
  makeTable(
    ["变量", "稳态值", "τ/s", "β", "RMSE", "R²"],
    [
      ["烘房温度（辅助）", "50.016", "1884.1", "1.1503", "0.14419 °C", "0.999202"],
      ["烘房含水率", "0.05025", "2729.9", "1.2532", "0.00020768", "0.999346"],
    ],
    [1800, 1700, 1500, 1300, 1900, 1700],
    { size: 18 }
  ),
  figureParagraph("boundary_curve_fit.png", 640, 272, "附件1非线性边界拟合"),
  new Paragraph({ children: [new PageBreak()] }),
  heading("六、Crank–Nicolson 与有限体积求解"),
  textParagraph("空间采用圆柱径向有限体积法，避免 r=0 奇点；时间使用 Crank–Nicolson。D(X) 的非线性通过每个时间步的 Picard 迭代处理。"),
  ...equation("crank_nicolson", "CN 离散形式（M 为容量矩阵，L 为径向通量算子）"),
  makeTable(
    ["检查项", "结果"],
    [
      ["细网格", "Δr=0.0125 cm，Δt=0.5 s"],
      ["温度最大网格差", "9.26×10⁻⁵ °C"],
      ["含水率最大网格差", "1.418×10⁻³ kg/kg"],
      ["热量守恒相对误差", "1.07×10⁻¹²"],
      ["水分守恒相对误差", "2.42×10⁻¹⁴"],
      ["Picard 最大迭代次数", "13"],
    ],
    [4300, 5900],
    { leftFirst: true, size: 18 }
  ),
  figureParagraph("cn_center_surface_history.png", 640, 272, "CN中心和表面响应"),
  heading("七、PINN 交叉验证"),
  ...equation("pinn_loss", "PINN 损失函数结构"),
  textParagraph("PINN 使用 PyTorch 2.13.0+cpu，温度和水分各采用4层、每层48个神经元的 tanh 网络；训练点只用于方程和初边界条件，CN 解仅在训练结束后用于比较。"),
  makeTable(
    ["指标", "温度", "含水率"],
    [
      ["PINN 对 CN 的 RMSE", "0.01024 °C", "0.01146 kg/kg"],
      ["PINN 对 CN 的 MAE", "0.00792 °C", "0.00742 kg/kg"],
      ["最大绝对差", "0.04723 °C", "0.05507 kg/kg"],
      ["训练物理损失", "2.32×10⁻⁴", "2.25×10⁻³"],
    ],
    [3600, 3200, 3400],
    { size: 18 }
  ),
  figureParagraph("pinn_training_and_validation.png", 640, 272, "PINN物理残差与CN交叉验证"),
  new Paragraph({ children: [new PageBreak()] }),
  heading("八、表1：30分钟内药材的温度（°C）"),
  makeTable(["时间/s", "0 cm", "0.5 cm", "1 cm", "1.5 cm", "2 cm"], table1, [1200, 1760, 1760, 1760, 1760, 1760], { size: 16 }),
  heading("九、表2：30分钟内药材的水分浓度（kg/kg）"),
  makeTable(["时间/s", "0 cm", "0.5 cm", "1 cm", "1.5 cm", "2 cm"], table2, [1200, 1760, 1760, 1760, 1760, 1760], { size: 16 }),
  heading("十、建议教师审阅结论"),
  callout("请在以下项目后标注“同意”或给出修改意见", [
    "一维径向简化：____________",
    "表面传热/传质边界：____________",
    "D(X) 经验式读取：____________",
    "边界数据拟合方式：____________",
    "CN/FVM 数值方法：____________",
    "PINN 验证表述：____________",
  ], "EDE9FE"),
  textParagraph("教师总体意见：____________________________________________________________", { after: 200 }),
  textParagraph("签字：____________________    日期：____________________", { after: 100 })
);

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { font: "Microsoft YaHei", size: 29, bold: true, color: "17365D" },
        paragraph: { spacing: { before: 260, after: 140 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { font: "Microsoft YaHei", size: 25, bold: true, color: "1F4E78" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: 16838 },
          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
        },
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "A题第一问模型教师检查版  |  第 ", font: "Microsoft YaHei", size: 18, color: "6B7280" }),
                new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 18, color: "6B7280" }),
                new TextRun({ text: " 页", font: "Microsoft YaHei", size: 18, color: "6B7280" }),
              ],
            }),
          ],
        }),
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputFile, buffer);
  process.stdout.write(outputFile);
});
