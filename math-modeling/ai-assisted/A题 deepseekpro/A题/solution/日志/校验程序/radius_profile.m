function [Rf, Rdf] = radius_profile(A2)
%RADIUS_PROFILE  由附件 2 的半径实测数据构造 R(t) 与 dR/dt 的函数句柄
%
% 输入：
%   A2 —— 附件 2 数据矩阵 [t(s), R(cm)]，t ∈ [0,259200]
% 输出：
%   Rf  —— @(t) 半径 (m)
%   Rdf —— @(t) dR/dt (m/s)
%
% 说明：
%   1) 采用 PCHIP（保形分段三次 Hermite 插值）而非普通三次样条，
%      因为 PCHIP 是单调保持的，不会在数据拐点附近产生虚假振荡；
%   2) dR/dt 由 PCHIP 多项式系数解析求导得到，同样不会产生振荡；
%   3) t 超过数据末端（259200 s）时钳位到末端值，此时 dR/dt ≈ 0。

tA = A2(:,1);                     % 时间列 (s)
RA = A2(:,2)/100;                 % 半径列，cm 换算为 m
tEnd = tA(end);                   % 数据末时刻 (s)

pp  = pchip(tA, RA);              % 保形三次插值多项式（结构体）
ppd = pp_deriv(pp);               % 解析求导得到的导数多项式

Rf  = @(t) ppval(pp , min(t,tEnd));   % 半径函数（超界钳位）
Rdf = @(t) ppval(ppd, min(t,tEnd));   % 导数函数（超界钳位，末端近似为 0）
end


function dpp = pp_deriv(pp)
%PP_DERIV  对 ppval 使用的分段多项式结构体求一阶导数（不依赖 Curve Fitting Toolbox）
%   pp.coefs 的每一行是 [c_p, c_{p-1}, ..., c_0]，对应 p 次多项式。
%   求导后系数变为 [p*c_p, (p-1)*c_{p-1}, ..., 1*c_1]，阶数减 1。
p = pp.order;                                        % 原多项式的阶数（系数个数）
mult = (p-1):-1:1;                                   % 求导系数 [p-1, p-2, ..., 1]
dpp = pp;                                            % 复制结构体
dpp.order  = p - 1;                                  % 阶数减 1
dpp.coefs  = pp.coefs(:,1:p-1) .* repmat(mult, pp.pieces, 1);  % 系数逐项乘幂次
end
