# -*- coding: utf-8 -*-
"""검토전체7 M7b: 장7B 7.6–7.8절의 수치·항등식 검산 (python -I)."""
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, pi, factorial, ceil, floor, lgamma

# ---------- 기본 양 ----------
def p(m):  # 주차함수 수 p_m=(m+1)^(m-1)
    return (m + 1) ** (m - 1) if m >= 1 else 1

def A_table(nmax, ell):
    """A_{m,ell}, 0<=m<=nmax. 마지막 차 재귀(정리 old-2-6)."""
    if ell < 0:
        return [0] * (nmax + 1)
    A = [0] * (nmax + 1)
    A[0] = 1
    for m in range(1, nmax + 1):
        s = 0
        for j in range(1, m + 1):
            s += comb(m - 1, j - 1) * min(j, ell + 1) * A[j - 1] * A[m - j]
        A[m] = s
    return A

def g(x):
    return (x - 1) * log(1 + 1 / x)

def Bor(d):
    return Fr(0) if d < 1 else None  # 자리표시

def BorF(d):  # float
    return exp(-d + (d - 1) * log(d) - lgamma(d + 1))

def Pn(n, j):  # 균등 마지막 차 자리 법칙 (Fraction)
    return Fr(j * comb(n - 1, j - 1) * p(j - 1) * p(n - j), p(n))

report = []
def ok(name, cond, detail=""):
    report.append(("OK " if cond else "FAIL ") + name + (" " + detail if detail else ""))

# ---------- (1) 보조정리 root-symmetry ----------
for k in range(2, 9):
    for nu in range(1, 6):
        n = 2 * k + nu
        rw = lambda q: Fr(k, k + 1 + q) * Pn(n, k + 1 + q) / Pn(n, k)
        ok(f"rw(nu)=1 k={k} nu={nu}", rw(nu) == 1)
        for q in range(0, k + nu - 1):
            lhs = float(rw(q + 1) / rw(q))
            rhs = exp(g(k + 1 + q) - g(k + nu - 1 - q))
            ok(f"rw ratio k={k} nu={nu} q={q}", abs(lhs - rhs) < 1e-9 * max(1, rhs))
        ok(f"rw>=1 for q>=nu k={k} nu={nu}", all(rw(q) >= 1 for q in range(nu, k + nu)))

# ---------- (2) 보조정리 explicit-bounds ----------
for m in range(1, 80):
    im = m * log(m / (m + 1)) + 1
    ok(f"i_m bounds m={m}", 0 <= im <= 1 / (2 * (m + 1)) + 1 / (6 * m * (m + 1)) + 1e-15)
    for U in range(0, m):
        lhs = float(Pn(m, m - U))
        rhs = BorF(U + 1) * exp(im) * (m + 1) / (m - U)
        ok(f"P_m(m-U)<=Bor e^i (m+1)/(m-U) m={m} U={U}", lhs <= rhs * (1 + 1e-12))
    for j in range(1, m + 1):
        lhs = float(Pn(m, j))
        Ren = j ** (j - 1) * exp(-j) / factorial(j - 1)
        rhs = Ren * exp(im) * (m + 1) / (m + 1 - j) ** 2
        ok(f"P_m(j)<=Ren e^i (m+1)/(m+1-j)^2 m={m} j={j}", lhs <= rhs * (1 + 1e-12))
# Borel 상계와 꼬리
for d in range(1, 400):
    ok(f"Bor(d)<=(2pi)^-1/2 d^-3/2 d={d}", BorF(d) <= (2 * pi) ** -0.5 * d ** -1.5 * (1 + 1e-12))
for m in range(1, 200):
    tail = 1 - sum(BorF(d) for d in range(1, m + 1))
    ok(f"tail Bor <=0.8/sqrt m m={m}", tail <= 0.8 / sqrt(m) + 1e-12)
ok("sum_{U<=300} Bor(U+1) >= 0.9538", sum(BorF(d) for d in range(1, 302)) >= 0.9538,
   f"{sum(BorF(d) for d in range(1, 302)):.6f}; 1-0.8/sqrt(301)={1-0.8/sqrt(301):.6f}")
ok("(2pi)^-1/2 <= 0.398943", (2 * pi) ** -0.5 <= 0.398943, f"{(2*pi)**-0.5:.7f}")
ok("0.9538/0.398943 >= 2.38", 0.9538 / 0.398943 >= 2.38, f"{0.9538/0.398943:.5f}")

