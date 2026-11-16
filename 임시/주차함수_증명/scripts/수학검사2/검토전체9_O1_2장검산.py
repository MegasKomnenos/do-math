# O1: 2장의 식들을 직접 센다 (brute force + 정확 유리수 급수).
import itertools, functools, math, random
from fractions import Fraction as Fr
from math import comb, factorial

def park(a):
    n=len(a); occ=[False]*(n+2); pos=[0]*n
    for i,ai in enumerate(a):
        q=ai
        while q<=n and occ[q]: q+=1
        if q>n: return None
        occ[q]=True; pos[i]=q
    return pos
def caps(sigma):  # sigma[i]=car at position i+1 ; returns h_1..h_n
    n=len(sigma); h=[]
    for i in range(n):
        z=0
        for j in range(i-1,-1,-1):
            if sigma[j]>sigma[i]: z=j+1; break
        h.append(i+1-z)
    return h
@functools.lru_cache(None)
def A(n,l):
    if n==0: return 1
    if l<0: return 0
    return sum(comb(n-1,m)*A(m,l)*A(n-1-m,l)*min(m+1,l+1) for m in range(n))
def p(n): return (n+1)**(n-1) if n>=1 else 1
def b(n,l): return A(n,l)-A(n,l-1)
def d(n,k): return b(n,k)-b(n,k-1)

# --- 2.2: n<=6 섬유 단봉, n=7 첫 반례 ---
def fiber_rows(n):
    rows={}
    for sigma in itertools.permutations(range(1,n+1)):
        h=caps(sigma)
        Al=[1]+[math.prod(min(hi,l+1) for hi in h) for l in range(n)]
        rows[sigma]=[Al[l+1]-Al[l] for l in range(n)]
    return rows
def unimodal(z):
    i=0
    while i+1<len(z) and z[i]<=z[i+1]: i+=1
    while i+1<len(z) and z[i]>=z[i+1]: i+=1
    return i==len(z)-1
for n in range(1,8):
    rows=fiber_rows(n); bad=[s for s,r in rows.items() if not unimodal(r)]
    print("n=",n,"섬유 수",len(rows),"비단봉 섬유 수",len(bad), bad[:3] if bad else "")
    assert sum(math.prod(caps(s)) for s in rows)==p(n)
print("sigma=(1,2,3,5,4,6,7) 행:", fiber_rows(7)[(1,2,3,5,4,6,7)])
s9=(3,4,5,7,6,8,9,2,1); h=caps(s9); Al=[1]+[math.prod(min(hi,l+1) for hi in h) for l in range(9)]
print("n=9 sigma' h=",h,"행=",[Al[l+1]-Al[l] for l in range(9)])

# --- 정리 2.28 d=2E-B, 따름 2.29, 보조 2.30 (brute n<=7) ---
def stats(n):
    E={}; E2={}; B={}
    for a in itertools.product(range(1,n+1),repeat=n):
        pos=park(a)
        if pos is None: continue
        disp=[pos[i]-a[i] for i in range(n)]; M=max(disp); cnt=disp.count(M)
        sigma=[0]*n
        for i in range(n): sigma[pos[i]-1]=i+1
        h=caps(sigma)
        if cnt%2==0: E[M]=E.get(M,0)+1
        if cnt==2: E2[M]=E2.get(M,0)+1
        blocked=all(h[pos[i]-1]==M+1 for i in range(n) if disp[i]==M)
        if blocked: B[M]=B.get(M,0)+1
    return E,E2,B
def Jn(n,k,z):
    tot=0
    for sigma in itertools.permutations(range(1,n+1)):
        h=caps(sigma); H=sum(1 for x in h if x==k); Z=sum(1 for x in h if x>k)
        if H==0: continue
        tot+=H*k**(H-1)*z**Z*math.prod(x for x in h if x<k)
    return tot
def Bform(n,k):
    tot=0
    for sigma in itertools.permutations(range(1,n+1)):
        h=caps(sigma); H=sum(1 for x in h if x==k); Z=sum(1 for x in h if x>k)
        tot+=math.prod(x for x in h if x<k)*(k-1)**Z*(k**H-(k-1)**H)
    return tot
for n in range(1,8):
    E,E2,B=stats(n)
    for k in range(1,n+1):
        assert d(n,k)==2*E.get(k,0)-B.get(k-1,0), (n,k)
        assert 2*E2.get(k,0)-B.get(k-1,0)<=d(n,k)
        assert B.get(k-1,0)==Bform(n,k), (n,k)
        J=Jn(n,k,k-1); assert B.get(k-1,0)<=J
        if n<=2*k-1: assert B.get(k-1,0)==J,(n,k)
        if n==2*k:
            Xi=comb(2*k-1,k-1)*p(k-1)**2
            assert J-B.get(k-1,0)==Xi,(n,k,J,B.get(k-1,0),Xi)
    assert B.get(0,0)==1
