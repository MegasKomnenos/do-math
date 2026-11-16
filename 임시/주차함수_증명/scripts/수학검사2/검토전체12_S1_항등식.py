# 장2의 항등식들을 작은 n에서 전수 검산: 정리 2-28 (d=2E-B), 보조정리 2-30 (B 식, B<=J(k-1), Xi), 보조정리 J-egf (가)(나), 정리 2-40 (다섯 몫), 명제 2-41, 정리 2-13, 정리 moving-tail (가) Q1 닫힌꼴/(나)
from itertools import product, permutations
from math import comb, factorial
from fractions import Fraction
import sympy as sp
def park(a):
    n=len(a); occ=[False]*n; pos=[0]*n
    for i,ai in enumerate(a):
        p=ai-1
        while p<n and occ[p]: p+=1
        if p>=n: return None
        occ[p]=True; pos[i]=p+1
    return pos
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        z=0
        for j in range(i):
            if sig[j]>sig[i]: z=j+1
        h.append(i+1-z)
    return h
NMAX=7
PF={}
for n in range(1,NMAX+1):
    L=[]
    for a in product(range(1,n+1),repeat=n):
        pos=park(a)
        if pos is None: continue
        d=[pos[i]-a[i] for i in range(n)]
        M=max(d); Msh=d.count(M)
        sig=[0]*n
        for i in range(n): sig[pos[i]-1]=i+1
        h=caps(sig)
        blocked = all(h[pos[i]-1]==M+1 for i in range(n) if d[i]==M)
        L.append((M,Msh,blocked,tuple(sig)))
    PF[n]=L
def b(n,l): return sum(1 for x in PF[n] if x[0]==l) if n>=1 else (1 if l>=0 else 0)
def A(n,l): return sum(1 for x in PF[n] if x[0]<=l) if n>=1 else (1 if l>=0 else 0)
p=lambda n:(n+1)**(n-1) if n>=1 else 1
ok=True
# 정리 2-28, 따름정리 2-29
for n in range(1,NMAX+1):
    for k in range(1,n+1):
        d=b(n,k)-b(n,k-1)
        E=sum(1 for x in PF[n] if x[0]==k and x[1]%2==0)
        E2=sum(1 for x in PF[n] if x[0]==k and x[1]==2)
        B=sum(1 for x in PF[n] if x[0]==k-1 and x[2])
        if d!=2*E-B: ok=False; print('2-28 fail',n,k)
        if 2*E2-B>d: ok=False; print('2-29 fail',n,k)
        # 보조정리 2-30
        B2=0; J=0
        for sig in permutations(range(1,n+1)):
            h=caps(sig); Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
            pr=1
            for x in h:
                if x<k: pr*=x
            B2+=pr*(k-1)**Z*(k**H-(k-1)**H)
            J+=H*k**(H-1)*(k-1)**Z*pr if H>0 else 0
        if B2!=B: ok=False; print('2-30 B formula fail',n,k)
        if B>J: ok=False; print('2-30 B<=J fail',n,k)
        if n<=2*k-1 and B!=J: ok=False; print('2-30 equality fail',n,k)
        if n==2*k and J-B!=comb(2*k-1,k-1)*p(k-1)**2: ok=False; print('Xi fail',n,k)
print('2-28/2-29/2-30 checked up to n=',NMAX, ok)
# J-egf: J_n(z) 다항식 직접 vs (가) 재귀 vs (나) 생성함수, k=2,3
z,x=sp.symbols('z x')
def Jdirect(n,k):
    if n==0: return sp.Integer(0)
    tot=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); Z=sum(1 for v in h if v>k); H=sum(1 for v in h if v==k)
        pr=1
        for v in h:
            if v<k: pr*=v
        if H>0: tot+=H*k**(H-1)*z**Z*pr
    return sp.expand(tot)
for k in [2,3]:
    Js={n:Jdirect(n,k) for n in range(0,min(2*k+1,NMAX)+1)}
    for n in range(0,2*k):
        if n+1>NMAX: break
        rhs=sum(comb(n,i)*(z+i+1)*p(i)*Js[n-i] for i in range(n+1))+(comb(n,k-1)*p(k-1)*p(n-k+1) if n>=k-1 else 0)
        if sp.expand(rhs-Js[n+1])!=0: ok=False; print('J-egf (가) fail',k,n)
    # (나)
    N=min(2*k,NMAX)
    T=sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1,N+2))
    Gr=sp.expand(T-T**2/2)
    s=sp.symbols('s')
    inner=sp.integrate(sp.series(sp.exp(-z*Gr.subs(x,s)),s,0,N+1).removeO()*s**(k-1)/sp.factorial(k-1),(s,0,x))
    Y=sp.series(p(k-1)*sp.exp(T)*sp.exp(z*Gr)*inner,x,0,N+1).removeO()
    for n in range(0,N+1):
        coef=sp.expand(Y.coeff(x,n)*sp.factorial(n))
        if sp.expand(coef-Js[n])!=0: ok=False; print('J-egf (나) fail',k,n,coef,Js[n])
