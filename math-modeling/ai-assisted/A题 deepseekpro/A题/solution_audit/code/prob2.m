%% =========================================================================
%  问题 2：整个烘干过程（预热平衡 + 恒温干燥）前 3 小时的温度场与水分浓度场
%  ------------------------------------------------------------------------
%  与问题 1 的差别：
%    (1) 物性改用附录 3 的经验公式：rho(X), cp(X), k(X), D(X,T)；
%    (2) 环境条件分两段：0~14400 s 用附件 1 实测值，之后为恒温干燥段
%        T_f = 50 degC、X_f = 0.05 kg/kg；
%    (3) 时间推进 3 h = 10800 s，输出间隔 1 s。
% =========================================================================
clear; clc;
ROOT = rootdir();

%% ---- 1. 环境条件（预热平衡段 + 恒温干燥段）----
A1 = readmatrix(fullfile(ROOT,'data','附件1.xlsx'));   % 附件 1：[t, T_air, X_air]
Tset = 50;                                        % 恒温干燥段烘房温度 (degC)
Xset = 0.05;                                      % 恒温干燥段烘房水分浓度 (kg/kg)
[Tf, Xf] = ambient_profile(A1, Tset, Xset);       % 两段式环境函数句柄

%% ---- 2. 模型参数 ----
R0 = 0.02;                                        % 药材半径 (m)
h  = 25;                                          % 对流换热系数 W/(m^2*K)（沿用附录 2）
hm = 8e-7;                                        % 对流传质系数 m/s（沿用附录 2）

%% ---- 3. 附录 3 的经验公式（函数句柄）----
rho_f = @(X) 650 + 128*X;                         % 密度 kg/m^3
cp_f  = @(X) 1450 + 2736*X./(X+1);                % 比热容 J/(kg*K)
kc_f  = @(X) 0.21 + 0.38*X./(X+1);                % 导热系数 W/(m*K)
D_f   = @(X,TK) 2.4e-3*exp(-0.45./X).*exp(-3850./TK);  % 扩散系数 m^2/s（TK 为 K）

%% ---- 4. 组装求解器输入 ----
P = struct();
P.N      = 320;                                   % 网格份数（dr = 0.00625 cm，保证 4 位小数精度）
P.dt     = 1;                                     % 时间步长 1 s
P.tEnd   = 10800;                                 % 3 h
P.R0     = R0;  P.T0 = 28;  P.X0 = 2.55;          % 半径、初温、初含水率
P.h      = h;   P.hm = hm;                        % 传递系数
P.rho    = rho_f; P.cp = cp_f; P.kc = kc_f; P.Dco = D_f;   % 物性函数
P.Tf     = Tf;    P.Xf = Xf;                      % 环境函数
P.Rf     = @(t) R0 + 0*t;                         % 半径不变
P.Rdf    = @(t) 0*t;                              % dR/dt = 0
P.record = 0:1:10800;                             % 每 1 s 输出
P.picard = 4;                                     % Picard 迭代 4 次（物性随 X、T 变化较强）

%% ---- 5. 求解 ----
tic; S = herb_solver(P); fprintf('问题2 求解耗时 %.2f s\n', toc);

%% ---- 6. 论文表 3、表 4 ----
r_node = S.xi*R0*100;                             % 节点距离 (cm)
rq = [0 0.5 1 1.5 2];                             % 表格距离 (cm)
th = [0.5 1.0 1.5 2.0 2.5 3.0];                   % 表格时刻 (h)
tq = th*3600;                                     % 换算为 s
Tq = interp1(r_node, S.T.', rq, 'pchip').';       % 按距离插值
Xq = interp1(r_node, S.X.', rq, 'pchip').';
iT = tq + 1;                                      % S.t = 0:1:10800，故步号 = 时刻+1
Ttab = Tq(iT,:);  Xtab = Xq(iT,:);

fid = savelog('prob2_tables.txt');                % UTF-8 日志
fprintf(fid,'===== 表3  3 小时内药材的温度 (degC) =====\n');
fprintf(fid,'%8s %10.1f %10.1f %10.1f %10.1f %10.1f\n','时间/h',rq);
for i = 1:numel(th)
    fprintf(fid,'%8.1f %10.4f %10.4f %10.4f %10.4f %10.4f\n', th(i), Ttab(i,:));
end
fprintf(fid,'\n===== 表4  3 小时内药材的水分浓度 (kg/kg) =====\n');
fprintf(fid,'%8s %10.1f %10.1f %10.1f %10.1f %10.1f\n','时间/h',rq);
for i = 1:numel(th)
    fprintf(fid,'%8.1f %10.4f %10.4f %10.4f %10.4f %10.4f\n', th(i), Xtab(i,:));
end
fprintf(fid,'\n----- 附：恒温段开始的含水量剖面 -----\n');
fprintf(fid,'t=14400s: X(r=0)=%.4f, X(表面)=%.4f\n', ...
        interp1(r_node,S.X(min(14401,end),:),0,'pchip'), ...
        interp1(r_node,S.X(min(14401,end),:),2,'pchip'));
fclose(fid);
fprintf('表 3、表 4 已写入 out/prob2_tables.txt\n');

%% ---- 7. 写出 result2.xlsx（每 1 s、每 0.1 cm）----
jq    = 1:round(P.N*0.05):numel(r_node);          % 每隔 0.1 cm 取一个节点
Tout  = S.T(:,jq);
Xout  = S.X(:,jq);
rout  = r_node(jq);
write_result_xlsx(fullfile(ROOT,'out','result2.xlsx'), ...
                  {'温度','水分浓度'}, S.t, rout, {Tout, Xout});
fprintf('已写出 out/result2.xlsx（%d 行 x %d 列）\n', numel(S.t), numel(rout));

%% ---- 8. 保存 ----
save(fullfile(ROOT,'out','sol2.mat'),'S','r_node','-v7.3');
