# 검토전체6 L6: 장7A.md 검산 (python -I)
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial, log, exp, ceil, sqrt, cosh
import mpmath as mp
mp.mp.dps = 60

def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)  # i-h = position of nearest larger (0 if none), 1-based: h_i = (i+1)-(j+1)
    return h

def Asig(h, k):  # A^sigma_{k-1} = prod min(h_i,k)
    p = 1
    for x in h: p *= min(x, k)
    return p

def A_table(N, ell):
    A = [Fr(1)] * (N + 1)
    for n in range(1, N + 1):
        A[n] = sum(comb(n - 1, j) * min(j + 1, ell + 1) * A[j] * A[n - 1 - j] for j in range(n))
    return A

print("== 1. 소규모 전수 대조 (정리 old-6-2, old-6-6, factorial-moment, old-6-7, old-6-10, old-6-5) ==")
bad = []
for n in range(1, 8):
    perms = list(permutations(range(1, n + 1)))
    H = [caps(s) for s in perms]
    for k in range(2, n + 2):
        W = [Asig(h, k) for h in H]
        Ak1 = sum(W)
        Ak = sum(Asig(h, k + 1) for h in H)
        Ak2 = sum(Asig(h, k - 1) for h in H)
        d = Ak - 2 * Ak1 + Ak2
        Z = [sum(1 for x in h if x > k) for h in H]
        Hk = [sum(1 for x in h if x == k) for h in H]
        # old-6-2
        mu = Fr(d, Ak1)
        ev = sum(Fr(w) * ((Fr(k + 1, k)) ** z + (Fr(k - 1, k)) ** (z + hh) - 2) for w, z, hh in zip(W, Z, Hk)) / Ak1
        if mu != ev: bad.append(("old-6-2", n, k))
        # old-6-6 (y=k)
        EZ = sum(Fr(w * z) for w, z in zip(W, Z)) / Ak1
        if k <= n and EZ < Fr(n - k, k + 1): bad.append(("old-6-6", n, k, EZ))
        # factorial moment iota=2
        if n >= 2 * k + 1:
            m = Fr(n - k, k + 1)
            EZZ = sum(Fr(w * z * (z - 1)) for w, z in zip(W, Z)) / Ak1
            if EZZ < m * (m - 1): bad.append(("fact-moment", n, k))
        # old-6-7
        R = Fr(Ak, Ak1); Zr = Fr(Ak2, Ak1)
        ok = float(Zr) > (1 - 1 / k) * float(R) ** (-(-2 * log(1 - 1 / k) / log(1 + 1 / k)))
        if not ok: bad.append(("old-6-7", n, k))
        # old-6-10
        if n >= k:
            EkH = sum(Fr(w * k * hh) for w, hh in zip(W, Hk)) / Ak1
            xk = Fr(k, k + 1) ** (k - 1)
            if EkH > xk * n: bad.append(("old-6-10", n, k))
            if n == k and EkH != xk * n: bad.append(("old-6-10-eq", n, k, EkH, xk * n))
        # old-6-5 Kink = A E[H]/k ; Conv = d + Kink >= 0
        Kink = sum(Fr(w * hh) for w, hh in zip(W, Hk)) / k
        if d + Kink < 0: bad.append(("old-6-5", n, k))
print("불일치:", bad if bad else "없음")

print("== 1b. 정리 old-6-11(가): E[H_k] = (n+1) a_{k-1} sum_j K_j a_{n+1-j}/a_n (소규모) ==")
def Kcoef(k, J):
    # j K_j = sum_{m=1}^{k-1} (k-m) a°_{m-1} K_{j-m} + [j=k+1]
    ac = lambda m: Fr((m + 1) ** (m - 1), factorial(m)) if m >= 1 else Fr(1)
    K = [Fr(0)] * (J + 1)
    for j in range(1, J + 1):
        s = Fr(0)
        for m in range(1, k):
            if j - m >= 0: s += (k - m) * ac(m - 1) * K[j - m]
        if j == k + 1: s += 1
        K[j] = s / j
    return K
bad = []
for k in range(2, 6):
    A = A_table(9, k - 1)
    a = [A[m] / factorial(m) for m in range(10)]
    K = Kcoef(k, 10)
    for n in range(1, 8):
        perms = list(permutations(range(1, n + 1)))
        H = [caps(s) for s in perms]
        W = [Asig(h, k) for h in H]
        EH = sum(Fr(w * sum(1 for x in h if x == k)) for w, h in zip(W, H)) / sum(W)
        rhs = (n + 1) * a[k - 1] * sum(K[j] * a[n + 1 - j] for j in range(k + 1, n + 2)) / a[n]
        if EH != rhs: bad.append((k, n, EH, rhs))
print("불일치:", bad if bad else "없음")

