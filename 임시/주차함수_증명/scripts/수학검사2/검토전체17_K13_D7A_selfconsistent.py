# K13: recompute the constants of theorem S (three ranges) and the three values of corollary S'
from fractions import Fraction as F
from math import factorial
import mpmath as mp
mp.mp.dps=60
def ac(m): return F((m+1)**(m-1), factorial(m)) if m>=1 else F(1)
def run(L, J, k0, Y):
    # j*
    m=0
    while ac(m+2)/ac(m+1) < L: m+=1   # e^{g(m+1)} = a_{m+1}/a_m ; find max m with a_{m+1}/a_m < L
    # above loop: find smallest m such that a_{m+2}/a_{m+1} >= L  -> j* = m
    jstar=m
    assert ac(jstar+1)/ac(jstar) < L and ac(jstar+2)/ac(jstar+1) >= L
    kR=max(2*jstar+2, -(-L**(jstar+2)//ac(jstar+1)) )
    kR=max(2*jstar+2, int(mp.ceil(mp.mpf(L.numerator)/L.denominator)) ) if False else kR
    # E_J lower, E_inf  (high precision floats)
    Lm=mp.mpf(L.numerator)/L.denominator
    EJ=mp.fsum( (mp.mpf((ac(J+i)/ac(J)).numerator)/(ac(J+i)/ac(J)).denominator)*mp.e**(-i) for i in range(1,k0-jstar+1))
    q=Lm/mp.e; Einf=q*(1-q**k0)/(1-q)
    RJ=max(1/(1+EJ),1/(1+Einf))
    # use RJ slightly rounded up as rational (8+ digits) - the paper rounds up; here just use exact high precision
    RJ_r=F(str(mp.nstr(RJ,30)))  # rational approx
    RJ_r+=F(1,10**29)
    fall=[ac(x)*L**(-(x+1)) for x in range(J)]
    qlow=[max(F(0),1-sum(ac(j)*L**(-(j+1)) for j in range(x))) for x in range(J)]
    Xi=sum(max(F(0),fall[x]-RJ_r*qlow[x]) for x in range(J))
    xk=F(k0,k0+1)**(k0-1)
    Xik=sum(max(F(0),ac(x)*xk*L**(-x)-RJ_r*qlow[x]) for x in range(J))
    A0=xk+Xik/(L*(1-Xi)); B0=RJ_r*(1+Xik/(1-Xi))
    xi=F(1,k0)
    val=(Y-xi)*(Y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*Y)
    vert=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={jstar} kR={kR} RJ={mp.nstr(RJ,10)} Xi={float(Xi):.7f} Xik={float(Xik):.7f} A0={float(A0):.6f} B0={float(B0):.7f} val={float(val):.4e} vertex={float(vert):.5f}<=Y={float(Y)} {vert<=Y}")
    return A0,B0
for (L,J,k0,Y,A0t,B0t) in [(F(267,100),25,501,F(13,100),F(14708,10**4),F(98505,10**6)),(F(27,10),70,1855,F(2,25),F(25335,10**4),F(60259,10**6)),(F(271,100),100,6098,F(11,200),F(27354,10**4),F(422,10**4))]:
    run(L,J,k0,Y)
    xi=F(1,k0); v=(Y-xi)*(Y-2*xi-xi*xi)-(1+xi)**2*(A0t*xi+B0t*Y); print('   with table-rounded A0,B0: val=%.4e'%float(v))
