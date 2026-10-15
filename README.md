# TFUIE 复现与高教社杯数学建模 A 题资料归档

这个私有仓库整理了三组本地资料：

- `tfuie/`：Task-Friendly Underwater Image Enhancement（TFUIE）论文、汇报 PPT、复现笔记和代码。
- `math-modeling/ai-assisted/`：高教社杯数学建模大赛 A 题的多套 AI 辅助求解路线。
- `math-modeling/manual-solution/`：手工建模代码、附件、结果、图表和 Notebook。
- `math-modeling/beginner-handbook/`：A 题零基础手册的 TeX 源码、代码和 PDF。
- `math-modeling/standard-analysis/`：标准分析求解包。
- `math-modeling/personal-solution/`：个人求解工作区中可复用的论文、代码和图表。

## 大文件

GitHub 单个普通 Git 文件不能超过 100 MB。以下源文件保留在本地原目录，并作为 GitHub Release 资产上传：

- `tfuie/code/TFUIE/model_data/vgg16-397923af.pth`
- `tfuie/code/TFUIE/model_data/vgg19-dcbb9e9d.pth`
- `math-modeling/manual-solution/packages/Q2_competition_final_outputs.zip`

下载 Release 资产后，按上述路径放回即可使用。会话日志、AI memory、缓存、编译后的 `.pyc`、临时目录和个人 `manifest.json` 已排除，以免把绝对路径和上下文日志提交到仓库。

## 说明

TFUIE 代码目录原本带有上游仓库历史；本仓库以当前本地复现材料为准，并保留原有许可证文件。数学建模资料包含多条独立求解路线，报告中的数值与图表按原目录保留，运行前请根据各子目录中的说明配置 Python/MATLAB 环境和输入附件。
