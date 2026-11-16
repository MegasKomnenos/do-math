from fractions import Fraction as F
from mpmath import mp, mpf, exp, ceil, log
mp.dps=60
def ao(m):  # a°_m = (m+1)^{m-1}/m!
    from math import factorial
    return F((m+1)**(m-1), factorial(m)) if m>=1 else F(1)
def ratio(m): return (1+F(1,m+1))**m  # a°_{m+1}/a°_m
tiers=[(F(267,100),25,501,F(13,100)),(F(27,10),70,1855,F(2,25)),(F(271,100),100,6098,F(11,200))]
for s,J,k0,y in tiers:
    m=0
    while ratio(m+1)<s: m+=1
    jstar=m
    # check: ratio(m+1)=e^{g(m+1)}? e^{g(m+1)} = a°_{m+1}/a°_m = ratio(m)
    # j* = max{m: a°_{m+1}/a°_m < s}
    m=0
    while ratio(m+1)<s: m+=1
    jstar=m
    kR=max(2*jstar+2, -(-(s**(jstar+2))//ao(jstar+1)))
    kR=int(kR)
    sm=mpf(s.numerator)/s.denominator
    EJ=sum((mpf(ao(J+i).numerator)/ao(J+i).denominator)/(mpf(ao(J).numerator)/ao(J).denominator)*exp(-i) for i in range(1,k0-jstar+1))
    Einf=(sm/mp.e)*(1-(sm/mp.e)**k0)/(1-sm/mp.e)
    RJ=max(1/(1+EJ),1/(1+Einf))
    xbar=[mpf(ao(k).numerator)/ao(k).denominator*sm**(-(k+1)) for k in range(J)]
    q=[max(mpf(0),1-sum(mpf(ao(j).numerator)/ao(j).denominator*sm**(-(j+1)) for j in range(k))) for k in range(J)]
    Xi=sum(max(mpf(0),xbar[k]-RJ*q[k]) for k in range(J))
    xk=(mpf(k0)/(k0+1))**(k0-1)
    Xik=sum(max(mpf(0),mpf(ao(k).numerator)/ao(k).denominator*xk*sm**(-k)-RJ*q[k]) for k in range(J))
    A0=xk+Xik/(sm*(1-Xi)); B0=RJ*(1+Xik/(1-Xi))
    xi=mpf(1)/k0; ym=mpf(y.numerator)/y.denominator
    val=(ym-xi)*(ym-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*ym)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"s={s} J={J} k0={k0}: j*={jstar} kR={kR} RJ={mp.nstr(RJ,7)} Xi={mp.nstr(Xi,7)} Xik0={mp.nstr(Xik,7)} A0={mp.nstr(A0,6)} B0={mp.nstr(B0,6)} val={mp.nstr(val,5)} vertex={mp.nstr(vert,5)} y={ym}")
