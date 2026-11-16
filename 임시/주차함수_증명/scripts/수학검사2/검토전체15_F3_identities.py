# F3: brute-force checks of lemma green-connection (가)(다), theorem source-rep (가)(나)(다), corollary SR-implies-QR, Newton positivity (5-4) for small r
import itertools, math
from fractions import Fraction
import sympy as sp
y, x = sp.symbols('y x')

def p(m): return (m+1)**(m-1) if m>=1 else 1
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)
    return h
def K_poly(n,k):   # frozen capacity polynomial
    tot=0
    for sigma in itertools.permutations(range(1,n+1)):
        h=caps(sigma); pr=1; z=0
        for hi in h:
            if hi<=k: pr*=hi
            else: z+=1
        tot+=pr*y**z
    return sp.expand(tot)
def Gamma(d,n):   # boundary response polynomial, recurrence of 4.2
    G=[sp.Integer(1)]
    for dd in range(1,d+1):
        s=sp.binomial(n,dd)*p(dd)+y*sum(sp.binomial(n-dd+j,j)*p(j)*G[dd-1-j] for j in range(dd))
        G.append(sp.expand(s))
    return G[d]
# Green response via formal power series, order N
def green_resp(i,n):
    N=n+1
    T=sp.series(sp.LambertW(-x)*(-1), x, 0, N).removeO()   # tree function T(x) = -W(-x)
    T=sp.expand(T)
    Gr=sp.expand(T-T**2/2)
    integrand=sp.expand(sp.series(sp.exp(-y*Gr),x,0,N).removeO()*x**i/sp.factorial(i))
    integ=sp.integrate(integrand,x)
    pre=sp.series(sp.exp(T)*sp.exp(y*Gr),x,0,N).removeO()
    prod=sp.expand(pre*integ)
    return sp.expand(sp.factorial(n)*prod.coeff(x,n))
print("== green-connection (가): Gamma_d(y;n) == G_{y,n-d-1,n} ==")
ok=True
for n in range(1,6):
    for d in range(0,n):
        g1=Gamma(d,n); g2=green_resp(n-d-1,n)
        if sp.expand(g1-g2)!=0: ok=False; print("MISMATCH",n,d,g1,g2)
print("ok:",ok)
print("== green-connection (다): K_{n,k}-K_{n,k+1} = (y-k-1) p_k Gamma_{n-k-1}(y;n), k+1<=n<=2k+1, n<=7 ==")
ok=True
Kcache={}
def K(n,k):
    if (n,k) not in Kcache: Kcache[(n,k)]=K_poly(n,k)
    return Kcache[(n,k)]
for n in range(2,8):
    for k in range(1,n):
        if k+1<=n<=2*k+1:
            lhs=sp.expand(K(n,k)-K(n,k+1)); rhs=sp.expand((y-k-1)*p(k)*Gamma(n-k-1,n))
            if sp.expand(lhs-rhs)!=0: ok=False; print("MISMATCH",n,k)
print("ok:",ok)
# A_{n,l} brute force via parking functions; B_{n,l}, E_{n,k}, E2
def pf_stats(n):
    A={}; B={}; E={}; E2={}
    for a in itertools.product(range(1,n+1),repeat=n):
        occ=[0]*(n+2); disp=[]; okpf=True
        for car in range(n):
            s=a[car]
            while s<=n and occ[s]: s+=1
            if s>n: okpf=False; break
            occ[s]=car+1; disp.append(s-a[car])
        if not okpf: continue
        M=max(disp); cnt=disp.count(M)
        A[M]=A.get(M,0)+1
        if cnt%2==0: E[M]=E.get(M,0)+1
        if cnt==2: E2[M]=E2.get(M,0)+1
        # blocked: all cars with disp==M stand at position i with h_i = M+1
        sigma=[occ[i] for i in range(1,n+1)]; h=caps(sigma)
        blocked=all(h[s-1]==M+1 for car in range(n) for s in [a[car]+disp[car]] if disp[car]==M)
        if blocked: B[M]=B.get(M,0)+1
    b=[A.get(l,0) for l in range(n)]
    return b,B,E,E2
