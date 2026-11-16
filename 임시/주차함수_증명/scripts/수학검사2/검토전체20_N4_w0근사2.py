# N4: (5.3) 하계의 정밀 부동소수점 근사 — kappa 적분을 mu>=theta^2/3 인 구간에서만, 끝점을 정확히 잡고 Simpson으로.
import math
h0=0.0342; ups=math.sqrt(6*h0); c2=1/(2*(1-ups))
def ti(vs,b,W0):
    T1=math.sqrt(vs*W0); T2=math.sqrt(b/W0)
    return 0.5*math.sqrt(math.pi/b)*(math.exp(-2*math.sqrt(vs*b))*math.erfc(T1-T2)-math.exp(2*math.sqrt(vs*b))*math.erfc(T1+T2))
def Tmax(th,mu):
    vs=max(th-h0,0)/2; b=th*th/2
    return th/math.sqrt(2*math.pi)*math.exp(th**3*h0/(3*mu*mu))*(h0*h0*mu**-1.5*math.exp(-vs*mu-b/mu)+ti(vs,b,mu))
def Pmin(k):
    return max(0.0, math.sqrt(2/math.pi)*(k+h0*h0)**-0.5*math.exp(-h0*h0/(12*(k+h0*h0)))-1.6*h0*math.sqrt(k))
def bmin(th): return math.exp(-th**1.5-c2*th*th*h0)
def Q(th,k):
    mu=6-k-th*h0
    return Pmin(k)*math.exp(-th*k-th*h0*h0)*(1-k*h0-h0**3)*max(0.0,bmin(th)-Tmax(th,mu))
def simpson(f,a,b,N):
    if b<=a: return 0.0
    if N%2: N+=1
    h=(b-a)/N; s=f(a)+f(b)
    for i in range(1,N): s+=(4 if i%2 else 2)*f(a+i*h)
    return s*h/3
def g(th):
    if th<=0: return 0.0
    up=min(6-th*h0, 6-th*h0-th*th/3)
    if up<=0: return 0.0
    # Pmin has sqrt(kappa) at 0 -> split [0,eps] finer
    return th*(simpson(lambda k:Q(th,k),0,min(0.05,up),400)+simpson(lambda k:Q(th,k),min(0.05,up),up,1600))
def rho(th):
    y=max(th/2,th-h0)
    return math.sqrt(2)*th**1.5*math.exp(-th*math.sqrt(y)+min(th*th*h0,ups*th**1.5)/3)*(1+min(th*h0*h0,6*h0))/(math.sqrt(y)-min(th*h0,ups*math.sqrt(th))/3)
# theta integral: g ~ theta near 0 (smooth), cut at sqrt(18)~4.2426 where g->0 continuously? check
Ig=simpson(g,0,4.1,1640)
ths=[i*4.1/1640 for i in range(1641)]; gv=[g(t) for t in ths]; gmax=max(gv)
Ir=simpson(rho,1e-9,12,2400); rv=[rho(1e-9+i*12/2400) for i in range(2401)]; rmax=max(rv)
Y=25000; O=(1/Y**2)*math.sqrt(12/math.pi)*Y**(1/3)*math.sqrt(2/Y)*(Y+1)
val=(Ig-h0*gmax)-h0*(Ir+h0*rmax+math.exp(-12+h0))-O
print(f"int g [0,4.1] = {Ig:.6f}; max g = {gmax:.5f} at {ths[gv.index(gmax)]:.4f}")
print(f"int rho [0,12] = {Ir:.6f}; max rho = {rmax:.5f}")
print(f"(5.3) float bound = {val:.6f}; certified w0 = 0.71216801")
print(f"int g over [4.1, 4.2427] (dropped) = {simpson(g,4.1,4.2427,200):.3e}")
