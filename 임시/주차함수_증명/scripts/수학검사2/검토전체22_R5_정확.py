# 검토 22차 R5: 장6 진술의 작은 범위 정확(유리수) 점검
from fractions import Fraction as Fr
from math import comb, factorial, exp, log, sqrt, pi, e
import sys
NMAX=112
def build(NMAX):
    A={}
    for l in range(-1,NMAX+1):
        row=[0]*(NMAX+1)
        if l>=0:
            row[0]=1
            for n in range(1,NMAX+1):
                s=0
                for j in range(n):
                    s+=comb(n-1,j)*min(j+1,l+1)*row[j]*row[n-1-j]
                row[n]=s
        else:
            row[0]=1  # A_{0,-1}: s_0(0) 안 씀
        A[l]=row
    return A
A=build(NMAX)
p=lambda n:(n+1)**(n-1) if n>=1 else 1
assert all(A[n-1][n]==p(n) for n in range(1,NMAX+1))
def s(m,y): return Fr(A[y-1][m],p(m))          # s_m(y)=A_{m,y-1}/p_m
def c(m,Y): return s(m,Y+1)-s(m,Y) if Y>=1 else Fr(A[0][m],p(m))
def Bor(m): return Fr(m**(m-1),factorial(m))   # e^{-m} 인자는 비에서 소거되게 따로 다룸
# Bor(m)=e^{-m} m^{m-1}/m!  ; 비 Bor(a)Bor(b)/Bor(a+b)는 e 소거
def pi_(n,m): return Fr(comb(n,m)*m**(m-1)*p(n-m),p(n))
bad=0
# (a) 6:old-7-20
for k in range(43,49):
    bound=Fr(k+1,k)**(k-1)
    for N in range(0,NMAX):
        r=Fr(A[k-1][N+1],(N+1)*A[k-1][N])
        if r>bound or (r==bound)!=(N==k-1): bad+=1; print("7-20 fail",k,N)
print("(a) 7-20 ok")
# (a') 6:old-7-21 등호
for k in (43,45):
    for n in range(k+1,NMAX+1):
        w=lambda t:comb(n,t)*t**(t-1)*A[k-1][n-t]
        for t in range(k,n):
            if w(t+1)<w(t) or (w(t+1)==w(t))!=((t,n)==(k,2*k)): bad+=1; print("7-21 fail",k,n,t)
print("(a') 7-21 ok")
# (c) 머묾 법칙 (6.20): y=50,51,52 ; 2<=d<=y+2
for y in (50,51,54):
    for d in range(2,y+3):
        if y+d>NMAX: continue
        st=s(y+d,y+1)-s(y+d-1,y)
        if (y+1)*st>(d-1)*c(y+d,y): bad+=1; print("stay fail",y,d)
print("(c) stay ok; 작은 y에서도?")
cnt=0
for y in range(1,50):
    for d in range(2,y+3):
        if y+d>NMAX: continue
        st=s(y+d,y+1)-s(y+d-1,y)
        if (y+1)*st>(d-1)*c(y+d,y): cnt+=1
print("   y<50 위반 수:",cnt)
# (d) (6.26)
mn=None
for d in range(1,56):
    for m in range(max(2,2*d-1),NMAX):
        w=m-d
        L=(w+2)*(m+1)*c(m+1,w+1); R=w*(m+2)*c(m,w)
        if not L>R: bad+=1; print("6.26 fail",d,m)
        else:
            if R>0:
                ratio=float(L/R); lb=exp(1/(4*(w+1)*(w+2)))
                if ratio<lb: bad+=1; print("6.26 ratio fail",d,m,ratio,lb)
print("(d) 6.26 ok")
# (e) 사슬 재귀 (6.21)와 d=y+3 보정, (6.22) d=y+2 보정
def sd(d,y): return s(y+d-1,y)
for y in range(1,36):
    for d in range(1,y+4):
        N=y+d-1
        rhs=1-sum(pi_(N,y+q) for q in range(1,d))+sum(pi_(N,y+q)*Fr(y,y+q)*sd(q,y) for q in range(1,d))
        if d==y+3:
            t=Fr(comb(2*y+2,y+1)*(y+1)**(2*y),2*p(2*y+2))
            rhs+=t/(y+1)**2
        if rhs!=sd(d,y): bad+=1; print("6.21 fail",y,d)
    for d in range(1,y+3):
        rhs=pi_(y+d,y+1)/(y+1)+sum(pi_(y+d,y+1+q)*((y+1)*c(y+q,y)+sd(q+1,y))/(y+1+q) for q in range(1,d))
        if d==y+2:
            t=Fr(comb(2*y+2,y+1)*(y+1)**(2*y),2*p(2*y+2)); rhs-=t/(y+1)**2
        if rhs!=c(y+d,y): bad+=1; print("6.22 fail",y,d)
