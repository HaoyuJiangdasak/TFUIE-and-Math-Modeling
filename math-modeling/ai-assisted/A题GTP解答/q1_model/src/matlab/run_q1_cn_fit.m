%RUN_Q1_CN_FIT Fit the furnace boundary and solve Question 1 by CN/FVM.
clc;
thisDir = fileparts(mfilename('fullpath'));
modelDir = fileparts(fileparts(thisDir));
workspaceDir = fileparts(modelDir);
dataFile = fullfile(workspaceDir,'A题','附件','附件1.xlsx');
resultsDir = fullfile(modelDir,'output','results');
figuresDir = fullfile(modelDir,'output','figures');
metricsDir = fullfile(modelDir,'output','metrics');
modelsDir = fullfile(modelDir,'output','models');
outputDirs = {resultsDir,figuresDir,metricsDir,modelsDir};
for i = 1:numel(outputDirs)
    if ~isfolder(outputDirs{i})
        mkdir(outputDirs{i});
    end
end

addpath(thisDir);
boundaryFit = fit_boundary_curves(dataFile,figuresDir,metricsDir);
solverBoundaryFit = boundaryFit;
% 问题1只计算附件1已有数据覆盖的0--1800 s。温度边界直接采用
% 附件1的分段线性插值，避免全4小时单曲线拟合给表1带来系统偏差。
% 水分边界仍沿用原非线性拟合，因此表2保持不变。
solverBoundaryFit.temperature = boundaryFit.temperatureForSolver;

fine = solve_q1_cn(solverBoundaryFit,dr=1.25e-4,dt=0.5,tEnd=1800);
coarse = solve_q1_cn(solverBoundaryFit,dr=2.5e-4,dt=1,tEnd=1800);

sampleTimes = [100 300 600 900 1200 1500 1800];
sampleRadiusCm = [0 0.5 1 1.5 2];
fineTemperature = interp2(fine.r_m*100,fine.t_s,fine.temperature_C, ...
    sampleRadiusCm,sampleTimes','linear');
fineMoisture = interp2(fine.r_m*100,fine.t_s,fine.moisture_kgkg, ...
    sampleRadiusCm,sampleTimes','linear');
coarseTemperature = interp2(coarse.r_m*100,coarse.t_s,coarse.temperature_C, ...
    sampleRadiusCm,sampleTimes','linear');
coarseMoisture = interp2(coarse.r_m*100,coarse.t_s,coarse.moisture_kgkg, ...
    sampleRadiusCm,sampleTimes','linear');

gridConvergenceTemperature = max(abs(fineTemperature-coarseTemperature),[],'all');
gridConvergenceMoisture = max(abs(fineMoisture-coarseMoisture),[],'all');

resultFile = fullfile(resultsDir,'result1_cn.xlsx');
export_q1_results(fine,resultFile);
save(fullfile(modelsDir,'q1_cn_reference.mat'),'fine','coarse','boundaryFit', ...
    'solverBoundaryFit', ...
    'fineTemperature','fineMoisture','sampleTimes','sampleRadiusCm');

fig = figure('Visible','off','Color','w','Position',[100 100 1050 420]);
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');
nexttile;
plot(fine.t_s/60,fine.temperature_C(:,1),'LineWidth',1.7); hold on;
plot(fine.t_s/60,fine.temperature_C(:,end),'LineWidth',1.7);
plot(fine.t_s/60,fine.temperatureBoundary_C,'--','LineWidth',1.4);
xlabel('Time (min)'); ylabel('Temperature (deg C)'); grid on;
legend('Center','Surface','Furnace','Location','northwest'); title('CN temperature solution');
nexttile;
plot(fine.t_s/60,fine.moisture_kgkg(:,1),'LineWidth',1.7); hold on;
plot(fine.t_s/60,fine.moisture_kgkg(:,end),'LineWidth',1.7);
plot(fine.t_s/60,fine.moistureBoundary_kgkg,'--','LineWidth',1.4);
xlabel('Time (min)'); ylabel('Moisture (kg/kg)'); grid on;
legend('Center','Surface','Furnace','Location','southwest'); title('CN moisture solution');
exportgraphics(fig,fullfile(figuresDir,'cn_center_surface_history.png'),'Resolution',180);
close(fig);

metrics = struct();
metrics.temperatureBoundaryMethod = 'linear interpolation of Attachment 1';
metrics.boundaryTemperatureRMSE = solverBoundaryFit.temperature.rmse;
metrics.boundaryTemperatureR2 = solverBoundaryFit.temperature.rSquared;
metrics.parametricTemperatureRMSE = boundaryFit.temperature.rmse;
metrics.parametricTemperatureR2 = boundaryFit.temperature.rSquared;
metrics.boundaryMoistureRMSE = boundaryFit.moisture.rmse;
metrics.boundaryMoistureR2 = boundaryFit.moisture.rSquared;
metrics.gridConvergenceTemperatureMaxAbs = gridConvergenceTemperature;
metrics.gridConvergenceMoistureMaxAbs = gridConvergenceMoisture;
metrics.heatBalanceRelativeError = fine.heatBalanceRelativeError;
metrics.moistureBalanceRelativeError = fine.moistureBalanceRelativeError;
metrics.maxPicardIterations = fine.maxPicardIterations;
metrics.temperatureMinimum = min(fine.temperature_C,[],'all');
metrics.temperatureMaximum = max(fine.temperature_C,[],'all');
metrics.moistureMinimum = min(fine.moisture_kgkg,[],'all');
metrics.moistureMaximum = max(fine.moisture_kgkg,[],'all');
fid = fopen(fullfile(metricsDir,'cn_validation_metrics.json'),'w');
fprintf(fid,'%s',jsonencode(metrics,PrettyPrint=true));
fclose(fid);

disp('Nonlinear boundary-fit parameters:');
disp(readtable(fullfile(metricsDir,'boundary_fit_parameters.csv')));
fprintf('Grid convergence max |dT| = %.6g C\n',gridConvergenceTemperature);
fprintf('Grid convergence max |dX| = %.6g kg/kg\n',gridConvergenceMoisture);
fprintf('Heat balance relative error = %.6g\n',fine.heatBalanceRelativeError);
fprintf('Moisture balance relative error = %.6g\n',fine.moistureBalanceRelativeError);
fprintf('Result workbook: %s\n',resultFile);
