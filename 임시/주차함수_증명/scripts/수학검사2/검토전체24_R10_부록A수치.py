# 부록 A의 뜻 칸에 적힌 항등식·수치를 다시 센다.
import io, sys
from fractions import Fraction as Fr
from math import comb, factorial, log, exp, sqrt, pi, floor
from mpmath import mp, mpf, zeta, log as mlog, e as E, factorial as mfac
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
mp.dps = 40
def p(n): return 1 if n == 0 else (n+1)**(n-1)
# 누적 개수 A_{n,l}: A_l = exp(T_l), N_l(t) = min(t,l+1) A_{t-1,l}
from functools import lru_cache
@lru_cache(None)
def A(n, l):
    if l < 0: return 0 if n > 0 else 1
    if n == 0: return 1
    return sum(comb(n-1, t-1) * min(t, l+1) * A(t-1, l) * A(n-t, l) for t in range(1, n+1))
rows = {4: [24, 51, 34, 16], 5: [120, 421, 377, 253, 125], 7: [5040, 42253, 62145, 57398, 46142, 32359, 16807]}
for n, r in rows.items():
    got = [A(n, l) - A(n, l-1) for l in range(n)]
    print('1.3절 표 n=%d 일치:' % n, got == r, ' A_{n,n-1}=p_n:', A(n, n-1) == p(n))
def Bor(m): return mp.exp(-m) * mpf(m)**(m-1) / mfac(m)
def Ren(j): return mpf(1) if j == 0 else j * Bor(j)
# (1) theta_t(k)
ok = True
for t in range(2, 30):
    for k in range(1, t+1):
        a = Ren(t-k) * Bor(k) / Bor(t)
        b = mpf(comb(t, k)) * mpf(k)**(k-1) * (mpf(t-k)**(t-k) if t > k else 1) / mpf(t)**(t-1)
        if abs(a - b) > mpf(10)**-30: ok = False
print('theta_t(k) 두 꼴 일치:', ok)
# theta_t(k) = E^T_t[H_k]: 크기 t 나무에서 크기 k 부분나무 수의 기댓값 — 셈: binom(t,k) k^{k-1} (t-k)^{t-k} / t^{t-1}
# (2) pi^two
ok = True
for k in range(2, 12):
    for nu in range(2, 12):
        N = k + nu
        a = Fr(comb(N-1, k) * k**(k-1) * (nu-1)**(nu-2), N**(N-2)) if nu > 1 else None
        b = Bor(k) * Bor(nu-1) / (E * Bor(N))
        if abs(mpf(a.numerator) / a.denominator - b) > mpf(10)**-30: ok = False
print('pi^two 두 꼴 일치:', ok)
# (3) lc_i(d): log nf(n,d) = sum lc_i(d) n^{-i}
def lognf(n, d):
    return d + mlog(mfac(n)) - mlog(mfac(n-d)) + (n-d-2) * mlog(mpf(n-d)) - (n-2) * mlog(mpf(n))
def lc(i, d): return (Fr(d**(i+1), i+1) + 2 * d**i - sum(r**i for r in range(d))) / i
for d in (1, 3, 7):
    n = 10**4
    s = sum(mpf(lc(i, d).numerator) / lc(i, d).denominator * mpf(n)**(-i) for i in range(1, 12))
    print('lc 전개 d=%d: 차 %.2e' % (d, float(abs(s - lognf(n, d)))))
# (4) c_Psi
cpsi = -zeta(mpf(1)/2) + zeta(mpf(3)/2) / 12
print('c_Psi =', mp.nstr(cpsi, 10), ' 3/2 < c_Psi < 1.6781:', mpf(3)/2 < cpsi < mpf('1.6781'))
# (5) v(k), DDL^natural, u, u^flat
def u(k): return 3/0.35 * (1.35 + 1/k) * (0.65 - 1/k)**-1.5 * k**-0.5
def ub(k): return 1.15/0.35 * (2 + 1/k) * (0.65 - 1/k)**-1.5 * k**-0.5
def DDL(k): return 14 * (log(3*k) - 1) / (5 * sqrt(pi * k)) + 37.6 / (5 * sqrt(pi) * k)
def v(k): return 2 - 4.6 / sqrt(k+1) - 2 * ub(k) - 0.5 * DDL(k)
print('v(2001)=%.5f v(6667)=%.5f  (>1.198, >1.549)' % (v(2001), v(6667)))
print('u(2001)=%.5f u^flat(2001)=%.5f DDL(2001)=%.5f DDL(6668)=%.5f' % (u(2001), ub(2001), DDL(2001), DDL(6668)))
print('DDL^natural 감소 k>=7:', all(DDL(k+1) < DDL(k) for k in range(7, 200000)), ' k=6→7:', DDL(6) < DDL(7), DDL(7) < DDL(8))
print('v 증가 k>=2001:', all(v(k+1) > v(k) for k in range(2001, 200000)))
# (6) f_1, theta_0, w_0
print('f_1 = %.6f' % (4 / (3 * sqrt(2*pi))), ' theta_0 = %.6f' % ((2*exp(-0.48) - 1) * exp(-0.48)), ' s_B = e/sqrt(2pi) = %.5f' % (exp(1)/sqrt(2*pi)))
# (8) 반감 경계
def tk(k):
    j = 0
    while (k+1)**j * k**(j+1) + (k-1)**(2*j+1) < 2 * k**(2*j+1): j += 1
    return j
bad = [k for k in range(2, 141) if k + (k+1) * tk(k) > k*k + 2*k]
print('n#_k <= k^2+2k (2<=k<=140) 위반:', bad, ' 최댓값 n#_k:', max(k + (k+1)*tk(k) for k in range(2, 141)), ' 140^2+280 =', 140*140+280)
print('n#_141 =', 141 + 142 * tk(141), ' n#_140 =', 140 + 141 * tk(140))
# (12)(13) 마지막 차 자리 법칙의 합
for m in (5, 9):
    s = sum(Fr(j * comb(m-1, j-1) * p(j-1) * p(m-j), p(m)) for j in range(1, m+1))
    k = 3
    s2 = sum(Fr(min(j, k) * comb(m-1, j-1) * A(j-1, k-1) * A(m-j, k-1), A(m, k-1)) for j in range(1, m+1))
    print('P_m(j) 합 =', s, ' P^(k)_m(j) 합 =', s2)
# (21) m(n) at 20001
mm = max([170] + [m for m in range(171, 2000) if m**1.5 + 9*m <= 20001])
print('m(20001) =', mm)
# 6.2: w_n(m+1) = n A_{n,k-1} w_m
n, k = 11, 3
ok = all(comb(n, m+1) * (m+1)**m * A(n-m-1, k-1) == n * comb(n-1, m) * p(m) * A(n-1-m, k-1) for m in range(0, n))
print('표시 나무 무게와 분할 무게의 관계:', ok)
# Theta_n, delta_t 항등식
ok = True
for k in range(2, 6):
    for t in range(k+1, 12):
        N = lambda l, t=t: min(t, l+1) * A(t-1, l)
        dl = (N(k) - N(k-1)) - (N(k-1) - N(k-2))
        b = lambda n, l: A(n, l) - A(n, l-1)
        if dl != (k+1) * b(t-1, k) - (k-1) * b(t-1, k-1): ok = False
print('delta_t = (k+1)b_{t-1,k}-(k-1)b_{t-1,k-1}:', ok)
