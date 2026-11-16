# M13 item D.self-consistent-constants: recompute the three-range constants of Theorem S and Corollary S'.
from mpmath import mp, mpf, e as E, ceil, factorial, log
from fractions import Fraction as F
mp.dps=60
def acirc(m): return mpf((m+1)**(m-1))/factorial(m) if m>0 else mpf(1)
def xk(k): return (mpf(k)/(k+1))**(k-1)
for (L,J,k0,y) in [(F(267,100),25,501,F(13,100)),(F(27,10),70,1855,F(2,25)),(F(271,100),100,6098,F(11,200))]:
    Lm=mpf(L.numerator)/L.denominator
    m=0
    while acirc(m+2)/acirc(m+1)<Lm: m+=1
    jstar=m
    kR=max(2*jstar+2,int(ceil(Lm**(jstar+2)/acirc(jstar+1))))
    EJ=sum(acirc(J+i)/acirc(J)*E**(-i) for i in range(1,k0-jstar+1))
    Einf=(Lm/E)*(1-(Lm/E)**k0)/(1-Lm/E)
    R=max(1/(1+EJ),1/(1+Einf))
    fall=[acirc(x)*Lm**(-(x+1)) for x in range(J)]
    q=[max(mpf(0),1-sum(acirc(j)*Lm**(-(j+1)) for j in range(x))) for x in range(J)]
    Xi=sum(max(mpf(0),fall[x]-R*q[x]) for x in range(J))
    Xik=sum(max(mpf(0),acirc(x)*xk(k0)*Lm**(-x)-R*q[x]) for x in range(J))
    A0=xk(k0)+Xik/(Lm*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    xi=mpf(1)/k0; ym=mpf(y.numerator)/y.denominator
    g=lambda A,B:(ym-xi)*(ym-2*xi-xi**2)-(1+xi)**2*(A*xi+B*ym)
    print(f"L={L} J={J} k0={k0}: j*={jstar} kR={kR} R={mp.nstr(R,10)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik,8)} A0={mp.nstr(A0,8)} B0={mp.nstr(B0,8)} g_exact={mp.nstr(g(A0,B0),6)} vertex/k^2={mp.nstr((3*xi+xi**2)/2+(1+xi)**2*B0/2,5)}")
tab={1:(mpf('1.4708'),mpf('0.098505')),2:(mpf('2.5335'),mpf('0.060259')),3:(mpf('2.7354'),mpf('0.0422'))}
for i,(k0,y) in enumerate([(501,F(13,100)),(1855,F(2,25)),(6098,F(11,200))],1):
    xi=mpf(1)/k0; ym=mpf(y.numerator)/y.denominator; A,B=tab[i]
    print(f"range {i} with table (rounded-up) A0,B0: g={mp.nstr((ym-xi)*(ym-2*xi-xi**2)-(1+xi)**2*(A*xi+B*ym),6)}")
