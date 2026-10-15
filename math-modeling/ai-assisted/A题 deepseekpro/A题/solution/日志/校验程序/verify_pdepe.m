%% =========================================================================
%  独立交叉验证：用 MATLAB 内置 pdepe 重新求解问题 1/2/3，
%  与自编有限体积求解器 herb_solver 的结果逐点比较。
%  pdepe 采用自适应时间步长 + 二阶空间离散，与自编程序是两套完全不同的算法，
%  两者一致即可排除编程错误。
% =========================================================================
clear; clc;
ROOT = fileparts(mfilename('fullpath'));
A1 = readmatrix(fullfile(ROOT,'附件1.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
R0 = 0.02;
fid = savelog('verify_pdepe.txt');

%% ================= 问题 1 =================
m = 1;                                   % 柱坐标
N = 1280; xmesh = linspace(0,R0,N+1)';
tt = [0 100 300 600 900 1200 1500 1800];   % pdepe 在 tspan(1) 处施加初值，故必须包含 t=0
sol = pdepe(m, @pde1, @ic1, @bc1, xmesh, tt, ...
            odeset('RelTol',1e-8,'AbsTol',1e-10));
% pdepe 返回 sol: [nt x (N+1) x 2]
P = struct(); P.N=320; P.dt=1; P.tEnd=1800;
P.R0=R0; P.T0=28; P.X0=2.55; P.h=25; P.hm=8e-7;
P.rho=@(X) 820+0*X; P.cp=@(X) 2600+0*X; P.kc=@(X) 0.36+0*X;
P.Dco=@(X,TK) 7e-9*exp(-0.89./X);
P.Tf=Tf; P.Xf=Xf; P.Rf=@(t) R0+0*t; P.Rdf=@(t) 0*t;
P.record=tt; P.picard=4;
S = herb_solver(P);
rn = S.xi*R0*100;  rq = [0 0.5 1 1.5 2];
Tfv_ = interp1(rn, S.T.', rq, 'pchip').';
Xfv_ = interp1(rn, S.X.', rq, 'pchip').';
Tfv_ = Tfv_(2:end,:); Xfv_ = Xfv_(2:end,:);   % 去掉 t=0 行（FV 的 record 含 0）
Tp = squeeze(sol(:,:,1));  Xp = squeeze(sol(:,:,2));
Tp = Tp(2:end,:); Xp = Xp(2:end,:);      % 去掉 t=0 行，与 FV 的 100..1800 s 对齐
xp = xmesh*100;
Tp_ = interp1(xp, Tp.', rq, 'pchip').';
Xp_ = interp1(xp, Xp.', rq, 'pchip').';
fprintf(fid,'【问题1】自编 FV 与 pdepe 对比（t = 100..1800 s，r = 0,.5,1,1.5,2 cm）\n');
fprintf(fid,'温度最大绝对偏差 = %.2e degC ;  含水率最大绝对偏差 = %.2e kg/kg\n', ...
        max(abs(Tfv_(:)-Tp_(:))), max(abs(Xfv_(:)-Xp_(:))));
fprintf(fid,'  温度表(FV):\n'); disp2(fid, Tfv_);
fprintf(fid,'  温度表(pdepe):\n'); disp2(fid, Tp_);
fprintf(fid,'  含水率表(FV):\n'); disp2(fid, Xfv_);
fprintf(fid,'  含水率表(pdepe):\n'); disp2(fid, Xp_);

%% ================= 问题 2（3 h）=================
tt2 = [0 (0.5:0.5:3)*3600];
sol2 = pdepe(m, @pde2, @ic1, @bc2, xmesh, tt2, ...
             odeset('RelTol',1e-8,'AbsTol',1e-10));
P2 = struct(); P2.N=320; P2.dt=1; P2.tEnd=10800;
P2.R0=R0; P2.T0=28; P2.X0=2.55; P2.h=25; P2.hm=8e-7;
P2.rho=@(X) 650+128*X; P2.cp=@(X) 1450+2736*X./(X+1);
P2.kc=@(X) 0.21+0.38*X./(X+1);
P2.Dco=@(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
P2.Tf=Tf; P2.Xf=Xf; P2.Rf=@(t) R0+0*t; P2.Rdf=@(t) 0*t;
P2.record=tt2; P2.picard=4;
S2 = herb_solver(P2);
Tf2_ = interp1(rn, S2.T.', rq, 'pchip').';
Xf2_ = interp1(rn, S2.X.', rq, 'pchip').';
Tf2_ = Tf2_(2:end,:); Xf2_ = Xf2_(2:end,:);   % 去掉 t=0 行
Tp2 = squeeze(sol2(:,:,1));  Xp2 = squeeze(sol2(:,:,2));
Tp2 = Tp2(2:end,:); Xp2 = Xp2(2:end,:);  % 去掉 t=0 行，与 FV 的 0.5..3 h 对齐
Tp2_ = interp1(xp, Tp2.', rq, 'pchip').';
Xp2_ = interp1(xp, Xp2.', rq, 'pchip').';
fprintf(fid,'\n【问题2】自编 FV 与 pdepe 对比（t = 0.5..3 h）\n');
fprintf(fid,'温度最大绝对偏差 = %.2e degC ;  含水率最大绝对偏差 = %.2e kg/kg\n', ...
        max(abs(Tf2_(:)-Tp2_(:))), max(abs(Xf2_(:)-Xp2_(:))));
fprintf(fid,'  温度表(FV):\n'); disp2(fid, Tf2_);
fprintf(fid,'  温度表(pdepe):\n'); disp2(fid, Tp2_);
fprintf(fid,'  含水率表(FV):\n'); disp2(fid, Xf2_);
fprintf(fid,'  含水率表(pdepe):\n'); disp2(fid, Xp2_);

%% ================= 问题 3 干燥时间 =================
% pdepe 用事件不可用，改为扫到 X_centre < 0.15
t3 = unique([0:600:210000, 206900:10:207100])';
sol3 = pdepe(m, @pde2, @ic1, @bc2, xmesh, t3, ...
             odeset('RelTol',1e-8,'AbsTol',1e-10));
Xc = squeeze(sol3(:,1,2));                 % 中心含水率历史
i1 = find(Xc < 0.15, 1, 'first');
if ~isempty(i1)
    t_dry_pdepe = interp1(Xc(i1-1:i1), t3(i1-1:i1), 0.15);
    fprintf(fid,'\n【问题3】pdepe 给出中心含水率降到 0.15 的时刻 = %.0f s = %.4f h\n', ...
            t_dry_pdepe, t_dry_pdepe/3600);
    P3 = struct(); P3.N=1280; P3.dt=2; P3.tEnd=10*86400;
    P3.R0=R0; P3.T0=28; P3.X0=2.55; P3.h=25; P3.hm=8e-7;
    P3.rho=@(X) 650+128*X; P3.cp=@(X) 1450+2736*X./(X+1);
    P3.kc=@(X) 0.21+0.38*X./(X+1);
    P3.Dco=@(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
    P3.Tf=Tf; P3.Xf=Xf; P3.Rf=@(t) R0+0*t; P3.Rdf=@(t) 0*t;
    P3.record=0:60:P3.tEnd; P3.picard=4; P3.Xdry=0.15;
    S3f = herb_solver(P3);          % 现场重算 FV 的烘干时长，不再硬编码
    fprintf(fid,'        自编 FV（N=1280,dt=2）= %.0f s = %.4f h ;  相对偏差 %.3e\n', ...
            S3f.dryTime, S3f.dryTime/3600, abs(t_dry_pdepe-S3f.dryTime)/S3f.dryTime);
else
    fprintf(fid,'\n【问题3】pdepe 在扫描时间范围内未降到 0.15（请扩大时间范围）\n');
end
fclose(fid);
disp('pdepe 交叉验证完成');


% ------------------------- 嵌套函数区 -------------------------
function [c,f,s] = pde1(x,t,u,DuDx)      % 问题1：常物性
c = [820*2600; 1];
D = 7e-9*exp(-0.89/max(u(2),1e-6));      % 防止迭代中 u(2) 变负
f = [0.36*DuDx(1); D*DuDx(2)];
s = [0; 0];
end
function u0 = ic1(x)                      % 初值
u0 = [28; 2.55];
end
function [pl,ql,pr,qr] = bc1(xl,ul,xr,ur,t)
A1 = evalin('base','A1'); Tset=50; Xset=0.05;
Tf_ = amb(A1,2,t,Tset); Xf_ = amb(A1,3,t,Xset);   % 第2列=温度，第3列=水分浓度
pl = [0;0];  ql = [1;1];
pr = [25*(ur(1)-Tf_); 8e-7*(ur(2)-Xf_)];  qr = [1;1];
end
function [c,f,s] = pde2(x,t,u,DuDx)      % 问题2/3：附录3 变物性
rho = 650 + 128*u(2);
cp  = 1450 + 2736*u(2)/(u(2)+1);
kk  = 0.21 + 0.38*u(2)/(u(2)+1);
D   = 2.4e-3*exp(-0.45/max(u(2),1e-6))*exp(-3850/(u(1)+273.15));
c = [rho*cp; 1];
f = [kk*DuDx(1); D*DuDx(2)];
s = [0; 0];
end
function [pl,ql,pr,qr] = bc2(xl,ul,xr,ur,t)
A1 = evalin('base','A1'); Tset=50; Xset=0.05;
Tf_ = amb(A1,2,t,Tset); Xf_ = amb(A1,3,t,Xset);   % 第2列=温度，第3列=水分浓度
pl = [0;0];  ql = [1;1];
pr = [25*(ur(1)-Tf_); 8e-7*(ur(2)-Xf_)];  qr = [1;1];
end
function v = amb(A1, col, t, vset)
tA = A1(:,1); ya = A1(:,col); t1 = tA(end);
v = interp1(tA, ya, min(t,t1), 'linear');
v(t>t1) = vset;
end
function disp2(fid, M)
for i = 1:size(M,1)
    fprintf(fid,'    %10.4f %10.4f %10.4f %10.4f %10.4f\n', M(i,:));
end
end
