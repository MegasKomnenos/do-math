# F13: D.self-consistent-constants 세 범위 상수와 따름정리 S' 세 값의 독립 재계산 (mpmath 60자리)
from mpmath import mp, mpf, e, ceil, factorial, exp
from fractions import Fraction as Fr
mp.dps = 60
def acirc(n):  # p_n/n! = (n+1)^{n-1}/n!
    return Fr((n+1)**(n-1), 1) / Fr(__import__('math').factorial(n)) if n>=1 else Fr(1)
def xk(k): return Fr(k, k+1)**(k-1)
ranges = [(Fr(267,100),25,501,Fr(13,100)), (Fr(27,10),70,1855,Fr(2,25)), (Fr(271,100),100,6098,Fr(11,200))]
for L, J, k0, y in ranges:
    # j*
    m = 0
    while Fr(m+3, m+2)**(m+1) < L: m += 1   # find max m with (1+1/(m+1))^m < L
    jstar = m
    assert Fr(jstar+2, jstar+1)**jstar < L and not (Fr(jstar+3, jstar+2)**(jstar+1) < L)
    kR = max(2*jstar+2, int(ceil(mpf(L.numerator)/L.denominator)**(jstar+2) / mpf(acirc(jstar+1).numerator)*acirc(jstar+1).denominator)) if False else None
    val = (mpf(L.numerator)/L.denominator)**(jstar+2) / (mpf(acirc(jstar+1).numerator)/acirc(jstar+1).denominator)
    kR = max(2*jstar+2, int(ceil(val)))
    # E_under
    Lm = mpf(L.numerator)/L.denominator
    Eu = mpf(0)
    aJ = acirc(J)
    for i in range(1, k0-jstar+1):
        r = acirc(J+i)/aJ
        Eu += (mpf(r.numerator)/r.denominator) * exp(-i)
    Einf = (Lm/e)*(1-(Lm/e)**k0)/(1-Lm/e)
    R = max(1/(1+Eu), 1/(1+Einf))
    fall = [mpf(acirc(x).numerator)/acirc(x).denominator * Lm**(-(x+1)) for x in range(J)]
    qlow = []
    for x in range(J):
        s = sum(mpf(acirc(j).numerator)/acirc(j).denominator * Lm**(-(j+1)) for j in range(x))
        qlow.append(max(mpf(0), 1-s))
    Xi = sum(max(mpf(0), fall[x]-R*qlow[x]) for x in range(J))
    x0 = mpf(xk(k0).numerator)/xk(k0).denominator
    Xik = sum(max(mpf(0), mpf(acirc(x).numerator)/acirc(x).denominator * x0 * Lm**(-x) - R*qlow[x]) for x in range(J))
    A0 = x0 + Xik/(Lm*(1-Xi)); B0 = R*(1+Xik/(1-Xi))
    xi = mpf(1)/k0; ym = mpf(y.numerator)/y.denominator
    val2 = (ym-xi)*(ym-2*xi-xi**2) - (1+xi)**2*(A0*xi+B0*ym)
    vertex = (3*xi+xi**2)/2 + (1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={jstar} kR={kR} R={mp.nstr(R,10)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik,8)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)} | S' value={mp.nstr(val2,6)} vertex={mp.nstr(vertex,6)} <= y={ym}: {vertex<=ym}")
    print("   Eu=",mp.nstr(Eu,8)," Einf=",mp.nstr(Einf,8), " 1/(1+Eu)=",mp.nstr(1/(1+Eu),8)," 1/(1+Einf)=",mp.nstr(1/(1+Einf),8))