print("== source-rep (가)(나)(다), SR-implies-QR, Gamma^- = B_{n,k-1}: n<=7 ==")
ok=True
for n in range(2,8):
    b,B,E,E2=pf_stats(n)
    Acum=[sum(b[:l+1]) for l in range(n)]
    def Aof(l): return 0 if l<0 else (Acum[l] if l<n else Acum[-1])
    for k in range(1,n):
        if n>2*k+1: continue
        Kn=K(n,k)
        # phi_m = K_{m,k}(0)
        phi=[K(m,k).subs(y,0) if m>=1 else 1 for m in range(n+1)]
        rhs=phi[n]+y*sum(phi[m]*Gamma(n-m-1,n) for m in range(k,n))
        if sp.expand(Kn-rhs)!=0: ok=False; print("(가) MISMATCH",n,k)
        # (나)
        def hg(d,yy): return yy*Gamma(d,n).subs(y,yy)
        def sd(d,yy): return hg(d,yy+1)-2*hg(d,yy)+hg(d,yy-1)
        Ek=E.get(k,0)
        lhs1=sum(phi[m]*sd(n-m-1,k) for m in range(k,n))
        if lhs1!=2*Ek: ok=False; print("(나) 2E mismatch",n,k,lhs1,2*Ek)
        c=Kn.subs(y,k+2)-3*Kn.subs(y,k+1)+3*Kn.subs(y,k)-Kn.subs(y,k-1)
        lhs2=sum(phi[m]*sd(n-m-1,k+1) for m in range(k,n))
        if lhs2!=2*Ek+c: ok=False; print("(나) second mismatch",n,k)
        if c<0: ok=False; print("c<0",n,k)
        # Gamma^- = B_{n,k-1} for k<=n<=2k-1 ; Gamma^+ = K(k+2)-A_{n,k+1} for k+1<=n<=2k+1
        r=n-k
        Gm=p(k-1)*Gamma(r,n).subs(y,k-1); Gp=p(k)*Gamma(r-1,n).subs(y,k+2) if r>=1 else None
        if k<=n<=2*k-1 and Gm!=B.get(k-1,0): ok=False; print("Gamma^- != B",n,k,Gm,B.get(k-1,0))
        if k<=n<=2*k-1 and Gm!=Kn.subs(y,k-1)-Aof(k-2): ok=False; print("Gamma^- != K(k-1)-A",n,k)
        if r>=1 and Gp!=Kn.subs(y,k+2)-Aof(k+1): ok=False; print("Gamma^+ mismatch",n,k)
        # (다)
        if k+2<=n<=2*k-1:
            d1=Aof(k)-2*Aof(k-1)+Aof(k-2); d2=Aof(k+1)-2*Aof(k)+Aof(k-1)
            if d1!=2*Ek-Gm or d2!=2*Ek+c-Gp: ok=False; print("(다) d mismatch",n,k)
            S=Gp*d1-Gm*d2
            S2=sum(phi[n-d-1]*(Gp*sd(d,k)-Gm*sd(d,k+1)) for d in range(1,r))
            if S!=S2: ok=False; print("(다) S mismatch",n,k,S,S2)
            # SR-implies-QR check on data: if S>=0 and b[k-1]>b[k] then concavity & logconcavity
            if S>=0 and b[k-1]>b[k]:
                if not (b[k-1]-2*b[k]+b[k+1]<=0 and b[k]**2>=b[k-1]*b[k+1]): ok=False; print("SR->QR fail",n,k)
        # 2-28 identity
        if b[k]-b[k-1]!=2*Ek-B.get(k-1,0): ok=False; print("2-28 mismatch",n,k)
print("ok:",ok)
# Newton forward-difference positivity (Thm 5-4 method) for 2<=r<=12
print("== Newton Nw_{r,d} positivity for r<=12 ==")
e15=sum(Fraction(1,math.factorial(j)) for j in range(16)); F15=math.factorial(15)
def GammaNum(d,yv,nv):  # exact Fraction value
    G=[Fraction(1)]
    for dd in range(1,d+1):
        G.append(Fraction(math.comb(nv,dd)*p(dd))+yv*sum(math.comb(nv-dd+j,j)*p(j)*G[dd-1-j] for j in range(dd)))
    return G[d]
ok=True
for r in range(2,13):
    for d in range(1,r):
        def Nw(nv):
            k=r+1+nv; n=k+r
            hg=lambda yv: yv*GammaNum(d,yv,n)
            sd=lambda yv: hg(yv+1)-2*hg(yv)+hg(yv-1)
            return F15*(2*e15*k*k*(k+1)*GammaNum(r-1,k+2,n)*sd(k)-(2*k*k+5*k+4)*GammaNum(r,k-1,n)*sd(k+1))
        vals=[Nw(j) for j in range(2*r+3)]
        if any(v.denominator!=1 for v in vals): ok=False; print("non-integer",r,d)
        # forward differences
        diffs=[]
        cur=vals[:]
        for i in range(2*r+3):
            diffs.append(cur[0]); cur=[cur[j+1]-cur[j] for j in range(len(cur)-1)]
        if not (diffs[0]>0 and all(dd>=0 for dd in diffs[1:])): ok=False; print("Newton fail",r,d,diffs[:3])
print("ok:",ok)
