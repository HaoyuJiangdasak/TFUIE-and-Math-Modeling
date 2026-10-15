%RUN_Q1_ALL Reproduce nonlinear fitting, CN/FVM solution, and PINN training.
% ========================================================================
% 【老师检查入口】第一问完整模型的一键运行文件
% 依次完成：边界数据非线性拟合 -> Crank-Nicolson/FVM 求解 -> PINN 验证。
% ========================================================================
clear; clc;
modelDir = fileparts(mfilename('fullpath'));
matlabDir = fullfile(modelDir,'src','matlab');
addpath(matlabDir);
run(fullfile(matlabDir,'run_q1_cn_fit.m'));
pythonExe = 'C:\Users\Public\miniconda3\envs\dl\python.exe';
summaryScript = fullfile(modelDir,'src','python','create_summary_tables.py');
summaryStatus = system(sprintf('"%s" "%s"',pythonExe,summaryScript));
if summaryStatus ~= 0
    warning('Corrected Table 1/Table 2 workbook generation failed.');
end
run(fullfile(matlabDir,'run_q1_pinn.m'));
