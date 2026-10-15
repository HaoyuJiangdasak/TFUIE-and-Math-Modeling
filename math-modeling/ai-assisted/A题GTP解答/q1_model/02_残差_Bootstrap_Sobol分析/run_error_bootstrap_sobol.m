% 第一问：残差、RMSE、R^2、Bootstrap 与 Sobol 全局敏感性分析
% 运行本文件会在当前文件夹的 output 子目录生成 CSV、XLSX、PNG 和 MAT 文件。
clear; clc;

analysisDir = fileparts(mfilename('fullpath'));
modelDir = fileparts(analysisDir);
workspaceDir = fileparts(modelDir);
srcDir = fullfile(modelDir,'src','matlab');
outputDir = fullfile(analysisDir,'output');
tablesDir = fullfile(outputDir,'tables');
figuresDir = fullfile(outputDir,'figures');
modelsDir = fullfile(outputDir,'models');
for folder = {outputDir,tablesDir,figuresDir,modelsDir}
    if ~isfolder(folder{1}), mkdir(folder{1}); end
end
addpath(srcDir);

rng(20260910,'twister');
bootstrapReplicates = environment_number('Q1_BOOTSTRAP_B',1000);
sobolBaseN = environment_number('Q1_SOBOL_N',2048);
sobolBootstrapReplicates = environment_number('Q1_SOBOL_BOOTSTRAP_B',1000);
if mod(sobolBaseN,2) ~= 0
    error('Q1_SOBOL_N must be even.');
end

%% 1. 读取基准拟合与附件数据
referenceFile = fullfile(modelDir,'output','models','q1_cn_reference.mat');
reference = load(referenceFile,'boundaryFit','solverBoundaryFit','fine');
boundaryFit = reference.boundaryFit;
if isfield(reference,'solverBoundaryFit')
    sensitivityBoundaryFit = reference.solverBoundaryFit;
else
    sensitivityBoundaryFit = boundaryFit;
end
dataFile = fullfile(workspaceDir,'A题','附件','附件1.xlsx');
raw = readmatrix(dataFile);
raw = raw(all(isfinite(raw(:,1:3)),2),1:3);
t = raw(:,1);
observedT = raw(:,2);
observedX = raw(:,3);
fittedT = evaluate_boundary_curve(boundaryFit.temperature,t);
fittedX = evaluate_boundary_curve(boundaryFit.moisture,t);
residualT = observedT-fittedT; % 残差定义：观测值-预测值
residualX = observedX-fittedX;

boundaryResiduals = table(t,observedT,fittedT,residualT,observedX,fittedX,residualX, ...
    'VariableNames',{'time_s','temperature_observed_C','temperature_fitted_C', ...
    'temperature_residual_C','moisture_observed_kgkg','moisture_fitted_kgkg', ...
    'moisture_residual_kgkg'});

metricRows = [error_metric_row("Boundary fit: temperature",observedT,fittedT,"C"); ...
              error_metric_row("Boundary fit: moisture",observedX,fittedX,"kg/kg")];

% PINN-CN 残差也纳入同一统计口径，CN 作为数值参照。
pinnFile = fullfile(modelDir,'output','results','pinn_requested_samples.csv');
pinn = readtable(pinnFile,'VariableNamingRule','preserve');
metricRows = [metricRows; ...
    error_metric_row("PINN vs CN: temperature",pinn.CN_temperature_C, ...
        pinn.PINN_temperature_C,"C"); ...
    error_metric_row("PINN vs CN: moisture",pinn.CN_moisture_kgkg, ...
        pinn.PINN_moisture_kgkg,"kg/kg")];

diagnostics = table( ...
    ["Heat balance relative residual";"Moisture balance relative residual"], ...
    [reference.fine.heatBalanceRelativeError;reference.fine.moistureBalanceRelativeError], ...
    ["relative";"relative"], ...
    'VariableNames',{'diagnostic','value','unit'});

%% 2. 移动块残差 Bootstrap：边界曲线参数与拟合带
fprintf('Running %d moving-block bootstrap fits for each boundary curve...\n',bootstrapReplicates);
bootT = bootstrap_curve(t,observedT,boundaryFit.temperature, ...
    [observedT(1),10,0.25],[65,20000,4],bootstrapReplicates,1101);
