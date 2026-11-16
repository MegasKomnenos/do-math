# N12: verify the four normalized recursions of D.central-gap-integer against a direct polynomial computation
import sys,io
from fractions import Fraction as F
from math import comb, factorial
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def padd(a,b):
    n=max(len(a),len(b)); return [ (a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(n)]
def pmul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x==0: continue
        for j,y in enumerate(b): r[i+j]+=x*y
    return r
def pscale(a,c): return [c*x for x in a]
def peval(a,y): return sum(c*y**i for i,c in enumerate(a))
def pder(a): return [i*a[i] for i in range(1,len(a))] or [0]
def K_polys(N,k):
    # K_{n,k}(y) as polynomial in y (list of int coeffs), via last-car recurrence with W(g)=g (g<=k), y (g>k)
    K=[[1]]
    for n in range(1,N+1):
        s=[0]
        for j in range(n):
            W=[j+1] if j+1<=k else [0,1]
            s=padd(s, pscale(pmul(W,pmul(K[j],K[n-1-j])),comb(n-1,j)))
        K.append(s)
    return K
def J_vals(N,k,z):
    p=[(m+1)**(m-1) if m>0 else 1 for m in range(N+2)]
    J=[F(0)]*(N+1)
    for n in range(1,N+1):   # J_n from J-egf (가) with index shifted: J_n = sum_{i<=n-1} C(n-1,i)(z+i+1)p_i J_{n-1-i} + 1[n>=k] C(n-1,k-1)p_{k-1}p_{n-k}
        if n<k: J[n]=F(0); continue
        s=sum(comb(n-1,i)*(z+i+1)*p[i]*J[n-1-i] for i in range(n))
        s+=comb(n-1,k-1)*p[k-1]*p[n-k]
        J[n]=F(s)
    return J
S=2918732888; s=F(S,2**30)
p=lambda m: (m+1)**(m-1) if m>0 else 1
def normalized(k):
    r=[F(p(i),factorial(i))/s**i for i in range(0,2*k+3)]
    A={i:r[i] for i in range(0,k+1)}; d={i:F(0) for i in range(0,k+1)}; z={i:F(0) for i in range(0,k+1)}
    j={i:F(0) for i in range(0,k)}; j[k]=r[k-1]/(s*k)
    out={}
    for n in range(k+1,2*k+1):
        rr=n-k
        A[n]=(sum((k+i+1)*r[i]*A[n-1-i] for i in range(0,rr-1))+sum(min(i+1,k)*r[i]*r[n-1-i] for i in range(rr-1,k+1)))/(s*n)
        d[n]=(sum((k+i+1)*r[i]*d[n-1-i] for i in range(0,rr-1))+sum(r[i]*A[n-1-i] for i in range(0,rr)))/(s*n)
        z[n]=(sum((k+i+1)*r[i]*z[n-1-i] for i in range(0,rr-1))+2*sum(r[i]*d[n-1-i] for i in range(0,rr-1)))/(s*n)
        j[n]=(sum((k+i)*r[i]*j[n-1-i] for i in range(0,rr))+r[k-1]*r[n-k])/(s*n)
        out[n]=(A[n],d[n],z[n],j[n])
    return out
for k in (5,8,9,12):
    N=2*k
    K=K_polys(N,k)
    J=J_vals(N,k,k-1)
    nz=normalized(k)
    for n in range(k+1,N+1):
        e_n=peval(pder(pder(K[n])),k); Kp=peval(pder(K[n]),k); Ak=peval(K[n],k)
        A_,d_,z_,j_=nz[n]
        norm=factorial(n)*s**n
        ok=(A_*norm==Ak, d_*norm==Kp, z_*norm==e_n, j_*norm==J[n])
        if not all(ok) or n in (15,16,17,18): print('k',k,'n',n,'match(A,Kp,e,J)=',ok,'e_n>J:',e_n>J[n], 'ratio', float(F(e_n)/J[n]) if J[n] else None)
print('done')
