# 검토 23차 R1: 2.9–2.12절의 부등식·항등식 수치 확인
import sys, math, itertools
from fractions import Fraction as Fr
from math import comb, factorial
sys.stdout.reconfigure(encoding='utf-8')
def p(n): return 1 if n==0 else (n+1)**(n-1)
N=70
A=[[0]*(N+3) for _ in range(N+1)]
for l in range(N+3): A[0][l]=1
for n in range(1,N+1):
    for l in range(N+3):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def b(n,l): return 0 if l<0 else A[n][l]-(A[n][l-1] if l>=1 else 0)
def s(m,y): return Fr(A[m][y-1],p(m)) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p(m))
def BorR(m): return Fr(m**(m-1),factorial(m))   # e^{-m} 생략(유리수 부분)
def RenR(j): return Fr(j**j,factorial(j)) if j>0 else Fr(1)
def Bor(m): return math.exp(-m+ (m-1)*math.log(m)-math.lgamma(m+1))
def Ren(j): return 1.0 if j==0 else j*Bor(j)
def theta(t,k): return Fr(comb(t,k)*k**(k-1)*(t-k)**(t-k),t**(t-1))
def sT(t,y): return Fr(min(t,y)*A[t-1][y-1],t**(t-1)) if y>=1 else Fr(0)
# 2:old-2-38
for k in range(2,25):
    for t in range(k,N):
        x=sT(t,k+1)-2*sT(t,k)+sT(t,k-1)
        assert k*x>=-theta(t,k),(k,t)
        if t>=k+1: assert x==Fr(1,t)*((k+1)*c(t-1,k)-(k-1)*c(t-1,k-1))
        if t==k: assert x==Fr(-1,k)
# supersolution (나): s_{y+q-1}(y) <= phi_1(q)
for y in range(2,30):
    for q in range(1,y+3):
        if y+q-1>N: continue
        phi1=1-sum(Bor(j)*(q-j)/(y+q-j) for j in range(1,q))
        assert float(s(y+q-1,y))<=phi1+1e-12,(y,q)
# 2:old-2-37 (가)(다)
Psi=lambda q: sum(Ren(j) for j in range(1,q+1))
for j in range(1,60):
    assert abs(Ren(j)-(Bor(j)+sum(Bor(m)*Ren(j-m) for m in range(1,j))))<1e-12
for q in range(1,60):
    assert abs(sum(Bor(m)*Psi(q-m) for m in range(1,q+1))-(Psi(q)-sum(Bor(m) for m in range(1,q+1))))<1e-12
# borel arithmetic (ㄷ), power-sum-renewal
z12=-1.4603545088095868; zm12=-0.20788622497735457; z32=2.6123753486854883
cPsi=-z12+z32/12
assert 1.5<cPsi<1.6781
tail=lambda q: 1-sum(Bor(m) for m in range(1,q+1))
for q in range(1,3000):
    S1=sum(j**-0.5 for j in range(1,q+1)) if q<400 else None
    if q<400:
        assert 2*q**0.5+z12+0.5*q**-0.5-q**-1.5/24<=S1+1e-12<=2*q**0.5+z12+0.5*q**-0.5+2e-12
        S2=sum(j**0.5 for j in range(1,q+1))
        assert (2/3)*q**1.5+0.5*q**0.5+zm12<=S2+1e-9 and S2<=(2/3)*q**1.5+0.5*q**0.5+zm12+q**-0.5/24+1e-9
        P=Psi(q)
        assert P<=(2*math.sqrt(q)-1)/math.sqrt(2*math.pi)
        low=(2*math.sqrt(q)-cPsi+0.5/math.sqrt(q)-q**-1.5/24)/math.sqrt(2*math.pi)
        assert P>=low,(q,P,low)
        t=tail(q)
        assert 2/math.sqrt(2*math.pi)*math.exp(-1/(12*(q+1)))*(q+1)**-0.5<=t+1e-13<=2/math.sqrt(2*math.pi)*(q+0.5)**-0.5+1e-13
# union-bound-closed
for n in range(2,N+1):
    for y in range(1,n):
        q=n-y
        lhs=float(1-s(n,y))
        mid=((n+1)/(y+1))**1.5/(y+1)*sum(Psi(i) for i in range(1,q+1))
        rhs=(2*math.pi)**-0.5*((n+1)/(y+1))**1.5/(y+1)*(4/3*q**1.5+math.sqrt(q)-q-1/3)
        assert lhs<=mid+1e-12<=rhs+1e-11,(n,y)