# ---------- (3) (7.22)·(7.23)·top-roots·theorem-W의 사슬 (정확 유리수) ----------
def quantities(k, n):
    Am1 = A_table(n, k - 2)  # 용량 k-1
    A0 = A_table(n, k - 1)   # 용량 k
    A1 = A_table(n, k)       # 용량 k+1
    s = lambda m, y: Fr({k - 1: Am1, k: A0, k + 1: A1}[y][m], p(m))
    c = lambda m, Y: s(m, Y + 1) - s(m, Y)  # 수준 질량 c_m(Y)
    cl_p = lambda m: c(m, k) / s(m, k)
    cl_m = lambda m: c(m, k - 1) / s(m, k)
    Pk = lambda j: Fr(min(j, k) * comb(n - 1, j - 1) * A0[j - 1] * A0[n - j], A0[n])
    def chi(j):
        v = Fr(0)
        if j == k:
            v -= Fr(1, k) * (1 - cl_m(n - k))
        if j > k:
            v += Fr(1, k) * (cl_p(j - 1) + cl_m(j - 1) + cl_p(n - j) + cl_m(n - j))
        v += (1 + Fr(int(j > k), k)) * cl_p(j - 1) * cl_p(n - j) + (1 - Fr(int(j > k), k)) * cl_m(j - 1) * cl_m(n - j)
        return v
    src = sum(Pk(j) * chi(j) for j in range(1, n + 1))
    mu = lambda m: cl_p(m) - cl_m(m)
    inh = sum(Pk(j) * (mu(j - 1) * (k <= j - 1 <= 2 * k) + mu(n - j) * (k <= n - j <= 2 * k)) for j in range(1, n + 1))
    return dict(s=s, c=c, cl_p=cl_p, cl_m=cl_m, Pk=Pk, chi=chi, src=src, inh=inh, mu=mu, A0=A0, Am1=Am1, A1=A1)

for k in range(2, 8):
    for nu in range(1, 2 * k + 2):
        n = 2 * k + nu
        Q = quantities(k, n)
        s, c, Pk, src = Q['s'], Q['c'], Q['Pk'], Q['src']
        lhs = k * s(n, k) * src
        rhs722 = sum(Fr(k, j) * Pn(n, j) * ((c(j - 1, k - 1) + c(j - 1, k)) * s(n - j, k) + s(j - 1, k) * (c(n - j, k - 1) + c(n - j, k))) for j in range(k + 1, n + 1)) - Pn(n, k) * s(n - k, k - 1)
        ok(f"(7.22) k={k} nu={nu}", lhs >= rhs722)
        rw = lambda q: Fr(k, k + 1 + q) * Pn(n, k + 1 + q) / Pn(n, k)
        br1 = sum(rw(q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1)
        br2 = c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1)
        ok(f"(7.23) chain k={k} nu={nu}", rhs722 >= Pn(n, k) * br1 >= Pn(n, k) * br2)
        # apex^H 항등식: k s_n(k) apex^H = P_n(k) * br1
        cl_p, cl_m = Q['cl_p'], Q['cl_m']
        apex = Fr(1, k) * (sum(Pk(j) * (cl_p(j - 1) + cl_m(j - 1)) for j in range(n - k + 1, n + 1)) - Pk(k) * (1 - cl_m(n - k)))
        ok(f"apex identity k={k} nu={nu}", k * s(n, k) * apex == Pn(n, k) * br1)
        # top-roots
        hz = lambda N: 1 - s(N + 1, k) / s(N, k)
        for U0 in range(0, k):
            br2b = br2 + sum((rw(k + nu - 1 - U) - 1) * (s(n - 1 - U, k) - s(n - U, k)) for U in range(0, U0 + 1))
            br3 = s(n, k) * (sum((rw(k + nu - 1 - U) - 1) * hz(n - 1 - U) for U in range(0, U0 + 1)) - 1)
            ok(f"top-roots k={k} nu={nu} U0={U0}", br1 >= br2b >= br3)