bootX = bootstrap_curve(t,observedX,boundaryFit.moisture, ...
    [max(observedX),10,0.25],[0.10,20000,4],bootstrapReplicates,2202);

bootstrapParameters = [bootstrap_parameter_table("temperature",boundaryFit.temperature,bootT); ...
                       bootstrap_parameter_table("moisture",boundaryFit.moisture,bootX)];
bootstrapFitMetrics = [bootstrap_metric_table("temperature",boundaryFit.temperature,bootT); ...
                       bootstrap_metric_table("moisture",boundaryFit.moisture,bootX)];
bootstrapBands = table(t,fittedT,bootT.bandLow,bootT.bandHigh, ...
    fittedX,bootX.bandLow,bootX.bandHigh, ...
    'VariableNames',{'time_s','temperature_fit','temperature_CI_low', ...
    'temperature_CI_high','moisture_fit','moisture_CI_low','moisture_CI_high'});

fig = figure('Visible','off','Color','w','Position',[100 100 1120 720]);
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
nexttile;
fill([t;flipud(t)]/3600,[bootT.bandLow;flipud(bootT.bandHigh)], ...
    [0.82 0.90 1.00],'EdgeColor','none'); hold on;
plot(t/3600,observedT,'.','Color',[0.25 0.25 0.25]);
plot(t/3600,fittedT,'b-','LineWidth',1.5);
xlabel('Time (h)'); ylabel('Temperature (deg C)'); grid on;
title('Boundary fit and 95% bootstrap band');
legend('95% bootstrap band','Data','Fit','Location','southeast');
nexttile;
plot(t/3600,residualT,'Color',[0.80 0.20 0.15]); yline(0,'k--');
xlabel('Time (h)'); ylabel('Observed - fitted (deg C)'); grid on;
title(sprintf('Temperature residuals: RMSE %.4f, R^2 %.6f', ...
    metricRows.RMSE(1),metricRows.R_squared(1)));
nexttile;
fill([t;flipud(t)]/3600,[bootX.bandLow;flipud(bootX.bandHigh)], ...
    [0.85 0.95 0.85],'EdgeColor','none'); hold on;
plot(t/3600,observedX,'.','Color',[0.25 0.25 0.25]);
plot(t/3600,fittedX,'Color',[0.10 0.55 0.20],'LineWidth',1.5);
xlabel('Time (h)'); ylabel('Moisture (kg/kg)'); grid on;
title('Boundary fit and 95% bootstrap band');
legend('95% bootstrap band','Data','Fit','Location','southeast');
nexttile;
plot(t/3600,residualX,'Color',[0.65 0.15 0.65]); yline(0,'k--');
xlabel('Time (h)'); ylabel('Observed - fitted (kg/kg)'); grid on;
title(sprintf('Moisture residuals: RMSE %.3g, R^2 %.6f', ...
    metricRows.RMSE(2),metricRows.R_squared(2)));
exportgraphics(fig,fullfile(figuresDir,'residuals_and_bootstrap_bands.png'),'Resolution',200);
close(fig);

%% 3. Sobol 一阶和总效应分析
% 附件没有参数概率分布。以下区间是工程探索假设，不是测量置信区间。
parameterNames = ["k";"Cv_rho_cp";"hT";"D0";"diffusivity_exponent";"hM"];
baseline = [0.36,820*2600,25,7e-9,0.89,8e-7];
lowerBound = [0.288,0.8*820*2600,17.5,3.5e-9,0.712,5.6e-7];
upperBound = [0.432,1.2*820*2600,32.5,1.4e-8,1.068,1.04e-6];
distribution = ["uniform";"uniform";"uniform";"log-uniform";"uniform";"uniform"];
parameterRanges = table(parameterNames,baseline',lowerBound',upperBound',distribution, ...
    'VariableNames',{'parameter','baseline','lower','upper','distribution'});

