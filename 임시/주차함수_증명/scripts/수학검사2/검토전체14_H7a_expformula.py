# Check (7.6) exponential formula and (7.7)/(pair-terms) mod x^{3k+3} for k=2 using brute-force K_{n,k}(z)
import sympy as sp
from itertools import permutations
from math import factorial
z,x=sp.symbols('z x')
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)
    return h
def Kpoly(n,k):
    if n==0: return sp.Integer(1)
    tot=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); w=1; Z=0
        for c in h:
            if c<=k: w*=c
            else: Z+=1
        tot+=w*z**Z
    return sp.expand(tot)
k=2; N=3*k+2  # need up to x^{3k+2}=x^8
K=[Kpoly(n,k) for n in range(N+1)]
D=sum(K[n]*x**n/factorial(n) for n in range(N+1))
E=sum((m+1)**(m-1)*x**m/factorial(m) for m in range(k))
Dge=D-E
Tle=sum(t**(t-1)*x**t/factorial(t) for t in range(1,k+1))
rhs=sp.exp(Tle+z*sp.integrate(Dge,(x,0,x)))
diff=sp.series(D-rhs,x,0,N+1).removeO()
print("(7.6) ok:", sp.simplify(sp.expand(diff))==0)
# (7.7): X = D - G*, G* = e^T(1 - T_{>k} + z int (G*-E))  (solve as series)
T=sum(t**(t-1)*x**t/factorial(t) for t in range(1,N+2))
eT=sp.series(sp.exp(T),x,0,N+1).removeO()
Tgt=sp.expand(T-Tle)
# solve G* iteratively
G=E
for it in range(N+2):
    G=sp.series(eT*(1-Tgt+z*sp.integrate(sp.expand(G-E),(x,0,x))),x,0,N+1).removeO()
X=sp.expand(D-G)
Xs=sp.series(X,x,0,N+1).removeO()
# lowest degree
print("X lowest degree:", min(sp.Poly(Xs,x).monoms())[0], " expected", 2*k+2)
bd=z*sp.integrate(Dge,(x,0,x))-Tgt
eTle=sp.series(sp.exp(Tle),x,0,N+1).removeO()
rhs7=sp.series(eTle*(z*sp.integrate(Xs,(x,0,x))+bd**2/2),x,0,N+1).removeO()
print("(7.7) mod x^{3k+3} ok:", sp.simplify(sp.expand(Xs-rhs7))==0)
# pair-terms: X'' at z=k vs Neumann series with Q_j
Xpp=sp.diff(Xs,z,2).subs(z,k)
bdz=bd
def Neu(f): return sp.series(eTle*sp.integrate(f,(x,0,x)),x,0,N+1).removeO()
tot=0
for j in range(0,N+1):
    Qj=sp.Rational(j*(j-1),2*k**2)*bdz**2+sp.Rational(2*j,k)*bdz*sp.diff(bdz,z)+sp.diff(bdz,z)**2+bdz*sp.diff(bdz,z,2)
    f=sp.series(eTle*Qj.subs(z,k),x,0,N+1).removeO()
    for _ in range(j): f=Neu(f)
    tot+=k**j*f
print("pair-terms X'' ok:", sp.simplify(sp.expand(sp.series(Xpp-tot,x,0,N+1).removeO()))==0)