print("== 1c. Riccati 반례 (k,z,n)=(3,1,2): 좌변 4, 우변 5 ==")
# 좌변: sum_sigma prod min(h,3) * H_1
lhs = sum(Asig(caps(s), 3) * sum(1 for x in caps(s) if x == 1) for s in permutations([1, 2]))
# 우변: n! [x^2] ( A_2 O_1 + 3 Ex/(Delta)^2 ∫ O_1 Ex ), Q_2 = 2x + x^2/2
x = mp.mpf  # 급수 계수를 직접 전개
# A_2(x) = 1 + x + 3x^2/2 ; O_1 = x ; Ex = e^{-Q_2} = 1 - 2x + ... ; Delta = 1 - 3∫Ex = 1-3x+3x^2 ; ∫O_1 Ex = x^2/2 + ...
rhs = 2 * (Fr(1) + Fr(3, 2))
print("좌변", lhs, "우변", rhs)

print("== 1d. C_{n,n}=(n-1)^{n-1} (소인 주차함수 전수, n<=6) ==")
def is_pf(a):
    n = len(a); return all(sum(1 for x in a if x <= i) >= i for i in range(1, n + 1))
def is_prime_pf(a):
    n = len(a); return all(sum(1 for x in a if x <= b) != b for b in range(1, n))
from itertools import product
for n in range(1, 7):
    c = sum(1 for a in product(range(1, n + 1), repeat=n) if is_pf(a) and is_prime_pf(a))
    print(n, c, (n - 1) ** (n - 1) if n > 1 else 1)

print("== 1e. rho_2 = log 2 : C_2(x)=e^x-1 → 1 at log2 ==", mp.e ** mp.log(2) - 1)

import sys
SKIP2 = "--skip2" in sys.argv
print("== 2. 마지막 차 재귀로 d_{n,k} 부호: n<=260, k<=min(120,ceil(n/2)) (정리 seed-transfer (라)) ==")
N = 260 if not SKIP2 else 30
Atab = {}
for ell in range(-1, 122):
    Atab[ell] = [Fr(0)] * (N + 1) if ell == -1 else A_table(N, ell)
Atab[-1] = [Fr(0)] * (N + 1)
neg = []
for n in range(16, N + 1):
    for k in range(1, min(120, ceil(n / 2)) + 1):
        if k+1 > len(Atab)-2: break
        d = Atab[k][n] - 2 * Atab[k - 1][n] + Atab[k - 2][n]
        if d <= 0: neg.append((n, k))
