%% 对比 D 的两种可能形式对结果的影响
clear; clc;
ROOT = fileparts(mfilename('fullpath'));
A1 = readmatrix(fullfile(ROOT,'附件1.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
R0 = 0.02;

forms = {'linear: exp(-k*X)', 'inverse: exp(-k/X)'};
Dfun = { @(X,TK) 7e-9*exp(-0.89*X),            @(X,TK) 7e-9*exp(-0.89./X) };
D3   = { @(X,TK) 2.4e-3*exp(-0.45*X).*exp(-3850./TK), @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK) };

for f = 1:2
    % ---- 问题1 ----
    P = struct(); P.N=160; P.dt=1; P.tEnd=1800;
    P.R0=R0; P.T0=28; P.X0=2.55; P.h=25; P.hm=8e-7;
    P.rho=@(X) 820+0*X; P.cp=@(X) 2600+0*X; P.kc=@(X) 0.36+0*X; P.Dco=Dfun{f};
    P.Tf=Tf; P.Xf=Xf; P.Rf=@(t) R0+0*t; P.Rdf=@(t) 0*t;
    P.record=[100 300 600 900 1200 1500 1800]; P.picard=3;
    S1 = herb_solver(P);
    rn = S1.xi*R0*100; rq=[0 0.5 1 1.5 2];
    X1 = interp1(rn, S1.X.', rq, 'pchip').';
    fprintf('%s\n', forms{f});
    fprintf('  D(X=2.55)=%.3e  D(X=1.0)=%.3e  D(X=0.15)=%.3e\n', Dfun{f}(2.55,301), Dfun{f}(1.0,301), Dfun{f}(0.15,301));
    fprintf('  问题1 X 表 (行=100..1800s, 列=r=0,.5,1,1.5,2cm):\n');
    disp(round(X1,4));

    % ---- 问题3 干燥时间（放宽上限）----
    P2 = struct(); P2.N=160; P2.dt=5; P2.tEnd=20*86400;
    P2.R0=R0; P2.T0=28; P2.X0=2.55; P2.h=25; P2.hm=8e-7;
    P2.rho=@(X) 650+128*X; P2.cp=@(X) 1450+2736*X./(X+1); P2.kc=@(X) 0.21+0.38*X./(X+1);
    P2.Dco=D3{f}; P2.Tf=Tf; P2.Xf=Xf; P2.Rf=@(t) R0+0*t; P2.Rdf=@(t) 0*t;
    P2.record=0:3600:P2.tEnd; P2.picard=3; P2.Xdry=0.15;
    t0=tic; S3 = herb_solver(P2); el=toc(t0);
    fprintf('  问题3 干燥时间 = %.0f s = %.2f h = %.3f d  (耗时%.1fs)\n', S3.dryTime, S3.dryTime/3600, S3.dryTime/86400, el);
    fprintf('  D3(X=2.55,323K)=%.3e   D3(X=0.15,323K)=%.3e\n\n', D3{f}(2.55,323), D3{f}(0.15,323));
end