print("정리2.28/따름2.29/보조2.30(B식, B<=J, n<=2k-1 등식, n=2k Xi) n<=7 통과")

# --- 보조정리 J-egf: 재귀 (가) 와 EGF (나) ---
N=12
def series_mul(a,c2):
    c=[Fr(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j,y in enumerate(c2):
            if i+j>N: break
            c[i+j]+=x*y
    return c
def series_exp(a):
    assert a[0]==0
    r=[Fr(0)]*(N+1); r[0]=Fr(1)
    for m in range(1,N+1):
        r[m]=sum(Fr(i)*a[i]*r[m-i] for i in range(1,m+1))/m
    return r
T=[Fr(0)]+[Fr(t**(t-1),factorial(t)) for t in range(1,N+1)]
eT=series_exp(T)
assert all(eT[m]==Fr(p(m),factorial(m)) for m in range(N+1))
TT=series_mul(T,T)
Gr=[T[i]-TT[i]/2 for i in range(N+1)]
def integ(a): return [Fr(0)]+[a[i-1]/i for i in range(1,N+1)]
def Yseq(k,z):
    zGr=[z*g for g in Gr]; e1=series_exp(zGr); e2=series_exp([-g for g in zGr])
    mono=[Fr(0)]*(N+1); mono[k-1]=Fr(1,factorial(k-1))
    inner=integ(series_mul(e2,mono))
    Y=series_mul(series_mul(eT,e1),inner)
    return [p(k-1)*Y[m]*factorial(m) for m in range(N+1)]
for k in (2,3,4):
    top=min(2*k+1,8)
    for z in range(0,2*k+3):
        Y=Yseq(k,Fr(z))
        Jv=[Jn(m,k,z) for m in range(0,top+1)]
        for m in range(0,min(2*k,8)+1):
            assert Y[m]==Jv[m],(k,z,m,Y[m],Jv[m])
        if 2*k+1<=8:
            print(f"k={k} z={z}: J_(2k+1)={Jv[2*k+1]} Y_(2k+1)={Y[2*k+1]} 같음? {Y[2*k+1]==Jv[2*k+1]}")
        for m in range(0,min(2*k-1,7)+1):
            rhs=sum(comb(m,i)*(z+i+1)*p(i)*Jv[m-i] for i in range(m+1))+(comb(m,k-1)*p(k-1)*p(m-k+1) if m>=k-1 else 0)
            assert rhs==Jv[m+1],(k,z,m)
print("보조정리 J-egf (가)(나) k=2,3,4 통과")

# --- 정리 2.13 ---
def pi0(n,y):
    Ty=[Fr(0)]+[Fr(t**(t-1),factorial(t)) if t<=y else Fr(0) for t in range(1,N+1)]
    e=series_exp(Ty); return e[n]*factorial(n)
for l in range(0,4):
    for n in range(1,min(2*l+3,N)+1):
        rhs=pi0(n,l+1)+sum(comb(n,m)*(l+1)*A(m-1,l)*p(n-m) for m in range(l+2,n+1))
        assert rhs==A(n,l),(l,n)
print("정리 2.13 첫 식 통과")

# --- 정리 2.40 다섯 몫 분해 (PAIR는 명제 2.41의 정수 꼴) ---
def Ncal(l,t): return min(t,l+1)*A(t-1,l) if t>=1 else 0
def bT(t,l): return Ncal(l,t)-Ncal(l-1,t)
for k in (2,3,4,5):
    for n in range(2*k+1,3*k):
        Theta=comb(n,k)*k**(k-2)*A(n-k,k-1)
        FL=sum(comb(n,t)*(bT(t,k)-bT(t,k-1))*A(n-t,k-1) for t in range(k+1,2*k+2))
        BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
        KD=sum(comb(n,m+1)*p(n-1-m)*k*d(m,k) for m in range(2*k+1,n))
        PAIR=Fr(1,2)*sum(Fr(factorial(n),factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1,k)*bT(t2,k)+bT(t1,k-1)*bT(t2,k-1))*p(n-t1-t2) for t1 in range(1,n) for t2 in range(1,n-t1+1))
        assert -Theta+FL+BV+KD+PAIR==d(n,k),(k,n)
        assert b(k,k-1)==k**(k-2)
    print(f"k={k}: 다섯 몫 분해 n=2k+1..3k-1 통과")

# --- 정리 2.31 (SM),(DM0); 보조 2.34; 따름 ratio-e ---
def s(m,y): return Fr(A(m,y-1),p(m)) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p(m))
for m in range(0,25):
    for y in range(1,25):
        assert s(m+1,y)<=s(m,y) and s(m,y)<=s(m+1,y+1)
        assert Fr(A(m+1,y-1),factorial(m+1))<=Fr(A(m,y-1),factorial(m))*Fr(2718281829,10**9)
