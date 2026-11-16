# L12 ch4 integer checks: rows n<=300, d_{n,k_n} sign, crossing, Q_L, central-gap recurrences vs brute force, e_n/J_n ratio
import math, itertools, time, sys
from fractions import Fraction
from math import comb
sys.setrecursionlimit(10000)
NMAX=60
t=time.time()
def column(l, N):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        if l>=n-1: A[n]=(n+1)**(n-1); continue
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
cols=[column(l,NMAX) for l in range(NMAX)]
print("cols",time.time()-t)
def A(n,l): return cols[l][n] if l>=0 else 0
def b(n,l): return A(n,l)-A(n,l-1)
rows={n:[b(n,l) for l in range(n)] for n in range(1,NMAX+1)}
kn=lambda n:(n+1)//2
# (ㄴ) of central-gap: d_{n,kn}<0 for 2..15, >0 for 16..300, right half nonincreasing for n<=15
neg=[n for n in range(2,NMAX+1) if rows[n][kn(n)]-rows[n][kn(n)-1]<0]
print("d_{n,kn}<0 for n in:",neg)
for n in range(2,16):
    r=rows[n]; ok=all(r[j]>=r[j+1] for j in range(kn(n),n-1)); print(" n",n,"right half nonincreasing",ok, end=";")
print()
# crossing: b_{n,kn}<b_{n,kn+1}
cross=[n for n in range(5,NMAX+1) if rows[n][kn(n)]<rows[n][kn(n)+1]]
print("crossing true for n in 5..19:",[n for n in cross if n<=19],"; false in 20..300:",[n for n in range(20,NMAX+1) if n not in cross])
# Q_L for 3<=n<=15 strict; decreasing levels count n<=300; strict unimodal & no adjacent ties
cnt=0; qlfail=[]; strictfail=[]; ties=[]
for n in range(1,NMAX+1):
    r=rows[n]
    for l in range(n-1):
        if r[l]==r[l+1]: ties.append((n,l))
    # strict unimodal
    i=0
    while i+1<n and r[i]<r[i+1]: i+=1
    while i+1<n and r[i]>r[i+1]: i+=1
    if i!=n-1: strictfail.append(n)
    for l in range(n-2):
        if r[l]>r[l+1]:
            cnt+=1
            if 2*l<=n-2 and not (r[l+1]**2>r[l]*r[l+2]): qlfail.append((n,l))
print("decreasing levels n<=300:",cnt,"QL strict fails:",qlfail[:5],"strict-unimodal fails:",strictfail,"ties:",ties)
# A^c recurrence check vs exact for n<=60, l>=kn-2
def Ac_rec(l,N):
    p=lambda m:(m+1)**(m-1) if m>=1 else 1
    Ac=[0]*(N+1)
    for n in range(1,N+1):
        if n>2*l+4: break
        s=sum(comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        s+=sum(Ac[i]*comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        Ac[n]=s
    return Ac
bad=0
for l in range(0,60):
    Ac=Ac_rec(l,min(2*l+4,NMAX))
    for n in range(1,min(2*l+4,NMAX)+1):
        if Ac[n]!=(n+1)**(n-1)-A(n,l): bad+=1
print("A^c recurrence mismatches:",bad)
# central gap: brute force K, K', K'', J for small n,k ; and recurrences
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=0
        for j in range(i-1,0,-1):
            if sig[j-1]>sig[i-1]: z=j;break
        h.append(i-z)
    return h
def brute(n,k):
    e=0; Kp=0; Aval=0; J=0
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        P=math.prod(x for x in h if x<=k); Pl=math.prod(x for x in h if x<k)
        Aval+=P*k**Z
        Kp+=P*Z*k**(Z-1) if Z>=1 else 0
        e+=P*Z*(Z-1)*k**(Z-2) if Z>=2 else 0
        J+=H*k**(H-1)*(k-1)**Z*Pl if H>=1 else 0
    return Aval,Kp,e,J
def rec_exact(k,N):
    p=lambda m:(m+1)**(m-1) if m>=1 else 1
    r=[Fraction(p(i),math.factorial(i)) for i in range(N+2)]
    Aa=[Fraction(0)]*(N+1); d=[Fraction(0)]*(N+1); z=[Fraction(0)]*(N+1); jj=[Fraction(0)]*(N+1)
    for i in range(0,k+1): Aa[i]=r[i]
    jj[k]=r[k-1]/k
    for n in range(k+1,min(N,2*k)+1):
        rr=n-k
        Aa[n]=(sum((k+i+1)*r[i]*Aa[n-1-i] for i in range(0,rr-1))+sum(min(i+1,k)*r[i]*r[n-1-i] for i in range(rr-1,k+1)))/n
        d[n]=(sum((k+i+1)*r[i]*d[n-1-i] for i in range(0,rr-1))+sum(r[i]*Aa[n-1-i] for i in range(0,rr)))/n
        z[n]=(sum((k+i+1)*r[i]*z[n-1-i] for i in range(0,rr-1))+2*sum(r[i]*d[n-1-i] for i in range(0,rr-1)))/n
        jj[n]=(sum((k+i)*r[i]*jj[n-1-i] for i in range(0,rr))+r[k-1]*r[n-k])/n
    f=lambda v,n: v*math.factorial(n)
    return [f(Aa[n],n) for n in range(N+1)],[f(d[n],n) for n in range(N+1)],[f(z[n],n) for n in range(N+1)],[f(jj[n],n) for n in range(N+1)]
mism=0
for k in (3,4,5):
    Aa,d,z,jj=rec_exact(k,2*k)
    for n in range(k+1,min(2*k,9)+1):
        bf=brute(n,k)
        if (Aa[n],d[n],z[n],jj[n])!=tuple(bf): mism+=1; print("MISMATCH",k,n,(Aa[n],d[n],z[n],jj[n]),bf)
        if Aa[n]!=A(n,k-1): mism+=1; print("A mismatch",k,n)
print("recurrence vs brute mismatches:",mism)
# e_n vs J_n(k-1) for n=2..60 with k=kn
res=[]
for k in range(1,31):
    if k==1: continue
    Aa,d,z,jj=rec_exact(k,2*k)
    for n in (2*k-1,2*k):
        if n<2 or n>60: continue
        e=z[n]; J=jj[n]
        res.append((n,k,e>J, e/J if J else None, (rows[n][k]-rows[n][k-1])>=e-J))
print("e_n>J_n(k-1):", [(n,ok) for n,k,ok,rt,_ in res])
print("min ratio over n>=16:", min(((rt,n) for n,k,ok,rt,_ in res if n>=16)))
print("d>=e-J all:", all(x[4] for x in res))
print("total time",time.time()-t)
