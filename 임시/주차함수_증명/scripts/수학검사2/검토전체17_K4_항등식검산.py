# K4: 5.5.1-5.5.5의 항등식·부등식을 정확 유리수로 작은 n에서 검산
# 생존 확률 s_n(y) (y >= (n-1)/2) 를 정리 2-13의 재귀로 계산하고, n<=7은 brute force와 대조한다.
from fractions import Fraction as Fr
from math import comb, floor
from itertools import product
import sys
sys.setrecursionlimit(10000)
NMAX=70
p=[1]*(NMAX+3)
for m in range(1,NMAX+3): p[m]=(m+1)**(m-1)
def pi(n,t): return Fr(comb(n,t)*t**(t-1)*p[n-t], p[n])
cache={}
def s(n,y):
    # s_n(y)=Pr_n(M<=y-1), valid via recursion when n<=2y+1
    if y<=0: return Fr(0)
    if n==0: return Fr(1)
    if n<=y: return Fr(1)   # max displacement <= n-1 <= y-1
    key=(n,y)
    if key in cache: return cache[key]
    assert n<=2*y+1, (n,y)
    tot=Fr(1)
    for t in range(y+1,n+1): tot-=pi(n,t)
    pi0=tot
    val=pi0
    for t in range(y+1,n+1): val+=pi(n,t)*Fr(y,t)*s(t-1,y)
    cache[key]=val; return val
def c(n,Y): return s(n,Y+1)-s(n,Y)
def b(n,Y): return c(n,Y)*p[n]
# brute force check n<=7
def brute_A(n):
    A=[0]*(n+1)
    for pref in product(range(1,n+1),repeat=n):
        occ=[0]*(n+2); disp=0; ok=True
        for a in pref:
            j=a
            while j<=n and occ[j]: j+=1
            if j>n: ok=False;break
            occ[j]=1; disp=max(disp,j-a)
        if ok:
            for l in range(disp,n+1): A[l]+=1
    return A
for n in range(1,8):
    A=brute_A(n)
    for y in range(max(1,(n-1+1)//2),n+2):
        if n<=2*y+1:
            assert s(n,y)==Fr(A[min(y-1,n)],p[n]) if y-1<=n else True, (n,y)
print("brute force n<=7 OK")
def sT(t,Y):  # tree survival
    if t<=Y: return Fr(1)
    return Fr(Y,t)*s(t-1,Y)
def x(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
def t0(y):
    t=y+2
    while not (y<=(t-1)-floor(Fr(3,4)*Fr(t-1)**Fr(2,3)) if False else y<=(t-1)-int((0.75*(t-1)**(2/3))//1)): t+=1
    return t
bad=[]
for n in range(3,NMAX+1):
    for y in range((n+1+1)//2, n):   # (n+1)/2 <= y <= n-1
        lhs=c(n,y)-c(n,y-1)
        # 5-19
        rhs=sum(pi(n,t)*x(t,y) for t in range(y,n+1))
        if lhs!=rhs: bad.append(("5-19",n,y))
        # x_t formula t>=y+1 and x_y=-1/y
        if x(y,y)!=Fr(-1,y): bad.append(("x_y",n,y))
        for t in range(y+1,n+1):
            if x(t,y)!=Fr(1,t)*((y+1)*c(t-1,y)-(y-1)*c(t-1,y-1)): bad.append(("x_t",n,y,t))
        # 5-27
        P=sum(x(t,y) for t in range(y,n+1))
        if P!=Fr(-1,y)+sum(((y+1)*c(m,y)-(y-1)*c(m,y-1))/Fr(m+1) for m in range(y,n)): bad.append(("5-27",n,y))
        # cor-L: y P >= -1 - y(y-1)c_{n-1}(y-1)/n
        if y*P < -1-Fr(y*(y-1))*c(n-1,y-1)/n: bad.append(("cor-L",n,y))
        # 5-25: (x_t)_- <= Ren(t-y)Bor(y)/(y Bor(t)) for y+1<=t<=2y-1 ; use theta_t(y)=C(t,y)y^{y-1}(t-y)^{t-y}/t^{t-1} (= Ren Bor/Bor by 2-37(마))
        for t in range(y+1,min(n,2*y-1)+1):
            vis=Fr(comb(t,y)*y**(y-1)*(t-y)**(t-y), t**(t-1))
            if -x(t,y) > vis/y: bad.append(("5-25",n,y,t))
        # 5-22 given IH
        T0=t0(y)
        if T0<=n:
            IH=all(b(m,y)>=b(m,y-1) for m in range(T0-1,n))
            if IH:
                win=sum((pi(n,t)-pi(n,y))*max(-x(t,y),0) for t in range(y+1,T0))
                pos=sum((pi(n,m+1)-pi(n,T0-1))*(c(m,y)+c(m,y-1))/Fr(m+1) for m in range(T0-1,n))
                if lhs < pi(n,y)*P - win + pos: bad.append(("5-22",n,y))
                # 5-30 identity
                top=Fr(y*(y-1))*c(n-1,y-1)/n
                posp=sum((pi(n,m+1)-pi(n,T0-1))*(c(m,y)+c(m,y-1))/Fr(m+1) for m in range(T0-1,n-1)) \
                     + (pi(n,n)-pi(n,T0-1))*c(n-1,y)/n + (pi(n,n)-pi(n,T0-1)-(y-1)*pi(n,y))*c(n-1,y-1)/n
                if pos - pi(n,y)/y*top != posp: bad.append(("5-30",n,y))
# 5-28: c_{m+1}(w+1) >= (1-z) c_m(w), m>=2, 1<=d<=m/2
import math
for m in range(2,NMAX):
    for d in range(1,m//2+1):
        w=m-d
        z=math.exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
        if float(c(m+1,w+1)) < (1-z)*float(c(m,w))-1e-15: bad.append(("5-28",m,d))
# diag-first-layer sign as used: (y+1)(m+1)c_{m+1}(y) > (y-1)(m+2)c_m(y-1) for m>=y>=2, m<=2y-1
for y in range(2,NMAX//2):
    for m in range(y,2*y):
        if not ((y+1)*(m+1)*c(m+1,y) > (y-1)*(m+2)*c(m,y-1)): bad.append(("6.31",y,m))
print("violations:",bad[:20], "count",len(bad))
