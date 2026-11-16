# K3 검산 3: 경계 응답 다항식·얼린 다항식·원천 표현·타일 모형의 소규모 대조 (n<=7)
import itertools, math
from fractions import Fraction as Fr
from math import comb, factorial
from decimal import Decimal, getcontext
def p(n): return (n+1)**(n-1) if n>=1 else 1
def Gamma(d,y,n):
    G=[Fr(1)]
    for dd in range(1,d+1):
        s=Fr(comb(n,dd)*p(dd))
        for j in range(0,dd):
            s+=y*comb(n-dd+j,j)*p(j)*G[dd-1-j]
        G.append(s)
    return G[d]
def caps(sigma):
    n=len(sigma); h=[0]*(n+1)
    for i in range(1,n+1):
        j=i-1
        while j>=1 and sigma[j-1]<sigma[i-1]: j-=1
        h[i]=i-j
    return h
def K(n,k,y):
    s=0
    for sg in itertools.permutations(range(1,n+1)):
        h=caps(sg); t=1
        for i in range(1,n+1):
            t*= h[i] if h[i]<=k else y
        s+=t
    return s
def Acount(n,l):
    s=0
    for sg in itertools.permutations(range(1,n+1)):
        h=caps(sg); t=1
        for i in range(1,n+1): t*=min(h[i],l+1)
        s+=t
    return s
def Bcount(n,k):  # B_{n,k-1} via old-2-30 first formula
    s=0
    for sg in itertools.permutations(range(1,n+1)):
        h=caps(sg); t=1; H=0; Z=0
        for i in range(1,n+1):
            if h[i]<k: t*=h[i]
            elif h[i]==k: H+=1
            else: Z+=1
        s+=t*(k-1)**Z*(k**H-(k-1)**H)
    return s
# phi^{[k]}_m : forests with all trees size<=k, via egf exp(sum_{t<=k} t^{t-1}x^t/t!)
def phi_list(k,N):
    tree=[Fr(0)]+[Fr(t**(t-1),factorial(t)) if t<=k else Fr(0) for t in range(1,N+1)]
    # exp of series
    F=[Fr(0)]*(N+1); F[0]=Fr(1)
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(1,n+1): s+=j*tree[j]*F[n-j]
        F[n]=s/n
    return [F[m]*factorial(m) for m in range(N+1)]
# brute-force E_{n,k} from check1 approach
def brute(n):
    b=[0]*n; E=[0]*(n+1); B=[0]*n
    for a in itertools.product(range(1,n+1), repeat=n):
        occ=[0]*(n+2); pos=[0]*n; ok=True
        for car,pref in enumerate(a):
            s=pref
            while s<=n and occ[s]: s+=1
            if s>n: ok=False;break
            occ[s]=car+1; pos[car]=s
        if not ok: continue
        disp=[pos[c]-a[c] for c in range(n)]
        M=max(disp); cnt=disp.count(M); b[M]+=1
        if cnt%2==0: E[M]+=1
        sigma=[occ[i] for i in range(1,n+1)]; h=caps(sigma)
        if all(h[pos[c]]==M+1 for c in range(n) if disp[c]==M): B[M]+=1
    return b,E,B
for n in range(2,8):
    b,E,B=brute(n)
    for k in range(1,n+1):
        # old-2-30 first formula
        assert Bcount(n,k)==B[k-1],(n,k)
        # K(k)=A_{n,k-1}, K(k+1)=A_{n,k}, K(k-1)=A_{n,k-2}+B_{n,k-1}
        Ak1=Acount(n,k-1); Ak=Acount(n,k); Ak2=Acount(n,k-2) if k>=2 else 0
        assert K(n,k,k)==Ak1 and K(n,k,k+1)==Ak and K(n,k,k-1)==Ak2+B[k-1],(n,k)
        if n<=2*k+1:
            phi=phi_list(k,n)
            assert all(x>=1 for x in phi)
            for y in [0,1,2,k-1,k,k+1,k+2,5]:
                rhs=phi[n]+y*sum(phi[m]*Gamma(n-m-1,y,n) for m in range(k,n))
                assert K(n,k,y)==rhs,(n,k,y,K(n,k,y),rhs)
            # 2E = second difference at k; c>=0
            sd=K(n,k,k+1)-2*K(n,k,k)+K(n,k,k-1)
            assert sd==2*E[k],(n,k,sd,E[k])
            c=K(n,k,k+2)-3*K(n,k,k+1)+3*K(n,k,k)-K(n,k,k-1); assert c>=0
            # Gamma^+ = K(k+2)-A_{n,k+1}
            if n>=k+1:
                assert p(k)*Gamma(n-k-1,k+2,n)==K(n,k,k+2)-Acount(n,k+1),(n,k)
        if k<=n<=2*k-1:
            assert p(k-1)*Gamma(n-k,k-1,n)==B[k-1],(n,k)
    print("n",n,"ok")
# inverse-renewal: Gamma_d(y;n) = (n)_d V_d(y/n,...,y/(n-d+1)); tile sum via recurrence
def tw(j): return Fr(1) if j==1 else Fr((j-1)**(j-1),factorial(j))
def V(co):
    d=len(co); Vs=[Fr(1)]
    for dd in range(1,d+1):
        s=(1+co[dd-1])*Vs[dd-1]
        for j in range(2,dd+1): s+=tw(j)*Vs[dd-j]
        Vs.append(s)
    return Vs[d]
for n in [5,9,12]:
    for d in range(0,n):
        for y in [Fr(1),Fr(3),Fr(7,2)]:
            co=[y/(n-i+1) for i in range(1,d+1)]
            ff=Fr(math.perm(n,d))
            assert Gamma(d,y,n)==ff*V(co),(n,d,y)
print("inverse-renewal ok")
# hb_d coefficients
import sympy
rho=sympy.symbols('rho')
def hb(d):
    Vs=[sympy.Integer(1)]
    for dd in range(1,d+1):
        s=(1+rho)*Vs[dd-1]+sum(sympy.Rational((j-1)**(j-1),factorial(j))*Vs[dd-j] for j in range(2,dd+1))
        Vs.append(sympy.expand(s))
    return Vs[d]
for d in range(1,9):
    P=sympy.Poly(hb(d),rho)
    for j in range(0,d+1):
        assert P.coeff_monomial(rho**j)==sympy.Rational((j+1)*(d+1)**(d-j-1),factorial(d-j)),(d,j)
    assert P.eval(1)==sympy.Rational((d+1)**d,factorial(d))
print("hb ok")
# Cayley inequality high precision near k=123704
getcontext().prec=50
for k in [123704,124034,10**6,10**7]:
    k=Decimal(k); cr=(1+1/k)**(k-2); rhs=Decimal(1).exp()*k*k/(k*k+Decimal('2.5')*k+2)
    print("k",k,"cr-rhs=",(cr-rhs))
