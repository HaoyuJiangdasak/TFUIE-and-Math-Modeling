function fid = savelog(name)
%SAVELOG  在 solution/out 下新建一个 UTF-8 文本日志文件并返回文件句柄
%   用于把结果表格以 UTF-8 编码写盘（Windows 控制台默认 GBK，中文会乱码）。
d = fullfile(rootdir(),'out');                    % 输出目录
if ~exist(d,'dir'), mkdir(d); end                 % 目录不存在则创建
fid = fopen(fullfile(d,name),'w','n','UTF-8');    % 以 UTF-8 编码打开写模式
end
