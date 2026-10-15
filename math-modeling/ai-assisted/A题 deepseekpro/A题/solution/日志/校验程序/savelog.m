function fid = savelog(name)
%SAVELOG  把校验结果以 UTF-8 写盘。本文件位于 日志/校验程序/，故写到上一级 日志/。
here   = fileparts(mfilename('fullpath'));
logdir = fileparts(here);
fid = fopen(fullfile(logdir, name), 'w', 'n', 'UTF-8');
end
