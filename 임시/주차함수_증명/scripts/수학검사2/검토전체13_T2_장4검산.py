# T2 검산: 4장 gauss-contraction 잔차 계수, Hermite 하계, 중앙 틈 부호
import sympy as sp
from fractions import Fraction as Fr
from math import comb, log, sqrt, exp, lgamma
g,x=sp.symbols('gamma x',positive=True)
iota=(1-g**2)/4
ups=(1+g)/2
C1=(1-ups)/g**2; C2=-(1-ups)*(2+ups)/g**5; C3=sp.Rational(5,1)*(1-ups)*(6+g-g**2)/(2*g**8)
# function of iota via gamma: shift iota -> iota - x  means gamma -> sqrt(1-4(iota-x)) = sqrt(g^2+4x)
gs=sp.sqrt(g**2+4*x)
def hat(gg):
    u=(1+gg)/2
    c1=(1-u)/gg**2; c2=-(1-u)*(2+u)/gg**5; c3=sp.Rational(5,1)*(1-u)*(6+gg-gg**2)/(2*gg**8)
    return u+x*c1+x**2*c2+x**3*c3
R=(hat(g)-1)*hat(gs)+iota
ser=sp.series(R,x,0,4).removeO()
for p in range(4):
    print("x^%d coeff:"%p, sp.simplify(ser.coeff(x,p)))
# log-derivative signs of |C_i| over gamma in (1/3,1)
for name,C in [("C1",C1),("C2",-C2),("C3",C3)]:
    ld=sp.simplify(sp.diff(sp.log(C),g))
    vals=[ld.subs(g,sp.Rational(1,3)+sp.Rational(i,30)*2) for i in range(1,10)]
    print(name,"logderiv samples:",[float(v) for v in vals])
# Hermite lower bound check (다) at k=10000, y=k, n=2k
k=10000; y=k; n=2*k; N=n+y+1
He0,He1=1,N
for j in range(2,n+1):
    He0,He1=He1,N*He1-(j-1)*y*He0
logHe=log(He1)  # python can log big ints? use len-based
import math
def logbig(v):
    s=str(v); return math.log(10)*(len(s)-1)+math.log(float(s[0]+'.'+s[1:16]))
logHe=logbig(He1)
q=n*y/N**2; xx=y/N**2
uo=(1+sqrt(1-4*q))/2
U=N*uo; W=N*(2*uo-1)
bound=0.5*log(U/W)+n*log(U)+(N-U)**2/(2*y)-5.5*xx-350*n*xx**2
print("logHe",logHe,"bound",bound,"ok",logHe>=bound, "q",q,"x",xx, "5.5x+350nx^2",5.5*xx+350*n*xx**2, "<10/k",10/k)
# central gap sign for n<=60
def rows(Nn):
    A=[[0]*(Nn+2) for _ in range(Nn+1)]
    for l in range(Nn+2): A[0][l]=1
    for m in range(1,Nn+1):
        for l in range(0,Nn+1):
            A[m][l]=sum(comb(m-1,j)*min(j+1,l+1)*A[j][l]*A[m-1-j][l] for j in range(m))
    return A
A=rows(60)
bad=[]
for m in range(2,61):
    b=[A[m][l]-(A[m][l-1] if l>0 else 0) for l in range(m)]
    kn=-(-m//2)
    d=b[kn]-b[kn-1]
    tail_dec=all(b[j]>=b[j+1] for j in range(kn,m-1))
    if m<=15 and not (d<0 and tail_dec): bad.append((m,d,tail_dec))
    if m>=16 and not d>0: bad.append((m,d))
print("central gap anomalies n<=60:",bad)
