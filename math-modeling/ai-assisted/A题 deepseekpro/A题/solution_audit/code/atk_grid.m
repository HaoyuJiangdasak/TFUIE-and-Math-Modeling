%% ATK 2: 空间/时间分辨率对烘干时长的影响（含 dt 无关的"精确穿越时刻"估计）
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
[Rf, Rdf] = radius_profile(A2);

fid = savelog('atk_grid.txt');
fprintf(fid,'==== ATK2 分辨率敏感性（Xdry=0.15，逐步记录 max X）====\n');
fprintf(fid,'  精确穿越时刻 = 对 max X(t) 在 0.15 附近做线性内插（与 dt 无关的估计）\n\n');
fprintf(fid,'%6s %6s %10s %14s %14s %14s %14s\n','问题','N','dt','dryTime(s)','精确穿越(s)','精确(h)','耗时(s)');

for which = [3 4]
    for N = [320 640 1280 2560]
        for dt = [2 20]
            P = struct('N',N,'dt',dt,'tEnd',8*86400,'R0',0.02,'T0',28,'X0',2.55,'h',25,'hm',8e-7, ...
                'record',[],'picard',4,'Xdry',0.15,'stopOnDry',true);
            if which==3
                P.rho=@(X) 650+128*X; P.cp=@(X) 1450+2736*X./(X+1); P.kc=@(X) 0.21+0.38*X./(X+1);
                P.Dco=@(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);
                P.Rf=@(t) 0.02+0*t; P.Rdf=@(t) 0*t;
            else
                P.rho=@(X) 760+90*X; P.cp=@(X) 1850+2150*X./(X+1); P.kc=@(X) 0.12+0.20*X./(X+1);
                P.Dco=@(X,TK) 4.2e-4*exp(-0.30./X).*exp(-3850./TK);
                P.R0=A2(1,2)/100; P.Rf=Rf; P.Rdf=Rdf;
            end
            P.Tf=Tf; P.Xf=Xf;
            t0=tic; S=atk_solver(P); el=toc(t0);
            mx=S.maxX; th=S.th;
            i2 = find(mx<0.15,1,'first');
            if isempty(i2)
                tc = NaN;
            else
                a = mx(i2-1); b = mx(i2); ta = th(i2-1); tb = th(i2);
                tc = ta + (0.15-a)/(b-a)*(tb-ta);
            end
            fprintf(fid,'%6d %6d %10g %14.0f %14.1f %14.4f %14.1f\n', ...
                which, N, dt, S.dryTime, tc, tc/3600, el);
        end
    end
end
fclose(fid);
disp('atk_grid 完成');
