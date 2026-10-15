%% 计时基准：不同网格数 N 与时间步长 dt 下的求解耗时（以问题2的长时段为背景）
clear; clc;
ROOT = fileparts(mfilename('fullpath'));
A1 = readmatrix(fullfile(ROOT,'附件1.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
R0 = 0.02;

cases = [ 40 1; 80 1; 160 1; 320 1; 160 5; 320 5; 320 10 ];
fid = savelog('timing.txt');
fprintf(fid,'%-6s %-6s %-12s %-10s %-12s\n','N','dt','tEnd(s)','耗时(s)','X表面(末)');
for k = 1:size(cases,1)
    N = cases(k,1); dt = cases(k,2); tEnd = 60000;
    P = struct();
    P.N = N; P.dt = dt; P.tEnd = tEnd;
    P.R0 = R0; P.T0 = 28; P.X0 = 2.55; P.h = 25; P.hm = 8e-7;
    P.rho = @(X) 650 + 128*X;
    P.cp  = @(X) 1450 + 2736*X./(X+1);
    P.kc  = @(X) 0.21 + 0.38*X./(X+1);
    P.Dco = @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
    P.Tf = Tf; P.Xf = Xf;
    P.Rf = @(t) R0 + 0*t; P.Rdf = @(t) 0*t;
    P.record = 0:60:tEnd; P.picard = 3;
    t0 = tic; S = herb_solver(P); el = toc(t0);
    fprintf(fid,'%-6d %-6d %-12d %-10.2f %-12.6f\n', N, dt, tEnd, el, S.X(end,end));
end
fclose(fid);
disp('计时完成');
