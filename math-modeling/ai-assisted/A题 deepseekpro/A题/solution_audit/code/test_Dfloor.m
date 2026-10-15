%% =========================================================================
%  扩散系数经验公式外推敏感性检验
%  D = a*exp(-b/X) 在 X 很小时按指数衰减，可能被外推到拟合区间之外。
%  考察给 D 加一个下限 Dmin 对烘干时长的影响，以判断"干壳"效应是否为控制因素。
% =========================================================================
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));
R0 = 0.02;
fid = savelog('Dfloor.txt');

for Xset = [0.05 0.02]
    [Tf, Xf] = ambient_profile(A1, 50, Xset);
    fprintf(fid,'\n===== 恒温段空气水分浓度 X_f = %.2f =====\n', Xset);
    fprintf(fid,'%14s %14s %14s %14s\n','Dmin(m^2/s)','问题3时长(h)','问题4时长(h)','问题3 末态X表面');
    for Dmin = [0 1e-13 1e-12 1e-11 3e-11]
        P3 = mk3(640,10,R0,Tf,Xf,Dmin);  S3 = herb_solver(P3);
        [Rf,Rdf] = radius_profile(A2);
        P4 = mk4(640,10,R0,Tf,Xf,Dmin,Rf,Rdf); S4 = herb_solver(P4);
        fprintf(fid,'%14.1e %14.4f %14.4f %14.6f\n', Dmin, ...
            S3.dryTime/3600, S4.dryTime/3600, S3.X(end,end));
    end
end
fclose(fid);
disp('完成');

function P = mk3(N,dt,R0,Tf,Xf,Dmin)
P = struct(); P.N=N; P.dt=dt; P.tEnd=60*86400; P.R0=R0; P.T0=28; P.X0=2.55;
P.h=25; P.hm=8e-7;
P.rho=@(X) 650+128*X; P.cp=@(X) 1450+2736*X./(X+1); P.kc=@(X) 0.21+0.38*X./(X+1);
P.Dco=@(X,TK) max(2.4e-3*exp(-0.45./X).*exp(-3850./TK), Dmin);
P.Tf=Tf; P.Xf=Xf; P.Rf=@(t) R0+0*t; P.Rdf=@(t) 0*t;
P.record=0:3600:P.tEnd; P.picard=4; P.Xdry=0.15;
end
function P = mk4(N,dt,R0,Tf,Xf,Dmin,Rf,Rdf)
P = struct(); P.N=N; P.dt=dt; P.tEnd=60*86400; P.R0=R0; P.T0=28; P.X0=2.55;
P.h=25; P.hm=8e-7;
P.rho=@(X) 760+90*X; P.cp=@(X) 1850+2150*X./(X+1); P.kc=@(X) 0.12+0.20*X./(X+1);
P.Dco=@(X,TK) max(4.2e-4*exp(-0.30./X).*exp(-3850./TK), Dmin);
P.Tf=Tf; P.Xf=Xf; P.Rf=Rf; P.Rdf=Rdf;
P.record=0:3600:P.tEnd; P.picard=4; P.Xdry=0.15;
end
