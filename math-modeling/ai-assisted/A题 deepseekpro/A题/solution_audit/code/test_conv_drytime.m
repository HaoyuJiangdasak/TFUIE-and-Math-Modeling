%% 烘干时长（问题3）的网格收敛性细化研究 + 末态剖面诊断
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
R0 = 0.02;
fid = savelog('conv_drytime.txt');

Nlist = [160 320 640 1280 2560];
fprintf(fid,'烘干时长随网格 N 的变化（dt = 10 s）\n');
fprintf(fid,'%6s %14s %10s %14s %14s\n','N','烘干时长(s)','(h)','末态 X 中心','末态 X 表面');
Sm = {};
for k = 1:numel(Nlist)
    N = Nlist(k);
    P = struct();
    P.N = N; P.dt = 10; P.tEnd = 15*86400;
    P.R0 = R0; P.T0 = 28; P.X0 = 2.55; P.h = 25; P.hm = 8e-7;
    P.rho = @(X) 650 + 128*X;
    P.cp  = @(X) 1450 + 2736*X./(X+1);
    P.kc  = @(X) 0.21 + 0.38*X./(X+1);
    P.Dco = @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
    P.Tf = Tf; P.Xf = Xf;
    P.Rf = @(t) R0 + 0*t; P.Rdf = @(t) 0*t;
    P.record = 0:3600:P.tEnd; P.picard = 4; P.Xdry = 0.15;
    t0 = tic; S = herb_solver(P); el = toc(t0);
    fprintf(fid,'%6d %14.0f %10.4f %14.6f %14.6f   (%.1f s)\n', ...
        N, S.dryTime, S.dryTime/3600, S.X(end,1), S.X(end,end));
    Sm{k} = S;
end

% 末态剖面（N = 1280）
S = Sm{end-1}; rn = S.xi*R0*100;
fprintf(fid,'\nN=%d 末态含水率剖面（中心附近）\n', Nlist(end-1));
for r = [0 0.05 0.1 0.2 0.3 0.5 0.75 1.0 1.25 1.5 1.75 1.9 1.95 1.99 2.0]
    fprintf(fid,'  r=%.2f cm : X=%.6f  D=%.3e\n', r, ...
        interp1(rn,S.X(end,:),min(r,max(rn)),'pchip'), ...
        P.Dco(interp1(rn,S.X(end,:),min(r,max(rn)),'pchip'), 323));
end
fclose(fid);
disp('完成');
