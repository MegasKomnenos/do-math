# Q12: 부록 D 장5A·장6 항목의 개수·작은 수치 재계산
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from math import comb, factorial, exp, sqrt, pi, ceil, floor, log
from fractions import Fraction
# exact-n20000 (ㄹ) 위치 수
tot=sum(n-2-(-(-(n-1)//2)) for n in range(5,20001))
print("(ㄹ) positions 5..20000:",tot)
print("c50 positions 20001..50000:",sum(n-2-(-(-(n-1)//2)) for n in range(20001,50001)))
print("pairs 20001..50000:",sum(n-2-(-(-(n-1)//2))+1 for n in range(20001,50001)))
# 열 인증 121..500 개수
def B(k): return -(-k*k//4)
d1=sum(2*B(k)-2*k for k in range(161,501)); r1=sum(B(k)+1 for k in range(161,501))
d0=sum(2*B(k)-2*k for k in range(121,161)); r0=sum(B(k)+1 for k in range(121,161))
print("column cert direct/ratio 161-500:",d1,r1," 121-160:",d0,r0)
print("2B<10000 for k<=:",max(k for k in range(121,501) if 2*B(k)<10000))
# newton 계수 수 (차수 r+d+3 -> r+d+4 계수)
print("newton coeff count r<=40:",sum(r+d+4 for r in range(2,41) for d in range(1,r)), " polys:",sum(r-1 for r in range(2,41)), sum(r-1 for r in range(2,171)))
# theorem-D-base 쌍 수
cnt=0; cnt2=0
for m in range(4,701):
    dmax=max(d for d in range(0,100) if 8*d**3<=m*m)
    cnt+=dmax
print("thmD pairs:",cnt, " m=700 dmax:",max(d for d in range(0,100) if 8*d**3<=700*700), " m=689:",max(d for d in range(0,100) if 8*d**3<=689*689))
# prop-W-thirteen
from mpmath import mp, mpf, e as E, factorial as mf
mp.dps=40
def eRen(m): return mpf(m)**(m-1)/(E**(m-1)*mf(m-1))
for d in range(1,15):
    L=3130*(eRen(d+1)-mpf(60)*(d+1)/(3131+d))
    R=2*(1+sum(eRen(r+1)+mpf(60)*(r+1)/(3131+d) for r in range(1,d)))
    print("d",d,"L",mp.nstr(L,8),"R",mp.nstr(R,8),"L-R",mp.nstr(L-R,6))
# tilt-sum
def tsum(k):
    return sum(Fraction(n**(n-1),factorial(n))*Fraction(k,k+1)**((k-1)*n) for n in range(2,k+2))
for k in [2,3,10,20,42,43]:
    print("tilt k",k,float(tsum(k)))
print("max over 2..60:",max((float(tsum(k)),k) for k in range(2,61)))
# theorem-U arithmetic
c=1/sqrt(2*pi)
print("3c(8.133+10.301c)=",3*c*(8.133+10.301*c)," 1.5*2.7323*0.8051*c*(17.951+23.462c)=",1.5*2.7323*0.8051*c*(17.951+23.462*c))
print("iv:",3*c*(8.13091+10.29939*c),1.5*2.7323*0.8051*c*(17.94855+23.46002*c),3*c*(8.13091+10.29939*c)+1.5*2.7323*0.8051*c*(17.94855+23.46002*c))
print("32000:",3*c*(8.12798+10.28899*c)+1.5*2.7323*0.8051*c*(17.94110+23.44135*c))
# c50 m(n) check: n-2-max{m>=171: m^{3/2}+9m<=n}
def mfun(n):
    ms=[m for m in range(171,2000) if m**3<=(n-9*m)**2 and n-9*m>=0]
    return max(ms) if ms else None
print("m(20001)=",mfun(20001),"m(50000)=",mfun(50000))
# critical window: box edges
print("10001^(-1/3)=",10001**(-1/3)," 30 boxes*0.0015=",0.045," 0.0015/1.25^12=",0.0015/1.25**12, " k for ku=1.0307e-4:",(1/1.0307e-4)**3)
# exact-n20000 (ㄱ) counts
print("(ㄱ) direct k<=120:",4*9989+sum(10000-2*k for k in range(6,121)))
print("row cert 501..4999:",sum(10000-2*k for k in range(501,5000)))
print("(ㄴ):",sum(-(-n//2)-1 for n in range(10001,20001)))
# tail-T1 (B) inequality at s=100
L4=0.845204
for s in [100,141.42,316.2]:
    lhs=s*(0.5+2*L4-sqrt(3*pi/2))+0.5-(1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3)
    print("T1(B) s",s,"lhs",lhs,"rhs",0.0196*s+0.496)
# zeta coarse check
from mpmath import zeta, nsum, inf
mp.dps=20
N=2000
S=nsum(lambda j: j**mpf(-1.5),[1,N])
print("coarse lower N=2000:",S+2*(N+1)**mpf(-0.5)," zeta(3/2)=",zeta(1.5))
# rig constants
print("1-cos1=",1-__import__('math').cos(1)," sin45=",sqrt(0.5)," 0.1267*10001=",0.1267*10001," ln(166/10001^(1/6))=",log(166/10001**(1/6)))