# ---------- (4) 7.7 (7.24)·(7.25)·(7.26)·분할 무게 ----------
for k in range(2, 8):
    for n in range(2 * k + 1, 3 * k + 4):
        Q = quantities(k, n)
        A0, Am1, A1, Pk, mu, cl_p, cl_m = Q['A0'], Q['Am1'], Q['A1'], Q['Pk'], Q['mu'], Q['cl_p'], Q['cl_m']
        d = lambda m: (A1[m] - A0[m]) - (A0[m] - Am1[m])
        w = lambda m: Fr(comb(n - 1, m) * p(m) * A0[n - 1 - m], A0[n])
        pp = lambda m: Fr((k + 1) * (A1[m] - A0[m]) - (k - 1) * (A0[m] - Am1[m]), p(m))  # 𝔭_m
        Left = sum(w(m) * pp(m) for m in range(k, 2 * k + 1))
        if n >= 3 * k + 1:
            inh_lin = Fr(1, k) * sum(Pk(j) * ((cl_p(j - 1) + cl_m(j - 1)) * (k <= j - 1 <= 2 * k) + (cl_p(n - j) + cl_m(n - j)) * (k <= n - j <= 2 * k)) for j in range(1, n + 1))
            ok(f"(7.24) k={k} n={n}", inh_lin + Q['inh'] == 2 * Left)
        # 분할 무게 비감소
        ok(f"w nondecreasing k={k} n={n}", all(w(m + 1) >= w(m) for m in range(k, 2 * k)))
        if n <= 3 * k:
            KD = sum((k + n - m) * comb(n - 1, m) * p(n - 1 - m) * d(m) for m in range(2 * k + 1, n))
            ok(f"(7.25) k={k} n={n}", A0[n] * (Q['src'] + Q['inh']) == d(n) - KD)
        if n == 3 * k:
            u = w(2 * k) * Fr(A1[2 * k], p(2 * k))
            Quad = sum(Pk(j) * ((1 + Fr(1, k)) * cl_p(j - 1) * cl_p(n - j) + (1 - Fr(1, k)) * cl_m(j - 1) * cl_m(n - j)) for j in range(k + 1, n + 1))
            Stem = Fr(1, k) * sum(Pk(j) * ((cl_p(j - 1) + cl_m(j - 1)) * (j - 1 > 2 * k) + (cl_p(n - j) + cl_m(n - j)) * (n - j > 2 * k)) for j in range(k + 1, n + 1))
            ok(f"(7.26) k={k}", Q['src'] + Q['inh'] == 2 * Left - u + Quad + Stem)
            # 문턱 단위 비의 망원 꼴
            s = Q['s']
            ratio = u / w(k)
            rthr = s(2 * k, k + 1) / s(2 * k - 1, k)
            ok(f"u/w_k = e^(g(2k)-g(k)) r_thr k={k}", abs(float(ratio) - exp(g(2 * k) - g(k)) * float(rthr)) < 1e-12)
            # 문턱 뿌리 항 항등식
            thr_term = Pk(k) * (mu(2 * k) - Fr(1, k) * (1 - cl_m(2 * k)))
            ok(f"threshold-root identity k={k}", thr_term == w(2 * k) * pp(2 * k) - u)

# ---------- (5) 𝔲_{3k}/w_k 의 추세 (부동소수점; k까지 적당히) ----------
def ratio_u_w(k):
    n = 3 * k
    A0 = A_table(2 * k, k - 1)
    A1 = A_table(2 * k, k)
    s2k1_k = Fr(A0[2 * k - 1], p(2 * k - 1))
    s2k_k1 = Fr(A1[2 * k], p(2 * k))
    return exp(g(2 * k) - g(k)) * float(s2k_k1 / s2k1_k), float(s2k_k1 / s2k1_k)
trend = []
for k in [5, 10, 20, 40, 80, 120]:
    r, rt = ratio_u_w(k)
    trend.append(f"k={k}: u_3k/w_k={r:.5f}, r_thr={rt:.5f}")

# ---------- (6) theorem-W (나)의 수치 ----------
def Dk(k, rho):
    return 0.33316 * sqrt(k) * (1 - 1 / rho) ** 2 - rho - 42.14 / k
def nPD(k):
    return ceil((k + 1) ** (4 / 3)) + k + 1
def Gk(k, n):
    i_n = n * log(n / (n + 1)) + 1
    return 0.14 / n * (2.38 * k ** 1.5 * (n - k + 1) ** 2 / (exp(i_n) * n * (n + 1)) - 301)
