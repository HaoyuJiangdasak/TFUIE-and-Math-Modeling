function S = herb_solver(P)
% =========================================================================
% herb_solver —— 圆柱形药材径向一维「导热 + 导湿」耦合干燥模型求解器
%               （支持药材半径随时间收缩，即问题 4 的移动边界情形）
%
% 【物理模型】取 Landau（前沿固定）坐标 xi = r/R(t) ∈ [0,1]
%   （xi=0 为药材中心，xi=1 为表面；R 恒定时 xi 就是 r/R0）
%   热量： rho*cp*dT/dt = (1/(R^2*xi))*d/dxi( k*xi*dT/dxi )
%   水分：        dX/dt = (1/(R^2*xi))*d/dxi( D*xi*dX/dxi )
%
%   【为什么没有对流项】X 是"干基含水率"= 水质量/绝干物料质量。在空间坐标 r 下，
%   干基守恒方程含固相牵连速度 v_s：
%        dX/dt + v_s*dX/dr = (1/(r))*d/dr( r*D*dX/dr )
%   对 xi = r/R(t) 做链式法则变换后，方程中出现的对流系数是"相对速度"
%        (v_s - xi*Rd)/R ,   Rd = dR/dt
%   在仿射（均匀）收缩假定下，任取质点满足 r(t) = R(t)/R0 * r(0)，即恒有
%        xi = r/R(t) = const  =>  v_s = dr/dt|_xi = xi*Rd
%   于是相对速度 (v_s - xi*Rd)/R ≡ 0，对流项恒等于零，方程与固定区域同形，
%   只是扩散系数前多一个 1/R(t)^2 因子、边界通量多一个 R(t) 因子。
%   物理含义：若 D = 0，只收缩不扩散时各质点的 X 保持不变（这是正确的物理行为；
%   若漏掉固相牵连速度而只保留网格速度 xi*Rd/R，则会得到"凭空浓缩/稀释"的错误结果）。
%   这一点已在 test_p4conv.m 的 (C) 组做了对照计算。
%
% 【定解条件】
%   xi=0（对称）：dT/dxi = 0 ,  dX/dxi = 0
%   xi=1（表面）：k*dT/dxi = R*h *(Tf - T)      （对流换热）
%                 D*dX/dxi = R*hm*(Xf - X)      （对流传质）
%   t=0        ：T = T0 ,  X = X0
%
% 【数值方法】
%   空间：节点式有限体积法（控制体按 2*pi*xi*dxi 加权），界面扩散系数取调和平均；
%   时间：扩散项后向欧拉（隐式，无条件稳定），
%         非线性物性 rho,cp,k,D 用 Picard 迭代逐次更新；
%   解法：三对角方程组用 Thomas 追赶法 O(n) 求解。
%
% 【输入 P】(struct)
%   P.N       网格份数（节点数 = N+1，xi_j = j/N）
%   P.tEnd    计算终止时间 (s)
%   P.dt      时间步长 (s)
%   P.R0      初始半径 (m)
%   P.T0      初始温度 (degC)
%   P.X0      初始干基含水率 (kg/kg)
%   P.h       对流换热系数 (W/(m^2*K))
%   P.hm      对流传质系数 (m/s)
%   P.rho     @(X)        密度 (kg/m^3)
%   P.cp      @(X)        比热容 (J/(kg*K))
%   P.kc      @(X)        导热系数 (W/(m*K))
%   P.Dco     @(X,TK)     水分扩散系数 (m^2/s)，TK 为热力学温度 (K)
%   P.Tf      @(t)        烘房温度 (degC)
%   P.Xf      @(t)        烘房水分浓度 (kg/kg)
%   P.Rf      @(t)        药材半径 (m)
%   P.Rdf     @(t)        dR/dt (m/s)
%   P.record  输出时刻向量 (s)，须为 dt 的整数倍（默认 0:dt:tEnd）
%   P.picard  Picard 迭代次数（默认 3）
%   P.Xdry    干燥判定阈值（默认 Inf，即不提前终止）
%
% 【输出 S】(struct)
%   S.t / S.T / S.X / S.R / S.xi / S.dryTime / S.nrec
% =========================================================================

