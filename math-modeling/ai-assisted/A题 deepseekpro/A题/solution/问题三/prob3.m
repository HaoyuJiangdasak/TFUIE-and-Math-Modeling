%% =========================================================================
%  问题 3：确定药材烘干所需时间（要求药材各处含水率均 < 0.15 kg/kg）
%  ------------------------------------------------------------------------
%  模型与问题 2 完全相同，只是把计算时间延长到"处处达标"为止。
%  由于中心点最后达标，程序以 max_j X_j < 0.15 作为终止判据。
% =========================================================================
clear; clc;
ROOT = fileparts(mfilename('fullpath'));

%% ---- 1. 环境与参数（同问题 2）----
A1 = readmatrix(fullfile(ROOT,'附件1.xlsx'));   % 附件 1
[Tf, Xf] = ambient_profile(A1, 50, 0.05);              % 两段式环境
R0 = 0.02;  h = 25;  hm = 8e-7;                        % 半径与传递系数

%% ---- 2. 附录 3 物性 ----
P = struct();
P.N = 1280; P.dt = 2;  P.tEnd = 10*86400;              % 上限取 10 天（程序会提前终止）；N=1280 已收敛
P.R0 = R0;  P.T0 = 28;  P.X0 = 2.55;
P.h  = h;   P.hm = hm;
P.rho = @(X) 650 + 128*X;                              % 密度
P.cp  = @(X) 1450 + 2736*X./(X+1);                     % 比热容
P.kc  = @(X) 0.21 + 0.38*X./(X+1);                     % 导热系数
P.Dco = @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);  % 扩散系数
P.Tf = Tf;  P.Xf = Xf;                                 % 环境函数
P.Rf = @(t) R0 + 0*t;   P.Rdf = @(t) 0*t;              % 无收缩
P.record = 0:60:P.tEnd;                                % 每 60 s 记录一次
P.picard = 4;                                          % Picard 迭代
P.Xdry   = 0.15;                                       % 干燥判据阈值

%% ---- 3. 求解 ----
tic; S = herb_solver(P); fprintf('问题3 求解耗时 %.2f s\n', toc);
td = S.dryTime;                                        % 烘干结束时间 (s)
fprintf('烘干结束时间 = %.0f s = %.3f h = %.3f d\n', td, td/3600, td/86400);

%% ---- 4. 论文表 5：每隔 6 h，距离 0,0.5,1,1.5,2 cm，最后一行给出烘干结束时间 ----
r_node = S.xi*R0*100;                                  % 节点距离 (cm)
rq = [0 0.5 1 1.5 2];                                  % 表格距离
th6 = 0:6:floor(td/3600/6)*6;                          % 6,12,18,... 直至不超过 td
tq6 = th6*3600;                                        % 换算为秒
Xq  = interp1(r_node, S.X.', rq, 'pchip').';           % 全时段插值到 5 个距离
X6  = interp1(S.t, Xq, tq6, 'linear');                 % 再插值到各时刻（60 s 网格）
Xend = interp1(r_node, S.X(end,:), rq, 'pchip');       % 烘干结束时刻的剖面

fid = savelog('prob3_tables.txt');
fprintf(fid,'===== 表5  药材烘干过程的水分浓度 (kg/kg) =====\n');
fprintf(fid,'%12s %10.1f %10.1f %10.1f %10.1f %10.1f\n','时间/h',rq);
for i = 1:numel(th6)
    fprintf(fid,'%12.1f %10.4f %10.4f %10.4f %10.4f %10.4f\n', th6(i), X6(i,:));
end
fprintf(fid,'%12s %10.4f %10.4f %10.4f %10.4f %10.4f\n','烘干结束时间', Xend);
fprintf(fid,'\n烘干时长：%.3f h = %.4f d（判据 max X < 0.15 kg/kg，实际最大值 %.8f）\n', ...
        td/3600, td/86400, max(S.X(end,:)));
fprintf(fid,'\n----- 末态温度剖面（degC）-----\n');
fprintf(fid,'%10s %10.4f %10.4f %10.4f %10.4f %10.4f\n','r/cm',rq);
fprintf(fid,'%10s %10.4f %10.4f %10.4f %10.4f %10.4f\n','T末',interp1(r_node,S.T(end,:),rq,'pchip'));
fclose(fid);
fprintf('表 5 已写入 prob3_tables.txt（见“日志”文件夹）\n');

%% ---- 5. 写出 result3.xlsx（每 60 s、每 0.1 cm）----
jq   = 1:round(P.N*0.05):numel(r_node);                % 每 0.1 cm 取一个节点
keep = mod(S.t,60)==0;                                 % 只保留 60 s 整数倍时刻，严格符合“每隔 60 s”
Xout = S.X(keep,jq);                                   % 每 60 s 一行
rout = r_node(jq);                                     % 0:0.1:2 cm
write_result_xlsx(fullfile(ROOT,'result3.xlsx'), 'Sheet1', S.t(keep), rout, {Xout});
%% ---- 6. 保存 ----
