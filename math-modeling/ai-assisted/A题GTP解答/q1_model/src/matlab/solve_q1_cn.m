function result = solve_q1_cn(boundaryFit, options)
%SOLVE_Q1_CN Conservative radial finite-volume Crank-Nicolson solver.
%   Moisture-dependent diffusivity is handled by Picard iteration.
% ========================================================================
% 【核心物理模型——请老师重点检查】
% 圆柱径向非稳态导热 + 非线性水分扩散；表面采用 Robin 边界。
% 空间离散：守恒有限体积；时间离散：Crank-Nicolson (theta = 0.5)。
% ========================================================================

arguments
    boundaryFit struct
    options.R (1,1) double = 0.02
    options.length (1,1) double = 0.25
    options.tEnd (1,1) double = 1800
    options.dt (1,1) double = 1
    options.dr (1,1) double = 2.5e-4
    options.theta (1,1) double = 0.5
    options.picardTolerance (1,1) double = 1e-11
    options.picardMaxIterations (1,1) double = 40
    options.picardRelaxation (1,1) double = 0.85
    options.rho (1,1) double = 820
    options.cp (1,1) double = 2600
    options.k (1,1) double = 0.36
    options.hT (1,1) double = 25
    options.hM (1,1) double = 8e-7
    options.T0 (1,1) double = 28
    options.X0 (1,1) double = 2.55
    options.D0 (1,1) double = 7e-9
    options.diffusivityExponent (1,1) double = 0.89
end

rho = options.rho;
cp = options.cp;
k = options.k;
hT = options.hT;
hM = options.hM;
T0 = options.T0;
X0 = options.X0;
D0 = options.D0;
diffusivityExponent = options.diffusivityExponent;

R = options.R;
dt = options.dt;
dr = options.dr;
theta = options.theta;
nIntervals = round(R/dr);
r = linspace(0,R,nIntervals+1)';
t = (0:dt:options.tEnd)';
nR = numel(r);
nT = numel(t);

volumeWeight = control_volume_weights(r,R);
massT = spdiags(rho*cp*volumeWeight,0,nR,nR);
massX = spdiags(volumeWeight,0,nR,nR);

[operatorT,boundaryT] = assemble_flux_operator(r,R,k*ones(nR,1),hT);
matrixT = massT/dt-theta*operatorT;
explicitT = massT/dt+(1-theta)*operatorT;

temperature = zeros(nT,nR);
moisture = zeros(nT,nR);
temperature(1,:) = T0;
moisture(1,:) = X0;
picardIterations = zeros(nT,1);

temperatureBoundary = evaluate_boundary_curve(boundaryFit.temperature,t);
moistureBoundary = evaluate_boundary_curve(boundaryFit.moisture,t);

for n = 1:nT-1
    oldT = temperature(n,:)';
    rhsT = explicitT*oldT + boundaryT*( ...
        theta*temperatureBoundary(n+1)+(1-theta)*temperatureBoundary(n));
    newT = matrixT\rhsT;
    temperature(n+1,:) = newT';

    oldX = moisture(n,:)';
    diffusivityOld = moisture_diffusivity(oldX,D0,diffusivityExponent);
    [operatorOld,boundaryX] = assemble_flux_operator(r,R,diffusivityOld,hM);
    explicitX = massX/dt+(1-theta)*operatorOld;
    guess = oldX;
    for iteration = 1:options.picardMaxIterations
        diffusivityGuess = moisture_diffusivity(guess,D0,diffusivityExponent);
        [operatorNew,~] = assemble_flux_operator(r,R,diffusivityGuess,hM);
        matrixX = massX/dt-theta*operatorNew;
        rhsX = explicitX*oldX + boundaryX*( ...
            theta*moistureBoundary(n+1)+(1-theta)*moistureBoundary(n));
        candidate = matrixX\rhsX;
        candidate = max(candidate,0);
        if max(abs(candidate-guess)) < options.picardTolerance
            guess = candidate;
            break;
        end
        guess = options.picardRelaxation*candidate + ...
            (1-options.picardRelaxation)*guess;
    end
    picardIterations(n+1) = iteration;
    moisture(n+1,:) = guess';
end

areaFactor = 2*pi*options.length;
storedEnergyChange = areaFactor*rho*cp*sum(volumeWeight.*(temperature(end,:)'-T0));
heatInputRate = areaFactor*R*hT*(temperatureBoundary-temperature(:,end));
integratedHeatInput = trapz(t,heatInputRate);
heatBalanceRelativeError = abs(storedEnergyChange-integratedHeatInput) / ...
    max(abs(integratedHeatInput),eps);

initialMoistureInventory = areaFactor*sum(volumeWeight.*moisture(1,:)');
finalMoistureInventory = areaFactor*sum(volumeWeight.*moisture(end,:)');
moistureOutRate = areaFactor*R*hM*(moisture(:,end)-moistureBoundary);
integratedMoistureOut = trapz(t,moistureOutRate);
moistureBalanceRelativeError = abs((initialMoistureInventory-finalMoistureInventory)- ...
    integratedMoistureOut)/max(abs(integratedMoistureOut),eps);

result = struct();
result.r_m = r;
result.t_s = t;
result.temperature_C = temperature;
result.moisture_kgkg = moisture;
result.temperatureBoundary_C = temperatureBoundary;
result.moistureBoundary_kgkg = moistureBoundary;
result.picardIterations = picardIterations;
result.maxPicardIterations = max(picardIterations);
result.heatBalanceRelativeError = heatBalanceRelativeError;
result.moistureBalanceRelativeError = moistureBalanceRelativeError;
result.options = options;
end

function weights = control_volume_weights(r,R)
n = numel(r);
weights = zeros(n,1);
for i = 1:n
    if i == 1
        west = 0;
    else
        west = 0.5*(r(i-1)+r(i));
    end
    if i == n
        east = R;
    else
        east = 0.5*(r(i)+r(i+1));
    end
    weights(i) = 0.5*(east^2-west^2);
end
end

function [L,b] = assemble_flux_operator(r,R,gamma,h)
n = numel(r);
rows = zeros(3*n,1);
cols = zeros(3*n,1);
values = zeros(3*n,1);
counter = 0;
b = zeros(n,1);
for i = 1:n
    diagonal = 0;
    if i > 1
        west = 0.5*(r(i-1)+r(i));
        gammaWest = harmonic_mean(gamma(i-1),gamma(i));
        coefficientWest = west*gammaWest/(r(i)-r(i-1));
        counter = counter+1;
        rows(counter)=i; cols(counter)=i-1; values(counter)=coefficientWest;
        diagonal = diagonal-coefficientWest;
    end
    if i < n
        east = 0.5*(r(i)+r(i+1));
        gammaEast = harmonic_mean(gamma(i),gamma(i+1));
        coefficientEast = east*gammaEast/(r(i+1)-r(i));
        counter = counter+1;
        rows(counter)=i; cols(counter)=i+1; values(counter)=coefficientEast;
        diagonal = diagonal-coefficientEast;
    else
        surfaceCoefficient = R*h;
        diagonal = diagonal-surfaceCoefficient;
        b(i) = surfaceCoefficient;
    end
    counter = counter+1;
    rows(counter)=i; cols(counter)=i; values(counter)=diagonal;
end
L = sparse(rows(1:counter),cols(1:counter),values(1:counter),n,n);
end

function value = harmonic_mean(a,b)
value = 2*a*b/max(a+b,realmin);
end

function D = moisture_diffusivity(X,D0,diffusivityExponent)
Xsafe = max(X,1e-8);
D = D0*exp(-diffusivityExponent./Xsafe);
end
