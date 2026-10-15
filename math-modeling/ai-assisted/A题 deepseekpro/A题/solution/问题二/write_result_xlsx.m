function write_result_xlsx(fname, sheetNames, timeVec, distVec, valCells, hdrLast)
%WRITE_RESULT_XLSX  按附件 3 的模板格式写出结果 Excel 文件
%
% 输入：
%   fname      —— 输出文件名（含路径）
%   sheetNames —— 工作表名，字符向量或 cellstr（每个表对应 valCells 中的一页）
%   timeVec    —— 时间列 (s)，长度 nt
%   distVec    —— 距离行 (cm)，长度 nr
%   valCells   —— cell 数组，valCells{k} 为第 k 个工作表的 nt x nr 数据矩阵
%   hdrLast    —— (可选) 最后一个列标题的替代文字，如 '药材表面'
%
% 输出文件的版式与附件 3 模板一致：
%   A1 = '时间\到药材中心的距离'，第 1 行其余为各距离，A 列其余为各时刻。
%   所有数值按题目要求保留 4 位小数。

if nargin < 6, hdrLast = ''; end
if ischar(sheetNames), sheetNames = {sheetNames}; end

% ---- 先删除同名旧文件，避免 writecell 只覆盖写入区域、留下上一次运行的残行 ----
if exist(fname,'file'), delete(fname); end

nt = numel(timeVec);                          % 时间行数
nr = numel(distVec);                          % 距离列数

% ---- 构造表头：第一个单元格为说明文字，其后为距离 ----
hdr = cell(1, nr+1);                          % 预分配表头行
hdr{1} = '时间\到药材中心的距离';             % A1 单元格
dv = round(distVec(:).',4);                   % 距离四舍五入到 4 位小数，避免 0.30000000000000004
for k = 1:nr
    hdr{k+1} = dv(k);                         % 依次填入 0, 0.1, ..., 2
end
if ~isempty(hdrLast)
    hdr{nr+1} = hdrLast;                      % 替换最后一列为 '药材表面'
end

% ---- 逐个工作表写盘 ----
for s = 1:numel(sheetNames)
    M = valCells{s};                          % 当前工作表的数据矩阵 nt x nr
    C = cell(nt+1, nr+1);                     % 预分配可写单元格
    C(1,:) = hdr;                             % 第 1 行为表头
    for i = 1:nt
        C{i+1,1} = timeVec(i);                % 第 1 列为时刻
    end
    Mr = round(M, 4);                         % 题目要求：所有结果保留 4 位小数
    for i = 1:nt
        for j = 1:nr
            C{i+1,j+1} = Mr(i,j);             % 逐元素填入数值
        end
    end
    writecell(C, fname, 'Sheet', sheetNames{s});   % 写入 xlsx
end
end
