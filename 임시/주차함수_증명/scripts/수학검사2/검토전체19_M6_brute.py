# M6 brute-force checks for chapter 7A (small n,k) and constants
from fractions import Fraction as Fr
from itertools import permutations, product
from math import factorial, comb, log, exp
import sys

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)
    return h

def A(n,l):  # A_{n,l}: max displacement <= l ; via sigma-sum, l>=-1
    if l<0: return 0
    if n==0: return 1
    s=0
    for sg in permutations(range(1,n+1)):
        p=1
        for hi in caps(sg): p*=min(hi,l+1)
        s+=p
    return s

out=[]
# 1. Theorem old-6-6: E[Z_k] >= (n-k)/(k+1) under Pr^sigma_{n,k}; factorial moment; Theorem old-6-10 equality at n=k
for n in range(1,8):
    for k in range(2,n+1):
        tot=0; EZ=0; EZZ=0; EH=0
        for sg in permutations(range(1,n+1)):
            h=caps(sg); w=1
            for hi in h: w*=min(hi,k)
            Z=sum(1 for hi in h if hi>k); H=sum(1 for hi in h if hi==k)
            tot+=w; EZ+=w*Z; EZZ+=w*Z*(Z-1); EH+=w*H
        EZ=Fr(EZ,tot); EZZ=Fr(EZZ,tot); EH=Fr(EH,tot)
        m=Fr(n-k,k+1)
        ok1 = EZ>=m
        ok2 = (EZZ>=m*(m-1)) if m>=1 else True
        xk=Fr(k,k+1)**(k-1)
        ok3 = k*EH<=xk*n
        ok4 = (k*EH==xk*n) if n==k else True
        if not(ok1 and ok2 and ok3 and ok4): out.append(("FAIL 6-6/fm/6-10",n,k,EZ,m,EZZ,k*EH,xk*n))
out.append("checked 6-6, factorial-moment, 6-10 for n<=7")

# 2. Prop old-6-7: R_flat > x_flat * R_sharp^{-o_k}
for n in range(0,8):
    for k in range(2,9):
        Ak=A(n,k); Ak1=A(n,k-1); Ak2=A(n,k-2)
        Rs=Ak/Ak1; Rf=Ak2/Ak1
        xs=1+1/k; xf=1-1/k; ok=-2*log(xf)/log(xs)
        if not Rf > xf*Rs**(-ok): out.append(("FAIL 6-7",n,k,Rf,xf*Rs**(-ok)))
out.append("checked 6-7 n<=7,k<=8")

# 3. t_k and n_sharp for small k
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1)>=2*k**(2*j+1)): j+=1
    return j
out.append(("t_k k=2..10",[tk(k) for k in range(2,11)],"n_sharp",[k+(k+1)*tk(k) for k in range(2,11)]))

# 4. Riccati counterexample (k,z,n)=(3,1,2): LHS n! coefficient of Y_z = sum_sigma w*H_z
k=3;z=1;n=2
lhs=0
for sg in permutations(range(1,n+1)):
    h=caps(sg); w=1
    for hi in h: w*=min(hi,k)
    lhs+=w*sum(1 for hi in h if hi==z)
# RHS: A_{k-1} O_z + k Ex/(Delta)^2 int O_z Ex ; series to x^2
# p_j=(j+1)^{j-1}; Q_{k-1}(x)=sum_{j=0}^{k-2}(k-1-j)p_j x^{j+1}/(j+1)!
N=6
def mul(a,b):
    c=[Fr(0)]*N
    for i in range(N):
        for j in range(N-i): c[i+j]+=a[i]*b[j]
    return c
def expser(a):
    # a[0]=0
    r=[Fr(0)]*N; r[0]=Fr(1); term=[Fr(0)]*N; term[0]=Fr(1)
    for i in range(1,N):
        term=mul(term,a); term=[t/ i for t in term]
        r=[r[j]+term[j] for j in range(N)]
    return r
def integ(a):
    r=[Fr(0)]*N
    for i in range(N-1): r[i+1]=a[i]/(i+1)
    return r
