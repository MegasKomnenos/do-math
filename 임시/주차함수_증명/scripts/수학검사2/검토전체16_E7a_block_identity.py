# 7.4절 명제 block-exponential (7.6)(7.7), 보조정리 pair-terms의 값 공식·Neumann 전개, heavy-block(나)를
# k=3, 차수 <= 3k+2 에서 정확 검산 (절단 멱급수를 리스트로 직접 다룸; 계수는 z의 다항식)
import sympy as sp, itertools, math
z=sp.symbols('z'); k=3; N=3*k+2  # 차수 0..N
def cap(sig):
    h=[]
    for i in range(len(sig)):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)
    return h
def K_brute(n):
    tot=0
    for sig in itertools.permutations(range(1,n+1)):
        w=1; Z=0
        for hi in cap(sig):
            if hi<=k: w*=hi
            else: Z+=1
        tot+=w*z**Z
    return sp.expand(tot)
W=lambda g: g if g<=k else z
K=[sp.Integer(1)]
for n in range(1,N+1):
    K.append(sp.expand(sum(sp.binomial(n-1,j)*W(j+1)*K[j]*K[n-1-j] for j in range(n))))
for n in range(0,8): assert sp.expand(K[n]-K_brute(n))==0
print("K_n recursion = brute force, n<=7")
# 급수: 리스트 c[i] = x^i 계수
E=lambda c: [sp.expand(v) for v in c]
def mul(a,b): return E([sum(a[i]*b[n-i] for i in range(n+1)) for n in range(N+1)])
def add(a,b): return E([a[i]+b[i] for i in range(N+1)])
def sub(a,b): return E([a[i]-b[i] for i in range(N+1)])
def scal(s,a): return E([s*v for v in a])
def integ(a): return E([sp.Integer(0)]+[a[i-1]/i for i in range(1,N+1)])
def deriv(a): return E([(i+1)*a[i+1] for i in range(N)]+[sp.Integer(0)])
def expS(a):  # a[0]=0 ; f'=a' f
    assert a[0]==0
    f=[sp.Integer(1)]+[sp.Integer(0)]*N; da=deriv(a)
    for n in range(1,N+1):
        f[n]=sp.expand(sum(da[i]*f[n-1-i] for i in range(n))/n)
    return f
p=lambda m: sp.Integer((m+1)**(m-1))
D=[K[n]/sp.factorial(n) for n in range(N+1)]
Elt=[p(m)/sp.factorial(m) if m<k else sp.Integer(0) for m in range(N+1)]
T=[sp.Integer(0)]+[sp.Integer(t**(t-1))/sp.factorial(t) for t in range(1,N+1)]
Tle=[T[t] if 1<=t<=k else sp.Integer(0) for t in range(N+1)]; Tgt=sub(T,Tle)
Dge=sub(D,Elt)
rhs=expS(add(Tle,scal(z,integ(Dge))))
print("(7.6) mod x^%d:"%(N+1), all(v==0 for v in sub(D,rhs)))
eT=expS(T); Qk=mul(sub([sp.Integer(1)]+[0]*N,T),sub(eT,Elt))
S=[sp.Integer(0)]*(N+1)
for n in range(0,N):  # (n+1)S_{n+1} = Qk_n + z (eT*S)_n
    S[n+1]=sp.expand((Qk[n]+z*sum(eT[i]*S[n-i] for i in range(n+1)))/(n+1))
Gst=add(add(Elt,Qk),scal(z,mul(eT,S)))
X=sub(D,Gst)
low=min(i for i in range(N+1) if X[i]!=0); print("X lowest degree:",low,"(2k+2 =",2*k+2,")")
bd=sub(scal(z,integ(Dge)),Tgt)
lhs=mul(expS(Tle),add(scal(z,integ(X)),scal(sp.Rational(1,2),mul(bd,bd))))
print("(7.7) mod x^%d:"%(N+1), all(v==0 for v in sub(X,lhs)))
ok=all(sp.expand(sp.diff(K[n],z,2).subs(z,k)-sp.factorial(n)*sp.diff(Gst[n],z,2).subs(z,k))==0 for n in range(0,2*k+2))
print("K''_n(k)=POS^G_n for n<=2k+1:",ok)
A=lambda m: K[m].subs(z,k)
for t in range(k+1,N+1):
    bdt=sp.expand(bd[t]*sp.factorial(t)); ex=sp.Rational(t*p(t-1),A(t-1))-k
    Zf=sp.diff(K[t-1],z).subs(z,k)*k/A(t-1); Z2=sp.diff(K[t-1],z,2).subs(z,k)*k**2/A(t-1)
    assert sp.simplify(bdt.subs(z,k)+A(t-1)*ex)==0
    assert sp.simplify(sp.diff(bdt,z).subs(z,k)-A(t-1)*(1+Zf))==0
    assert sp.simplify(sp.diff(bdt,z,2).subs(z,k)-A(t-1)/k*(2*Zf+Z2))==0
print("bd_t(k), bd'_t(k), bd''_t(k) formulas verified, t<=",N)
eTle=expS(Tle); Neu=lambda f: mul(eTle,integ(f))
bdk=lambda d: E([sp.diff(v,z,d).subs(z,k) for v in bd])
Xpp=E([sp.diff(v,z,2).subs(z,k) for v in X])
acc=[sp.Integer(0)]*(N+1)
for j in range(0,N+1):
    Qj=add(add(scal(sp.Rational(j*(j-1),2*k**2),mul(bdk(0),bdk(0))),scal(sp.Rational(2*j,k),mul(bdk(0),bdk(1)))),add(mul(bdk(1),bdk(1)),mul(bdk(0),bdk(2))))
    f=mul(eTle,Qj)
    for _ in range(j): f=Neu(f)
    acc=add(acc,scal(k**j,f))
print("Neumann expansion of X''(k) mod x^%d:"%(N+1), all(v==0 for v in sub(acc,Xpp)))
for q in range(1,k+3):
    t=k+q; s=sp.Rational(A(t-1),p(t-1)); assert sp.simplify(sp.Rational(t*p(t-1),A(t-1))-k-(q+(k+q)*(1-s)/s))==0
print("heavy-block (nb) verified")
# X''_n(k) >= 0 for n<=3k+2 at k=3 (sanity) and sign of X''_n
print("X''_n(k) for n=2k+2..3k+2:",[Xpp[n]*sp.factorial(n) for n in range(2*k+2,N+1)])