dimension = numel(parameterNames);
sequence = sobolset(2*dimension,'Skip',1024,'Leap',0);
sequence = scramble(sequence,'MatousekAffineOwen');
unitSamples = net(sequence,sobolBaseN);
sampleA = map_parameters(unitSamples(:,1:dimension),lowerBound,upperBound);
sampleB = map_parameters(unitSamples(:,dimension+1:end),lowerBound,upperBound);
allSamples = [sampleA;sampleB];
for i = 1:dimension
    mixed = sampleA;
    mixed(:,i) = sampleB(:,i);
    allSamples = [allSamples;mixed]; %#ok<AGROW>
end

outputNames = ["T_center_1800s";"T_surface_1800s";"T_volume_mean_1800s"; ...
    "maximum_radial_delta_T";"X_surface_1800s";"X_volume_mean_1800s"; ...
    "mean_moisture_loss";"maximum_radial_delta_X"];
numberOutputs = numel(outputNames);
allOutputs = zeros(size(allSamples,1),numberOutputs);

pool = gcp('nocreate');
if isempty(pool)
    try
        pool = parpool('threads');
    catch
        pool = parpool('local');
    end
end
fprintf('Running %d model evaluations on %d workers for Sobol analysis...\n', ...
    size(allSamples,1),pool.NumWorkers);
parfor row = 1:size(allSamples,1)
    allOutputs(row,:) = simulate_outputs(sensitivityBoundaryFit,allSamples(row,:));
end

YA = allOutputs(1:sobolBaseN,:);
YB = allOutputs(sobolBaseN+1:2*sobolBaseN,:);
YAB = zeros(sobolBaseN,numberOutputs,dimension);
offset = 2*sobolBaseN;
for i = 1:dimension
    rows = offset+(i-1)*sobolBaseN+(1:sobolBaseN);
    YAB(:,:,i) = allOutputs(rows,:);
end

[Sfirst,STotal,outputVariance] = sobol_jansen(YA,YB,YAB);
[SfirstHalf,STotalHalf] = sobol_jansen(YA(1:sobolBaseN/2,:), ...
    YB(1:sobolBaseN/2,:),YAB(1:sobolBaseN/2,:,:));

fprintf('Bootstrapping Sobol indices (%d resamples)...\n',sobolBootstrapReplicates);
[SbootLow,SbootHigh,STbootLow,STbootHigh] = bootstrap_sobol( ...
    YA,YB,YAB,sobolBootstrapReplicates,3303);

sobolRows = dimension*numberOutputs;
sobolOutput = strings(sobolRows,1);
sobolParameter = strings(sobolRows,1);
first = zeros(sobolRows,1); firstLow = first; firstHigh = first;
total = first; totalLow = first; totalHigh = first;
firstHalf = first; totalHalf = first; deltaN = first;
halfSampleSize = repmat(sobolBaseN/2,sobolRows,1);
fullSampleSize = repmat(sobolBaseN,sobolRows,1);
counter = 0;
for out = 1:numberOutputs
    for i = 1:dimension
        counter = counter+1;
        sobolOutput(counter) = outputNames(out);
        sobolParameter(counter) = parameterNames(i);
        first(counter) = Sfirst(i,out);
        firstLow(counter) = SbootLow(i,out);
        firstHigh(counter) = SbootHigh(i,out);
        total(counter) = STotal(i,out);
        totalLow(counter) = STbootLow(i,out);
        totalHigh(counter) = STbootHigh(i,out);
        firstHalf(counter) = SfirstHalf(i,out);
        totalHalf(counter) = STotalHalf(i,out);
        deltaN(counter) = max(abs(Sfirst(i,out)-SfirstHalf(i,out)), ...
            abs(STotal(i,out)-STotalHalf(i,out)));
    end
end
sobolIndices = table(sobolOutput,sobolParameter,first,firstLow,firstHigh, ...
    total,totalLow,totalHigh,halfSampleSize,fullSampleSize,firstHalf,totalHalf,deltaN, ...
    'VariableNames',{'output','parameter','S_first','S_first_CI_low', ...
    'S_first_CI_high','ST_total','ST_total_CI_low','ST_total_CI_high', ...
    'half_sample_size','full_sample_size','S_first_half_sample', ...
    'ST_total_half_sample','max_change_half_to_full'});
varianceTable = table(outputNames,outputVariance', ...
    'VariableNames',{'output','sample_variance'});

