function d = rootdir()
%ROOTDIR  返回 solution 根目录的绝对路径
%   rootdir.m 位于 <solution>/code/ 下，因此向上两级即得 <solution>。
%   这样可以保证无论从哪个目录启动 MATLAB，脚本中的相对路径都正确。
d = fileparts(fileparts(mfilename('fullpath')));
end
