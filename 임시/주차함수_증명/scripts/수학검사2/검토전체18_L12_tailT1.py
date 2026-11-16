# L12 검산: 보조정리 lemma-L(나)의 상수 M_i, M*_i, C_i와 L(r) (r=10^4, 2*10^4, 10^5), (B)의 부등식 계수.
from mpmath import mp, mpf, quad, exp, sqrt, pi, findroot, erfc
mp.dps=30
f=lambda y,i: y**i*exp(-y-y*y/2)
M=[quad(lambda y: f(y,i),[0,mp.inf]) for i in range(6)]
M0c=exp(mpf(1)/2)*sqrt(pi/2)*erfc(1/sqrt(2))
M26=quad(lambda y: f(y,2),[0,6])
Ms={}
for i in range(2,6):
    ys=(-1+sqrt(1+4*i))/2; Ms[i]=f(ys,i)
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
def L(r):
    s=sqrt(mpf(r))
    return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+exp(-mpf(1)/2))/s+1/s**2)
print("M_0..5:",[mp.nstr(x,7) for x in M]," M_0 closed:",mp.nstr(M0c,10)," recurrence check M_{i+1}=iM_{i-1}-M_i:",[mp.nstr(i*M[i-1]-M[i]-M[i+1],3) for i in range(1,5)])
print("M2^(6):",mp.nstr(M26,12)," M_2-M2^(6):",mp.nstr(M[2]-M26,5)," bound e^-6(6+1/6)e^-18:",mp.nstr(exp(-6)*(6+mpf(1)/6)*exp(-18),5))
print("C1..C4:",[mp.nstr(x,7) for x in (C1,C2,C3,C4)])
for r in (10**4,2*10**4,10**5): print("L(%d)="%r, mp.nstr(L(r),8))
s=mpf(100); lead=mpf(1)/2+2*mpf('0.845204')-sqrt(3*pi/2)
print("leading coeff 1/2+2*0.845204-sqrt(3pi/2) =",mp.nstr(lead,8))
P=lambda s: s*lead+mpf(1)/2-(1/(3*s)+8/(3*s**2)+mpf('2.507')/s**2+(1+mpf('2.1709')*s)/s**3)
print("P(100)=",mp.nstr(P(s),8)," rhs 0.0196*100+0.496=",mp.nstr(mpf('0.0196')*100+mpf('0.496'),8), " diff at s=100:",mp.nstr(P(s)-(mpf('0.0196')*s+mpf('0.496')),5), " diff grows with s:", mp.nstr(P(1000)-(mpf('0.0196')*1000+mpf('0.496')),5))