% 基准参数下检查分析网格相对原细网格的误差。
baselineOutputs = simulate_outputs(sensitivityBoundaryFit,baseline);
fineOutputs = extract_outputs(reference.fine);
gridCheck = table(outputNames,baselineOutputs',fineOutputs', ...
    (baselineOutputs-fineOutputs)',abs(baselineOutputs-fineOutputs)', ...
    'VariableNames',{'output','analysis_grid','fine_reference','difference','absolute_difference'});

% 输出 Sobol 分组图。
fig = figure('Visible','off','Color','w','Position',[100 100 1320 900]);
tiledlayout(2,4,'Padding','compact','TileSpacing','compact');
for out = 1:numberOutputs
    nexttile;
    bar([Sfirst(:,out),STotal(:,out)],'grouped');
    ylim([min(-0.1,min(Sfirst(:,out))-0.05),max(1.05,max(STotal(:,out))+0.05)]);
    xticks(1:dimension); xticklabels(parameterNames); xtickangle(35);
    ylabel('Sobol index'); grid on; title(strrep(outputNames(out),'_',' '));
    if out == 1, legend('First order','Total effect','Location','best'); end
end
exportgraphics(fig,fullfile(figuresDir,'sobol_first_and_total_effects.png'),'Resolution',200);
close(fig);

%% 4. 保存全部结果
writetable(metricRows,fullfile(tablesDir,'model_error_metrics.csv'));
writetable(boundaryResiduals,fullfile(tablesDir,'boundary_fit_residuals.csv'));
writetable(diagnostics,fullfile(tablesDir,'conservation_residuals.csv'));
writetable(bootstrapParameters,fullfile(tablesDir,'bootstrap_parameter_CI.csv'));
writetable(bootstrapFitMetrics,fullfile(tablesDir,'bootstrap_fit_metric_CI.csv'));
writetable(bootstrapBands,fullfile(tablesDir,'bootstrap_curve_bands.csv'));
writetable(parameterRanges,fullfile(tablesDir,'sobol_parameter_ranges.csv'));
writetable(sobolIndices,fullfile(tablesDir,'sobol_indices_with_bootstrap_CI.csv'));
writetable(varianceTable,fullfile(tablesDir,'sobol_output_variance.csv'));
writetable(gridCheck,fullfile(tablesDir,'sobol_grid_validation.csv'));

workbook = fullfile(outputDir,'第一问_残差_Bootstrap_Sobol结果.xlsx');
writetable(metricRows,workbook,'Sheet','误差指标');
writetable(diagnostics,workbook,'Sheet','守恒残差');
writetable(boundaryResiduals,workbook,'Sheet','边界拟合残差');
writetable(bootstrapParameters,workbook,'Sheet','Bootstrap参数区间');
writetable(bootstrapFitMetrics,workbook,'Sheet','Bootstrap指标区间');
writetable(bootstrapBands,workbook,'Sheet','Bootstrap拟合带');
writetable(parameterRanges,workbook,'Sheet','Sobol参数区间');
writetable(sobolIndices,workbook,'Sheet','Sobol指数');
writetable(varianceTable,workbook,'Sheet','输出方差');
writetable(gridCheck,workbook,'Sheet','网格验证');

save(fullfile(modelsDir,'bootstrap_sobol_full_results.mat'), ...
    'metricRows','boundaryResiduals','diagnostics','bootT','bootX', ...
    'parameterRanges','sampleA','sampleB','YA','YB','YAB','sobolIndices', ...
    'varianceTable','gridCheck','bootstrapReplicates','sobolBaseN', ...
    'sobolBootstrapReplicates');

summary = struct();
summary.residualDefinition = 'observed minus predicted';
summary.bootstrapMethod = 'circular moving-block residual bootstrap';
summary.bootstrapReplicates = bootstrapReplicates;
summary.sobolEstimator = 'Jansen first-order and total-effect estimators';
summary.sobolBaseSampleSize = sobolBaseN;
summary.sobolModelEvaluations = size(allSamples,1);
summary.sobolBootstrapReplicates = sobolBootstrapReplicates;
summary.parameterRangeCaveat = ['Ranges are engineering exploratory assumptions; ' ...
    'the problem attachments provide no parameter probability distributions.'];
