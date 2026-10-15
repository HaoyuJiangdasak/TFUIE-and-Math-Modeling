%% =========================================================================
%  网格收敛性检验（修正 D 公式后重做）
%   (A) 问题 1：t = 1800 s 时若干半径处的 T、X 随 N 的变化
%   (B) 问题 3：烘干总时长随 N 的变化
% =========================================================================
clear; clc;
ROOT = fileparts(mfilename('fullpath'));
A1 = readmatrix(fullfile(ROOT,'附件1.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
R0 = 0.02;
fid = savelog('convergence.txt');

%% ---------- (A) 问题 1 ----------
Nlist = [20 40 80 160 320 640];
res = zeros(numel(Nlist), 8);
for k = 1:numel(Nlist)
    P = struct();
    P.N = Nlist(k); P.dt = 1; P.tEnd = 1800;
    P.R0 = R0; P.T0 = 28; P.X0 = 2.55; P.h = 25; P.hm = 8e-7;
    P.rho = @(X) 820 + 0*X;  P.cp = @(X) 2600 + 0*X;
    P.kc  = @(X) 0.36 + 0*X; P.Dco = @(X,TK) 7e-9*exp(-0.89./X);
    P.Tf = Tf; P.Xf = Xf;
    P.Rf = @(t) R0 + 0*t;    P.Rdf = @(t) 0*t;
    P.record = 1800; P.picard = 5;
    S = herb_solver(P);
    rn = S.xi*R0*100;
    res(k,:) = [interp1(rn,S.T(end,:),[0 1 1.5 2],'pchip'), ...
                interp1(rn,S.X(end,:),[0 0.5 1.5 2],'pchip')];
end
ref = res(end,:);
fprintf(fid,'(A) 问题 1，t = 1800 s\n');
fprintf(fid,'%6s %10s %10s %10s %10s | %10s %10s %10s %10s | %10s\n', ...
  'N','T(r=0)','T(r=1)','T(r=1.5)','T(r=2)','X(r=0)','X(r=.5)','X(r=1.5)','X(r=2)','最大相对偏差');
for k = 1:numel(Nlist)
    fprintf(fid,'%6d %10.5f %10.5f %10.5f %10.5f | %10.5f %10.5f %10.5f %10.5f | %10.3e\n', ...
        Nlist(k), res(k,:), max(abs(res(k,:)-ref)./max(abs(ref),1e-12)));
end

%% ---------- (B) 问题 3 的烘干时长 ----------
fprintf(fid,'\n(B) 问题 3 烘干时长随网格的变化\n');
fprintf(fid,'%6s %6s %14s %14s\n','N','dt','烘干时长(s)','烘干时长(h)');
for N = [40 80 160 320]
  for dt = [1 5]
    P2 = struct();
    P2.N = N; P2.dt = dt; P2.tEnd = 10*86400;
    P2.R0 = R0; P2.T0 = 28; P2.X0 = 2.55; P2.h = 25; P2.hm = 8e-7;
    P2.rho = @(X) 650 + 128*X;
    P2.cp  = @(X) 1450 + 2736*X./(X+1);
    P2.kc  = @(X) 0.21 + 0.38*X./(X+1);
    P2.Dco = @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
    P2.Tf = Tf; P2.Xf = Xf;
    P2.Rf = @(t) R0 + 0*t; P2.Rdf = @(t) 0*t;
    P2.record = 0:3600:P2.tEnd; P2.picard = 4; P2.Xdry = 0.15;
    t0 = tic; S3 = herb_solver(P2); el = toc(t0);
    fprintf(fid,'%6d %6d %14.0f %14.4f   (耗时 %.1f s)\n', N, dt, S3.dryTime, S3.dryTime/3600, el);
  end
end
fclose(fid);
disp('完成');
