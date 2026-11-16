# N4: 정리 5-32의 하계 (5.3)을 계단함수 없이 부동소수점으로 근사 평가해 w0=0.71216의 크기를 가늠한다 (인증 아님).
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
    if mu<th*th/3: return 0.0
    return Pmin(k)*math.exp(-th*k-th*h0*h0)*(1-k*h0-h0**3)*max(0.0,bmin(th)-Tmax(th,mu))
def g(th):
    up=6-th*h0
    if up<=0: return 0.0
    N=600; dk=up/N
    return th*sum(Q(th,(i+0.5)*dk) for i in range(N))*dk
def rho(th):
    y=max(th/2,th-h0)
    return math.sqrt(2)*th**1.5*math.exp(-th*math.sqrt(y)+min(th*th*h0,ups*th**1.5)/3)*(1+min(th*h0*h0,6*h0))/(math.sqrt(y)-min(th*h0,ups*math.sqrt(th))/3)
N=820; dth=4.1/N
gs=[g((i+0.5)*dth) for i in range(N)]
Ig=sum(gs)*dth; gmax=max(gs)
M=1200; dr=12/M
rs=[rho((i+0.5)*dr) for i in range(1,M)]
Ir=sum(rs)*dr; rmax=max(rs)
Y=25000
O=(1/Y**2)*math.sqrt(12/math.pi)*Y**(1/3)*math.sqrt(2/Y)*(Y+1)
val=(Ig-h0*gmax)-h0*(Ir+h0*rmax+math.exp(-12+h0))-O
print(f"int g over [0,4.1] ~ {Ig:.5f}, max g ~ {gmax:.4f} at theta~{(gs.index(gmax)+0.5)*dth:.3f}")
print(f"int rho over [0,12] ~ {Ir:.5f}, max rho ~ {rmax:.4f}; O(25000)={O:.2e}")
print(f"float approx of (5.3) bound ~ {val:.5f}  (certified w0 = 0.71216 should be <= this and near)")
# where does g vanish?
for th in [4.0,4.2,4.24,4.25,4.3,6.0]:
    print(f"g({th})={g(th):.3e}")