fid = fopen(fullfile(outputDir,'analysis_metadata.json'),'w');
fprintf(fid,'%s',jsonencode(summary,PrettyPrint=true)); fclose(fid);

disp(metricRows);
disp(bootstrapParameters);
disp(sobolIndices(sobolIndices.output=="T_volume_mean_1800s" | ...
    sobolIndices.output=="mean_moisture_loss",:));
fprintf('Results workbook: %s\n',workbook);

%% Local functions
function row = error_metric_row(name,observed,predicted,unit)
observed = observed(:); predicted = predicted(:);
residual = observed-predicted;
sse = sum(residual.^2);
sst = sum((observed-mean(observed)).^2);
if sst <= eps(max(abs(observed)))
    rSquared = NaN;
else
    rSquared = 1-sse/sst;
end
row = table(string(name),numel(observed),sqrt(mean(residual.^2)), ...
    mean(abs(residual)),mean(residual),std(residual),max(abs(residual)), ...
    rSquared,string(unit),'VariableNames',{'comparison','N','RMSE','MAE', ...
    'residual_mean','residual_std','residual_max_abs','R_squared','unit'});
end

function boot = bootstrap_curve(t,y,curve,lowerBound,upperBound,B,seed)
rng(seed,'twister');
n = numel(y);
yHat = evaluate_curve(curve.y0,curve.params,t);
residual = y-yHat;
residual = residual-mean(residual);
blockLength = max(5,round(sqrt(n)));
indices = circular_block_indices(n,B,blockLength);
params = NaN(B,3); rmse = NaN(B,1); rSquared = NaN(B,1);
predictions = NaN(n,B);
options = optimoptions('lsqcurvefit','Display','off', ...
    'FunctionTolerance',1e-10,'StepTolerance',1e-10, ...
    'OptimalityTolerance',1e-10,'MaxFunctionEvaluations',2000);
y0 = curve.y0; p0 = curve.params;
sampledResiduals = residual(indices);
parfor b = 1:B
    yStar = yHat+sampledResiduals(:,b);
    model = @(p,x) evaluate_curve(y0,p,x);
    try
        p = lsqcurvefit(model,p0,t,yStar,lowerBound,upperBound,options);
        pred = model(p,t);
        params(b,:) = p;
        predictions(:,b) = pred;
        err = yStar-pred;
        rmse(b) = sqrt(mean(err.^2));
        rSquared(b) = 1-sum(err.^2)/sum((yStar-mean(yStar)).^2);
    catch
        % 保留 NaN，汇总前剔除失败拟合。
    end
end
valid = all(isfinite(params),2) & isfinite(rmse) & isfinite(rSquared);
boot.params = params(valid,:);
boot.rmse = rmse(valid);
boot.rSquared = rSquared(valid);
boot.predictions = predictions(:,valid);
boot.bandLow = prctile(boot.predictions,2.5,2);
boot.bandHigh = prctile(boot.predictions,97.5,2);
boot.blockLength = blockLength;
boot.successfulReplicates = nnz(valid);
boot.requestedReplicates = B;
end

function indices = circular_block_indices(n,B,L)
indices = zeros(n,B);
numberBlocks = ceil(n/L);
for b = 1:B
    starts = randi(n,numberBlocks,1);
    sample = zeros(numberBlocks*L,1);
    cursor = 1;
    for block = 1:numberBlocks
        values = mod((starts(block)-1)+(0:L-1),n)+1;
        sample(cursor:cursor+L-1) = values;
        cursor = cursor+L;
    end
    indices(:,b) = sample(1:n);
end
end

function result = bootstrap_parameter_table(variable,curve,boot)
names = ["ySteady";"tau_s";"beta"];
estimate = curve.params(:);
low = prctile(boot.params,2.5,1)';
high = prctile(boot.params,97.5,1)';
result = table(repmat(string(variable),3,1),names,estimate,low,high, ...
    repmat(boot.successfulReplicates,3,1),repmat(boot.blockLength,3,1), ...
    'VariableNames',{'variable','parameter','estimate','CI_2_5_percent', ...
    'CI_97_5_percent','successful_replicates','block_length'});