# level-mass chain repr / capacity shift ratio
for m in range(0,40):
    for y in range(1,30):
        for y2 in range(y,30):
            pr=Fr(1)
            for i in range(1,m+1): pr*=Fr(min(i,y),min(i,y2))
            assert s(m,y)>=pr*s(m,y2)
# heavy chain visit probability (2:old-2-45) via exact DP on S-chain: Pr(chain passes q)=tilt*Ren(q0-q)
def pi_(n,m): return Fr(comb(n,m)*m**(m-1)*p(n-m),p(n))
for y in range(2,9):
    for n in range(y+1,2*y+2):
        q0=n+1-y
        # visit prob by DP over excess
        vis={q0:Fr(1)}
        for q in range(q0,0,-1):
            if q not in vis: continue
            nn=y+q-1
            for q2 in range(1,q):
                vis[q2]=vis.get(q2,0)+vis[q]*pi_(nn,y+q2)
        for q in range(1,q0):
            # tilt*Ren = Bor(y+q)/Bor(y+q0)*Ren(q0-q): e-지수 -(y+q)+(y+q0)-(q0-q)=0
            assert vis[q]==BorR(y+q)/BorR(y+q0)*RenR(q0-q),(y,n,q)
# moving tail (다)(마)(바) and chain-normalization (다)
def nf(n,d): return math.exp(d)*math.factorial(n)/math.factorial(n-d)*(n-d)**(n-d-2)/n**(n-2)
for n in range(2,60):
    for d in range(0,n):
        v=nf(n,d)
        assert (n/(n-d))**2*(1-1e-12)<=v<=(n/(n-d))**2.5*(1+1e-12)
for n in range(3,N+1):
    for r in range(1,(n-1)//2+1):
        eren=math.e*Ren(r+1)
        val=nf(n,r)*eren+(b(n,n-r)-b(n,n-r-1))/n**(n-2)
        assert -1e-12<=val<=math.e*(5*r-1)/(4*n*(1-r/n)**4)+1e-12,(n,r,val)
        assert eren<=1+1e-12 and eren>=math.exp(-0.5)*r**-0.5
# chain-normalization (다): Delta^iota[p_n-A_{n,n-d}] = sum_j (-1)^{j+1} sum_gamma Wcal(gamma) Delta^iota[prod (d-G_i)_+/t_i]
def compositions(total_max,j):
    # all (g1..gj)>=1 with sum<=total_max
    if j==0:
        yield (); return
    for g in range(1,total_max-(j-1)+1):
        for rest in compositions(total_max-g,j-1):
            yield (g,)+rest
def Wcal(n,gam):
    tj=n+1-sum(gam)
    v=Fr(p(n))*BorR(tj)/BorR(n+1)
    for g in gam: v*=RenR(g)
    return v
def delta(f,r,iota): return sum((-1)**(iota-i)*comb(iota,i)*f(r+i) for i in range(iota+1))
cnt=0
for n in range(3,15):
    for iota in range(0,4):
        for r in range(1,n):
            if n<max(2*r+1,2*r+2*iota-3): continue
            if r+iota>n: continue
            lhs=delta(lambda d: p(n)-A[n][n-d] if n-d>=0 else p(n), r, iota)
            rhs=Fr(0)
            for j in range(1,r+iota):
                for gam in compositions(r+iota-1,j):
                    G=list(itertools.accumulate(gam)); ts=[n+1-g for g in G]
                    def f(d):
                        v=Fr(1)
                        for g,t in zip(G,ts): v*=Fr(max(d-g,0),t)
                        return v
                    rhs+=(-1)**(j+1)*Wcal(n,gam)*delta(f,r,iota)
            assert lhs==rhs,(n,iota,r,lhs,rhs); cnt+=1
print('chain-normalization(다) cases',cnt)
# nf-log (가) coefficients & (나)
for n in range(5,40):
    for d in range(0,n-1):
        term=lambda i: ((d/n)**i*d/(i+1)+2*(d/n)**i-sum((rho/n)**i for rho in range(d)))/i
        ser=sum(term(i) for i in range(1,400))
        if d/n<0.8: assert abs(ser-math.log(nf(n,d)))<1e-8,(n,d,ser,math.log(nf(n,d)))
        for d2 in range(0,n-d):
            assert abs(nf(n,d+d2)-nf(n,d)*nf(n-d,d2))<1e-9*nf(n,d+d2)
print('misc ok')
