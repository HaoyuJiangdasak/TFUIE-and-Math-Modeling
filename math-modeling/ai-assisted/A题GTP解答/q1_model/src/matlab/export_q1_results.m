function export_q1_results(result, outputFile)
%EXPORT_Q1_RESULTS Write the requested 1 s x 0.1 cm matrices.

arguments
    result struct
    outputFile (1,1) string
end

outputRadiusCm = (0:0.1:2)';
outputTimeS = (1:1800)';
temperature = interp2(result.r_m*100,result.t_s,result.temperature_C, ...
    outputRadiusCm',outputTimeS,'linear');
moisture = interp2(result.r_m*100,result.t_s,result.moisture_kgkg, ...
    outputRadiusCm',outputTimeS,'linear');
temperature = round(temperature,4);
moisture = round(moisture,4);

header = [{'时间\到药材中心的距离'},num2cell(outputRadiusCm')];
temperatureCells = [header;[num2cell(outputTimeS),num2cell(temperature)]];
moistureCells = [header;[num2cell(outputTimeS),num2cell(moisture)]];
writecell(temperatureCells,outputFile,'Sheet','温度','Range','A1');
writecell(moistureCells,outputFile,'Sheet','水分浓度','Range','A1');
end