for Y in range(1,8):
    for K in range(Y+1,20):
        assert sum(c(m,Y) for m in range(Y+1,K+1))>=1-s(K,Y)
print("정리2.31, 보조2.34, ratio-e 수치 통과 (m,y<25)")

# --- 보조 2.14 섬유 부호식 ---
random.seed(1)
for _ in range(200):
    n=random.randint(2,9); sigma=list(range(1,n+1)); random.shuffle(sigma); h=caps(sigma)
    def Al(l): return math.prod(min(x,l+1) for x in h) if l>=0 else 0
    for k in range(1,n+1):
        Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        lhs=Fr(Al(k)-2*Al(k-1)+Al(k-2)); rhs=Al(k-1)*((1+Fr(1,k))**Z+(1-Fr(1,k))**(Z+H)-2)
        assert lhs==rhs
print("보조 2.14 통과")

# --- 2.9: x_t(k), theta, 정리 2.38 (ii)(iii)(iv), 따름 2.39(d) ---
def sT(t,y): return Fr(Ncal(y-1,t),t**(t-1))
def xt(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
def theta(t,k): return Fr(comb(t,k)*k**(k-1)*(t-k)**(t-k),t**(t-1)) if t>k else Fr(1)
def Ren(j): return (j**j)*math.exp(-j)/math.factorial(j) if j>=1 else 1.0
def Psi(q): return sum(Ren(j) for j in range(1,q+1))
for k in range(2,12):
    assert xt(k,k)==Fr(-1,k)
    for t in range(k,min(3*k,24)+1):
        assert k*xt(t,k)>=-theta(t,k),(k,t)
        if t<=2*k:
            q=t-k; assert float(k*xt(t,k))<=float(-theta(t,k))+(2*q*q+q)*math.cosh(q/k)/k+1e-12,(k,t)
    assert k*xt(k+1,k)==Fr(-(k-1)*k**(k-1),(k+1)**k)
    for q in range(0,min(k,12)+1):
        P=sum(xt(tp,k) for tp in range(k,k+q+1))
        assert float(k*P)>=-(1+q/k)**1.5*(1+Psi(q))-1e-12,(k,q)
        assert Ren(q)-1e-12<=float(theta(k+q,k))<=Ren(q)*(1+q/k)**1.5+1e-12
print("2.9 (x_t, theta, 2.38(ii)(iii)(iv), 2.39(d)) 통과")

# --- 2.12 이동 꼬리 ---
def Wn(n,g):
    tj=n+1-sum(g)
    num=factorial(n)*tj**(tj-1)*g[0]**(g[0]-1)*math.prod(gi**gi for gi in g[1:])
    den=factorial(tj)*factorial(g[0]-1)*math.prod(factorial(gi) for gi in g[1:])
    return Fr(num,den)
def nf(n,dd): return math.exp(dd)*math.prod(range(n-dd+1,n+1))*(n-dd)**(n-dd-2)/n**(n-2)
for n in range(5,41):
    for r in range(1,(n-1)//2+1):
        lhs=b(n,n-r-1)-b(n,n-r)
        Q1=comb(n,r)*(n-r)**(n-r-2)*(r+1)**r
        assert Q1==Wn(n,[r+1])/(n-r)
        Q2=Fr(0)
        for g1 in range(1,r+1):
            for g2 in range(1,r+2-g1):
                t1=n+1-g1; t2=t1-g2
                if g1+g2<=r: Q2+=2*Wn(n,[g1,g2])/(t1*t2)
                else: Q2+=(g2+1)*Wn(n,[g1,g2])/(t1*t2)
        assert Q1-Q2<=lhs<=Q1,(n,r)
        mid=float(Q1-lhs)/n**(n-2)
        assert -1e-9<=mid<=math.e*(5*r-1)/(4*n*(1-r/n)**4)+1e-9,(n,r,mid)
        assert abs(float(lhs)/n**(n-2)-math.e*Ren(r+1))<=60*(r+1)/n
        assert abs(Q1/n**(n-2)-nf(n,r)*math.e*Ren(r+1))<1e-9
        assert (n/(n-r))**2-1e-9<=nf(n,r)<=(n/(n-r))**3+1e-9
for n in range(57,63): assert b(n,n-2)>b(n,n-1)
first=[n for n in range(3,60) if b(n,n-2)>b(n,n-1)][:3]
print("이동 꼬리 (가)(나)(다)(라)(마)(사) n<=40 통과; (아) D=2 n=57..62 통과; b_(n,n-2)>b_(n,n-1)인 첫 n들:",first)
for r in range(1,30): assert math.e*Ren(r+1)<=1 and math.e*Ren(r+1)>=math.exp(-0.5)*r**-0.5>1/(2*math.sqrt(r+1))
print("(바) 통과")
