# P6 검산: 7A 장의 수치·부등식을 브루트포스/정밀 계산으로 다시 센다.
from fractions import Fraction as Fr
from itertools import permutations, product
from math import comb, factorial, log, exp, sqrt, cosh, ceil
import mpmath as mp
mp.mp.dps = 60

def caps(sig):
    n=len(sig); h=[0]*n
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h[i]=i-j
    return h

def A(n,l):
    # A_{n,l}: PF of length n with max displacement <= l (l>=-1)
    if l<0: return 0
    if n==0: return 1
    s=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); p=1
        for x in h: p*=min(x,l+1)
        s+=p
    return s

print("== 7.1 old-6-2: mu_n(k)=E[v_k(Z,H)] brute force n<=6 ==")
ok=True
for n in range(1,7):
    for k in range(2,n+1):
        num=Fr(0); den=0
        for sig in permutations(range(1,n+1)):
            h=caps(sig); w=1
            for x in h: w*=min(x,k)
            Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
            num+=w*((Fr(k+1,k))**Z+(Fr(k-1,k))**(Z+H)-2); den+=w
        d=A(n,k)-2*A(n,k-1)+A(n,k-2)
        if num/den!=Fr(d,A(n,k-1)): ok=False; print("FAIL",n,k)
print("ok" if ok else "FAIL")

print("== 7.2 old-6-6: E[Z_k]>=(n-k)/(k+1) and factorial moment, brute n<=7 ==")
ok=True
for n in range(1,8):
    for k in range(1,n+1):
        num=Fr(0); num2=Fr(0); den=0
        for sig in permutations(range(1,n+1)):
            h=caps(sig); w=1
            for x in h: w*=min(x,k)
            Z=sum(1 for x in h if x>k)
            num+=w*Z; num2+=w*Z*(Z-1); den+=w
        m=Fr(n-k,k+1)
        if num/den<m: ok=False; print("FAIL mean",n,k)
        if m>=1 and num2/den<m*(m-1): ok=False; print("FAIL fact",n,k)
print("ok" if ok else "FAIL")

print("== 7.2 old-6-7: Z > x^flat R^{-o_k}, exact-ish check n<=8 ==")
ok=True
for n in range(0,9):
    for k in range(2,n+2):
        a0=A(n,k-2); a1=A(n,k-1); a2=A(n,k)
        R=mp.mpf(a2)/a1; Zr=mp.mpf(a0)/a1
        xf=mp.mpf(k-1)/k; ok_=mp.mpf(k+1)/k
        o=-2*mp.log(xf)/mp.log(ok_)
        if not (Zr> xf*R**(-o)): ok=False; print("FAIL",n,k,Zr,xf*R**(-o))
print("ok" if ok else "FAIL")

print("== 7.2 old-6-10: E[kH_k] <= x_k n, equality n=k, brute n<=7 ==")
ok=True
for n in range(1,8):
    for k in range(2,n+1):
        num=Fr(0); den=0
        for sig in permutations(range(1,n+1)):
            h=caps(sig); w=1
            for x in h: w*=min(x,k)
            H=sum(1 for x in h if x==k)
            num+=w*k*H; den+=w
        xk=Fr(k,k+1)**(k-1)
        if num/den>xk*n: ok=False; print("FAIL",n,k)
        if n==k and num/den!=xk*n: ok=False; print("FAIL eq",n,k)
print("ok" if ok else "FAIL")

print("== 7.1 t_k and n^sharp_k, 7.2 n^flat_k <= n^sharp_k for small k ==")
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1)>=2*k**(2*j+1)): j+=1
    return j
for k in [2,3,5,10,41,100,501,2000]:
    t=tk(k); ns=k+(k+1)*t
    xs=1+mp.mpf(1)/k; xf=1-mp.mpf(1)/k; xk=(mp.mpf(k)/(k+1))**(k-1)
    def phi(n): 
        m=mp.mpf(n-k)/(k+1); return xs**m+xf**(m+xk*n/k)-2
    nf=2*k+1
    while phi(nf)<0: nf+=1
    print(k,"t_k=",t,"n#=",ns,"nb=",nf, "phi(2k+1)<0:",phi(2*k+1)<0,"phi(n#)>=0:",phi(ns)>=0, "nb<=n#:",nf<=ns)

