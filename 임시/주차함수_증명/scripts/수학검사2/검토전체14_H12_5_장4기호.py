# H12 검산 5: D.central-gap-rational-audit 의 기호·유리수 항목 일부를 독립 재계산
import sympy as sp
from fractions import Fraction as Fr
import math
g,x,kap,th=sp.symbols('gamma x kappa theta')
# (ㄴ) residual R(iota) = (uhat(iota)-1)*uhat(iota-x)+iota, with gamma=sqrt(1-4 iota)
def uhat_of_gamma(G):
    u0=(1+G)/2
    C1=(1-u0)/G**2; C2=-(1-u0)*(2+u0)/G**5; C3=sp.Rational(5,2)*(1-u0)*(6+G-G**2)/G**8
    return u0+x*C1+x**2*C2+x**3*C3
iota=(1-g**2)/4
Gm=sp.sqrt(g**2+4*x)          # gamma(iota-x)=sqrt(1-4iota+4x)
Rres=(uhat_of_gamma(g)-1)*uhat_of_gamma(Gm)+iota
ser=sp.series(Rres,x,0,5).removeO()
for d in range(0,5):
    c=sp.simplify(sp.expand(ser.coeff(x,d)))
    print("x^%d coeff:"%d, c if d<4 else "(see below)")
c4=sp.simplify(ser.coeff(x,4)); print("x^4 coeff at gamma=1/3:", sp.nsimplify(c4.subs(g,sp.Rational(1,3))))
print("x^4 coeff numeric gamma=1/3:", float(c4.subs(g,sp.Rational(1,3))))
# (ㄷ) g(kappa) Taylor coefficients
for nu in (0,-1):
    Nt=3+(nu+1-th)*kap
    xx=(1-th*kap)*kap/Nt**2
    xn=(2+(nu-1)*kap)*(1-th*kap)/Nt**2
    G=sp.sqrt(1-4*xn)
    u0=(1+G)/2
    C1=(1-u0)/G**2; C2=-(1-u0)*(2+u0)/G**5; C3=sp.Rational(5,2)*(1-u0)*(6+G-G**2)/G**8
    uh=u0+xx*C1+xx**2*C2+xx**3*C3
    gk=(Nt*uh-2-nu*kap)/kap
    s=sp.series(gk,kap,0,5).removeO()
    coeffs=[sp.expand(sp.simplify(s.coeff(kap,d))) for d in range(0,5)]
    print("nu=",nu)
    for d,c in enumerate(coeffs): print("  kappa^%d:"%d, c)
    for d in (3,4):
        poly=sp.Poly(coeffs[d],th)
        # max |.| on [0,1]: check endpoints and critical points
        vals=[abs(float(coeffs[d].subs(th,t))) for t in (0,1)]
        for r in sp.real_roots(sp.diff(coeffs[d],th)):
            rv=float(r)
            if 0<=rv<=1: vals.append(abs(float(coeffs[d].subs(th,rv))))
        print("  max|g_%d| on [0,1] ="%d, max(vals))
# corollary (나),(다) exact rationals
w=Fr(699,100)
val=w-Fr(7,2)-(4*w+Fr(1,2))*Fr(3,2)*Fr(1,31)-Fr(13,2)*w*1*Fr(1,961)-12*w*Fr(1,30000)
print("(나) exact:",val, "== 495594511/240250000:", val==Fr(495594511,240250000), float(val))
w=Fr(698,100); a0=Fr(12879,10000); a1=Fr(939,1000); k13=Fr(464159,10**7); k23=k13**2
val2=w-Fr(7,2)-(4*w+Fr(1,2))*a0*k13-Fr(13,2)*w*a1*k23-12*w*Fr(1,10000)
print("(다) with k^{-1/3}<=0.0464159, k^{-2/3}<=0.0464159^2:",float(val2),">=1.6809:",val2>=Fr(16809,10000))
print("   10000^{-1/3}=",10000**(-1/3))
# two-corrections arithmetic
import mpmath as mp
print("46sqrt2-12 - 5000/173 - 0.02 =", float(46*mp.sqrt(2)-12-mp.mpf(5000)/173-mp.mpf('0.02')), ">24")
print("0.451*3*2.51+0.056+0.01 =",0.451*3*2.51+0.056+0.01)
print("46sqrt2-12-54.6828 =", float(46*mp.sqrt(2)-12-54.6828), "> -1.63")
print("0.4503*3*2.50663+1675.2/10000 =",0.4503*3*2.50663+1675.2/10000, "<3.554")
print("sqrt2/pi*e^(1/10000)=",float(mp.sqrt(2)/mp.pi*mp.e**(mp.mpf(1)/10000)), "<0.4503;  sqrt2/pi e^{1/30000}=",float(mp.sqrt(2)/mp.pi*mp.e**(mp.mpf(1)/30000)),"<0.451")
print("130(k/256)^6 e^{-k/512} k=30000:", float(130*(mp.mpf(30000)/256)**6*mp.e**(-mp.mpf(30000)/512)))
print("(2pi)^{-1/2}(1-1/120000)=",float((2*mp.pi)**-0.5*(1-mp.mpf(1)/120000)), ">=0.39893")
print("11/2*39/100*2-7/2=",5.5*0.39*2-3.5, " 79/100")
# 16988k+404903k^2+1000*100^5 k^3/(1-100k)+9300k at k=1/30000
kk=Fr(1,30000); print("Cauchy sum k=1/30000:",float(16988*kk+404903*kk**2+1000*100**5*kk**3/(1-100*kk)+9300*kk))
