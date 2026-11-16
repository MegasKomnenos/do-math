# 검토전체6 L7a: 보조정리 hermite-nu (나)(라)(마)의 계수와 명제 pair-check-10000의 수를 다시 센다.
import sympy as sp
from fractions import Fraction
from math import isqrt

# ---------- (나) H_0, H_1, H_2 ----------
w, nu, th = sp.symbols('w nu theta')   # w = 1/k
Nk = 3 + (nu + 1 - th) * w                      # N/k
x = w * (1 - th * w) / Nk**2                    # x = y/N^2 = (k-θ)/N^2 → in units: w(1-θw)/(N/k)^2
xn = (2 + (nu - 1) * w) * (1 - th * w) / Nk**2  # x_n = (n-1) x
gam = sp.sqrt(1 - 4 * xn)
ups0 = (1 + gam) / 2
C1 = (1 - ups0) / gam**2
C2 = -(1 - ups0) * (2 + ups0) / gam**5
C3 = 5 * (1 - ups0) * (6 + gam - gam**2) / (2 * gam**8)
upshat = ups0 + x * C1 + x**2 * C2 + x**3 * C3
H = (Nk * upshat - 2 - nu * w) / w
ser = sp.series(H, w, 0, 3).removeO()
ser = sp.expand(ser)
print("H_0 =", sp.simplify(ser.coeff(w, 0)))
print("H_1 =", sp.factor(sp.simplify(ser.coeff(w, 1))))
print("H_2 =", sp.expand(sp.simplify(ser.coeff(w, 2))))
# nm check
nm = sp.expand(sp.simplify((1 - 4 * xn) * Nk**2))
print("nm =", sp.collect(nm, w))

# ---------- (라) U_r, V_r via Hermite recursion ----------
k, d = sp.symbols('k d')
n = 2 * k + nu
N = 3 * k + nu + 1          # y = k, θ = 0
# He_{j-1} = (N He_j - He_{j+1})/(k j); He_n = (n+d) He_{n-1}; set He_{n-1} = 1
He = {n: n + d, n - 1: sp.Integer(1)}
for j in [n - 1, n - 2, n - 3, n - 4]:
    He[j - 1] = sp.simplify((N * He[j] - He[j + 1]) / (k * j))
def M(r):
    # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i C(r+1,i)(-1)^i n!/(n-i)! He_{n-i}
    tot = 0
    for i in range(r + 2):
        ff = 1
        for t in range(i):
            ff *= (n - t)
        tot += sp.binomial(r + 1, i) * (-1)**i * ff * He[n - i]
    return sp.simplify(tot)
M0, M2, M4 = M(0), M(2), M(4)
r2 = sp.simplify(M2 / M0)
r4 = sp.simplify(M4 / M0)
# write as U - V/d
U2 = sp.simplify(sp.limit(r2, d, sp.oo)); V2 = sp.simplify(-(r2 - U2) * d)
U4 = sp.simplify(sp.limit(r4, d, sp.oo)); V4 = sp.simplify(-(r4 - U4) * d)
def kexp(e):
    return sp.collect(sp.expand(e), k)
print("U2 =", kexp(U2)); print("V2 =", kexp(V2))
print("U4 =", kexp(U4)); print("V4 =", kexp(V4))
# (마) general y: M2/M0 = 1 - 2n/y + n(n+1)/y^2 - n(n+1)/(y^2 d)
yv = sp.symbols('y')
Ny = n + yv + 1
Hey = {n: n + d, n - 1: sp.Integer(1)}
for j in [n - 1, n - 2]:
    Hey[j - 1] = sp.simplify((Ny * Hey[j] - Hey[j + 1]) / (yv * j))
def My(r):
    tot = 0
    for i in range(r + 2):
        ff = 1
        for t in range(i):
            ff *= (n - t)
        tot += sp.binomial(r + 1, i) * (-1)**i * ff * Hey[n - i]
    return sp.simplify(tot)
ratio_y = sp.simplify(My(2) / My(0))
claim = 1 - 2 * n / yv + n * (n + 1) / yv**2 - n * (n + 1) / (yv**2 * d)
print("(마) ratio - claim =", sp.simplify(ratio_y - claim))

# ---------- (ㄱ) pair-check-10000 ----------
K = 10000
def exbar(q):
    pi = Fraction(q * (q - 1), 2 * (K + 1))
    return q + (K + q) * pi / (1 - pi)
cnt = 0; best = None
for q in range(1, 50):
    for qp in range(q, 51 - q):
        for j in range(0, 51 - q - qp):
            cnt += 1
            v = 1 - Fraction(j, K) * (exbar(q) + exbar(qp)) - (exbar(q) * (qp - 1) + exbar(qp) * (q - 1)) / (2 * K)
            if best is None or v < best[0]:
                best = (v, q, qp, j)
print("pair-check count =", cnt, " min =", float(best[0]), best[1:])
# ordered count
print("ordered count =", sum(1 for q in range(1,50) for qp in range(1,51-q) for j in range(0,51-q-qp)))
# ---------- misc numerics ----------
import math
for (M_, C_) in [(120,0.54),(250,0.593),(300,0.522),(450,0.548),(700,0.519)]:
    print("C M^1.5 =", M_, C_, C_ * M_**1.5)
print("n_X(2002) =", math.ceil(2002**(4/3)), 2002**(4/3))
print("2e^{-5.3146*0.6996} =", 2*math.exp(-5.3146*0.6996), " 0.3^1.5/2 =", 0.3**1.5/2, " rhs =", 0.3**1.5/2*math.exp(-3/25233))
print("needed sigma:", -math.log(0.0820/2)/0.6996)
print("n_M ratios:", 20507/841**1.5, 73032/2000**1.5)
print("9400 check:", 2e7*3.07/9**4, " 3.07 check:", 3+601/1e4)
print("1.84 check:", (1.5+1/2e4)**1.5*math.exp(1/240000), 1.84*2/math.sqrt(math.pi), 2.08/math.sqrt(2*math.pi))
print("0.6996 check:", 0.7*2001/2002)
print("(1,33,16) value:", float(1 - Fraction(16,K)*(exbar(1)+exbar(33)) - (exbar(1)*32)/(2*K)))
