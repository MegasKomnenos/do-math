# F6: brute-force checks of chapter 7A statements on small n,k
import itertools, math
from fractions import Fraction as Fr

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)  # i-h = j  (0-based: position i+1, nearest larger at j+1 or 0)
    return h

def A_sigma(h,l):  # number with M<=l
    p=1
    for x in h: p*=min(x,l+1)
    return p

def A(n,l):
    if n==0: return 1
    if l<0: return 0
    return sum(A_sigma(caps(s),l) for s in itertools.permutations(range(1,n+1)))

def b(n,l): return A(n,l)-A(n,l-1)
def d(n,k): return A(n,k)-2*A(n,k-1)+A(n,k-2)

# brute force parking functions for small n
def pf_all(n):
    res=[]
    for a in itertools.product(range(1,n+1),repeat=n):
        s=sorted(a)
        if all(s[i]<=i+1 for i in range(n)): res.append(a)
    return res
def park(a):
    n=len(a); spot=[0]*n; pos=[0]*n
    for car,pref in enumerate(a,1):
        p=pref
        while spot[p-1]: p+=1
        spot[p-1]=car; pos[car-1]=p
    return spot,pos

print("== check A_{n,l} via sigma formula vs direct PF count, n<=6")
for n in range(1,7):
    pfs=pf_all(n)
    for l in range(0,n):
        cnt=sum(1 for a in pfs if max(park(a)[1][i]-a[i] for i in range(n))<=l)
        assert cnt==A(n,l),(n,l,cnt,A(n,l))
print("ok")

print("== Theorem old-6-2 mu_n(k)=E[v_k], Prop old-6-5 Conv-Kink, old-6-6 E[Z_k]>=(n-k)/(k+1), factorial moment, old-6-10 E[kH]<=x_k n")
for n in range(1,9):
    perms=list(itertools.permutations(range(1,n+1)))
    H=[caps(s) for s in perms]
    for k in range(2,n+1):
        Ank1=sum(A_sigma(h,k-1) for h in H)
        EZ=Fr(sum(A_sigma(h,k-1)*sum(1 for x in h if x>k) for h in H),Ank1)
        EZZ=Fr(sum(A_sigma(h,k-1)*(lambda Z:Z*(Z-1))(sum(1 for x in h if x>k)) for h in H),Ank1)
        EH=Fr(sum(A_sigma(h,k-1)*sum(1 for x in h if x==k) for h in H),Ank1)
        Ev=Fr(0)
        for h in H:
            Z=sum(1 for x in h if x>k); Hh=sum(1 for x in h if x==k)
            Ev+=Fr(A_sigma(h,k-1),Ank1)*((Fr(k+1,k))**Z+(Fr(k-1,k))**(Z+Hh)-2)
        mu=Fr(d(n,k),Ank1)
        assert mu==Ev,(n,k)
        # Kink
        Kink=Fr(Ank1*EH,k)
        Conv=d(n,k)+Kink
        assert Conv>=0
        # conv via second derivative integral: compute polynomials
        # check old-6-6
        m=Fr(n-k,k+1)
        assert EZ>=m,(n,k,EZ,m)
        if n>=2*k+1: assert EZZ>=m*(m-1),(n,k)
        xk=Fr(k,k+1)**(k-1)
        assert k*EH<=xk*n,(n,k,k*EH,xk*n)
        if n==k: assert k*EH==xk*n
        # Prop old-6-7
        Rs=Fr(A(n,k),Ank1); Rf=Fr(A(n,k-2),Ank1)
        ok=math.log(1-1/k); os_=math.log(1+1/k); o=-2*ok/os_
        assert float(Rf)>(1-1/k)*float(Rs)**(-o)-1e-12,(n,k)
print("ok")

print("== prime PF count C_{n,n}=(n-1)^{n-1} and A_{k-1}=1/(1-C_k) small n")
def boundary_pts(a):
    n=len(a); return [bt for bt in range(1,n+1) if sum(1 for x in a if x<=bt)==bt]
for n in range(1,7):
    pfs=pf_all(n)
    primes=[a for a in pfs if boundary_pts(a)==[n]]
    assert len(primes)==(n-1)**(n-1),(n,len(primes))
print("ok")
# C_{n,k} and identity A_{n,k-1} = sum over compositions
def C(n,k):
    return sum(1 for a in pf_all(n) if boundary_pts(a)==[n] and max(park(a)[1][i]-a[i] for i in range(n))<=k-1)