print("== column-lemma integer inequality ==")
print(10**21*400**10>17**21*123**10, 10**21*400**10, 17**21*123**10)
print("o_41 <= 2.1:", float(-2*log(40/41)/log(42/41)), "phi#(1.7)>0 at k=41:", 1.7+ (40/41)*1.7**(-(-2*log(40/41)/log(42/41)))-2)

print("== self-consistent-S table ==")
def a0(m): return Fr(1) if m==0 else Fr((m+1)**(m-1), factorial(m))
def egr(m): return a0(m+1)/a0(m)
for (Ls,J,k0,yS) in [("267/100",25,501,Fr(13,100)),("27/10",70,1855,Fr(2,25)),("271/100",100,6098,Fr(11,200))]:
    L=Fr(Ls)
    j=0
    while egr(j+1)<L: j+=1
    jstar=j
    kR=max(2*jstar+2, ceil(L**(jstar+2)/a0(jstar+1)))
    E_und=sum(mp.mpf(a0(J+i)/a0(J))*mp.e**(-i) for i in range(1,k0-jstar+1))
    Le=mp.mpf(L)/mp.e
    E_inf=Le*(1-Le**k0)/(1-Le)
    RJ=max(1/(1+E_und),1/(1+E_inf))
    xb=[mp.mpf(a0(v))*mp.mpf(L)**(-(v+1)) for v in range(J)]
    qu=[max(mp.mpf(0),1-sum(mp.mpf(a0(jj))*mp.mpf(L)**(-(jj+1)) for jj in range(v))) for v in range(J)]
    Xi=sum(max(mp.mpf(0),xb[v]-RJ*qu[v]) for v in range(J))
    xk0=(mp.mpf(k0)/(k0+1))**(k0-1)
    Xik=sum(max(mp.mpf(0),mp.mpf(a0(v))*xk0*mp.mpf(L)**(-v)-RJ*qu[v]) for v in range(J))
    A0=xk0+Xik/(mp.mpf(L)*(1-Xi)); B0=RJ*(1+Xik/(1-Xi))
    xi=mp.mpf(1)/k0; y=mp.mpf(yS)
    g=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={Ls} J={J} k0={k0}: j*={jstar} kR={kR} RJ={mp.nstr(RJ,10)} Xi={mp.nstr(Xi,8)} Xik={mp.nstr(Xik,8)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)} g={mp.nstr(g,5)} vert={mp.nstr(vert,5)}<=y:{vert<=y}")

print("== polar-N numerics ==")
k=2001
print("2/sqrt(2001)=",2/sqrt(2001), " e^{-1+2/2002}=",exp(-1+2/2002), " 0.75/sqrt(k)=",0.75/sqrt(k), " 2k^1.5+1=",2*k**1.5+1, " 0.3476k^2=",0.3476*k*k)
print("x_2001=",(2001/2002)**2000)
print("== polar-W k>=1e7 constants ==")
k=10**7
print("(1+0.91/sqrt k)^3*8=",8*(1+0.91/sqrt(k))**3, " 8.344/sqrt(k)=",8.344/sqrt(k))
print("== riccati counterexample (k,z,n)=(3,1,2) ==")
# LHS: sum over sigma of prod min(h,3) * H_1
lhs=0
for sig in permutations([1,2]):
    h=caps(sig); w=1
    for x in h: w*=min(x,3)
    lhs+=w*sum(1 for x in h if x==1)
print("lhs=",lhs)
# RHS series: A_{2}(x)=sum A_{n,2} x^n/n!, Q_2=2x+x^2/2
x=mp.mpf
import sympy as sp
X=sp.symbols('x')
Q2=2*X+X**2/2
Ex=sp.exp(-Q2)
Delta=1-3*sp.integrate(Ex,(X,0,X))
Ak=Ex/Delta
O1=X
rhs=Ak*O1+3*Ex/Delta**2*sp.integrate(O1*Ex,(X,0,X))
print("rhs coeff*2!=", sp.series(rhs,X,0,3).coeff(X,2)*2)
print("== rho_2 = ln 2 check: A_{n,1} Fubini ==")
print([A(n,1) for n in range(0,6)])
