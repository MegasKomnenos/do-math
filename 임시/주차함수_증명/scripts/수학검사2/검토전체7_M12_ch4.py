# 4장 D 항목 재계산: 얼린 용량 다항식 재귀 검증(n<=8 전수), e_n/J_n(k-1) 비 n=17, 유리수 (ㅅ), sympy로 (ㄴ)(ㄷ)
import itertools, math
from fractions import Fraction
from math import comb
import sympy as sp
# --- brute force K_{n,k}(y), J_n(z) over permutations
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: m=j
        h.append(i-m)
    return h
y,z=sp.symbols('y z')
def K_brute(n,k):
    tot=0
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s); pr=1; Z=0
        for x in h:
            if x<=k: pr*=x
            else: Z+=1
        tot+=pr*y**Z
    return sp.expand(tot)
def J_brute(n,k):
    tot=0
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s); pr=1; Z=0; H=0
        for x in h:
            if x<k: pr*=x
            elif x==k: H+=1
            else: Z+=1
        tot+=H*k**(H-1)*z**Z*pr if H>0 else 0
    return sp.expand(tot)
p=[1]+[(n+1)**(n-1) for n in range(1,60)]
def K_rec(nmax,k):
    K=[sp.Integer(1)]
    for n in range(1,nmax+1):
        s=0
        for j in range(n):
            W=(j+1) if j+1<=k else y
            s+=comb(n-1,j)*W*K[j]*K[n-1-j]
        K.append(sp.expand(s))
    return K
def J_rec(nmax,k):
    J=[sp.Integer(0)]
    for n in range(1,nmax+1):
        s=sum(comb(n-1,i)*(z+i+1)*p[i]*J[n-1-i] for i in range(n))
        if n>=k: s+=comb(n-1,k-1)*p[k-1]*p[n-k]
        J.append(sp.expand(s))
    return J
for k in (2,3,4):
    K=K_rec(8,k); J=J_rec(min(8,2*k),k)
    okK=all(sp.simplify(K[n]-K_brute(n,k))==0 for n in range(1,9))
    okJ=all(sp.simplify(J[n]-J_brute(n,k))==0 for n in range(1,min(8,2*k)+1))
    print("k",k,"K recursion == brute (n<=8):",okK," J recursion == brute (n<=2k):",okJ)
# e_n, J_n(k-1), d_{n,k} for n in {2k-1,2k}, k=8..12 via exact polynomials
for k in range(8,13):
    K=K_rec(2*k,k); J=J_rec(2*k,k)
    for n in (2*k-1,2*k):
        e=sp.diff(K[n],y,2).subs(y,k); Jv=J[n].subs(z,k-1)
        A=lambda l: K_rec(n,l+1)[n].subs(y,l+1) if l>=0 else 0
        print(f"n={n} k={k} e_n={e} J={Jv} e>J:{e>Jv} ratio={float(e)/float(Jv):.7f}")
# (ㅅ) exact
F=Fraction
v=F(699,100)-F(7,2)-(6*F(699,100)+F(3,4))/31-(13*F(699,100)/2)/961-12*F(699,100)/30000
print("(ㅅ) value",v, v==F(495594511,240250000), float(v))
print("5.642*1.6809*0.39893-0.0163-3.554 =",float(F('5.642')*F('1.6809')*F('0.39893')-F('0.0163')-F('3.554')))
# (ㄴ) residual expansion
x,g=sp.symbols('x gamma',positive=True)
def coefs(gam):
    u=(1+gam)/2
    C1=(1-u)/gam**2; C2=-(1-u)*(2+u)/gam**5; C3=sp.Rational(5,2)*(1-u)*(6+gam-gam**2)/gam**8
    return u+x*C1+x**2*C2+x**3*C3
gshift=g*sp.sqrt(1+4*x/g**2)
R=(coefs(g)-1)*coefs(gshift)+(1-g**2)/4
ser=sp.series(R,x,0,5).removeO()
for i in range(5):
    c=sp.simplify(ser.coeff(x,i))
    print("x^%d coeff:"%i, c if i<4 else "", " at gamma=1/3:", sp.nsimplify(c.subs(g,sp.Rational(1,3))))
# (ㄷ) g(kappa) series
kap,th,nu=sp.symbols('kappa theta nu')
Nt=3+(nu+1-th)*kap
xx=(1-th*kap)*kap/Nt**2
xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
gam_n=sp.sqrt(1-4*xn)
u=(1+gam_n)/2
C1=(1-u)/gam_n**2; C2=-(1-u)*(2+u)/gam_n**5; C3=sp.Rational(5,2)*(1-u)*(6+gam_n-gam_n**2)/gam_n**8
uhat=u+xx*C1+xx**2*C2+xx**3*C3
gfun=(Nt*uhat-2-nu*kap)/kap
s=sp.series(gfun,kap,0,5).removeO()
for i in range(5):
    print("kappa^%d:"%i, sp.factor(sp.simplify(s.coeff(kap,i))))
g3=sp.simplify(s.coeff(kap,3)); g4=sp.simplify(s.coeff(kap,4))
import numpy as np
for nv in (0,-1):
    f3=sp.lambdify(th,g3.subs(nu,nv)); f4=sp.lambdify(th,g4.subs(nu,nv))
    ts=np.linspace(0,1,2001)
    print("nu",nv,"max|g3|",max(abs(f3(t)) for t in ts),"max|g4|",max(abs(f4(t)) for t in ts))
