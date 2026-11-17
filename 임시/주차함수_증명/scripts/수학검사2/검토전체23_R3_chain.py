# R3 검산: 5.2.3절 — W^{[1]}, W^{[2]}의 닫힌 꼴, 전달 다항식, 표시 사슬 합 생성함수 재귀 (Y_j, O_j)를
# 직접 열거와 대조한다. Ren(m)은 임의의 유리수열로 두어도 재귀 항등식은 성립해야 한다.
import sympy as sp, itertools, random
from fractions import Fraction as Fr
z, t = sp.symbols('z t')   # t = 1/n
M = 9   # truncation degree in z
random.seed(3)
Ren = {m: sp.Rational(random.randint(1, 9), random.randint(1, 9)) for m in range(1, M+3)}
C = sum(Ren[m]*z**m for m in range(1, M+3))
def trunc(e, N=M+2):
    e = sp.expand(e)
    return sum(e.coeff(z, i)*z**i for i in range(0, N+1))
def lc(i, d):
    return sp.Rational(1, i)*(sp.Rational(d**(i+1), i+1) + 2*d**i - sum(r**i for r in range(d)))
def W_series(gam, order=2):
    # log W = log nf(n, d_j - 1) - sum_{i<j} log(1-(d_i-1)/n), expand in t=1/n
    part = list(itertools.accumulate(gam))
    dj = part[-1]
    L = sum(lc(i, dj-1)*t**i for i in range(1, order+1)) + sum(sum(sp.Rational((di-1)**s, s)*t**s for s in range(1, order+1)) for di in part[:-1])
    W = sp.series(sp.exp(L), t, 0, order+1).removeO()
    return [W.coeff(t, s) for s in range(order+1)]
# direct check of nf log coefficients against definition for a sample
def nf(n, d):
    return sp.exp(d)*sp.factorial(n)/sp.factorial(n-d)*sp.Integer(n-d)**(n-d-2)/sp.Integer(n)**(n-2)
import mpmath as mp
mp.mp.dps = 40
n0, d0 = 4000, 7
approx = mp.log(mp.e**d0*mp.factorial(n0)/mp.factorial(n0-d0)*mp.mpf(n0-d0)**(n0-d0-2)/mp.mpf(n0)**(n0-2))
ser = sum(mp.mpf(sp.N(lc(i, d0), 40))*mp.mpf(n0)**(-i) for i in range(1, 12))
print("log nf check:", approx, ser)
okLN = True
def Lf(gam):
    part = list(itertools.accumulate(gam)); dj = part[-1]
    return sp.Rational(5, 2)*(dj-1) + sum(di-1 for di in part[:-1])
def Nf(gam):
    part = list(itertools.accumulate(gam)); dj = part[-1]
    return Lf(gam)**2/2 + sp.Rational(5, 4)*(dj-1)**2 - sp.Rational(dj-1, 12) + sp.Rational(1, 2)*sum((di-1)**2 for di in part[:-1])
for gam in [(1,), (3,), (2, 1), (1, 4, 2), (3, 3, 1, 2)]:
    w = W_series(gam)
    if w[1] != Lf(gam) or w[2] != Nf(gam): okLN = False; print("L/N FAIL", gam)
    j = len(gam)
    if j >= 2:
        g = gam[0]; gp = gam[1:]
        if Lf(gam) != Lf(gp) + (j+sp.Rational(3, 2))*g - 1: okLN = False; print("L split FAIL", gam)
        if Nf(gam) != Nf(gp) + ((j+sp.Rational(5, 2))*g-1)*Lf(gp) + sp.Rational(1, 2)*(j+sp.Rational(3, 2))*(j+sp.Rational(5, 2))*g*g - (j+sp.Rational(31, 12))*g + 1:
            okLN = False; print("N split FAIL", gam)
print("L, N closed forms and splittings ok:", okLN)
# direct enumeration of Ch^{[s]}_j(d)
def comps(j, maxsum):
    if j == 0:
        yield ()
        return
    for g in range(1, maxsum - (j-1) + 1):
        for rest in comps(j-1, maxsum-g):
            yield (g,)+rest
def Ch(j, d, s):
    tot = 0
    for gam in comps(j, d-1):
        part = list(itertools.accumulate(gam))
        w = [1, Lf(gam), Nf(gam)][s]
        term = w
        for g in gam: term *= Ren[g]
        for di in part: term *= max(d-di, 0)
        tot += term
    return tot
Cp = sp.diff(C, z); zCp = z*Cp; zzCpp = z*sp.diff(zCp, z)
Z = {1: trunc(z*C)}
Y = {1: trunc(sp.Rational(5, 2)*z*(zCp - C))}
O = {1: trunc(z*(sp.Rational(35, 8)*(zzCpp - 2*zCp + C) - sp.Rational(1, 12)*(zCp - C)))}
inv = sum(z**i for i in range(0, M+3))   # 1/(1-z) truncated
def op(F): return trunc(z*(sp.diff(F, z) + 2*inv*F))
for j in range(2, 5):
    Z[j] = trunc(C*op(Z[j-1]))
    Y[j] = trunc(C*op(Y[j-1]) + ((j+sp.Rational(3, 2))*zCp - C)*op(Z[j-1]))
    O[j] = trunc(C*op(O[j-1]) + ((j+sp.Rational(5, 2))*zCp - C)*op(Y[j-1]) + (sp.Rational((2*j+3)*(2*j+5), 8)*zzCpp - (j+sp.Rational(31, 12))*zCp + C)*op(Z[j-1]))
ok = True
for j in range(1, 5):
    for r in range(0, M-1):
        for s, G in ((0, Z), (1, Y), (2, O)):
            lhs = Ch(j, r+2, s) - 2*Ch(j, r+1, s) + Ch(j, r, s)
            rhs = sp.expand(G[j]).coeff(z, r+2)
            if sp.simplify(lhs - rhs) != 0: ok = False; print("GF FAIL", j, r, s, lhs, rhs)
print("generating-function recursions (Z, Y, O) match enumeration:", ok)
