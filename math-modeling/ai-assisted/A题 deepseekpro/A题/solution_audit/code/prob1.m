%% =========================================================================
%  问题 1：预热平衡阶段（0 ~ 1800 s）药材温度场与水分浓度场
%  ------------------------------------------------------------------------
%  模型：一维径向导热（常物性）+ 一维径向导湿（变扩散系数）
%        rho*cp*dT/dt = (1/r)*d/dr( k*r*dT/dr )
%               dX/dt = (1/r)*d/dr( D*r*dX/dr )
%        边界：表面 r=R0 分别为第三类边界（对流换热、对流传质）；
%              中心 r=0 为对称边界。
%  参数：附录 2 全部参数 + 附件 1 的烘房温湿条件。
% =========================================================================
clear; clc;                                       % 清空工作区与命令行
ROOT = rootdir();                                 % solution 根目录

%% ---- 1. 读入附件 1，构造烘房环境函数（预热平衡段） ----
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));   % 241x3: [t(s), T(degC), X(kg/kg)]
[Tf, Xf] = ambient_profile(A1, 50, 0.05);              % 环境函数句柄（问题1 只用到 t<=1800）

%% ---- 2. 附录 2 给定的物性与传递参数 ----
R0 = 0.02;                                        % 药材初始半径 (m)  = 2 cm
h  = 25;                                          % 对流换热系数 (W/(m^2*K))
hm = 8e-7;                                        % 对流传质系数 (m/s)

%% ---- 3. 组装求解器输入结构体 ----
P = struct();                                     % 新建结构体
P.N      = 320;                                   % 320 个控制体（节点 321 个，网格足够细，4 位小数已收敛）
P.dt     = 1;                                     % 时间步长 1 s（满足显式稳定性且对应输出步长）
P.tEnd   = 1800;                                  % 计算到 1800 s
P.R0     = R0;                                    % 初始半径 (m)
P.T0     = 28;                                    % 初始温度 (degC)
P.X0     = 2.55;                                  % 初始干基含水率 (kg/kg)
P.h      = h;                                     % 换热系数
P.hm     = hm;                                    % 传质系数
P.rho    = @(X) 820 + 0*X;                        % 密度 820 kg/m^3（常物性，0*X 用于匹配数组尺寸）
P.cp     = @(X) 2600 + 0*X;                       % 比热容 2600 J/(kg*K)
P.kc     = @(X) 0.36 + 0*X;                       % 导热系数 0.36 W/(m*K)
P.Dco    = @(X,TK) 7e-9*exp(-0.89./X);            % 附录2：D = 7e-9*exp(-0.89/X)，只依赖含水率
P.Tf     = Tf;                                    % 烘房温度函数
P.Xf     = Xf;                                    % 烘房水分浓度函数
P.Rf     = @(t) R0 + 0*t;                         % 半径恒定：R(t) = R0
P.Rdf    = @(t) 0*t;                              % dR/dt = 0（无收缩）
P.record = 0:1:1800;                              % 输出时刻：每 1 s
P.picard = 3;                                     % Picard 迭代 3 次

%% ---- 4. 调用求解器 ----
tic;                                              % 计时开始
S = herb_solver(P);                               % 求解
fprintf('问题1 求解耗时 %.2f s，记录 %d 个时刻\n', toc, S.nrec);

%% ---- 5. 论文表 1、表 2：指定时刻、指定距离的结果 ----
r_node = S.xi*R0*100;                             % 节点到中心的距离 (cm)
rq = [0 0.5 1 1.5 2];                             % 表格要求的 5 个距离 (cm)
tq = [100 300 600 900 1200 1500 1800];            % 表格要求的 7 个时刻 (s)

Tq = interp1(r_node, S.T.', rq, 'pchip').';       % 按距离插值，得到 nrec x 5
Xq = interp1(r_node, S.X.', rq, 'pchip').';       % 同上（含水率）
iT = tq + 1;                                      % 因 S.t 恰为 0:1:1800，步号 = 时刻+1
Ttab = Tq(iT,:);                                  % 提取 7x5 温度表
Xtab = Xq(iT,:);                                  % 提取 7x5 含水率表

fid = savelog('prob1_tables.txt');                % 打开 UTF-8 日志
fprintf(fid,'===== 表1  30 分钟内药材的温度 (degC) =====\n');
fprintf(fid,'%8s %10.1f %10.1f %10.1f %10.1f %10.1f\n','时间/s',rq);
for i = 1:numel(tq)
    fprintf(fid,'%8d %10.4f %10.4f %10.4f %10.4f %10.4f\n', tq(i), Ttab(i,:));
end
fprintf(fid,'\n===== 表2  30 分钟内药材的水分浓度 (kg/kg) =====\n');
fprintf(fid,'%8s %10.1f %10.1f %10.1f %10.1f %10.1f\n','时间/s',rq);
for i = 1:numel(tq)
    fprintf(fid,'%8d %10.4f %10.4f %10.4f %10.4f %10.4f\n', tq(i), Xtab(i,:));
end
fprintf(fid,'\n----- 表面与中心含水率随时间 -----\n');
fprintf(fid,'%8s %12s %12s %12s\n','t/s','X(r=0)','X(r=1cm)','X(r=2cm)');
for i = 1:numel(tq)
    fprintf(fid,'%8d %12.4f %12.4f %12.4f\n', tq(i), Xtab(i,1), Xtab(i,3), Xtab(i,5));
end
fclose(fid);                                      % 关闭日志
fprintf('表 1、表 2 已写入 out/prob1_tables.txt\n');

%% ---- 6. 写出 result1.xlsx（每 1 s、每 0.1 cm） ----
jq  = 1:round(P.N*0.05):numel(r_node);            % 每隔 0.1 cm 取一个节点（xi 步长 1/N，0.05*N 个节点 = 0.1 cm）
Tout = S.T(:,jq);                                 % 抽取温度场
Xout = S.X(:,jq);                                 % 抽取含水率场
tout = S.t;                                       % 时间列 (s)
rout = r_node(jq);                                % 距离行 (cm) = 0:0.1:2
write_result_xlsx(fullfile(ROOT,'out','result1.xlsx'), ...
                  {'温度','水分浓度'}, tout, rout, {Tout, Xout});
fprintf('\n已写出 %s\n', fullfile(ROOT,'out','result1.xlsx'));

%% ---- 7. 保存结果供绘图/校验 ----
save(fullfile(ROOT,'out','sol1.mat'),'S','r_node','-v7.3');
