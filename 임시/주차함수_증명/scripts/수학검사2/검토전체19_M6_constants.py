# M6: recompute constants of Theorem self-consistent-S table and Corollary S' values (mpmath high precision)
from fractions import Fraction as Fr
from math import factorial
import mpmath as mp
mp.mp.dps=50
def ac(m): return Fr((m+1)**(m-1),factorial(m)) if m>0 else Fr(1)
def free_ratio(m): return ac(m+1)/ac(m)
for (L,J,k0,y) in [(Fr(267,100),25,501,Fr(13,100)),(Fr(27,10),70,1855,Fr(2,25)),(Fr(271,100),100,6098,Fr(11,200))]:
    m=0
    while free_ratio(m+1)<L: m+=1
    jstar=m
    kR=max(2*jstar+2, -(-(L**(jstar+2))//ac(jstar+1)) )
    Lm=mp.mpf(L.numerator)/L.denominator
    Eund=sum(mp.mpf((ac(J+i)/ac(J)).numerator)/mp.mpf((ac(J+i)/ac(J)).denominator)*mp.e**(-i) for i in range(1,k0-jstar+1))
    Einf=(Lm/mp.e)*(1-(Lm/mp.e)**k0)/(1-Lm/mp.e)
    R=max(1/(1+Eund),1/(1+Einf))
    fall=lambda x: mp.mpf(ac(x).numerator)/ac(x).denominator*Lm**(-(x+1))
    def qund(x):
        s=sum(mp.mpf(ac(j).numerator)/ac(j).denominator*Lm**(-(j+1)) for j in range(x))
        return max(0,1-s)
    xk=lambda k: (mp.mpf(k)/(k+1))**(k-1)
    Xi=sum(max(0,fall(x)-R*qund(x)) for x in range(J))
    Xik=sum(max(0,mp.mpf(ac(x).numerator)/ac(x).denominator*xk(k0)*Lm**(-x)-R*qund(x)) for x in range(J))
    A0=xk(k0)+Xik/(Lm*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    xi=mp.mpf(1)/k0; ym=mp.mpf(y.numerator)/y.denominator
    val=(ym-xi)*(ym-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*ym)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={jstar} kR={kR} R={mp.nstr(R,10)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik,8)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)} val={mp.nstr(val,6)} vertex/k^2={mp.nstr(vert,6)} y k0^2-2k0-1={float(y)*k0**2-2*k0-1:.1f}")
# o_k bound, hf(17/10) check at k=41
k=41; xs=1+mp.mpf(1)/k; xf=1-mp.mpf(1)/k; ok=-2*mp.log(xf)/mp.log(xs)
print("o_41=",mp.nstr(ok,8),"<=2.1:",ok<=2.1," hf(1.7)=",mp.nstr(mp.mpf(1.7)-2+xf*mp.mpf(1.7)**(-ok),6))
print("(40/41)(10/17)^2.1=",mp.nstr(mp.mpf(40)/41*(mp.mpf(10)/17)**2.1,6))
# polar-N numbers
k=2001; print("2k^1.5+1=",mp.nstr(2*mp.mpf(k)**1.5+1,8)," 0.3476k^2=",0.3476*k*k, " 2/sqrt(k)=",mp.nstr(2/mp.sqrt(k),5), " e^{-1+2/(k+1)}=",mp.nstr(mp.e**(-1+mp.mpf(2)/(k+1)),6))
# rho_2 = log 2 check: C_2 = e^x -1 ; and A_1 EGF = 1/(2-e^x)
print("A_{n,1} from 1/(2-e^x):",[int(mp.nint(mp.taylor(lambda x:1/(2-mp.e**x),0,6)[n]*factorial(n))) for n in range(7)])