k0 = 3131
nums = []
nums.append(f"D_k(2) at 3131 = {Dk(k0, 2):.4f} (text 2.647)")
t = k0 ** (1 / 6)
nums.append(f"k^(1/6) at 3131 = {t:.4f} (text 3.8248)")
rhs_right = 0.33316 * (sqrt(k0) - 2 * t + 1 / t) - 1.0005 * k0 ** (1 / 3) - 1.0145
nums.append(f"right-end lower bound at 3131 = {rhs_right:.4f} (text 0.529)")
deriv = 0.33316 * (3 * k0 ** (1 / 3) - 2 - k0 ** (-1 / 3)) - 2.001 * t
nums.append(f"derivative wrt k^(1/6) at 3131 = {deriv:.3f} (>0?)")
nums.append(f"(1+1/3131)^(4/3) = {(1+1/k0)**(4/3):.6f} (<=1.0005), 2/k = {2/k0:.6f} (<=0.001)")
nums.append(f"n_PD(3131)/3131 = {nPD(k0)/k0:.4f}; bound 1.0005k^(1/3)+1.001 = {1.0005*k0**(1/3)+1.001:.4f}")
n0 = 2 * k0 + 1
i_n0 = n0 * log(n0 / (n0 + 1)) + 1
nums.append(f"e^-i_n at n=6263: {exp(-i_n0):.6f} (>=0.9999)")
nums.append(f"0.14*2.38*0.9999 = {0.14*2.38*0.9999:.6f} (>=0.33316); 0.14*301={0.14*301}")
nums.append(f"n_PD(3131) = {nPD(k0)}, 3k+2 = {3*k0+2}")
# D_k(2) 증가, D_k 오른쪽 끝 하계 증가 확인 (표본)
ks = [3131, 3500, 5000, 10000, 10 ** 5, 10 ** 6]
nums.append("D_k(2): " + ", ".join(f"{k}:{Dk(k,2):.3f}" for k in ks))
nums.append("right bound: " + ", ".join(f"{k}:{0.33316*(sqrt(k)-2*k**(1/6)+k**(-1/6))-1.0005*k**(1/3)-1.0145:.3f}" for k in ks))
# 𝔊_k(n)>1 직접 확인(표본 열, 모든 n은 작은 k에서 전수)
bad = []
for k in [3131, 3200, 4000, 6667, 10000]:
    for n in range(2 * k + 1, nPD(k)):
        if Gk(k, n) <= 1:
            bad.append((k, n, Gk(k, n)))
            break
nums.append(f"G_k(n)>1 violations (k in 3131,3200,4000,6667,10000): {bad[:3]}")
# 최솟값 위치 대략
k = 3131
mn = min((Gk(k, n), n) for n in range(2 * k + 1, nPD(k)))
nums.append(f"min G_3131(n) = {mn[0]:.4f} at n={mn[1]}, n/k={mn[1]/k:.3f}")
# k=3130에서 (나)가 깨지는지(문턱이 날카로운지) 참고
k = 3130
mn2 = min((Gk(k, n), n) for n in range(2 * k + 1, nPD(k)))
nums.append(f"min G_3130(n) = {mn2[0]:.4f} at n={mn2[1]} (참고)")

# ---------- (7) 보조정리 threshold-unit-ratio의 수치 ----------
k = 6667
j0 = floor(0.3 * k)
val = -(0.3 * k - 1) * (0.3 * k) / (2 * (1.3 * k + 1))
nums.append(f"-(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 = {val:.2f} (text -230.6); exact sum bound -j0(j0+1)/(2(k+1+j0)) = {-j0*(j0+1)/(2*(k+1+j0)):.2f}")
nums.append(f"1+1.5 log k + that = {1+1.5*log(k)+val:.2f} (text -216.4)")
nums.append(f"e^0.3 = {exp(0.3):.6f} (<1.34986); e^(3/(2k)) = {exp(3/(2*k)):.6f} (<=1.00023); 1.00023*1.34986 = {1.00023*1.34986:.6f} (<1.3502)")
nums.append(f"2*0.7654-1.3502 = {2*0.7654-1.3502:.4f} (>=0.18)")
nums.append(f"(1-1/k)^(k-2) >= e^-1 at k=6667: {(1-1/k)**(k-2):.6f} vs {exp(-1):.6f}")
nums.append(f"C(2k-1,k) >= 4^k/(4 sqrt k) at k=50: {comb(99,50) >= 4**50/(4*sqrt(50))}")
# 7.7 LRP2 => P 의 수치: 𝔳 상계
k = 501; n = 2 * k + 1
xk = (k / (k + 1)) ** (k - 1)
nums.append(f"x_k n at k=501,n=1003: {xk*n:.2f} (>368); x_k >= e^-1: {xk:.5f}")
# 7.7 잔여 경계
nums.append(f"3*3333-1={3*3333-1}, 3*3334-1={3*3334-1}, 3*6666-1={3*6666-1}, 3*6667-1={3*6667-1}, 3*6668-1={3*6668-1}, 2*6668+103={2*6668+103}")
nums.append(f"(40103,20000): nu={40103-40000}, 3k-1={3*20000-1}")

fails = [r for r in report if r.startswith("FAIL")]
print(f"검사 {len(report)}건, 실패 {len(fails)}건")
for f in fails[:40]:
    print(f)
print("--- 추세 ---")
print("\n".join(trend))
print("--- 수치 ---")
print("\n".join(nums))
