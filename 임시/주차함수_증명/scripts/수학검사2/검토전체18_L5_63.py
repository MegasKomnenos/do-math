# 6.3 검산: 상수들, 보조정리 Ω·Φ의 수치 확인(y=50, 10..), 정리 old-8-13 (6.21)의 정확 정수 검증(y=50..70)
from fractions import Fraction as Fr
from math import comb
from mpmath import mp, mpf, e, exp, log, sqrt, pi, factorial
mp.dps=30
print("X*=", (5-sqrt(7))/6, "max=", (10+7*sqrt(7))/54)
print("tl^-1 bound:", 1/(1-mpf(3)/4/51), "e^(1/24+1/612)=", exp(mpf(1)/24+mpf(1)/612), "1+1/51=", 1+mpf(1)/51)
u=mpf('1.0443')*mpf('1.0150')*mpf('1.01961')*mpf(4)/3; print("u<=",u, "0.5282*1.449=",mpf('0.5282')*mpf('1.449'))
print("L/G V>=2:", mpf(1.5)/53*mpf(4)/3*mpf(0.5)*mpf('1.01961')*mpf('1.0150'))
print("L/G V=1:", mpf(1.5)/52*mpf('2.02')*mpf('0.51')*mpf('1.01961')*(1/(1-mpf(1.5)/(52*51))))
print("e^(3/102)=",exp(mpf(3)/102), "e^-2=",exp(-2), "1.545e^-1=",mpf('1.545')*exp(-1))
y=mpf(50); print("c_{y+2} lower at y=50:", (2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/(y+1))/(y+2), "0.6/(y+3)=",mpf('0.6')/(y+3))
print("0.2e^-1*0.6=",mpf('0.2')*exp(-1)*mpf('0.6'))
r=mpf('0.0441')*(y-1)/(y+3)**2/(mpf('1.2')*(y+1)/((y+2)**2*(y+3))); print("ratio y=50:",r)
print("e^{-1+3/102}/(2*51)*51 =", exp(-1+mpf(3)/102)/2)
# Borel 정확(유리수*e^-n은 아니므로 mpmath)
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
def g(x): x=mpf(x); return (x-1)*log(1+1/x)
def check_omega(y):
    worst=mpf(10)
    for d in range(2,y+3):
        for q in range(1,d):
            t=y+d; V=d-q
            pi1=lambda qq: Bor(d-qq)*Bor(y+1+qq)/Bor(y+1+d)   # pi_{y+d}(y+1+q)
            pi0=lambda qq: Bor(d-qq)*Bor(y+qq)/Bor(y+d)       # pi_{y+d-1}(y+q)
            Er=lambda qq: pi0(qq)-pi1(qq)
            Cv=(d-1)*(y+1)-mpf((q-1)*y*(y+1+q))/(y+q)-mpf((y+1)*q)/(y+q)
            G=pi1(q)*Cv/(y+1+q)
            Om=G-(y+1)*(sum(Er(qq) for qq in range(q+1,d))+Er(q)*mpf(q)/(y+q))
            worst=min(worst,Om/G)
    return worst
print("min Omega/G y=50:", check_omega(50), " y=51:", check_omega(51))
def check_phi(y):
    bad=[]
    for d in range(2,y+3):
        for q in range(1,d):
            pi1=Bor(d-q)*Bor(y+1+q)/Bor(y+1+d); pi0=Bor(d-q)*Bor(y+q)/Bor(y+d)
            Cs=(d-1)-mpf((y+1)*q)/(y+q)
            Mg=pi1*Cs/(y+1+q)-(y+1)*(pi0-pi1)*mpf(q)/(y+q)
            if Mg<0: bad.append((d,q))
    return bad
for yy in (10,11,20,50): print("Phi exceptions y=",yy,":",check_phi(yy))
# 정확 정수 A_{n,l}, 정리 old-2-6
NMAX=150
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1): A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+1):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
p=[(n+1)**(n-1) if n>0 else 1 for n in range(NMAX+1)]
def s(m,yc): # s_m(y)=A_{m,y-1}/p_m
    return Fr(A[m][yc-1],p[m]) if yc>=1 else Fr(0)
def c(m,Y): return s(m,Y+1)-s(m,Y)
viol=[]; minratio=None
for y in range(50,71):
    for d in range(2,y+3):
        lhs=(y+1)*(s(y+d,y+1)-s(y+d-1,y)); rhs=(d-1)*c(y+d,y)
        if lhs>rhs: viol.append((y,d))
        r=lhs/rhs if rhs else None
        if r is not None: minratio = r if minratio is None else max(minratio,r)
print("6.21 violations y=50..70:", viol, "max lhs/rhs:", float(minratio))
# 작은 y에서는 어떤가(정리 범위 밖, 참고)
viol2=[(y,d) for y in range(2,50) for d in range(2,y+3) if (y+1)*(s(y+d,y+1)-s(y+d-1,y))>(d-1)*c(y+d,y)]
print("6.21 violations y<50 (참고):", viol2[:20], len(viol2))
# (6.22) 정확 검증 y=20, d=1..23 (d=y+3 보정 포함)
def Borf(n): return Fr(n**(n-1))  # e^{-n}/n! 인자는 비에서 지워짐: pi=Bor(a)Bor(b)/Bor(a+b) = a^{a-1}b^{b-1}(a+b)!/(a!b!(a+b)^{a+b-1}) * e^{0}
def pi(N,m): a=m;b=N+1-m; return Fr(a**(a-1)*b**(b-1)*comb(a+b,a), (a+b)**(a+b-1))
y=20; ok=True
for d in range(1,y+4):
    rhs=1-sum(pi(y+d-1,y+q) for q in range(1,d))+sum(pi(y+d-1,y+q)*Fr(y,y+q)*s(y+q-1,y) for q in range(1,d))
    if d==y+3:
        t=Fr(comb(2*y+2,y+1)*(y+1)**(2*y),2*p[2*y+2]); rhs+=t/(y+1)**2
    if rhs!=s(y+d-1,y): ok=False; print("6.22 mismatch d=",d)
print("6.22 exact ok (y=20, d=1..y+3):", ok)
