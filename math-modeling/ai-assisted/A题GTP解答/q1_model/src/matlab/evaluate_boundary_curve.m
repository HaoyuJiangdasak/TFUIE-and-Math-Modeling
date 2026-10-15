function y = evaluate_boundary_curve(curve, t)
%EVALUATE_BOUNDARY_CURVE Evaluate a fitted or interpolated boundary curve.
if isfield(curve,'method') && any(strcmpi(string(curve.method),["linear","pchip"]))
    y = interp1(curve.timeData,curve.valueData,t,char(string(curve.method)),'extrap');
    return;
end
p = curve.params;
y = curve.y0 + (p(1)-curve.y0).*(1-exp(-(max(t,0)./p(2)).^p(3)));
end
