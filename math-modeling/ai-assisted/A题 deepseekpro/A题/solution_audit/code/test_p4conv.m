%% =========================================================================
%  问题 4 的网格收敛性 + 模型/参数敏感性分析
% =========================================================================
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
[Rf, Rdf] = radius_profile(A2);
R0 = 0.02;
fid = savelog('p4conv.txt');

%% ---------- (A) 网格与步长收敛 ----------
fprintf(fid,'(A) 问题 4 网格收敛性（关键量：烘干时长、6h/24h 时若干位置的 X）\n');
fprintf(fid,'%6s %6s %12s %14s %14s %14s\n','N','dt','烘干时长(h)','X(r0=0,24h)','X(r0=1,24h)','X(表面,24h)');
for N = [160 320 640 1280 2560]
  for dt = [2 10]
    P = mkp4(N,dt,R0,Tf,Xf,Rf,Rdf);
    t0=tic; S = herb_solver(P); el=toc(t0);
    r0n = S.xi*R0*100;  Xq = interp1(r0n,S.X.',[0 1 2],'pchip').';
    v24 = interp1(S.t, Xq, 86400, 'linear');
    fprintf(fid,'%6d %6d %12.4f %14.6f %14.6f %14.6f   (%.1fs)\n', N, dt, S.dryTime/3600, v24, el);
  end
end

%% ---------- (B) 参数敏感性 ----------
fprintf(fid,'\n(B) 问题 3 / 问题 4 对假设参数的敏感性（N=640, dt=10）\n');
fprintf(fid,'%-28s %14s %14s\n','参数设置','问题3 时长(h)','问题4 时长(h)');
cases = {
  '基准 h=25, hm=8e-7, Xf=0.05, Tf=50', 25, 8e-7, 0.05, 50;
  'hm = 1.6e-6 (×2)',                  25, 1.6e-6, 0.05, 50;
  'hm = 4e-7  (×0.5)',                 25, 4e-7, 0.05, 50;
  'h  = 50    (×2)',                   50, 8e-7, 0.05, 50;
  'Xf = 0.02',                         25, 8e-7, 0.02, 50;
  'Xf = 0.10',                         25, 8e-7, 0.10, 50;
  'Tf = 45 degC',                      25, 8e-7, 0.05, 45;
  'Tf = 55 degC',                      25, 8e-7, 0.05, 55;
};
for k = 1:size(cases,1)
    h_ = cases{k,2}; hm_ = cases{k,3}; Xs_ = cases{k,4}; Ts_ = cases{k,5};
    [Tfk, Xfk] = ambient_profile(A1, Ts_, Xs_);
    Pa = mkp3(640,10,R0,Tfk,Xfk,h_,hm_);  Sa = herb_solver(Pa);
    Pb = mkp4(640,10,R0,Tfk,Xfk,Rf,Rdf,h_,hm_);  Sb = herb_solver(Pb);
    fprintf(fid,'%-28s %14.4f %14.4f\n', cases{k,1}, Sa.dryTime/3600, Sb.dryTime/3600);
end

%% ---------- (C) 收缩模型对比：仿射（正确）vs 只算网格运动（错误对照） ----------
fprintf(fid,'\n(C) 收缩坐标处理方式对比（N=640, dt=10）\n');
Pa = mkp4(640,10,R0,Tf,Xf,Rf,Rdf);              Sa = herb_solver(Pa);
Pb = mkp4(640,10,R0,Tf,Xf,Rf,Rdf); Pb.advModel='grid'; Sb = herb_solver(Pb);
fprintf(fid,'  仿射收缩（无对流项，正确） : 烘干时长 = %.4f h，末端 X(中心) = %.6f\n', Sa.dryTime/3600, Sa.X(end,1));
fprintf(fid,'  仅网格运动（错误对照）     : 烘干时长 = %.4f h，末端 X(中心) = %.6f\n', Sb.dryTime/3600, Sb.X(end,1));
fclose(fid);
disp('完成');


function P = mkp4(N,dt,R0,Tf,Xf,Rf,Rdf,h,hm)
if nargin<8, h=25; end
if nargin<9, hm=8e-7; end
P = struct();
P.N=N; P.dt=dt; P.tEnd=15*86400; P.R0=R0; P.T0=28; P.X0=2.55;
P.h=h; P.hm=hm;
P.rho=@(X) 760+90*X;  P.cp=@(X) 1850+2150*X./(X+1);
P.kc =@(X) 0.12+0.20*X./(X+1);
P.Dco=@(X,TK) 4.2e-4*exp(-0.30./X).*exp(-3850./TK);
P.Tf=Tf; P.Xf=Xf; P.Rf=Rf; P.Rdf=Rdf;
P.record=0:3600:P.tEnd; P.picard=4; P.Xdry=0.15;
end
function P = mkp3(N,dt,R0,Tf,Xf,h,hm)
P = struct();
P.N=N; P.dt=dt; P.tEnd=15*86400; P.R0=R0; P.T0=28; P.X0=2.55;
P.h=h; P.hm=hm;
P.rho=@(X) 650+128*X;  P.cp=@(X) 1450+2736*X./(X+1);
P.kc =@(X) 0.21+0.38*X./(X+1);
P.Dco=@(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
P.Tf=Tf; P.Xf=Xf;
P.Rf=@(t) R0+0*t;  P.Rdf=@(t) 0*t;
P.record=0:3600:P.tEnd; P.picard=4; P.Xdry=0.15;
end
