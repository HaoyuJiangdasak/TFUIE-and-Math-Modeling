function S = atk_solver(P)
%ATK_SOLVER  验证用：与 herb_solver 完全相同的数值内核，额外记录每步的 max(X)、argmax(X)
%   额外输出：
%     S.maxX  —— 每步结束时的 max_j X_j (长度 nt)
%     S.argX  —— 每步 max_j X_j 所在节点号 (1..N+1)
%     S.th    —— 对应时刻 (s)
%   其余输入/输出与 herb_solver 一致（P.Xdry 默认 Inf 且不再提前 break，除非 P.stopOnDry）

if ~isfield(P,'picard'), P.picard = 3;  end
if ~isfield(P,'Xdry'),   P.Xdry   = Inf; end
if ~isfield(P,'stopOnDry'), P.stopOnDry = false; end

N   = P.N;  dxi = 1/N;  n = N+1;  dt = P.dt;  nt = round(P.tEnd/dt);

xi   = (0:N)'*dxi;
xmid = ((1:N)'-0.5)*dxi;
xiN  = (N-0.5)*dxi;
wSurf = 1 - xiN^2;

tv  = (0:nt)'*dt;
Tfv = P.Tf(tv);  Xfv = P.Xf(tv);  Rv = P.Rf(tv);  Rdv = P.Rdf(tv);

T = P.T0*ones(n,1);  X = P.X0*ones(n,1);
maxX = zeros(nt,1);  argX = zeros(nt,1);
dryTime = Inf;

for m = 1:nt
    Rn = Rv(m+1); Rdn = Rdv(m+1); Tf = Tfv(m+1); Xf = Xfv(m+1);
    To = T; Xo = X;
    for it = 1:P.picard
        rho = P.rho(X); cp = P.cp(X); kc = P.kc(X); Dc = P.Dco(X, T+273.15);
        rc = rho.*cp;
        kmid = 2*kc(1:N).*kc(2:n)./(kc(1:N)+kc(2:n));
        Dmid = 2*Dc(1:N).*Dc(2:n)./(Dc(1:N)+Dc(2:n));
        if isfield(P,'advModel') && strcmp(P.advModel,'grid')
            aadv = (Rdn/Rn)*xi;
        else
            aadv = zeros(n,1);
        end
        aadv(1) = 0;
        wX = zeros(n,1); wT = zeros(n,1);
        ip = find(aadv>0); ip = ip(ip<n);
        im = find(aadv<0); im = im(im>1);
        wX(ip) = (X(ip+1)-X(ip))/dxi;  wX(im) = (X(im)-X(im-1))/dxi;
        wT(ip) = (T(ip+1)-T(ip))/dxi;  wT(im) = (T(im)-T(im-1))/dxi;
        advX = aadv.*wX;  advT = aadv.*wT;

        aX = zeros(n,1); bX = zeros(n,1); cX = zeros(n,1); dX = zeros(n,1);
        g0 = 4*dt*Dmid(1)/(Rn^2*dxi^2);
        bX(1) = 1 + g0;  cX(1) = -g0;  dX(1) = Xo(1);
        jj = (2:N)';
        al = dt./(Rn^2*xi(jj)*dxi^2);
        aX(jj) = -al.*xmid(jj-1).*Dmid(jj-1);
        cX(jj) = -al.*xmid(jj)  .*Dmid(jj);
        bX(jj) = 1 + al.*(xmid(jj).*Dmid(jj) + xmid(jj-1).*Dmid(jj-1));
        dX(jj) = Xo(jj) + dt*advX(jj);
        beX = 2*dt/(Rn^2*wSurf);
        aX(n) = -beX*xiN*Dmid(N)/dxi;
        bX(n) = 1 + beX*(Rn*P.hm + xiN*Dmid(N)/dxi);
        cX(n) = 0;
        dX(n) = Xo(n) + dt*advX(n) + beX*Rn*P.hm*Xf;

        aT = zeros(n,1); bT = zeros(n,1); cT = zeros(n,1); dT = zeros(n,1);
        g0T = 4*dt*kmid(1)/(Rn^2*dxi^2*rc(1));
        bT(1) = 1 + g0T;  cT(1) = -g0T;  dT(1) = To(1);
        alT = dt./(Rn^2*xi(jj)*dxi^2.*rc(jj));
        aT(jj) = -alT.*xmid(jj-1).*kmid(jj-1);
        cT(jj) = -alT.*xmid(jj)  .*kmid(jj);
        bT(jj) = 1 + alT.*(xmid(jj).*kmid(jj) + xmid(jj-1).*kmid(jj-1));
        dT(jj) = To(jj) + dt*advT(jj);
        beT = 2*dt/(Rn^2*wSurf*rc(n));
        aT(n) = -beT*xiN*kmid(N)/dxi;
        bT(n) = 1 + beT*(Rn*P.h + xiN*kmid(N)/dxi);
        cT(n) = 0;
        dT(n) = To(n) + dt*advT(n) + beT*Rn*P.h*Tf;

        X = thomas(aX,bX,cX,dX);
        T = thomas(aT,bT,cT,dT);
        X = max(X,0);
    end
    [mx, ix] = max(X);
    maxX(m) = mx;  argX(m) = ix;
    if isfinite(P.Xdry) && mx < P.Xdry
        dryTime = m*dt;
        if P.stopOnDry, break; end
    end
end
S.maxX = maxX(1:m);  S.argX = argX(1:m);  S.th = (1:m)'*dt;
S.dryTime = dryTime;  S.xi = xi;  S.Tend = T;  S.Xend = X;
S.rend = Rv(min(m+1,nt+1));  S.nstep = m;
end

function x = thomas(a,b,c,d)
n = numel(d);
for k = 2:n
    w = a(k)/b(k-1);  b(k) = b(k) - w*c(k-1);  d(k) = d(k) - w*d(k-1);
end
x = zeros(n,1);  x(n) = d(n)/b(n);
for k = n-1:-1:1
    x(k) = (d(k) - c(k)*x(k+1))/b(k);
end
end
