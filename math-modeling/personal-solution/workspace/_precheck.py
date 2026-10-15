import numpy as np, pandas as pd
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

a1=pd.read_excel('user_data/附件1.xlsx'); a2=pd.read_excel('user_data/附件2.xlsx')
t1=a1['时间'].values.astype(float); Ta=a1['温度'].values; Ca=a1['水分浓度'].values
t2=a2['时间'].values.astype(float); Rr=a2['半径'].values/100.0
Tair=lambda t: float(np.interp(t, t1, Ta))
Cair=lambda t: float(np.interp(t, t1, Ca))
_R=PchipInterpolator(t2, Rr, extrapolate=False)
def Rt(t):
    tc=min(max(t,0.0),t2[-1]); return float(np.clip(_R(tc), Rr.min(), Rr[0]))
h, hm = 25.0, 8e-7
ones=lambda C,v: np.full_like(C, v)
P1=dict(rho=lambda C:ones(C,820.0), cp=lambda C:ones(C,2600.0), lam=lambda C:ones(C,0.36),
        D=lambda C,TK: 7e-9*np.exp(-0.89/np.maximum(C,1e-4)))
P3=dict(rho=lambda C:650+128*C, cp=lambda C:1450+2736*C/(C+1), lam=lambda C:0.21+0.38*C/(C+1),
        D=lambda C,TK: 2.4e-3*np.exp(-0.45/np.maximum(C,1e-4))*np.exp(-3850.0/TK))
P4=dict(rho=lambda C:760+90*C, cp=lambda C:1850+2150*C/(C+1), lam=lambda C:0.12+0.20*C/(C+1),
        D=lambda C,TK: 4.2e-4*np.exp(-0.30/np.maximum(C,1e-4))*np.exp(-3850.0/TK))

def make_rhs(N,P,Rof,latent=0.0,cs=1.0):
    deta=1.0/N; ef=np.arange(N+1)*deta; eta=(np.arange(N)+0.5)*deta
    V=(ef[1:]**2-ef[:-1]**2)/2.0
    def rhs(t,y):
        T=y[:N]; C=np.maximum(y[N:],1e-6); R=Rof(t); Ta_=Tair(t); Ca_=Cair(t)*cs
        TK=T+273.15
        Dc=P['D'](C,TK); lam=P['lam'](C); rho=P['rho'](C); cp=P['cp'](C)
        Df=0.5*(Dc[1:]+Dc[:-1]); lf=0.5*(lam[1:]+lam[:-1])
        Cs_=(2*Dc[-1]/(R*deta)*C[-1]+hm*Ca_)/(2*Dc[-1]/(R*deta)+hm)
        jin=ef[1:N]*Df*(C[1:]-C[:-1])/deta
        jsurf=-R*hm*(Cs_-Ca_)
        dC=np.empty(N)
        dC[0]=jin[0]/(R**2*V[0]); dC[1:N-1]=(jin[1:]-jin[:-1])/(R**2*V[1:N-1])
        dC[N-1]=(jsurf-jin[-1])/(R**2*V[N-1])
        Ts_=(2*lam[-1]/(R*deta)*T[-1]+h*Ta_)/(2*lam[-1]/(R*deta)+h)
        qin=ef[1:N]*lf*(T[1:]-T[:-1])/deta
        rho_d=rho[-1]/(1+C[-1])
        qsurf=R*(h*(Ta_-Ts_)-latent*rho_d*hm*max(Cs_-Ca_,0.0))
        dT=np.empty(N)
        dT[0]=qin[0]/(R**2*V[0])/(rho[0]*cp[0])
        dT[1:N-1]=(qin[1:]-qin[:-1])/(R**2*V[1:N-1])/(rho[1:N-1]*cp[1:N-1])
        dT[N-1]=(qsurf-qin[-1])/(R**2*V[N-1])/(rho[N-1]*cp[N-1])
        return np.concatenate([dT,dC])
    return rhs, eta, V

def run(P,tend,N=30,Rof=None,latent=0.0,cs=1.0,teval=None,thr=None):
    Rof=Rof or (lambda t:0.02)
    rhs,eta,V=make_rhs(N,P,Rof,latent,cs)
    y0=np.concatenate([np.full(N,28.0),np.full(N,2.55)])
    ev=None
    if thr is not None:
        def ev_(t,y): return np.max(y[N:])-thr
        ev_.terminal=True; ev_.direction=-1; ev=ev_
    s=solve_ivp(rhs,(0,tend),y0,method='BDF',rtol=1e-7,atol=1e-9,t_eval=teval,events=ev)
    return s,eta,V
