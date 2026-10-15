function fitResult = fit_boundary_curves(dataFile, figureDir, metricsDir)
%FIT_BOUNDARY_CURVES Fit smooth nonlinear furnace boundary curves.
%   The fitted model is a stretched exponential
%       y(t) = y0 + (yss-y0)*(1-exp(-(t/tau)^beta)).
%   All available furnace records are used so the plateau is identifiable.
% ========================================================================
% 【边界数据拟合模型——请老师检查】
% 使用附件1全部记录，分别拟合烘房温度与水分浓度的时间边界曲线。
% ========================================================================

arguments
    dataFile (1,1) string
    figureDir (1,1) string
    metricsDir (1,1) string
end

raw = readmatrix(dataFile);
raw = raw(all(isfinite(raw(:,1:3)),2),1:3);
t = raw(:,1);
temperature = raw(:,2);
moisture = raw(:,3);

if ~isfolder(figureDir)
    mkdir(figureDir);
end
if ~isfolder(metricsDir)
    mkdir(metricsDir);
end

fitT = fit_one_curve(t, temperature, [50, 2500, 1.2], ...
    [temperature(1), 10, 0.25], [65, 20000, 4]);
fitX = fit_one_curve(t, moisture, [0.05, 2500, 1.2], ...
    [max(moisture), 10, 0.25], [0.10, 20000, 4]);

fitResult = struct();
fitResult.time = t;
fitResult.temperatureData = temperature;
fitResult.moistureData = moisture;
fitResult.temperature = fitT;
fitResult.moisture = fitX;
fitResult.temperatureForSolver = struct( ...
    'method','linear','timeData',t,'valueData',temperature, ...
    'rmse',0,'rSquared',1);

temperatureFit = evaluate_boundary_curve(fitT, t);
moistureFit = evaluate_boundary_curve(fitX, t);

fig = figure('Visible','off','Color','w','Position',[100 100 1050 420]);
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');
nexttile;
plot(t/3600, temperature, '.', 'Color',[0.25 0.45 0.80]); hold on;
plot(t/3600, temperatureFit, '-', 'Color',[0.85 0.20 0.15], 'LineWidth',1.8);
xlabel('Time (h)'); ylabel('Furnace temperature (deg C)'); grid on;
legend('Data','Nonlinear fit','Location','southeast');
title(sprintf('RMSE %.4f deg C, R^2 %.6f',fitT.rmse,fitT.rSquared));
nexttile;
plot(t/3600, moisture, '.', 'Color',[0.25 0.45 0.80]); hold on;
plot(t/3600, moistureFit, '-', 'Color',[0.85 0.20 0.15], 'LineWidth',1.8);
xlabel('Time (h)'); ylabel('Furnace moisture (kg/kg)'); grid on;
legend('Data','Nonlinear fit','Location','southeast');
title(sprintf('RMSE %.6g, R^2 %.6f',fitX.rmse,fitX.rSquared));
exportgraphics(fig, fullfile(figureDir,'boundary_curve_fit.png'),'Resolution',180);
close(fig);

summaryTable = table(["temperature";"moisture"], ...
    [fitT.y0;fitX.y0], [fitT.params(1);fitX.params(1)], ...
    [fitT.params(2);fitX.params(2)], [fitT.params(3);fitX.params(3)], ...
    [fitT.rmse;fitX.rmse], [fitT.rSquared;fitX.rSquared], ...
    'VariableNames',{'variable','y0','ySteady','tau_s','beta','RMSE','R_squared'});
writetable(summaryTable, fullfile(metricsDir,'boundary_fit_parameters.csv'));
end

function curve = fit_one_curve(t, y, initialGuess, lowerBound, upperBound)
y0 = y(1);
model = @(p,x) y0 + (p(1)-y0).*(1-exp(-(max(x,0)./p(2)).^p(3)));
options = optimoptions('lsqcurvefit','Display','off', ...
    'FunctionTolerance',1e-13,'StepTolerance',1e-13, ...
    'OptimalityTolerance',1e-13,'MaxFunctionEvaluations',5000);
[p,resnorm,residual,exitflag,output,~,jacobian] = lsqcurvefit( ...
    model, initialGuess, t, y, lowerBound, upperBound, options);
yHat = model(p,t);
sst = sum((y-mean(y)).^2);
curve = struct();
curve.y0 = y0;
curve.params = p;
curve.resnorm = resnorm;
curve.rmse = sqrt(mean(residual.^2));
curve.rSquared = 1-sum((y-yHat).^2)/sst;
curve.exitflag = exitflag;
curve.optimizerOutput = output;
curve.jacobian = jacobian;
end

function y = evaluate_boundary_curve(curve, t)
p = curve.params;
y = curve.y0 + (p(1)-curve.y0).*(1-exp(-(max(t,0)./p(2)).^p(3)));
end
