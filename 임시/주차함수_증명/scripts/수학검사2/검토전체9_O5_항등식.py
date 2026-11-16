from fractions import Fraction as Fr
from math import factorial, comb, exp, sqrt, pi, log
import sys
NMAX=130
# A[n][l] by last-car recursion (old-2-6), exact ints
A=[[0]*(NMAX+2) for _ in range(NMAX+1)]
for l in range(NMAX+2): A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+2):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
p=[(n+1)**(n-1) if n>0 else 1 for n in range(NMAX+1)]
for n in range(NMAX+1): assert A[n][n]==p[n] if n>0 else True
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
def s(m,y): return Fr(A[m][y-1],p[m]) if y>=1 else Fr(0)
def c(m,Y): return Fr(b(m,Y),p[m])
def Bor(n): return Fr(n**(n-1),factorial(n))  # times e^{-n}; use ratios only
def pi_n(n,m): return Fr(comb(n,m)*m**(m-1)*p[n-m],p[n])
def P_last(m,j): return Fr(j*comb(m-1,j-1)*p[j-1]*p[m-j],p[m])
# (6.1) check
for m in range(1,40):
    for k in range(1,m+1):
        rhs=sum(P_last(m,j)*Fr(min(j,k),j)*s(j-1,k)*s(m-j,k) for j in range(1,m+1))
        assert rhs==s(m,k),(m,k)
print("(6.1) ok")
# (6.22) chain recursion
for y in range(1,30):
    for d in range(1,y+3):
        N=y+d-1
        rhs=1-sum(pi_n(N,y+q) for q in range(1,d))+sum(pi_n(N,y+q)*Fr(y,y+q)*s(y+q-1,y) for q in range(1,d))
        assert rhs==s(N,y),(y,d)
    # d=y+3 with t(y)
    d=y+3; N=2*y+2
    t=Fr(comb(2*y+2,y+1)*(y+1)**(2*y),2*p[2*y+2])
    rhs=1-sum(pi_n(N,y+q) for q in range(1,d))+sum(pi_n(N,y+q)*Fr(y,y+q)*s(y+q-1,y) for q in range(1,d))+t/(y+1)**2
    assert rhs==s(N,y),("t",y)
print("(6.22) ok incl. d=y+3")
# (6.21) stay law for y in 50..62 (m<=128)
viol=[]
for y in range(50,63):
    for d in range(2,y+3):
        if y+d>NMAX: continue
        lhs=(y+1)*(s(y+d,y+1)-s(y+d-1,y)); rhs=(d-1)*c(y+d,y)
        if lhs>rhs: viol.append((y,d,float(lhs/rhs)))
print("(6.21) violations:",viol[:5], "count",len(viol))
# also small y to see where it fails
fails=[]
for y in range(1,50):
    for d in range(2,y+3):
        lhs=(y+1)*(s(y+d,y+1)-s(y+d-1,y)); rhs=(d-1)*c(y+d,y)
        if lhs>rhs: fails.append((y,d))
print("(6.21) small-y fails (first 10):",fails[:10],"n=",len(fails))
# (6.31) diag
viol=[]
for d in range(1,30):
    for m in range(max(2,2*d-1),100):
        w=m-d
        L=(w+2)*(m+1)*c(m+1,w+1); R=w*(m+2)*c(m,w)
        if not L>R: viol.append((d,m))
        # ratio bound exp(1/(4(w+1)(w+2)))
        if R>0 and float(L/R)<exp(1/(4*(w+1)*(w+2)))-1e-15: viol.append(("ratio",d,m,float(L/R)))
print("(6.31) violations:",viol[:5])
# (6.29) pair rearrange
for k in range(2,40):
    x=lambda t: Fr((k+1)*b(t-1,k)-(k-1)*b(t-1,k-1),t**(t-1))
    phi=k*sum(x(t) for t in range(k+1,2*k+2))
    Ppair=k*sum(Fr((k+1)*c(m+1,k),m+2)-Fr((k-1)*c(m,k-1),m+1) for m in range(k,2*k))
    Ups=Fr(k*(k-1)*b(2*k,k-1),(2*k+1)*p[2*k])
    assert phi==Ppair-Ups,k
    # cor-L / D-bound: k P_{2k+1}(k) = phi-1
    P=sum(x(t) for t in range(k+1,2*k+2))-Fr(1,k)
    assert k*P==phi-1
