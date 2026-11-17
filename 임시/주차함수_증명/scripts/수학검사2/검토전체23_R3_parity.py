# R3 검산: 보조정리 kernel-crude, parity-tail(Z^{(2)}_j ⪯ dc'_j (1-z)^{-ϑ'_j}), laurent-coeff 네 경우를 계수로 확인.
from fractions import Fraction as Fr
from math import comb, exp, lgamma, log
import mpmath as mp
M = 60
Ren = [0.0] + [exp(-m + m*log(m) - lgamma(m+1)) for m in range(1, M+1)]
cb = [comb(2*m, m)/4**m for m in range(0, M+1)]
r = [Ren[m]/cb[m] for m in range(1, M+1)]
assert all(r[i] > r[i+1] for i in range(len(r)-1)) and abs(r[0]-2/exp(1)) < 1e-15
def mul(a, b):
    c = [0.0]*(M+1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            if i+j > M: break
            c[i+j] += x*y
    return c
def der(a): return [(i+1)*a[i+1] for i in range(M)] + [0.0]
def zmul(a): return [0.0] + a[:M]
inv = [1.0]*(M+1)
C = Ren[:]
Z = {1: zmul(C)}
for j in range(2, 8):
    t = [u + 2*v for u, v in zip(der(Z[j-1]), mul(inv, Z[j-1]))]
    Z[j] = mul(C, zmul(t))
th = lambda j: 1.5*j - 1
dc = {2: 2.0}
for j in range(2, 8): dc[j+1] = 0.75*(th(j)+2)*dc[j]
ok = True
for j in range(2, 8):
    for U in range(0, M-8):   # derivative truncation makes top coefficients unreliable
        bound = dc[j]*float(mp.binomial(U+th(j)-1, U))
        if Z[j][U] > bound*(1+1e-12): ok = False; print("parity-tail FAIL", j, U, Z[j][U], bound)
print("parity-tail holds on checked coefficients:", ok, " e.g. Z_2[10], bound:", Z[2][10], dc[2]*float(mp.binomial(10+1, 10)))
# laurent-coeff four cases
mp.mp.dps = 30
def coef(i, U): return mp.taylor(lambda zz: (1-zz)**(mp.mpf(i)/2), 0, U)[U]
for U in (1, 3, 7):
    cbU = mp.binomial(2*U, U)/mp.mpf(4)**U
    for Up in (1, 2, 4):
        assert abs(coef(-2*Up, U) - mp.binomial(U+Up-1, Up-1)) < 1e-15
        v3 = cbU*mp.fprod([U+mp.mpf(1)/2+t for t in range(Up)])/mp.fprod([mp.mpf(1)/2+t for t in range(Up)])
        assert abs(coef(-(2*Up+1), U) - v3) < 1e-12*abs(v3)
        v4 = cbU*mp.fprod([-(mp.mpf(1)/2+t) for t in range(Up)])/mp.fprod([U-mp.mpf(1)/2-t for t in range(Up)])
        assert abs(coef(2*Up-1, U) - v4) < 1e-12*max(1, abs(v4)), (U, Up, coef(2*Up-1, U), v4)
    assert abs(coef(-1, U) - cbU) < 1e-15 and abs(coef(1, U) + cbU/(2*U-1)) < 1e-15
print("laurent-coeff four cases ok")