def inv(a):
    r=[Fr(0)]*N; r[0]=1/a[0]
    for i in range(1,N):
        s=sum(a[j]*r[i-j] for j in range(1,i+1)); r[i]=-s/a[0]
    return r
p=lambda j:(j+1)**(j-1) if j>0 else 1
Q=[Fr(0)]*N
for j in range(0,k-1): Q[j+1]+=Fr((k-1-j)*p(j),factorial(j+1))
Ex=expser([-q for q in Q]); Delta=[Fr(1)]+[Fr(0)]*(N-1)
I=integ(Ex); Delta=[Delta[i]-k*I[i] for i in range(N)]
Ak1=mul(Ex,inv(Delta))
# a_{z-1}=A_{z-1,k-1}/(z-1)!
az1=Fr(A(z-1,k-1),factorial(z-1))
O=[Fr(0)]*N; O[z]=Fr(min(z,k))*az1/z
rhs=mul(Ak1,O)
t=mul(inv(mul(Delta,Delta)),mul(Ex,integ(mul(O,Ex))))
rhs=[rhs[i]+k*t[i] for i in range(N)]
out.append(("riccati (3,1,2) LHS",lhs,"RHS n!*coef",rhs[n]*factorial(n)))
# check Riccati identity holds for z>=k-1 small cases
bad=[]
for k in (2,3,4):
    for z in range(k-1,5):
        Q=[Fr(0)]*N
        for j in range(0,k-1): Q[j+1]+=Fr((k-1-j)*p(j),factorial(j+1))
        Ex=expser([-q for q in Q]); I=integ(Ex); Delta=[Fr(1)-k*I[0]]+[-k*I[i] for i in range(1,N)]
        Ak1=mul(Ex,inv(Delta))
        az1=Fr(A(z-1,k-1),factorial(z-1)); O=[Fr(0)]*N; O[z]=Fr(min(z,k))*az1/z
        rhs=mul(Ak1,O); t=mul(inv(mul(Delta,Delta)),mul(Ex,integ(mul(O,Ex)))); rhs=[rhs[i]+k*t[i] for i in range(N)]
        for n in range(1,N):
            lhs=0
            for sg in permutations(range(1,n+1)):
                h=caps(sg); w=1
                for hi in h: w*=min(hi,k)
                lhs+=w*sum(1 for hi in h if hi==z)
            if Fr(lhs,factorial(n))!=rhs[n]: bad.append((k,z,n,lhs,rhs[n]*factorial(n)))
out.append(("riccati identity z>=k-1 mismatches",bad))

# 5. Theorem old-6-11 (가): E[H_k] = (n+1) a_{k-1} sum_j K_j a_{n+1-j}/a_n ; K from recursion
for k in (2,3):
    a=[Fr(A(m,k-1),factorial(m)) for m in range(0,N)]
    ac=lambda m: Fr(p(m),factorial(m))
    K=[Fr(0)]*(N+1)
    for j in range(1,N+1):
        s=Fr(0)
        for m in range(1,k):
            if j-m>=0: s+=(k-m)*ac(m-1)*K[j-m]
        if j==k+1: s+=1
        K[j]=s/j
    for n in range(1,N):
        EH=0; tot=0
        for sg in permutations(range(1,n+1)):
            h=caps(sg); w=1
            for hi in h: w*=min(hi,k)
            tot+=w; EH+=w*sum(1 for hi in h if hi==k)
        EH=Fr(EH,tot)
        rhs=(n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1,n+2))/a[n]
        if EH!=rhs: out.append(("FAIL 6-11",k,n,EH,rhs))
out.append("checked 6-11(가) k=2,3 n<=5")

# 6. k=1 claim: b_{n,1} >= (n-1) n!/2 for n>=4 (exact b_{n,1} = A_{n,1}-A_{n,0})
for n in range(2,8):
    b1=A(n,1)-A(n,0)
    out.append(("k=1",n,b1,(n-1)*factorial(n)//2, b1>factorial(n)))

# 7. column lemma integer inequality
out.append(("int ineq", 10**21*400**10 > 17**21*123**10, 10**21*400**10, 17**21*123**10))
for s in out: print(s)