for k in range(1,5):
    Cs={n:C(n,k) for n in range(1,7)}
    for n in range(1,7):
        # A_{n,k-1} via EGF 1/(1-C_k): a_n = sum_{j=1}^n C(n,j) a_{n-j} with binomials
        pass
    an={0:Fr(1)}
    for n in range(1,7):
        an[n]=sum(Fr(Cs[j],math.factorial(j))*an[n-j] for j in range(1,n+1))
        assert an[n]*math.factorial(n)==A(n,k-1),(n,k)
print("ok")

print("== Theorem old-6-11(가): E[H_k] formula via kernel K for small n,k")
# a_m = A_{m,k-1}/m!, K coefficients from j K_j = sum_{m=1}^{k-1}(k-m) a°_{m-1} K_{j-m} + [j=k+1]
for k in range(2,5):
    N=8
    a={m:Fr(A(m,k-1),math.factorial(m)) for m in range(0,N+2)}
    ao={m:Fr((m+1)**(m-1),math.factorial(m)) if m>0 else Fr(1) for m in range(0,N+2)}
    K={j:Fr(0) for j in range(0,N+3)}
    for j in range(1,N+3):
        s=Fr(1 if j==k+1 else 0)
        for m in range(1,k):
            if j-m>=0: s+=(k-m)*ao[m-1]*K[j-m]
        K[j]=s/j
    assert K[k+1]==Fr(1,k+1)
    for n in range(1,N+1):
        perms=list(itertools.permutations(range(1,n+1))); H=[caps(s) for s in perms]
        Ank1=sum(A_sigma(h,k-1) for h in H)
        EH=Fr(sum(A_sigma(h,k-1)*sum(1 for x in h if x==k) for h in H),Ank1)
        rhs=(n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1,n+2))/a[n]
        assert EH==rhs,(n,k,EH,rhs)
print("ok")

print("== Riccati counterexample (k,z,n)=(3,1,2): LHS 4 vs RHS 5")
# RHS = A_{k-1} O_z + k Ex/(Delta)^2 int O_z Ex ; truncated series arithmetic
def series_mul(p,q,N): 
    r=[Fr(0)]*(N+1)
    for i,x in enumerate(p):
        for j,y in enumerate(q):
            if i+j<=N: r[i+j]+=x*y
    return r
def series_exp(p,N):  # p[0]=0
    r=[Fr(0)]*(N+1); r[0]=Fr(1)
    # r' = p' r
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(1,n+1): s+=j*p[j]*r[n-j]
        r[n]=s/n
    return r
k,z,N=3,1,4
Q=[Fr(0)]*(N+1)
for j in range(0,k-1): Q[j+1]+=Fr((k-1-j)*((j+1)**(j-1) if j>0 else 1),math.factorial(j+1))
Ex=series_exp([-x for x in Q],N)
integ=[Fr(0)]+[Ex[i]/(i+1) for i in range(N)]
Delta=[Fr(1)]+[-k*x for x in integ[1:]]
# inverse of Delta
inv=[Fr(0)]*(N+1); inv[0]=Fr(1)
for n in range(1,N+1): inv[n]=-sum(Delta[j]*inv[n-j] for j in range(1,n+1))
Ak1=series_mul(Ex,inv,N)
assert [Ak1[n]*math.factorial(n) for n in range(0,4)]==[A(n,k-1) for n in range(0,4)]
az=Fr(A(z-1,k-1),math.factorial(z-1))
O=[Fr(0)]*(N+1); O[z]=Fr(min(z,k))*az/z
term1=series_mul(Ak1,O,N)
OEx=series_mul(O,Ex,N); intOEx=[Fr(0)]+[OEx[i]/(i+1) for i in range(N)]
term2=series_mul(series_mul([k*x for x in Ex],series_mul(inv,inv,N),N),intOEx,N)
rhs=[term1[i]+term2[i] for i in range(N+1)]
n=2
perms=list(itertools.permutations(range(1,n+1))); H=[caps(s) for s in perms]
lhs=sum(A_sigma(h,k-1)*sum(1 for x in h if x==z) for h in H)
print("LHS",lhs,"RHS*n!",rhs[n]*math.factorial(n))

print("== k=1: b_{n,1} vs n! and the lower bound (n-1)n!/2")
for n in range(2,8):
    print(n, b(n,1), math.factorial(n), (n-1)*math.factorial(n)//2, b(n,1)>math.factorial(n))