print('J-egf checked', ok)
# 정리 2-13 (첫 식) 숲 쪽: 쪼개짐 확률은 직접 계산 어려우므로 n<=2l+3에서 A_{n,l} = p_n pi0 + sum ... 을 pi0 = 1 - sum_{m>n/2} pi_n(m) 으로 확인 (m>l+1 >= n/2 범위에서만 큰 나무 가능하므로 pi0 = 1 - sum_{m=l+2}^n pi_n(m))
for l in range(0,4):
    for n in range(1,min(2*l+3,NMAX)+1):
        pi=lambda m: Fraction(comb(n,m)*m**(m-1)*p(n-m),p(n))
        pi0=1-sum(pi(m) for m in range(l+2,n+1))
        rhs=p(n)*pi0+sum(comb(n,m)*(l+1)*A(m-1,l)*p(n-m) for m in range(l+2,n+1))
        if rhs!=A(n,l): ok=False; print('2-13 fail',n,l)
print('2-13 checked', ok)
# 정리 2-40 다섯 몫: k=2,n=5; k=3,n=7,8  (NMAX=7 이므로 k=2,n=5 와 k=3,n=7)
def N_(l,t): return min(t,l+1)*A(t-1,l)
for k,n in [(2,5),(3,7)]:
    bT=lambda t,l: N_(l,t)-N_(l-1,t)
    delta=lambda t: bT(t,k)-bT(t,k-1)
    Theta=comb(n,k)*k**(k-2)*A(n-k,k-1)
    FL=sum(comb(n,t)*delta(t)*A(n-t,k-1) for t in range(k+1,2*k+2) if t<=n)
    BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
    KD=sum(comb(n,m+1)*p(n-1-m)*k*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
    PAIR=Fraction(1,2)*sum(Fraction(factorial(n),factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1,k)*bT(t2,k)+bT(t1,k-1)*bT(t2,k-1))*p(n-t1-t2) for t1 in range(1,n+1) for t2 in range(1,n+1-t1))
    d=b(n,k)-b(n,k-1)
    print('2-40', (k,n), 'd=',d, 'sum=', -Theta+FL+BV+KD+PAIR, 'Theta,FL,BV,KD,PAIR=',Theta,FL,BV,KD,PAIR)
# moving-tail (가) Q1 닫힌꼴 & 상하계, n<=7, r>=1, n>=2r+1
def Wn(g):
    j=len(g); t=[n+1-sum(g[:i+1]) for i in range(j)]
    num=factorial(n)*t[-1]**(t[-1]-1)*g[0]**(g[0]-1)
    for gi in g[1:]: num*=gi**gi
    den=factorial(t[-1])*factorial(g[0]-1)
    for gi in g[1:]: den*=factorial(gi)
    return Fraction(num,den), t
for n in range(3,NMAX+1):
    for r in range(1,(n-1)//2+1):
        Q1=comb(n,r)*(n-r)**(n-r-2)*(r+1)**r
        Q2=0
        for g1 in range(1,r+1):
            for g2 in range(1,r+2-g1):
                W,t=Wn((g1,g2))
                coef=2 if g1+g2<=r else (g2+1)
                Q2+=Fraction(coef)*W/(t[0]*t[1])
        lhs=b(n,n-r-1)-b(n,n-r)
        if not (Q1-Q2<=lhs<=Q1): ok=False; print('moving-tail fail',n,r,Q1,Q2,lhs)
        # 전체 교대합 = lhs 확인 (chain-expansion 라)
        tot=Fraction(0)
        def rec(prefix, remaining, j):
            global tot
            if prefix:
                W,t=Wn(tuple(prefix))
                f=lambda d: 1 if True else 0
                def prod(d):
                    v=Fraction(1)
                    for ti in t: v*=Fraction(max(d-(n+1-ti),0),ti)
                    return v
                tot+=(-1)**(j+1)*W*(prod(r+2)-2*prod(r+1)+prod(r))
            for g in range(1,remaining+1):
                rec(prefix+[g], remaining-g, j+1)
        rec([], r+1, 0)
        if tot!=lhs: ok=False; print('chain-expansion fail',n,r,tot,lhs)
print('moving-tail/chain-expansion checked', ok)
