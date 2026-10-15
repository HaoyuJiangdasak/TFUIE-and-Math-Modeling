function fid = savelog(name)
%SAVELOG  把结果表格以 UTF-8 编码写盘，并返回文件句柄。
%   优先写到与本问目录同级的“日志”文件夹；若该文件夹不存在，就写在本问目录下。
%   （Windows 控制台默认 GBK，直接把中文写屏会乱码，所以统一落盘为 UTF-8。）
here   = fileparts(mfilename('fullpath'));        % 本文件所在目录（即某一问的目录）
logdir = fullfile(fileparts(here), '日志');       % 同级的“日志”目录
if ~exist(logdir, 'dir')
    logdir = here;                                % 没有日志目录就退回本问目录
end
fid = fopen(fullfile(logdir, name), 'w', 'n', 'UTF-8');
end