end

function result = bootstrap_metric_table(variable,curve,boot)
metric = ["RMSE";"R_squared"];
estimate = [curve.rmse;curve.rSquared];
low = [prctile(boot.rmse,2.5);prctile(boot.rSquared,2.5)];
high = [prctile(boot.rmse,97.5);prctile(boot.rSquared,97.5)];
result = table(repmat(string(variable),2,1),metric,estimate,low,high, ...
    repmat(boot.successfulReplicates,2,1), ...
    'VariableNames',{'variable','metric','estimate','CI_2_5_percent', ...
    'CI_97_5_percent','successful_replicates'});
end

function y = evaluate_curve(y0,p,t)
y = y0+(p(1)-y0).*(1-exp(-(max(t,0)./p(2)).^p(3)));
end

function parameters = map_parameters(U,lower,upper)
parameters = lower+U.*(upper-lower);
% 第4列 D0 使用对数均匀分布。
parameters(:,4) = exp(log(lower(4))+U(:,4).*(log(upper(4))-log(lower(4))));
end

function values = simulate_outputs(boundaryFit,p)
cpFixed = 2600;
solution = solve_q1_cn(boundaryFit,dr=5e-4,dt=5,tEnd=1800, ...
    picardTolerance=1e-8,picardMaxIterations=25,picardRelaxation=0.85, ...
    rho=p(2)/cpFixed,cp=cpFixed,k=p(1),hT=p(3),D0=p(4), ...
    diffusivityExponent=p(5),hM=p(6));
values = extract_outputs(solution);
end

function values = extract_outputs(solution)
r = solution.r_m(:);
R = r(end);
finalT = solution.temperature_C(end,:)';
finalX = solution.moisture_kgkg(end,:)';
meanT = 2/R^2*trapz(r,finalT.*r);
meanX = 2/R^2*trapz(r,finalX.*r);
deltaT = max(solution.temperature_C(:,end)-solution.temperature_C(:,1));
deltaX = max(solution.moisture_kgkg(:,1)-solution.moisture_kgkg(:,end));
values = [finalT(1),finalT(end),meanT,deltaT,finalX(end),meanX, ...
    solution.moisture_kgkg(1,1)-meanX,deltaX];
end

function [S,ST,V] = sobol_jansen(YA,YB,YAB)
[~,numberOutputs,dimension] = size(YAB);
V = var([YA;YB],1,1);
S = NaN(dimension,numberOutputs);
ST = NaN(dimension,numberOutputs);
for out = 1:numberOutputs
    if V(out) <= 100*eps(max(1,mean(abs([YA(:,out);YB(:,out)]))))
        continue;
    end
    for i = 1:dimension
        S(i,out) = 1-mean((YB(:,out)-YAB(:,out,i)).^2)/(2*V(out));
        ST(i,out) = mean((YA(:,out)-YAB(:,out,i)).^2)/(2*V(out));
    end
end
end

function [SLow,SHigh,STLow,STHigh] = bootstrap_sobol(YA,YB,YAB,B,seed)
rng(seed,'twister');
N = size(YA,1);
[~,numberOutputs,dimension] = size(YAB);
Ssamples = NaN(B,dimension,numberOutputs);
STsamples = NaN(B,dimension,numberOutputs);
indices = randi(N,N,B);
for b = 1:B
    idx = indices(:,b);
    [Sb,STb] = sobol_jansen(YA(idx,:),YB(idx,:),YAB(idx,:,:));
    Ssamples(b,:,:) = reshape(Sb,[1,dimension,numberOutputs]);
    STsamples(b,:,:) = reshape(STb,[1,dimension,numberOutputs]);
end
SLow = squeeze(prctile(Ssamples,2.5,1));
SHigh = squeeze(prctile(Ssamples,97.5,1));
STLow = squeeze(prctile(STsamples,2.5,1));
STHigh = squeeze(prctile(STsamples,97.5,1));
end

function value = environment_number(name,defaultValue)
text = getenv(name);
if isempty(text)
    value = defaultValue;
else
    value = str2double(text);
    if ~isfinite(value) || value <= 0 || value ~= floor(value)
        error('%s must be a positive integer.',name);
    end
end
end