%% ---------------- 0. 输入缺省值与基本量 ----------------
if ~isfield(P,'picard'), P.picard = 3;  end   % Picard 迭代次数缺省为 3
if ~isfield(P,'Xdry'),   P.Xdry   = Inf; end  % 不设干燥阈值
if ~isfield(P,'record'), P.record = 0:P.dt:P.tEnd; end

N   = P.N;                 % 网格份数
dxi = 1/N;                 % 归一化空间步长
n   = N+1;                 % 节点总数
dt  = P.dt;                % 时间步长
nt  = round(P.tEnd/dt);    % 总时间步数

%% ---------------- 1. 几何系数（只依赖 xi，循环外一次算好）----------------
xi   = (0:N)'*dxi;              % 节点坐标 xi_j = j*dxi，j=0..N
xmid = ((1:N)'-0.5)*dxi;        % 单元界面 xi_{j+1/2}，j=1..N（节点 j 与 j+1 之间）
xiN  = (N-0.5)*dxi;             % 表面单元左界面 xi_{N-1/2}
wSurf = 1 - xiN^2;              % 表面单元权重：2*∫_{xi_{N-1/2}}^{1} xi dxi

%% ---------------- 2. 时间相关的外部条件（循环外一次性求值，减少循环内开销）-----
tv  = (0:nt)'*dt;               % 各时间层时刻 (s)
Tfv = P.Tf(tv);                 % 烘房温度序列 (degC)
Xfv = P.Xf(tv);                 % 烘房水分浓度序列 (kg/kg)
Rv  = P.Rf(tv);                 % 半径序列 (m)
Rdv = P.Rdf(tv);                % dR/dt 序列 (m/s)

%% ---------------- 3. 输出时刻（步号）----------------
irec  = round(P.record(:)/dt) + 1;   % 输出时刻对应的步号（MATLAB 从 1 开始）
irec  = irec(irec>=1 & irec<=nt+1);  % 越界保护
nrec  = numel(irec);

%% ---------------- 4. 初值与历史存储 ----------------
T = P.T0*ones(n,1);             % 温度场初值 (degC)，全场 28 degC
X = P.X0*ones(n,1);             % 含水率初值 (kg/kg)，全场 2.55
Trec = zeros(nrec+1,n);         % 温度输出缓存（+1 预留给可能追加的干燥末时刻）
Xrec = zeros(nrec+1,n);         % 含水率输出缓存
Rrec = zeros(nrec+1,1);         % 半径输出缓存
trec = zeros(nrec+1,1);         % 每次记录对应的真实时刻 (s)
nstored = 0;                    % 已写入缓存的记录条数
krec    = 1;                    % 下一个待写入缓存的行号
if irec(1) == 1                 % 仅当输出时刻清单里确实含 t=0 时才先记录初值
    nstored = 1;                % 已存 1 条（t=0）
    trec(1)  = 0;               % 时刻 0
    Trec(1,:) = T.';            % 记录 t=0 的温度
    Xrec(1,:) = X.';            % 记录 t=0 的含水率
    Rrec(1)  = Rv(1);           % 记录 t=0 的半径
    krec = 2;                   % 下一个位置变成第 2 行
end
dryTime = Inf;                  % 达到干燥要求的时间（默认无穷大）

%% ---------------- 5. 时间推进主循环 ----------------
for m = 1:nt
    % ---- 5.1 本时间层的外部条件 ----
    Rn  = Rv(m+1);              % 本步末半径 (m)
    Rdn = Rdv(m+1);             % 本步末 dR/dt (m/s)
    Tf  = Tfv(m+1);             % 本步末烘房温度 (degC)
    Xf  = Xfv(m+1);             % 本步末烘房水分浓度 (kg/kg)

    To = T;                     % 保存上一步（t^n）温度，作为 RHS 的基准
    Xo = X;                     % 保存上一步（t^n）含水率

    % ---- 5.2 Picard 迭代：非线性物性线性化 ----
    for it = 1:P.picard
        % 由当前迭代值计算物性（第一次迭代时即为上一步的值，即"滞后系数"）
        rho = P.rho(X);         % 密度 (kg/m^3)
        cp  = P.cp(X);          % 比热容 (J/(kg*K))
        kc  = P.kc(X);          % 导热系数 (W/(m*K))
        Dc  = P.Dco(X, T+273.15); % 扩散系数 (m^2/s)，温度换算成 K

        rc  = rho.*cp;          % 体积热容 (J/(m^3*K))

        % 界面扩散系数：调和平均，保证界面通量守恒且适应系数的强非线性变化
        kmid = 2*kc(1:N).*kc(2:n)./(kc(1:N)+kc(2:n));   % 长度 N，对应 xi_{j+1/2}
        Dmid = 2*Dc(1:N).*Dc(2:n)./(Dc(1:N)+Dc(2:n));

        % ---- 5.3 对流（网格速度）项 ----
        % 【重要】含水率 X 的定义是"干基含水率"= 水质量/绝干物料质量。
        % 在仿射收缩（均匀收缩）假定下，任取质点恒有 xi = r/R(t) 不变，
        % 即固相速度 v_s = xi*Rd。做 Landau 坐标变换后，方程中出现的是
        % "相对速度 (v_s - xi*Rd)/R"，在仿射收缩下该相对速度恒等于 0，
        % 对流项自动消失。物理含义：只收缩而不扩散时，各质点的 X 保持不变。
        % 因此问题 4 的 ξ 坐标方程与固定区域方程形式完全相同，只是 R = R(t)。
        % 为便于对比，保留 P.advModel 开关：
        %   'affine'（默认）= 仿射收缩，无对流项（物理正确）
        %   'grid'         = 仅考虑网格运动、忽略固相牵连运动（错误模型，仅供对照）
        if isfield(P,'advModel') && strcmp(P.advModel,'grid')
            aadv = (Rdn/Rn)*xi;             % 错误的对照模型：只保留网格速度
        else
            aadv = zeros(n,1);              % 仿射收缩：相对速度为零
        end
        aadv(1) = 0;                        % xi=0 处对流项恒等于零
        wX = zeros(n,1);  wT = zeros(n,1);  % 迎风差商 dX/dxi、dT/dxi
        ip = find(aadv>0); ip = ip(ip<n);   % a>0：信息来自 xi 增大方向（前差）
        im = find(aadv<0); im = im(im>1);   % a<0：信息来自 xi 减小方向（后差）
        wX(ip) = (X(ip+1)-X(ip))/dxi;       % 前向差商
        wX(im) = (X(im)-X(im-1))/dxi;       % 后向差商
        wT(ip) = (T(ip+1)-T(ip))/dxi;
        wT(im) = (T(im)-T(im-1))/dxi;
        advX = aadv.*wX;                    % 含水率方程的对流项 (1/s * kg/kg)
        advT = aadv.*wT;                    % 温度方程的对流项 (1/s * degC)

        % ---- 5.4 组装含水率的三对角方程组 A*X^{n+1} = d ----
        aX = zeros(n,1); bX = zeros(n,1); cX = zeros(n,1); dX = zeros(n,1);

        % (1) 中心节点 j=1（xi=0）：对 xi 加权积分后用洛必达法则得 4*D*dX/(R^2*dxi^2)
        g0 = 4*dt*Dmid(1)/(Rn^2*dxi^2);
        bX(1) = 1 + g0;                     % 主对角
        cX(1) = -g0;                        % 上对角
        dX(1) = Xo(1);                      % 右端项（中心处对流项为 0）

        % (2) 内部节点 j=2..N
        jj  = (2:N)';                       % 内部节点编号
        al  = dt./(Rn^2*xi(jj)*dxi^2);      % 系数 alpha_j = dt/(R^2*xi_j*dxi^2)
        aX(jj) = -al.*xmid(jj-1).*Dmid(jj-1);                          % 下对角
        cX(jj) = -al.*xmid(jj)  .*Dmid(jj);                            % 上对角
        bX(jj) = 1 + al.*(xmid(jj).*Dmid(jj) + xmid(jj-1).*Dmid(jj-1));% 主对角
        dX(jj) = Xo(jj) + dt*advX(jj);                                 % 右端项

        % (3) 表面节点 j=N+1：控制体权重 wSurf，边界通量 R*hm*(Xf-X)
        beX = 2*dt/(Rn^2*wSurf);            % beta = 2*dt/(R^2*wSurf)
        aX(n) = -beX*xiN*Dmid(N)/dxi;       % 下对角（来自内部扩散通量）
        bX(n) = 1 + beX*(Rn*P.hm + xiN*Dmid(N)/dxi);  % 主对角
        cX(n) = 0;                          % 无上对角（边界）
        dX(n) = Xo(n) + dt*advX(n) + beX*Rn*P.hm*Xf;  % 右端项含对流传质源

        % ---- 5.5 组装温度的三对角方程组 ----
        aT = zeros(n,1); bT = zeros(n,1); cT = zeros(n,1); dT = zeros(n,1);

        % (1) 中心节点
        g0T = 4*dt*kmid(1)/(Rn^2*dxi^2*rc(1));
        bT(1) = 1 + g0T;
        cT(1) = -g0T;
        dT(1) = To(1);

        % (2) 内部节点（除以体积热容 rc_j）
        alT = dt./(Rn^2*xi(jj)*dxi^2.*rc(jj));
        aT(jj) = -alT.*xmid(jj-1).*kmid(jj-1);
        cT(jj) = -alT.*xmid(jj)  .*kmid(jj);
        bT(jj) = 1 + alT.*(xmid(jj).*kmid(jj) + xmid(jj-1).*kmid(jj-1));
        dT(jj) = To(jj) + dt*advT(jj);

        % (3) 表面节点
        beT = 2*dt/(Rn^2*wSurf*rc(n));
        aT(n) = -beT*xiN*kmid(N)/dxi;
        bT(n) = 1 + beT*(Rn*P.h + xiN*kmid(N)/dxi);
        cT(n) = 0;
        dT(n) = To(n) + dt*advT(n) + beT*Rn*P.h*Tf;

        % ---- 5.6 Thomas 追赶法求解两个三对角方程组 ----
        X = thomas(aX,bX,cX,dX);
        T = thomas(aT,bT,cT,dT);
        X = max(X,0);                       % 物理约束：含水率非负
    end

    % ---- 5.7 记录输出 ----
    if krec<=nrec && irec(krec)==m+1
        Trec(krec,:) = T.';                 % 写入温度
        Xrec(krec,:) = X.';                 % 写入含水率
        Rrec(krec)   = Rn;                  % 写入半径
        trec(krec)   = irec(krec)*dt - dt;  % 写入真实时刻：步号 m+1 对应时刻 m*dt
        nstored = krec;                     % 更新已存条数
        krec = krec+1;                      % 指向下一行
    end

    % ---- 5.8 干燥终止判定：全场含水率均低于阈值（仅当设定了有限阈值时生效）----
    if isfinite(P.Xdry) && max(X) < P.Xdry
        dryTime = m*dt;                     % 干燥达标时刻（第 m 步结束时对应的物理时刻）
        nstored = nstored + 1;              % 追加记录该时刻的场
        trec(nstored)  = dryTime;           % 时刻
        Trec(nstored,:) = T.';              % 温度（达标瞬间）
        Xrec(nstored,:) = X.';              % 含水率（达标瞬间）
        Rrec(nstored)   = Rn;               % 半径
        break;                              % 提前跳出，节省计算量
    end
end

%% ---------------- 6. 打包输出（只保留已实际记录的部份）----------------
S.t  = trec(1:nstored);             % 实际输出的时刻
S.T  = Trec(1:nstored,:);           % 温度场历史
S.X  = Xrec(1:nstored,:);           % 含水率场历史
S.R  = Rrec(1:nstored);             % 半径历史
S.xi = xi;                          % 归一化节点坐标
S.dryTime = dryTime;                % 干燥达标时刻 (s)
S.nrec = nstored;                   % 实际记录条数
end


% =========================================================================
function x = thomas(a,b,c,d)
%THOMAS  追赶法（TDMA）求解三对角线性方程组 M*x = d
%   a 下对角，b 主对角，c 上对角，d 右端项（均为长度 n 的列向量）
%   原地前向消元 + 回代，复杂度 O(n)
n = numel(d);                       % 方程个数
for k = 2:n                         % ---- 前向消元 ----
    w = a(k)/b(k-1);                % 消元因子
    b(k) = b(k) - w*c(k-1);         % 更新主对角
    d(k) = d(k) - w*d(k-1);         % 更新右端项
end
x = zeros(n,1);                     % ---- 回代 ----
x(n) = d(n)/b(n);                   % 最后一个未知量
for k = n-1:-1:1
    x(k) = (d(k) - c(k)*x(k+1))/b(k);
end
end