print("n in [16,260]에서 비양 위치 수:", len(neg), neg[:10])
print("작은 행 n<=15, 왼쪽 절반 2k+1<=n 의 비양 위치:",
      [(n, k) for n in range(3, 16) for k in range(1, (n - 1) // 2 + 1)
       if Atab[k][n] - 2 * Atab[k - 1][n] + Atab[k - 2][n] <= 0])
if not SKIP2: print("k=120, 120<=n<=142 음수? ", all(Atab[120][n] - 2 * Atab[119][n] + Atab[118][n] < 0 for n in range(120, 143)),
      " n=143..239 양?", all(Atab[120][n] - 2 * Atab[119][n] + Atab[118][n] > 0 for n in range(143, 240)))

print("== 3. t_k, n#_k, n♭_k, n°_k ==")
def t_k(k):
    j = 0
    while not ((k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) >= 2 * k ** (2 * j + 1)): j += 1
    return j
def vk(k, Z, H): return (1 + mp.mpf(1) / k) ** Z + (1 - mp.mpf(1) / k) ** (Z + H) - 2
def phi_k(k, n):
    xk = (mp.mpf(k) / (k + 1)) ** (k - 1)
    return vk(k, mp.mpf(n - k) / (k + 1), xk * n / k)
def n_flat(k):
    lo, hi = 2 * k + 1, k + (k + 1) * t_k(k)
    assert phi_k(k, lo) < 0 and phi_k(k, hi) >= 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if phi_k(k, mid) >= 0: hi = mid
        else: lo = mid
    return hi
for k in [2, 3, 5, 10, 41, 120, 121, 500, 501, 1855, 2000, 2001, 6098, 10000]:
    t = t_k(k); ns = k + (k + 1) * t; nf = n_flat(k); nc = ceil(2 * k ** 1.5)
    print(f"k={k}: t_k={t} (1<=t<=k {1<=t<=k}), n#={ns}, phi(n#)={mp.nstr(phi_k(k, ns), 6)}, n♭={nf}, n°={nc}, n♭>n° {nf > nc}, n#/k^2={ns/k**2:.4f}")

print("== 4. 열 인증 상수 ==")
print("10^21*400^10 > 17^21*123^10:", 10 ** 21 * 400 ** 10 > 17 ** 21 * 123 ** 10, 10 ** 21 * 400 ** 10, 17 ** 21 * 123 ** 10)
print("17^21 < 6.95e25:", 17 ** 21 < 6.95e25, " 123^10 < 7.93e20:", 123 ** 10 < 7.93e20, " product < 5.52e46:", 17 ** 21 * 123 ** 10 < 5.52e46)
k = 41
ok_ = -2 * log(1 - 1 / k) / log(1 + 1 / k)
print("o_41 =", ok_, "<= 2.1:", ok_ <= 2.1, " (40/41)(10/17)^2.1 =", (40 / 41) * (10 / 17) ** 2.1, "> 0.3")
print("phi'(1.7) >= 1-2.1*(10/17)^3 =", 1 - 2.1 * (10 / 17) ** 3)

print("== 5. 정리 S 표 재계산 ==")
def ac(m): return Fr((m + 1) ** (m - 1), factorial(m)) if m >= 1 else Fr(1)
def free_ratio(m): return ac(m + 1) / ac(m)  # e^{g(m+1)}
def table(L, J, k0):
    jstar = 0
    while free_ratio(jstar + 1) < L: jstar += 1  # max m with e^{g(m+1)}<L
    # jstar = max{m>=0: ac(m+1)/ac(m) < L}
    kR = max(2 * jstar + 2, ceil(L ** (jstar + 2) / ac(jstar + 1)))
    e = mp.e
    Eund = sum(mp.mpf((ac(J + i) / ac(J)).numerator) / mp.mpf((ac(J + i) / ac(J)).denominator) * e ** (-i) for i in range(1, k0 - jstar + 1))
    Lm = mp.mpf(L.numerator) / L.denominator
    Einf = (Lm / e) * (1 - (Lm / e) ** k0) / (1 - Lm / e)
    R = max(1 / (1 + Eund), 1 / (1 + Einf))
    Rq = Fr(str(mp.nstr(R, 15)))  # 상계 유리수 비슷 (검산용)
    Rq = Rq + Fr(1, 10**12)
    xbar = [ac(v) * L ** (-(v + 1)) for v in range(J)]
    qund = [max(Fr(0), 1 - sum(ac(j) * L ** (-(j + 1)) for j in range(v))) for v in range(J)]
    Xi = sum(max(Fr(0), xbar[v] - Rq * qund[v]) for v in range(J))
    xk0 = Fr(k0, k0 + 1) ** (k0 - 1)
    Xik = sum(max(Fr(0), ac(v) * xk0 * L ** (-v) - Rq * qund[v]) for v in range(J))
    A0 = xk0 + Xik / (L * (1 - Xi)); B0 = Rq * (1 + Xik / (1 - Xi))
    return jstar, kR, float(R), float(Xi), float(Xik), float(A0), float(B0), A0, B0
for (L, J, k0, y) in [(Fr(267, 100), 25, 501, Fr(13, 100)), (Fr(27, 10), 70, 1855, Fr(2, 25)), (Fr(271, 100), 100, 6098, Fr(11, 200))]:
    js, kR, R, Xi, Xik, A0, B0, A0q, B0q = table(L, J, k0)
    xi = Fr(1, k0)
    val = (y - xi) * (y - 2 * xi - xi * xi) - (1 + xi) ** 2 * (A0q * xi + B0q * y)
    vert = (3 * xi + xi * xi) / 2 + (1 + xi) ** 2 * B0q / 2
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R={R:.6f} Xi={Xi:.6f} Xi^(k0)={Xik:.6f} A0={A0:.5f} B0={B0:.6f} | S' 값={float(val):.4e} 꼭짓점/k^2={float(vert):.5f}<=y {vert <= y} | y k0^2>2k0+1 {y*k0*k0 > 2*k0+1}")

print("== 6. polar-N 상수 (k=2001) ==")
k = 2001
print("2/sqrt(k)=", 2 / sqrt(k), " e^{-1+2/(k+1)}=", exp(-1 + 2 / (k + 1)), " 0.75/sqrt k=", 0.75 / sqrt(k),
      " e^{-.0448}*.991*.3678=", exp(-0.0448) * (1 - 0.0085) * 0.3678, " 2k^1.5+1=", 2 * k ** 1.5 + 1, " .3476k^2=", 0.3476 * k * k)
y = 0.0448; print(" y^4/(12(1-y^2))/y^2 =", y ** 2 / (12 * (1 - y ** 2)))
print("== 6b. polar-W k>=1e7 상수 ==")
k = 10 ** 7
print(" 8(1+0.91/sqrt k)^3 =", 8 * (1 + 0.91 / sqrt(k)) ** 3, " 8.01/6=", 8.01 / 6, " (4.004+3+1.34)/sqrt k + 2/k =", (4.004 + 3 + 1.34) / sqrt(k) + 2 / k)
print("== 7. S1 식 (7.1)·수준 사슬 항등식 (m+1)a_m = sum a_{m-z'} n(z') (k=3, m<=8) ==")
k = 3; A = A_table(12, k - 1); a = [A[m] / factorial(m) for m in range(13)]
def nz(z): return Fr(1) if z == 0 else min(z, k) * a[z - 1]
print(all((m + 1) * a[m] == sum(a[m - z] * nz(z) for z in range(m + 1)) for m in range(1, 12)))
print("== 8. x_{k+1}/x_k <= 1 (k=2..50) ==", all((Fr(k + 1, k + 2) ** k) <= Fr(k, k + 1) ** (k - 1) for k in range(2, 51)))
print("== 9. flat-threshold (다): x_k <= k/(k+1), n#/(k+1) = t_k + k/(k+1) ==", all(Fr(k, k + 1) ** (k - 1) <= Fr(k, k + 1) for k in range(2, 30)))
