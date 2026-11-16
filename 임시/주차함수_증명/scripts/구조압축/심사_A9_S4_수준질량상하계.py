# A9 S4 검산: 명제 9.7(9:prop-6)의 상하계와 정리 6.48(나)(6:theorem-D)의 상하계 비교.
# 6.48(나): Psi(d)/(2m) <= c_m(m-d) <= 3Psi(d)/(2m), m>=4, 1<=d<=m^{2/3}/2.
# 9.7:  Lo97 = Psi(d)/w * exp(-[g*(2pi)^{-1/2}(4/3 d^{3/2}+2 sqrt d) + g^2(5/8 d^2+d)]/(w Psi(d)))
#       Up97 = Psi(d) (m+1)^{3/2} e^{1/(12(m+1))}/(m-d+1)^{5/2},  w=m-d, g=((m+1)/(m-d+1))^{3/2} e^{1/(12(m-d+1))}
# 또 작은 m에서 정확값 c_m(m-d)를 정리 2.6의 재귀로 구해 두 상하계가 모두 유효한지와 여유를 본다.
from fractions import Fraction
from math import sqrt, exp, pi, log, lgamma, floor, comb
import sys

def Ren(j):
    return exp(j*log(j)-j-lgamma(j+1))
PSI=[0.0]
def Psi(d):
    while len(PSI)<=d: PSI.append(PSI[-1]+Ren(len(PSI)))
    return PSI[d]
def lo97(m,d):
    w=m-d; g=((m+1)/(m-d+1))**1.5*exp(1/(12*(m-d+1)))
    P=Psi(d)
    return P/w*exp(-(g*(2*pi)**-0.5*(4/3*d**1.5+2*sqrt(d))+g*g*(5/8*d*d+d))/(w*P))
def up97(m,d):
    return Psi(d)*(m+1)**1.5*exp(1/(12*(m+1)))/(m-d+1)**2.5
def lo648(m,d): return Psi(d)/(2*m)
def up648(m,d): return 3*Psi(d)/(2*m)

worse_lo=[]; worse_up=[]
def scan(ms):
    for m in ms:
        D=int(floor(m**(2/3)/2))
        for d in range(1,D+1):
            if lo97(m,d)<lo648(m,d): worse_lo.append((m,d))
            if up97(m,d)>up648(m,d): worse_up.append((m,d))
scan(range(4,30001))
print("m<=30000 전수: 9.7 하계가 6.48 하계보다 나쁜 (m,d) 수 =",len(worse_lo),"; 최대 m =",max(worse_lo)[0] if worse_lo else None)
print("           9.7 상계가 6.48 상계보다 나쁜 (m,d) 수 =",len(worse_up),"; 최대 m =",max(worse_up)[0] if worse_up else None)
print("  하계 예외 m 목록(서로 다른 m):",sorted(set(m for m,d in worse_lo)))
print("  상계 예외 m 목록:",sorted(set(m for m,d in worse_up)))
worse_lo.clear(); worse_up.clear()
scan([int(10**(3+0.05*i)) for i in range(0,61)])
print("표본 m in [1e3,1e6]: 하계 예외",len(worse_lo),"상계 예외",len(worse_up))

mn=10.0; arg=None
for k in [3131,3500,4000,5000,6668,10000,20000,50000,100000,10**6]:
    d=14
    while True:
        m=k+d
        if d>m**(2/3)/2: break
        r=lo97(m,d)/lo648(m,d)
        if r<mn: mn=r; arg=(k,d)
        d+=1
print("6.49(다) 소비 범위(k 표본, 14<=d<=m^{2/3}/2)에서 min Lo97/(Psi/(2m)) =",round(mn,4),"at (k,d)=",arg)

MAXN=140
A={}
def Aval(n,l):
    if n==0: return Fraction(1)
    if (n,l) in A: return A[(n,l)]
    if l<0: return Fraction(0)
    s=Fraction(0)
    for j in range(1,n+1):
        s+=comb(n-1,j-1)*min(j,l+1)*Aval(j-1,l)*Aval(n-j,l)
    A[(n,l)]=s; return s
sys.setrecursionlimit(10000)
viol=[]; minslack97=[(10,None),(10,None)]; minslack648=[(10,None),(10,None)]
for m in range(4,MAXN+1):
    pm=Fraction((m+1)**(m-1))
    D=int(floor(m**(2/3)/2))
    for d in range(1,D+1):
        w=m-d
        c=float((Aval(m,w)-Aval(m,w-1))/pm)
        for name,lo,up,store in (("9.7",lo97(m,d),up97(m,d),minslack97),("6.48",lo648(m,d),up648(m,d),minslack648)):
            if lo>c*(1+1e-12) or up<c*(1-1e-12): viol.append((name,m,d,lo,c,up))
            if c/lo<store[0][0]: store[0]=(c/lo,(m,d))
            if up/c<store[1][0]: store[1]=(up/c,(m,d))
print("정확값 대조 m<=%d: 위반 수 ="%MAXN,len(viol), viol[:5])
print("  9.7: min c/Lo =",minslack97[0]," min Up/c =",minslack97[1])
print("  6.48: min c/Lo =",minslack648[0]," min Up/c =",minslack648[1])
for m in (60,100,140):
    pm=Fraction((m+1)**(m-1))
    row=[]
    for d in (1,2,4,8,int(m**(2/3)/2)):
        if d>m**(2/3)/2: continue
        c=float((Aval(m,m-d)-Aval(m,m-d-1))/pm)
        row.append((d,round(lo97(m,d)/c,3),round(lo648(m,d)/c,3),round(up97(m,d)/c,3),round(up648(m,d)/c,3)))
    print(" m=%d (d, Lo97/c, Lo648/c, Up97/c, Up648/c):"%m,row)

def Low653(k,d):
    rho=d/k**(2/3); eps=k**(-1/3)
    a=(2*pi)**-0.5*k**(1/3)*(2*sqrt(rho)-2.218*eps)
    return a/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/((2*pi)**-0.5*(2*sqrt(rho)-2.218*eps)))
for k in (3131,6668,20000):
    out=[]
    for rho in (0.5,1,2,3,4,6):
        d=int(round(rho*k**(2/3))); m=k+d
        if d>m/2: continue
        out.append((rho, round((k+1)*lo97(m,d),4), round(Low653(k,d),4)))
    print(" k=%d (rho, (k+1)Lo97, Low653):"%k,out)
