%RUN_Q1_PINN Launch the PyTorch PINN in the conda dl environment.
clc;
thisDir = fileparts(mfilename('fullpath'));
modelDir = fileparts(fileparts(thisDir));
pythonExe = 'C:\Users\Public\miniconda3\envs\dl\python.exe';
scriptFile = fullfile(modelDir,'src','python','train_q1_pinn.py');
command = sprintf('"%s" "%s"',pythonExe,scriptFile);
status = system(command);
if status ~= 0
    error('PINN training failed with exit status %d.',status);
end
