# R3 검산: 5.4.1절의 포락선(weight-envelope), 거친 꼬리(parity-tail), 꼬리 비(omitted-tail (가)), tail-cells (나), cover-edge (가)의 수치 점검.
import mpmath as mp, itertools, random, math
mp.mp.dps=40
def nf(n,d): return mp.e**d*mp.factorial(n)/mp.factorial(n-d)*mp.mpf(n-d)**(n-d-2)/mp.mpf(n)**(n-2)
def W(n,g):
    dd=list(itertools.accumulate(g)); t=[n+1-x for x in dd]
    return nf(n,n-t[-1])*mp.fprod([mp.mpf(n)/x for x in t[:-1]])
def L(g):
    dd=list(itertools.accumulate(g)); return mp.mpf(5)/2*(dd[-1]-1)+sum(x-1 for x in dd[:-1])
def N(g):
    dd=list(itertools.accumulate(g)); return L(g)**2/2+mp.mpf(5)/4*(dd[-1]-1)**2-mp.mpf(dd[-1]-1)/12+mp.mpf(1)/2*sum((x-1)**2 for x in dd[:-1])
random.seed(1); ok=True
for _ in range(400):
    j=random.randint(1,6); g=[random.randint(1,9) for _ in range(j)]; r=sum(g)-1+random.randint(0,5); n=2*r+1+random.randint(0,300)
    if n<=r+1: continue
    rq=mp.mpf(r)/n; w=W(n,g)
    Rm=(1-rq)**(-j-mp.mpf(3)/2)-1-(j+mp.mpf(3)/2)*rq; Rm2=Rm-mp.mpf(1)/2*(j+mp.mpf(3)/2)*(j+mp.mpf(5)/2)*rq**2
    a=w-1-L(g)/n; b=a-N(g)/n**2
    if not (0<=a<=Rm and 0<=b<=Rm2 and 1<=w<=(1-rq)**(-j-mp.mpf(3)/2)): ok=False; print("envelope fails",g,r,n,a,Rm,b,Rm2)
print("weight-envelope / chain-normalization(나) random check:",ok)
# parity-tail: Z^{(2)}_j coefficientwise <= dc'_j (1-z)^{-theta'_j}, j=2..6, degree<=40
D=40
Ren=[mp.mpf(0)]+[mp.mpf(m)**m*mp.e**(-m)/mp.factorial(m) for m in range(1,D+1)]
def mul(a,b):
    c=[mp.mpf(0)]*(D+1)
    for i,x in enumerate(a):
        if x==0: continue
        for k in range(0,D+1-i): c[i+k]+=x*b[k]
    return c
def der(a): return [ (i+1)*a[i+1] for i in range(D)]+[mp.mpf(0)]
inv=[mp.mpf(1)]*(D+1)
zmul=lambda a:[mp.mpf(0)]+a[:D]
def op(F): 
    d=der(F); t=mul(F,inv); return zmul([d[i]+2*t[i] for i in range(D+1)])
Z=zmul(Ren); dc=None; th=None; ok2=True
for j in range(2,7):
    Z=mul(Ren,op(Z))
    th=mp.mpf(3*j)/2-1
    dc=mp.mpf(2) if j==2 else mp.mpf(3)/4*((mp.mpf(3*(j-1))/2-1)+2)*dc
    for m in range(0,D-1):   # 차수 D 근처는 절단(도함수) 때문에 믿지 않는다
        if Z[m]>dc*mp.binomial(th+m-1,m)*(1+mp.mpf(10)**-30): ok2=False; print("parity-tail fails",j,m)
print("parity-tail j<=6, degree<%d:"%(D-1),ok2)
# omitted-tail ratio formula
def Tl(j,n,r):
    th=mp.mpf(3*j)/2-1; d=mp.mpf(2)
    for i in range(2,j): d=mp.mpf(3)/4*((mp.mpf(3*i)/2-1)+2)*d
    return mp.e*mp.mpf(n)**(1-j)*(1-mp.mpf(r)/n)**(-j-mp.mpf(3)/2)*d*mp.binomial(th+r+1,r+2)
for (j,n,r) in [(3,20032,598),(25,20032,598),(7,50001,1200)]:
    lhs=Tl(j+2,n,r)/Tl(j,n,r); x32=mp.mpf(r)**1.5/n; rq=mp.mpf(r)/n; th=mp.mpf(3*j)/2-1
    rhs=mp.mpf(9)/16*x32**2/(1-rq)**2*mp.mpf(2*(3*j+5))/(3*j*(3*j-2))*mp.fprod([(r+2+th+i)/r for i in range(3)])
    print("Tl ratio",j,n,r,mp.nstr(lhs,12),mp.nstr(rhs,12))
# tail-cells (나), cover-edge (가)
def mm(n):
    lo,hi=170,int(n**(2/3))+5
    best=170
    # largest m>=171 with m^3<=(n-9m)^2 and n-9m>=0
    m=max(171,int(n**(2/3)-6*n**(1/3))-3)
    if not (n-9*m>=0 and m**3<=(n-9*m)**2):
        m=171
        if not (n-9*m>=0 and m**3<=(n-9*m)**2): return 170
    while (n-9*(m+1)>=0 and (m+1)**3<=(n-9*(m+1))**2): m+=1
    return m
ok3=True; worst=10
import random
ns=list(range(20001,60000,7))+[random.randint(60000,10**9) for _ in range(3000)]
for n in ns:
    m=mm(n); c=n**(1/3)
    if not (c*c-6*c-1<=m<=c*c-6*c+37 and m<c*c-4.5*c): ok3=False; print("tail-cells(나) fails",n,m)
    z=m+1; t=z**1.5/n
    worst=min(worst,t)
    if not (0.73<t<=1 and z>=598): ok3=False; print("cover-edge(가) fails",n,z,t)
print("tail-cells(나), cover-edge(가) on sample:",ok3," min z*^{3/2}/n =",worst)
