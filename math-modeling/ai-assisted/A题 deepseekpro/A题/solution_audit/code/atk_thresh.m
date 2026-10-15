%% ATK 1/5/7: 阈值敏感性 + 谁是最后干燥的节点 + 合理性
clear; clc;
ROOT = rootdir();
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));
[Tf, Xf] = ambient_profile(A1, 50, 0.05);
[Rf, Rdf] = radius_profile(A2);

base3 = struct('N',1280,'dt',2,'tEnd',5*86400,'R0',0.02,'T0',28,'X0',2.55, ...
    'h',25,'hm',8e-7, ...
    'rho',@(X) 650+128*X,'cp',@(X) 1450+2736*X./(X+1),'kc',@(X) 0.21+0.38*X./(X+1), ...
    'Dco',@(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK), ...
    'Tf',Tf,'Xf',Xf,'Rf',@(t) 0.02+0*t,'Rdf',@(t) 0*t, ...
    'record',0:600:5*86400,'picard',4,'Xdry',Inf);

base4 = base3;
base4.tEnd = 5*86400;
base4.rho = @(X) 760+90*X; base4.cp = @(X) 1850+2150*X./(X+1);
base4.kc  = @(X) 0.12+0.20*X./(X+1);
base4.Dco = @(X,TK) 4.2e-4*exp(-0.30./X).*exp(-3850./TK);
base4.Rf = Rf; base4.Rdf = Rdf; base4.R0 = A2(1,2)/100;

thr = [0.14 0.145 0.15 0.155 0.16 0.17 0.20 0.25 0.30];
fid = savelog('atk_thresh.txt');
fprintf(fid,'==== ATK1 阈值敏感性（N=1280, dt=2, 历史记录每步 max X）====\n');

for which = [3 4]
    P = base3;  if which==4, P = base4; end
    P.record = 0:600:P.tEnd;
    t0=tic; S = atk_solver(P); el=toc(t0);
    mx = S.maxX; th = S.th; ax = S.argX; xi = S.xi;
    fprintf(fid,'\n---- 问题 %d （耗时 %.1f s，步数 %d，最终 max X = %.6f）----\n', which, el, S.nstep, mx(end));
    fprintf(fid,'%10s %14s %12s %12s %14s\n','阈值','首次达标时刻(s)','(h)','(d)','argmax节点/位置(cm)');
    for k = 1:numel(thr)
        idx = find(mx < thr(k), 1, 'first');
        if isempty(idx)
            fprintf(fid,'%10.3f %14s %12s %12s\n', thr(k), '未达到', '-','-');
        else
            j = ax(idx);
            fprintf(fid,'%10.3f %14.0f %12.4f %12.4f   j=%d  xi=%.4f  r=%.4f cm\n', ...
                thr(k), th(idx), th(idx)/3600, th(idx)/86400, j, xi(j), xi(j)*P.R0*100);
        end
    end
    % max X 是否单调下降？在最关键时刻附近检查剖面单调性
    if which==3, tt = 0.15; else, tt = 0.15; end
    idx = find(mx < tt, 1,'first');
    fprintf(fid,'  达标瞬间剖面（max X < %.3f）：\n', tt);
    fprintf(fid,'    节点 1..n 的 X：前 8 个 = %s\n', mat2str(mx(idx),6));
    % 用 atk_solver 内部的 Xend 不可用（未存），改为重新计算剖面：取 argX 序列
    fprintf(fid,'  argmax 在整个过程中是否恒为 1（中心）？%d\n', all(ax==1));
    fprintf(fid,'  argmax 出现过的节点集合 = %s\n', mat2str(unique(ax)'));
    fprintf(fid,'  max X 随时间单调不增？%d（单调下降的最大增幅 = %.3e）\n', ...
        all(diff(mx)<=1e-12), max(diff(mx)));
end

%% 与 herb_solver 交叉校验：Xdry=0.15 时的 dryTime
fprintf(fid,'\n==== 交叉校验：herb_solver(Xdry=0.15) vs 历史法 ====\n');
for which = [3 4]
    P = base3; if which==4, P=base4; end
    P.record = 0:60:P.tEnd;  P.Xdry = 0.15;
    S = herb_solver(P);
    fprintf(fid,'  问题%d: herb_solver dryTime = %d s = %.4f h ; 历史法 = %.0f s = %.4f h ; S.t(end)=%.0f\n', ...
        which, S.dryTime, S.dryTime/3600, ...
        th(find(mx<0.15,1,'first')), th(find(mx<0.15,1,'first'))/3600, S.t(end));
end
fclose(fid);
disp('atk_thresh 完成');
