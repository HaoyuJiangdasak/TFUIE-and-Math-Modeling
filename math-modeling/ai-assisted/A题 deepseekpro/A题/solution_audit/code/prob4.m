%% =========================================================================
%  问题 4：考虑药材失水收缩（半径由附件 2 给定）的烘干过程与烘干时长
%  ------------------------------------------------------------------------
%  1) 半径 R(t) 直接取附件 2 的实测数据（保形三次插值），是"已知输入"而非待求量；
%  2) 物性用附录 4 的经验公式；
%  3) 采用 Landau（前沿固定）变换 xi = r/R(t)，把动边界 [0,R(t)] 映射为固定区间 [0,1]；
%     在仿射（均匀）收缩假定下固相牵连速度 v_s = xi*dR/dt，
%     与网格速度 xi*dR/dt 相消，故 xi 坐标下的控制方程不含对流项：
%         rho*cp*dT/dt = (1/(R^2*xi))*d/dxi( k*xi*dT/dxi )
%                dX/dt = (1/(R^2*xi))*d/dxi( D*xi*dX/dxi )
%  4) 输出的"到药材中心距离"按【物质坐标】给出：即该质点在 t=0 时刻到中心的距离
%     xi*R0，最后一列"药材表面"恒为 xi = R0 的表面质点。
%     与当前几何位置的换算关系： r(t) = xi * R(t)。
% =========================================================================
clear; clc;
ROOT = rootdir();

%% ---- 1. 环境条件（预热平衡段 + 恒温干燥段）----
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));   % 附件 1
[Tf, Xf] = ambient_profile(A1, 50, 0.05);              % 两段式环境函数

%% ---- 2. 附件 2 的半径数据 → R(t) 与 dR/dt ----
A2 = readmatrix(fullfile(ROOT,'data','附件2.xlsx'));   % [t(s), R(cm)]
[Rf, Rdf] = radius_profile(A2);                        % PCHIP 保形插值及其解析导数

%% ---- 3. 模型参数（h、hm 沿用附录 2；半径初值取附件 2 第一行）----
R0 = A2(1,2)/100;                                      % 初始半径 2 cm -> 0.02 m
h  = 25;  hm = 8e-7;                                   % 传递系数

%% ---- 4. 求解 ----
P = struct();
P.N  = 1280;  P.dt = 2;  P.tEnd = 15*86400;            % 网格与步长（已做收敛性检验）
P.R0 = R0;  P.T0 = 28;  P.X0 = 2.55;                   % 初值
P.h  = h;   P.hm = hm;
P.rho = @(X) 760 + 90*X;                               % 附录4 密度
P.cp  = @(X) 1850 + 2150*X./(X+1);                     % 附录4 比热容
P.kc  = @(X) 0.12 + 0.20*X./(X+1);                     % 附录4 导热系数
P.Dco = @(X,TK) 4.2e-4*exp(-0.30./X).*exp(-3850./TK);  % 附录4 扩散系数
P.Tf = Tf;  P.Xf = Xf;                                 % 环境函数
P.Rf = Rf;  P.Rdf = Rdf;                               % 收缩半径及其导数
P.record = 0:60:P.tEnd;                                % 每 60 s 记录
P.picard = 4;                                          % Picard 迭代
P.Xdry   = 0.15;                                       % 干燥判据

tic; S = herb_solver(P); fprintf('问题4 求解耗时 %.2f s\n', toc);
td = S.dryTime;
fprintf('烘干结束时间 = %.0f s = %.3f h = %.3f d\n', td, td/3600, td/86400);

%% ---- 5. 论文表 6 ----
% 物质坐标：质点初始到中心距离 r0 = xi*R0（cm）
r0_node = S.xi*R0*100;                                 % 物质坐标节点 (cm)
rq = [0 0.5 1 1.5];                                    % 固定距离列 (cm)
th6 = 0:6:floor(td/3600/6)*6;                          % 6,12,18,... 直至不超过 td
tq6 = th6*3600;
Xq  = interp1(r0_node, S.X.', rq, 'pchip').';          % 全时段插值到 4 个固定距离
X6  = interp1(S.t, Xq, tq6, 'linear');                 % 再插到各时刻
Xsurf = interp1(S.t, S.X(:,end), tq6, 'linear');       % 表面质点（xi=1）随时间的值
Xend_fix  = interp1(r0_node, S.X(end,:), rq, 'pchip'); % 结束时刻的固定距离值
Xend_surf = S.X(end,end);                              % 结束时刻的表面值（物质坐标 r0 = 2 cm）
Hcur = interp1(A2(:,1), A2(:,2), td, 'pchip');         % 结束时刻的实际半径 (cm)

fid = savelog('prob4_tables.txt');
fprintf(fid,'===== 表6  药材烘干过程的水分浓度 (kg/kg)，列名为物质坐标 (cm) =====\n');
fprintf(fid,'%12s %10.1f %10.1f %10.1f %10.1f %14s %14s\n','时间/h',rq,'药材表面(2cm)','当时实际半径/cm');
for i = 1:numel(th6)
    Rt = interp1(A2(:,1), A2(:,2), tq6(i), 'pchip');   % 该时刻的实际半径 (cm)
    fprintf(fid,'%12.1f %10.4f %10.4f %10.4f %10.4f %14.4f %14.4f\n', ...
            th6(i), X6(i,:), Xsurf(i), Rt);
end
fprintf(fid,'%12s %10.4f %10.4f %10.4f %10.4f %14.4f %14.4f\n', ...
        '烘干结束时间', Xend_fix, Xend_surf, Hcur);
fprintf(fid,'\n烘干时长：%.3f h = %.4f d（判据 max X < 0.15 kg/kg，实际最大值 %.6f）\n', ...
        td/3600, td/86400, max(S.X(end,:)));
fprintf(fid,'结束时半径 R = %.4f cm（初始 2.0000 cm，收缩比 %.4f）\n', Hcur, Hcur/2);
fprintf(fid,'\n----- 末态含水率剖面（物质坐标 r0 / 当前几何位置 r=xi*R ）-----\n');
fprintf(fid,'%12s %12s %12s %12s\n','r0/cm','r当前/cm','X(kg/kg)','T(degC)');
for rr = [0 0.1 0.25 0.5 0.75 1 1.25 1.5 1.75 1.9 1.95 1.99 2.0]
    xx = interp1(r0_node,S.X(end,:),min(rr,2),'pchip');
    tt = interp1(r0_node,S.T(end,:),min(rr,2),'pchip');
    fprintf(fid,'%12.2f %12.4f %12.6f %12.4f\n', rr, rr*Hcur/2, xx, tt);
end
fclose(fid);
fprintf('表 6 已写入 out/prob4_tables.txt\n');

%% ---- 6. 写出 result4.xlsx ----
jq   = 1:round(P.N*0.05):numel(r0_node);               % 每 0.1 cm 取一个物质坐标节点
Xout = S.X(:,jq);
rout = r0_node(jq);                                    % 0:0.1:2.0 cm
write_result_xlsx(fullfile(ROOT,'out','result4.xlsx'), 'Sheet1', S.t, rout, {Xout}, '药材表面');
fprintf('已写出 out/result4.xlsx（%d 行 x %d 列）\n', numel(S.t), numel(rout));

%% ---- 7. 保存 ----
save(fullfile(ROOT,'out','sol4.mat'),'S','r0_node','td','A2','-v7.3');
