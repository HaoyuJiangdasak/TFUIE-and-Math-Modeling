function [Tf, Xf, t1] = ambient_profile(A1, Tset, Xset)
%AMBIENT_PROFILE  由附件 1 构造"预热平衡 + 恒温干燥"两段式烘房环境函数
%
% 输入：
%   A1   —— 附件 1 数据矩阵 [t(s), T(degC), X(kg/kg)]，t ∈ [0,14400]
%   Tset —— 恒温干燥阶段的烘房温度 (degC)，取 50
%   Xset —— 恒温干燥阶段的烘房水分浓度 (kg/kg)，取 0.05
% 输出：
%   Tf, Xf —— 函数句柄 @(t)，t 可为标量或列向量
%   t1     —— 预热平衡阶段结束时刻 (s)，即附件 1 的末时刻 14400
%
% 说明：0<=t<=t1 用附件 1 的实测数据线性插值；t>t1 取恒温恒定值。
%       附件 1 在 9000 s 之后温度稳定在约 50.1 degC、水分浓度稳定在约 0.05 kg/kg，
%       故恒温段取整定值 T=50 degC、X=0.05 kg/kg。

tA = A1(:,1);              % 附件 1 的时间列 (s)
TA = A1(:,2);              % 附件 1 的烘房温度列 (degC)
XA = A1(:,3);              % 附件 1 的烘房水分浓度列 (kg/kg)
t1 = tA(end);              % 预热平衡阶段末时刻 = 14400 s

Tf = @(t) stage_eval(t, tA, TA, Tset, t1);   % 构造温度函数句柄
Xf = @(t) stage_eval(t, tA, XA, Xset, t1);   % 构造水分浓度函数句柄
end


function v = stage_eval(t, tt, yy, yset, t1)
%STAGE_EVAL  分段求值：t<=t1 线性插值；t>t1 取恒定值 yset
tq = min(t, t1);                      % 对 t>t1 的时刻钳位到数据末端，避免线性外插
v  = interp1(tt, yy, tq, 'linear');   % 线性插值（tt 等间隔 60 s）
v(t > t1) = yset;                     % 恒温干燥阶段：赋恒定值
end