print("(6.29) ok")
# (6.45) theorem-D identity
for m in range(1,60):
    for d in range(1,(m+1)//2+1):
        lhs=c(m,m-d)
        tot=Fr(0)
        for J in range(0,d):
            sz=m-J-1
            sv=s(sz,m-d+1) if sz>0 else Fr(1)
            cc=c(sz,m-d) if sz>0 and m-d<=sz else Fr(0)
            if sz==m-d: cc=Fr(0)
            tot+=pi_n(m,J+1)/m*(sv+(m-d)*cc)
        for Q in range(1,min(d-1,m-d)+1):
            tot+=P_last(m,Q)*c(m-Q,m-d)
        assert tot==lhs,(m,d)
print("(6.45) ok")
# (6.41) V-core identity
for k in range(2,40):
    V=sum((k+1)*c(m,k)-(k-1)*c(m,k-1) for m in range(k,2*k+1))
    Bd=2-2*s(2*k+1,k+1)-(k-1)*(s(2*k+1,k+1)-s(2*k,k))-(k-1)*c(2*k,k-1)
    DD=lambda m,y:(y+2)*s(m+2,y+2)-2*(y+1)*s(m+1,y+1)+y*s(m,y)
    assert V==Bd+sum(DD(m,k-1) for m in range(k,2*k)),k
print("(6.41) ok")
# (6.37) chain formula: X_d(y)=y(1-s_{y+d-1}(y)) = sum over walk paths
from functools import lru_cache
import itertools
def BorF(n): return Fr(n**(n-1),factorial(n))  # Bor(n)*e^n ; tilt ratio Bor(y+q)/Bor(y+d) = BorF(y+q)/BorF(y+d) * e^{d-q}
# exact check impossible w/ e; use floats
def Borf(n): return exp(-n)*n**(n-1)/factorial(n)
def compositions_prefix(d):
    # all sequences q_0=d>q_1>...>q_j>=1
    res=[]
    def rec(path):
        last=path[-1]
        for q in range(last-1,0,-1):
            res.append(path+[q]); rec(path+[q])
    rec([d]); return res
for y in range(1,15):
    for d in range(2,min(y+2,9)+1):
        X=float(y*(1-s(y+d-1,y)))
        tot=0.0
        for path in compositions_prefix(d):
            pr=1.0
            for i in range(1,len(path)): pr*=Borf(path[i-1]-path[i])
            qj=path[-1]; j=len(path)-1
            R=Borf(y+qj)/Borf(y+d)
            Pi=1.0
            for i in range(1,len(path)): Pi*=y/(y+path[i])
            tot+=pr*R*qj*Pi
        assert abs(tot-X)<1e-9*max(1,X),(y,d,tot,X)
print("(6.37) ok")
# path-shift (가): sum wt = Bor(n) c_{n-1}(k-1)
def pi0(N,x): # P(all trees <= x) for forest size N: 1-sum_{m>x} pi_N(m) valid when x>=N/2 ... use exact: A_{N,x}... Actually pi0_N(x)=Pr(G<=x); for N<=2x+1 use formula
    return 1-sum(pi_n(N,m) for m in range(x+1,N+1))
for k in range(2,12):
    for n in range(k+1,2*k+1):
        tot=[0.0]
        # paths S_1>...>S_L>=k, S_1<=n-1
        def rec(prefix):
            last=prefix[-1]
            for S in range(last-1,k-1,-1):
                path=prefix+[S]
                L=len(path)-1
                wt=1.0
                for i in range(L): wt*=Borf(path[i]-path[i+1])
                SL=path[-1]
                wt*=Borf(SL)*float(pi0(SL-1,k-1))*(k**L-(k-1)**L)/1.0
                pr=1.0
                for j in range(1,L+1): pr*=path[j]
                tot[0]+=wt/pr
                rec(path)
        rec([n])
        tgt=Borf(n)*float(c(n-1,k-1))
        assert abs(tot[0]-tgt)<1e-12*max(1e-300,tgt),(k,n,tot[0],tgt)
print("path-shift (가) ok")
