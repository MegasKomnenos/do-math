# 검토전체2 H2 검산: 3장 수치 (python -I 로 실행)
from fractions import Fraction as Fr
from math import comb, sqrt, pi

# 1. 정리 3-6 의 유리수 상계 (J=8, lambda=751/1000, n^{-1/2}<=1/31, n^{-1}<=1/1000)
lam = Fr(751, 1000)
J = 8
val = lam**J + Fr(1, 31) * sum(i * lam**(i - 1) for i in range(1, J + 1)) \
    + Fr(1, 1000) * sum((i - 1) * lam**(i - 1) for i in range(1, J + 1))
print("3-6 rational:", val)
print("  == 7309649993107890414228499/15500000000000000000000000 ?",
      val == Fr(7309649993107890414228499, 15500000000000000000000000))
print("  float:", float(val), "< 0.4716:", val < Fr(4716, 10000))

# 2. E_n omega_n for n=1..5, and bound check n>=6
def p(n):
    return (n + 1)**(n - 1) if n >= 1 else 1

def E_omega(n):
    return sum(Fr(comb(n, j) * j**j * p(n - j), p(n)) for j in range(1, n // 2 + 1))

for n in range(1, 6):
    e = E_omega(n)
    print("E_omega", n, e, "<= sqrt n:", float(e) <= sqrt(n))
for n in range(6, 60):
    e = E_omega(n)
    assert float(e) <= sqrt(n), n
    rhs = sqrt(2 / pi) * sqrt((n + 1) * (n + 2) / n)
    assert float(e) <= rhs <= sqrt(n) + 1e-12, (n, float(e), rhs)
print("E_omega <= sqrt(2/pi)sqrt((n+1)(n+2)/n) <= sqrt n for 6<=n<60: ok")

# 3. 극한 꼬리 비 (3/4)^{3/2}
print("(3/4)^{3/2} =", 0.75**1.5, " 2^-3/3^-1.5 =", 2**-3 / 3**-1.5)

# 4. 마지막 차 재귀로 b_{80,.} 과 n<=80 의 로그오목성 판정
NMAX = 80
A = {}  # A[(n,l)]
for l in range(0, NMAX):
    A[(0, l)] = 1
    for n in range(1, NMAX + 1):
        s = 0
        for j in range(0, n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)]
        A[(n, l)] = s

def b(n, l):
    return A[(n, l)] - (A[(n, l - 1)] if l >= 1 else 0)

first = None
for n in range(1, NMAX + 1):
    row = [b(n, l) for l in range(0, n)]
    assert sum(row) == p(n), n
    for l in range(1, n - 1):
        if row[l]**2 < row[l - 1] * row[l + 1]:
            if first is None:
                first = (n, l)
            if n <= 80:
                print("LC failure at", (n, l))
print("first failure:", first)
r = [b(80, l) for l in (39, 40, 41)]
print("b_80_39<b_80_40<b_80_41:", r[0] < r[1] < r[2])
print("ratios:", float(Fr(r[1], r[0])), float(Fr(r[2], r[1])))
print("b_80_39 =", r[0])

# 5. 1.3 표의 증인과 ceil(n/2)
for n in range(1, 11):
    row = [b(n, l) for l in range(0, n)]
    m = max(row)
    wit = [l for l in range(n) if row[l] == m]
    print(n, "witness", wit, "ceil(n/2)=", (n + 1) // 2, "all < :", all(w < (n + 1) // 2 for w in wit))

# ===================== 4장 =====================
print("\n==== 4장 ====")
# 6. 정리 4-5 의 작은 n: d_{n,k_n} 부호와 2<=n<=15 의 오른쪽 절반 비증가 (A 는 위에서 n<=80 까지 채움)
for n in range(2, NMAX + 1):
    kn = (n + 1) // 2
    d = b(n, kn) - b(n, kn - 1)
    if n <= 15:
        right_noninc = all(b(n, j) >= b(n, j + 1) for j in range(kn, n - 1))
        assert d < 0 and right_noninc, (n, d, right_noninc)
    else:
        assert d > 0, (n, d)
print("d_{n,k_n}<0 and right half nonincreasing for 2<=n<=15; d_{n,k_n}>0 for 16<=n<=80: ok")

# 7. 따름정리 gauss-coeff-numeric (나)(다)
w = Fr(699, 100)
val_na = w - Fr(7, 2) - (6 * w + Fr(3, 4)) / 31 - (13 * w / 2) / 961 - 12 * w / 30000
print("(나) rational:", val_na, "==495594511/240250000:", val_na == Fr(495594511, 240250000), float(val_na))
w = Fr(698, 100); a0 = Fr(12879, 10000); a1 = Fr(939, 1000); c13 = Fr(464159, 10**7)
val_da = w - Fr(7, 2) - (4 * w + Fr(1, 2)) * a0 * c13 - (13 * w / 2) * a1 * c13**2 - 12 * w / 10000
print("(다) value:", float(val_da), ">=1.6809:", val_da >= Fr(16809, 10000))
print("a0 =", 3**(-2/3) * __import__('math').gamma(1/3), " a1 =", 3**(-1/3) * __import__('math').gamma(2/3))

# 8. Hermite 수로 (4.9) 와 M_4/M_0 공식 검산 (y=k 정수, 정확 유리수)
def hermite_list(N, y, nmax):
    He = [Fr(1), Fr(N)]
    for j in range(2, nmax + 1):
        He.append(N * He[j - 1] - (j - 1) * y * He[j - 2])
    return He

def M_num(r, He, n):
    # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i (-1)^i C(r+1,i) n!/(n-i)! He_{n-i}
    s = Fr(0)
    for i in range(0, r + 2):
        if n - i < 0:
            break
        f = 1
        for t in range(n - i + 1, n + 1):
            f *= t
        s += (-1)**i * comb(r + 1, i) * f * He[n - i]
    return s

for k in (50, 200, 1000):
    for nu in (0, -1):
        n = 2 * k + nu; y = k; N = n + y + 1
        He = hermite_list(N, y, n)
        M0, M2, M4 = (M_num(r, He, n) for r in (0, 2, 4))
        theta = He[n] / He[n - 1] - n
        lhs = M2 / M0
        rhs = (theta * ((n - y)**2 + n) - n * (n + 1)) / (y**2 * theta)
        assert lhs == rhs, ("4.9", k, nu)
        kk = Fr(k)
        if nu == 0:
            f4 = 1 + 16 / kk + 18 / kk**2 + 2 / kk**3 - (4 + 38 / kk + 22 / kk**2 + 2 / kk**3) / theta
        else:
            f4 = 1 + 12 / kk - 6 / kk**2 - (4 + 26 / kk - 14 / kk**2) / theta
        assert M4 / M0 == f4, ("M4/M0", k, nu)
        print(f"k={k} nu={nu}: (4.9) ok, M4/M0 formula ok; theta={float(theta):.6f}, "
              f"center={4-26/k+506/k**2 if nu==0 else 4-22/k+414/k**2:.6f}, k^2*M4/M0={float(M4/M0)*k*k:.3f}")

# 9. 조립 산술
print("11/2*39/100*2-7/2 =", Fr(11, 2) * Fr(39, 100) * 2 - Fr(7, 2))
print("5.642*1.6809*0.39893-0.0163-3.554 =", 5.642 * 1.6809 * 0.39893 - 0.0163 - 3.554)
print("Bor(k)k^{3/2} lower at k=1e4:", (2 * pi)**-0.5 * (1 - 1 / 120000), ">=0.39893")
print("46sqrt2-12 =", 46 * sqrt(2) - 12, "; -5000/173-0.02 ->", 46 * sqrt(2) - 12 - 5000 / 173 - 0.02)
print("(나) -1.63 check:", (46 * sqrt(2) - 12 - 5468.28 / 100) * 10000 / 9999)
print("(나) bJ:", 0.4503 * 3 * 2.50663 + 1675.2 / 10000, "<3.554")
print("(가) bJ:", 0.451 * 3 * 2.51 + 1678 / 30000 + 0.01, "<3.47")
print("sqrt2/pi =", sqrt(2) / pi)

# 10. borel-tail-arc 의 상수 -2/3: sum_j (j Bor(j) - (2pi)^{-1/2} j^{-1/2}) + (2pi)^{-1/2} zeta(1/2)
from math import lgamma, log, exp
def Bor(j):
    return exp((j - 1) * log(j) - j - lgamma(j + 1))
S = 0.0
J = 2_000_000
for j in range(1, J + 1):
    S += j * Bor(j) - (2 * pi)**-0.5 * j**-0.5
# tail correction: j Bor(j) - j^{-1/2}/sqrt(2pi) ~ -(1/12)(2pi)^{-1/2} j^{-3/2}; tail sum ~ -(1/12)(2pi)^{-1/2}*2/sqrt(J)
S_tail = -(1 / 12) * (2 * pi)**-0.5 * 2 / sqrt(J)
zeta_half = -1.4603545088095868
print("S + (2pi)^{-1/2}zeta(1/2) =", S + S_tail + (2 * pi)**-0.5 * zeta_half, " (expect -2/3 =", -2 / 3, ")")

# 11. 중앙 상쇄 항등식과 int F_1 = 46 sqrt2 - 12 (수치 적분)
try:
    import numpy as np
    from scipy import integrate, special
    ninf = 2 / sqrt(pi)
    def Pq(z, r):
        mu = 1 - r * r
        return mu * z * z + mu * mu * z**4 / 4
    def bor_ld_R(beta):
        # e^{beta^2/2} (2 - 2 beta D(beta)), D(beta)=e^{-beta^2/2} int_0^beta e^{v^2/2} dv = dawsn(beta/sqrt2)*sqrt2
        Dw = sqrt(2) * special.dawsn(beta / sqrt(2))
        return exp(beta * beta / 2) * (2 - 2 * beta * Dw)
    def F0(z):
        inner = integrate.quad(lambda r: r * r * exp((1 - r * r) * z * z / 2) * Pq(z, r) * (2 * pi)**-0.5 * bor_ld_R(r * z), 0, 1)[0]
        return -ninf * z**4 * exp(-z * z) * inner
    def F1(z):
        inner = integrate.quad(lambda r: r * r * exp((1 - r * r) * z * z / 2) * Pq(z, r) * (4 / 3 * r * r * z * z - 2 / 3 * r * z**4), 0, 1)[0]
        return -ninf * z**4 * exp(-z * z) * inner
    I0 = integrate.quad(F0, -12, 12, limit=200)[0]
    I1 = integrate.quad(F1, -12, 12, limit=200)[0]
    print("int F0 =", I0, "(expect 0); int F1 =", I1, "(expect", 46 * sqrt(2) - 12, ")")
    # J leading integral
    IJ = integrate.quad(lambda z: z**3 * exp(-z * z / 2) * (4 / 15 * z**3 - z / 3), -12, 12)[0]
    print("J leading =", IJ, "(expect 3 sqrt(2pi) =", 3 * sqrt(2 * pi), ")")
except Exception as e:
    print("scipy unavailable:", e)

# 12. D.crossing-small-n (n<=80 부분) 과 D.QL-small-n
bad = [n for n in range(5, 20) if b(n, (n + 1) // 2) < b(n, (n + 1) // 2 + 1)]
good = all(b(n, (n + 1) // 2) < b(n, (n + 1) // 2 + 1) for n in range(20, NMAX + 1))
print("b_{n,k_n}<b_{n,k_n+1} true for 20<=n<=80:", good, "; true-cases in 5..19:", bad)
ql = True
for n in range(3, 16):
    for l in range(0, n - 2):
        if 2 * l <= n - 2 and b(n, l) > b(n, l + 1):
            ql = ql and (b(n, l + 1)**2 >= b(n, l) * b(n, l + 2))
print("Q_L(n) for 3<=n<=15:", ql)