print("(e) 6.21/6.22 ok")
# (g) cor-L: P_n(y)=sum x_t(y), x_y=-1/y, x_t=[(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)]/t
for y in range(2,40):
    for n in range(y+1,2*y+2):
        if n>NMAX: continue
        P=Fr(-1,y)+sum(((y+1)*c(t-1,y)-(y-1)*c(t-1,y-1))/t for t in range(y+1,n+1))
        if y*P< -1-Fr(y*(y-1),n)*c(n-1,y-1): bad+=1; print("cor-L fail",y,n)
print("(g) cor-L ok")
# (h) (6.40)
for k in range(3,50):
    V=sum((k+1)*c(m,k)-(k-1)*c(m,k-1) for m in range(k,2*k+1))
    DD=lambda m,y:(y+2)*s(m+2,y+2)-2*(y+1)*s(m+1,y+1)+y*s(m,y)
    Bd=2-2*s(2*k+1,k+1)-(k-1)*(s(2*k+1,k+1)-s(2*k,k))-(k-1)*c(2*k,k-1)
    if V!=Bd+sum(DD(m,k-1) for m in range(k,2*k)): bad+=1; print("6.40 fail",k)
print("(h) 6.40 ok")
# (f) first-layer-mass / one-step-loss  (Bor에 e^{-n} 포함해 float)
def Bf(n): return exp(-n+(n-1)*log(n)-sum(log(i) for i in range(1,n+1)))
for k in range(2,50):
    W0=sum(Bf(n)*float(c(n-1,k-1)) for n in range(k+1,2*k+1))
    if not W0<2*(2*pi)**-0.5*k**-1.5: bad+=1; print("W0 fail",k)
    for n in range(k+1,2*k+1):
        loss=(k+1)*Bf(n+1)*float(c(n,k))-(k-1)*Bf(n)*float(c(n-1,k-1))
        if loss< -(k-1)/(2*n)*Bf(n)*float(c(n-1,k-1)): bad+=1; print("loss fail",k,n)
print("(f) ok")
# (i) lemma-H (6.43), H'
def theta(t,k): return Fr(comb(t,k)*k**(k-1)*(t-k)**(t-k),t**(t-1))
z32=2.61238
for m in range(1,60):
    for d in range(1,(m+1)//2+1):
        mu1=sum(theta(m+1,m+1-j) for j in range(1,d+1))
        mu2=mu1+2*sum(theta(m+1,m+1-j)*theta(m+1-j,m+1-jp) for j in range(1,d+1) for jp in range(j+1,d+1))
        if m==d==1: continue
        lb=float(mu1)/m*(1-d/m)**(float(mu2/mu1)-1)
        if float(c(m,m-d))<lb*(1-1e-12): bad+=1; print("H fail",m,d)
        k=m-d
        if d>=2 and k>=1:
            rho=d/k**(2/3); ep=k**(-1/3); br=(2*pi)**-0.5*(2*sqrt(rho)-2.218*ep)
            Low=k**(1/3)*br/(1+rho*ep)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*ep)**1.5*exp(1/(4*(k+1)))/br)
            if (k+1)*float(c(m,k))<Low: bad+=1; print("H' fail",k,d)
print("(i) H,H' ok")
# (b) 위험률 (6.18)(6.19)(다) k=43..46
def g(x): return (x-1)*log(1+1/x)
for k in range(43,47):
    xk=Fr(k,k+1)**(k-1)
    U=[Fr(A[k-1][N],factorial(N))*xk**N for N in range(0,NMAX+1)]
    for N in range(k,NMAX):
        if N<=2*k-1: O=sum(U[j] for j in range(N-k+1,k))+(N-k+1)*U[k]
        else: O=k*U[k]
        kap=1-float(xk*O)
        hz=1-float(s(N+1,k)/s(N,k))
        epsN=g(N+1)-g(k)
        if hz<1-exp(-epsN)*(1-kap/(N+1))-1e-13: bad+=1; print("6.18 fail",k,N)
        if k*hz+k*(1-g(N+1))<1.5-47/(24*k)+(1-1.5/k)*kap*k/(N+1)-1e-12: bad+=1; print("6.19 fail",k,N)
        if N+1>=2*k and hz<(0.75-11/(6*k))/k: bad+=1; print("(다) fail",k,N)
        if (N+1)*(U[N]-U[N+1])<U[N]*(1-xk*O): bad+=1; print("6.15 fail",k,N)
print("(b) ok")
print("bad",bad)
