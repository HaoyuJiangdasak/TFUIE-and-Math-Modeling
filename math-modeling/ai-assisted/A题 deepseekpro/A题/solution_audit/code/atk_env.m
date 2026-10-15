%% ATK 3/4/6: 切换时刻、附件1插值方式、h/hm 敏感性
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));
[Rf, Rdf] = radius_profile(A2);
tA = A1(:,1); TA = A1(:,2); XA = A1(:,3);

N=640; dt=10;                       % 便宜档；关键配置再用 N=1280,dt=2 复核
mkP = @(which, Tf, Xf, h, hm) struct( ...
    'N',N,'dt',dt,'tEnd',8*86400,'R0',0.02,'T0',28,'X0',2.55,'h',h,'hm',hm, ...
    'rho',tern(which==4, @(X) 760+90*X, @(X) 650+128*X), ...
    'cp', tern(which==4, @(X) 1850+2150*X./(X+1), @(X) 1450+2736*X./(X+1)), ...
    'kc', tern(which==4, @(X) 0.12+0.20*X./(X+1), @(X) 0.21+0.38*X./(X+1)), ...
    'Dco', tern(which==4, @(X,TK) 4.2e-4*exp(-0.30./X).*exp(-3850./TK), ...
                          @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK)), ...
    'Tf',Tf,'Xf',Xf, ...
    'Rf', tern(which==4, Rf, @(t) 0.02+0*t), ...
    'Rdf',tern(which==4, Rdf, @(t) 0*t), ...
    'record',0:3600:8*86400,'picard',4,'Xdry',0.15);

cfgs = {};
cfgs{end+1} = {'基准 linear, t1=14400',   prof(tA,TA,50   ,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 25, 8e-7};
cfgs{end+1} = {'切换 t1=9000',            prof(tA,TA,50   , 9000,'linear'), prof(tA,XA,0.05, 9000,'linear'), 25, 8e-7};
cfgs{end+1} = {'切换 t1=10800',           prof(tA,TA,50   ,10800,'linear'), prof(tA,XA,0.05,10800,'linear'), 25, 8e-7};
cfgs{end+1} = {'切换 t1=12600',           prof(tA,TA,50   ,12600,'linear'), prof(tA,XA,0.05,12600,'linear'), 25, 8e-7};
cfgs{end+1} = {'切换 t1=1800 (早)',       prof(tA,TA,50   , 1800,'linear'), prof(tA,XA,0.05, 1800,'linear'), 25, 8e-7};
cfgs{end+1} = {'插值 pchip, t1=14400',    prof(tA,TA,50   ,14400,'pchip'),  prof(tA,XA,0.05,14400,'pchip'),  25, 8e-7};
cfgs{end+1} = {'插值 spline, t1=14400',   prof(tA,TA,50   ,14400,'spline'), prof(tA,XA,0.05,14400,'spline'), 25, 8e-7};
cfgs{end+1} = {'末段取附件实测 50.165/0.04986', prof(tA,TA,50.165,14400,'linear'), prof(tA,XA,0.04986,14400,'linear'), 25, 8e-7};
cfgs{end+1} = {'h = 12.5 (x0.5)',         prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 12.5, 8e-7};
cfgs{end+1} = {'h = 50 (x2)',             prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 50, 8e-7};
cfgs{end+1} = {'h = 250 (x10)',           prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 250, 8e-7};
cfgs{end+1} = {'h = 1e6 (准等温边界)',    prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 1e6, 8e-7};
cfgs{end+1} = {'hm = 4e-7 (x0.5)',        prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 25, 4e-7};
cfgs{end+1} = {'hm = 1.6e-6 (x2)',        prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 25, 1.6e-6};
cfgs{end+1} = {'hm = 8e-6 (x10)',         prof(tA,TA,50,14400,'linear'), prof(tA,XA,0.05,14400,'linear'), 25, 8e-6};

fid = savelog('atk_env.txt');
fprintf(fid,'==== ATK3/4/6 环境-插值-系数敏感性（N=%d, dt=%d, Xdry=0.15）====\n\n',N,dt);
fprintf(fid,'%-38s %14s %14s\n','配置','问题3时长(h)','问题4时长(h)');
for k = 1:numel(cfgs)
    c = cfgs{k};
    r = zeros(1,2);
    for which = [3 4]
        P = mkP(which, c{2}, c{3}, c{4}, c{5});
        S = herb_solver(P);
        r(which-2) = S.dryTime/3600;
    end
    fprintf(fid,'%-38s %14.4f %14.4f\n', c{1}, r(1), r(2));
end

%% 关键配置的 N=1280,dt=2 复核
fprintf(fid,'\n==== N=1280, dt=2 复核 ====\n');
fprintf(fid,'%-38s %14s %14s\n','配置','问题3时长(h)','问题4时长(h)');
ck = [1 2 6 13 15];
for k = ck
    c = cfgs{k};
    r = zeros(1,2);
    for which = [3 4]
        P = mkP(which, c{2}, c{3}, c{4}, c{5});
        P.N = 1280; P.dt = 2; P.record = 0:3600:P.tEnd;
        S = herb_solver(P);
        r(which-2) = S.dryTime/3600;
    end
    fprintf(fid,'%-38s %14.4f %14.4f\n', c{1}, r(1), r(2));
end
fclose(fid);
disp('atk_env 完成');

function h = prof(tA, yA, yset, t1, method)
h = @(t) ev(t, tA, yA, yset, t1, method);
end
function v = ev(t, tt, yy, yset, t1, method)
tq = min(t, t1);
switch method
    case 'pchip',  v = interp1(tt, yy, tq, 'pchip');
    case 'spline', v = interp1(tt, yy, tq, 'spline');
    otherwise,     v = interp1(tt, yy, tq, 'linear');
end
v(t > t1) = yset;
end
function a = tern(c, x, y)
if c, a = x; else, a = y; end
end
