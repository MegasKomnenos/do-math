# D.central-gap-rational-audit: a_0, a_1, the fraction 495594511/240250000, the final margin, and the x^4 coefficient of R at gamma=1/3.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from fractions import Fraction as F
from mpmath import mp, mpf, gamma, quad, exp, inf
mp.dps = 30
a0 = quad(lambda w: exp(-w**3/3), [0, inf]); a1 = quad(lambda w: w*exp(-w**3/3), [0, inf])
print("a0", a0, 3**mpf(-2)/3*0 + mpf(3)**(-mpf(2)/3)*gamma(mpf(1)/3), " a1", a1, mpf(3)**(-mpf(1)/3)*gamma(mpf(2)/3))
print("1.287899<a0<1.2879:", 1.287899 < a0 < 1.2879, " 0.938892<a1<0.939:", 0.938892 < a1 < 0.939)
om = F(699,100)
val = om - F(7,2) - (4*om + F(1,2))*F(3,2)/31 - F(13,2)*om*1/961 - 12*om/30000
print("fraction:", val, "==495594511/240250000:", val == F(495594511,240250000), float(val))
print("0.213 check:", 5.642*1.6809*0.39893 - 0.0163 - 3.554)
# x^4 coefficient of R(iota) = (uhat(iota)-1) uhat(iota-x) + iota at gamma=1/3, as Laurent in gamma
import sympy as sp
g, x, t = sp.symbols('gamma x t', positive=True)
up = (1+g)/2
C1 = (1-up)/g**2; C2 = -(1-up)*(2+up)/g**5; C3 = sp.Rational(5,2)*(1-up)*(6+g-g**2)/g**8
uhat = up + x*C1 + x**2*C2 + x**3*C3
# iota = (1-g^2)/4 ; at iota - x: gamma' = sqrt(g^2+4x)
gp = sp.sqrt(g**2 + 4*x)
uhat_shift = uhat.subs(g, gp)
R = (uhat - 1)*uhat_shift + (1-g**2)/4
ser = sp.series(R, x, 0, 5).removeO()
for i in range(5):
    c = sp.simplify(sp.expand(ser.coeff(x, i)))
    print("x^%d coeff:" % i, sp.simplify(c), " at gamma=1/3:", sp.nsimplify(c.subs(g, sp.Rational(1,3))))
