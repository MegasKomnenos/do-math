# K3 검산 2: n<=300 행의 사슬·단봉·Q_R·증인 상계, 조각 수, Cayley 비, 생일 평균, L(10^4)
import math, sys
from math import comb
N=300
# A[l][n] only for l<=n-1 needed; compute full for simplicity l<=N
A=[[0]*(N+1) for _ in range(N+1)]
for l in range(N+1):
    A[l][0]=1
    for n in range(1,N+1):
        if l>=n-1 and l>0:
            A[l][n]=A[l-1][n] if l-1>=n-1 else None
        s=0
        for j in range(1,n+1):
            s+=min(j,l+1)*comb(n-1,j-1)*A[l][j-1]*A[l][n-j]
        A[l][n]=s
def row(n): return [A[l][n]-(A[l-1][n] if l>=1 else 0) for l in range(n)]
breaks=[]; nonuni=[]; QRfail=[]; lstar={}
for n in range(1,N+1):
    b=row(n); kn=(n+1)//2
    # first piece chain strict
    if n>=3 and not all(b[i]<b[i+1] for i in range(kn-1)): breaks.append(n)
    # unimodality & smallest witness
    mx=max(b); ls=b.index(mx); lstar[n]=ls
    ok=all(b[i]<=b[i+1] for i in range(ls)) and all(b[i]>=b[i+1] for i in range(ls,n-1))
    if not ok: nonuni.append(n)
    # Q_R(n): (n-1)/2<=l<=n-3
    for l in range(math.ceil((n-1)/2), n-2):
        if b[l]>b[l+1] and not (b[l+1]**2>=b[l]*b[l+2]): QRfail.append((n,l))
print("chain breaks (n<=300):",breaks)
print("non-unimodal:",nonuni,"QR fail:",QRfail)
print("l*_n n<=10:",[lstar[n] for n in range(1,11)])
# witness bound
vals=[(n+1-lstar[n]-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3)) for n in range(50,N+1)]
print("witness excess 50..300: min %.4f max %.4f"%(min(vals),max(vals)))
vals2=[(n+1-lstar[n]-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3)) for n in range(5,50)]
print("witness excess 5..49: min %.4f max %.4f"%(min(vals2),max(vals2)))
# n<=15 d_{n,k_n} sign
print("d_{n,k_n} n=2..16:",[ (n, row(n)[(n+1)//2]-row(n)[(n+1)//2-1]) for n in range(2,17)])
# counts
c2=sum(((n+1)//2)-1 for n in range(10001,20001))
c4=sum(n-2-math.ceil((n-1)/2) for n in range(5,20001))
c5=sum(n-2-math.ceil((n-1)/2) for n in range(20001,50001))
print("counts:",c2,c4,c5)
# Cayley ratio
e=math.e
for k in range(1,10):
    cr=(1+1/k)**(k-2); v=cr*(1+5/(2*k)+2/k**2)
    print(k, round(v,5), v>87/32)
bad=[k for k in range(1,10**6) if not (1+1/k)**(k-2) > e*k*k/(k*k+2.5*k+2)]
print("cayley ineq fails:",bad[:5], "e<65/24+1/100:", e<65/24+0.01, 65/24+0.01<87/32)
# tm_d(1) <= sqrt(pi d/2)
worst=0
for d in range(1,3001):
    t=0.0; prod=1.0
    for j in range(1,d+1):
        prod*=1-j/(d+1); t+=prod
    worst=max(worst,t/math.sqrt(math.pi*d/2))
print("max tm_d(1)/sqrt(pi d/2) d<=3000: %.6f"%worst)
# L(10^4)
def integ(f,a,b,n=200000):
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n): s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3
M=[integ(lambda y,i=i: y**i*math.exp(-y-y*y/2),0,40) for i in range(6)]
M26=integ(lambda y: y*y*math.exp(-y-y*y/2),0,6)
Ms=[max(y**i*math.exp(-y-y*y/2) for y in [t/100000 for t in range(1,1000000)]) for i in range(6)]
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
def L(r):
    s=math.sqrt(r)
    return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+math.exp(-0.5))/s+1/s**2)
print("M:",[round(x,6) for x in M],"M2(6):",round(M26,6),"M*:",[round(x,6) for x in Ms])
print("L(10^4)=%.6f  L(171)=%.6f L(9999)=%.6f"%(L(10**4),L(171),L(9999)))
# m(n)
def mfun(n):
    m=170
    for t in range(171,int(n**(2/3))+2):
        if t**1.5+9*t<=n: m=max(m,t)
    return m
print("m(20001)=",mfun(20001),"m(50001)=",mfun(50001))
# 5-2 (나) threshold m>=171 at n=20001 ok?
print("597^1.5+9*597=",597**1.5+9*597, "598:",598**1.5+9*598)
# Pc bound check numeric at s=100
s=100
br=1/(3*s)+8/(3*s*s)+2.507/s**2+(1+2.1709*s)/s**3
print("bracket at s=100:",br, "coef:",0.5+2*0.845204-math.sqrt(3*math.pi/2))
