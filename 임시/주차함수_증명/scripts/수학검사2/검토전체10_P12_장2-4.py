# -*- coding: utf-8 -*-
"""P12 검산: 부록 D 장2·장3·장4 항목의 수치를 다시 센다. python -I 로 돌린다."""
import sys, itertools
from fractions import Fraction as Fr
from math import comb, factorial, prod
from mpmath import iv, mp, mpf, gamma

out = []
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)

# ---------- 1. zeta(3/2) 구간, 기록 cemaj_iv.py zeta32 (N=2000, iv.dps=25) ----------
iv.dps = 25
def zeta32(N):
    s = iv.mpf(0)
    for n in range(1, N): s += iv.mpf(n) ** iv.mpf('-1.5')
    lo = s + 2 * iv.mpf(N) ** iv.mpf('-0.5') + iv.mpf(N) ** iv.mpf('-1.5') / 2
    hi = s + 2 * (iv.mpf(N) - iv.mpf('0.5')) ** iv.mpf('-0.5')
    return mpf(lo.a), mpf(hi.b)
lo, hi = zeta32(2000)
log('[1] zeta32 N=2000: [%s, %s]  D: [2.6123753479, 2.6123753491]  outward-rounded ok:' % (mp.nstr(lo, 14), mp.nstr(hi, 14)),
    bool(lo >= mpf('2.6123753479')) and bool(hi <= mpf('2.6123753491')))
# 성긴 방법: 부분합 sum_{j<=N} + 2(N+1)^{-1/2}
s = iv.mpf(0)
for n in range(1, 2001): s += iv.mpf(n) ** iv.mpf('-1.5')
coarse_lo = s + 2 * iv.mpf(2001) ** iv.mpf('-0.5')
log('[1] coarse lower end N=2000:', mp.nstr(mpf(coarse_lo.a), 10), ' D says 2.6123698')

# ---------- 2. 마지막 차 재귀로 n<=80 전체 표 ----------
N = 80
P = [1] + [(n + 1) ** (n - 1) for n in range(1, N + 1)]
C = [[comb(m, j) for j in range(m + 1)] for m in range(N)]
A = [[0] * (N + 1) for _ in range(N + 1)]   # A[n][l], l=0..N
for l in range(N + 1):
    A[0][l] = 1
    for n in range(1, N + 1):
        s = 0
        for j in range(n):
            s += C[n - 1][j] * min(j + 1, l + 1) * A[j][l] * A[n - 1 - j][l]
        A[n][l] = s
def b(n, l):
    if l < 0: return 0
    return A[n][l] - (A[n][l - 1] if l >= 1 else 0)
for n in range(1, N + 1):
    assert A[n][n - 1] == P[n] and sum(b(n, l) for l in range(n)) == P[n] and b(n, 0) == factorial(n)
b39, b40, b41 = b(80, 39), b(80, 40), b(80, 41)
log('[2] b_80,39 =', b39); log('[2] b_80,40 =', b40); log('[2] b_80,41 =', b41)
log('[2] b39*b41 - b40^2 > 0:', b39 * b41 - b40 ** 2 > 0, '; 25000 b40 < 25928 b39:', 25000 * b40 < 25928 * b39,
    '; 25928 b40 < 25000 b41:', 25928 * b40 < 25000 * b41)
log('[2] ratios:', mp.nstr(mpf(b40) / b39, 12), mp.nstr(mpf(b41) / b40, 12))
fails = [(n, l) for n in range(1, N + 1) for l in range(1, n - 1) if b(n, l) ** 2 < b(n, l - 1) * b(n, l + 1)]
log('[2] log-concavity failures n<=80:', fails)

# (ㄴ) 중앙 틈 작은 n: d_{n,k_n}<0 인 n, 오른쪽 절반 비증가
def kn(n): return (n + 1) // 2
neg = [n for n in range(2, N + 1) if b(n, kn(n)) - b(n, kn(n) - 1) < 0]
log('[2] d_{n,k_n}<0 for n in', neg, ' (D: exactly 2..15)')
rh_ok = all(all(b(n, j) >= b(n, j + 1) for j in range(kn(n), n - 1)) for n in neg)
log('[2] right half non-increasing on those n:', rh_ok)
pos = all(b(n, kn(n)) - b(n, kn(n) - 1) > 0 for n in range(16, N + 1))
log('[2] d_{n,k_n}>0 for 16..80:', pos)
# 횡단: b_{n,k_n} < b_{n,k_n+1}
cross_false = [n for n in range(5, N + 1) if not (b(n, kn(n)) < b(n, kn(n) + 1))]
log('[2] b_{n,k_n}<b_{n,k_n+1} false for n in', cross_false, ' (D: 5..19)')
# Q_L(n), Q_R(n), 단봉성
def Q(n, l): return (not (b(n, l) > b(n, l + 1))) or (b(n, l + 1) ** 2 >= b(n, l) * b(n, l + 2))
QL_fail = [n for n in range(3, N + 1) if not all(Q(n, l) for l in range(0, n - 2) if 2 * l <= n - 2)]
QR_fail = [n for n in range(3, N + 1) if not all(Q(n, l) for l in range(0, n - 2) if 2 * l >= n - 1)]
log('[2] Q_L fails n<=80:', QL_fail, ' Q_R fails:', QR_fail)
def unimodal(row):
    i = 0
    while i + 1 < len(row) and row[i] <= row[i + 1]: i += 1
    return all(row[j] >= row[j + 1] for j in range(i, len(row) - 1))
log('[2] all rows unimodal n<=80:', all(unimodal([b(n, l) for l in range(n)]) for n in range(1, N + 1)))

# ---------- 3. 넘는 수의 선형 재귀 (D.crossing-small-n 식) ----------
def deficit_column(l, nmax):
    """A^c_{n,l} for n<=nmax by the linear recursion (valid for n<=2l+4)."""
    assert nmax <= 2 * l + 4
    Ac = [0] * (nmax + 1)
    Pp = [1] + [(m + 1) ** (m - 1) for m in range(1, nmax + 1)]
    for n in range(l + 2, nmax + 1):
        s = 0
        for j in range(l + 1, n):
            s += comb(n - 1, j) * (j - l) * Pp[j] * Pp[n - 1 - j]
        for i in range(l + 2, n):
            s += Ac[i] * comb(n - 1, i) * Pp[n - 1 - i] * ((l + 1) + min(n - i, l + 1))
        Ac[n] = s
    return Ac
# 전체 표와 대조 (n<=80, 필요한 수준)
mism = 0
for n in range(5, N + 1):
    for l in (kn(n) - 2, kn(n) - 1, kn(n), kn(n) + 1):
        if l < 0 or n > 2 * l + 4: continue
        Ac = deficit_column(l, n)
        if Ac[n] != P[n] - A[n][l]: mism += 1
log('[3] deficit recursion vs full table (n<=80): mismatches', mism)
# n<=300: b_{n,k_n} < b_{n,k_n+1} ?
NM = 300
cols = {}
def Ac_val(n, l):
    if l not in cols: cols[l] = deficit_column(l, min(NM, 2 * l + 4))
    return cols[l][n]
cf = []
for n in range(5, NM + 1):
    k = kn(n)
    bk = Ac_val(n, k - 1) - Ac_val(n, k); bk1 = Ac_val(n, k) - Ac_val(n, k + 1)
    if not (bk < bk1): cf.append(n)
log('[3] via deficit recursion, b_{n,k_n}<b_{n,k_n+1} false for n<=300:', cf)

# ---------- 4. a_0, a_1 ----------
mp.dps = 30
a0 = gamma(mpf(1) / 3) / mpf(3) ** (mpf(2) / 3)
a1 = gamma(mpf(2) / 3) / mpf(3) ** (mpf(1) / 3)
log('[4] a0 =', mp.nstr(a0, 12), ' in (1.287899,1.2879):', bool(mpf('1.287899') < a0 < mpf('1.2879')))
log('[4] a1 =', mp.nstr(a1, 12), ' in (0.938892,0.939):', bool(mpf('0.938892') < a1 < mpf('0.939')))
# 교대급수 + 꼬리 (D의 식) 로 유리수 상하계
def a_bounds(j, W=4, M=60):
    # int_0^W w^j e^{-w^3/3} dw = sum_m (-1)^m W^{3m+j+1} / (3^m m! (3m+j+1)); alternating with decreasing terms eventually
    terms = [Fr((-1) ** m * W ** (3 * m + j + 1), 3 ** m * factorial(m) * (3 * m + j + 1)) for m in range(M)]
    S = sum(terms)
    tail = Fr(1, 16) if j == 0 else Fr(1, 4)   # times e^{-64/3}
    e_bound = Fr(1, 10 ** 9)  # e^{-64/3} < 1e-9
    return S, S + tail * e_bound, abs(terms[-1])
S0, S0hi, t0 = a_bounds(0); S1, S1hi, t1 = a_bounds(1)
log('[4] alternating series a0 in ~[%s, %s] (last term %.1e)' % (float(S0), float(S0hi), float(t0)))
log('[4] alternating series a1 in ~[%s, %s] (last term %.1e)' % (float(S1), float(S1hi), float(t1)))

# ---------- 5. 유리수 조립 ----------
v = Fr(699, 100) - Fr(7, 2) - (6 * Fr(699, 100) + Fr(3, 4)) / 31 - (13 * Fr(699, 100) / 2) / 961 - 12 * Fr(699, 100) / 30000
log('[5] 699/100-7/2-(6*6.99+0.75)/31-(13*6.99/2)/961-12*6.99/30000 =', v, '== 495594511/240250000:', v == Fr(495594511, 240250000), ' >2:', v > 2)
w = Fr('5.642') * Fr('1.6809') * Fr('0.39893') - Fr('0.0163') - Fr('3.554')
log('[5] 5.642*1.6809*0.39893-0.0163-3.554 =', float(w), ' >0.213:', w > Fr('0.213'))
# (다) k>=10000: omega=6.98, k^{-1/3}<=0.0464159, a0<1.2879, a1<0.939
om = Fr(698, 100); k13 = Fr('0.0464159')
lb = om - Fr(7, 2) - (4 * om + Fr(1, 2)) * Fr('1.2879') * k13 - Fr(13, 2) * om * Fr('0.939') * k13 ** 2 - 12 * om / 10000
log('[5] k>=10000 lower bound kR/Bor >=', float(lb), ' >=1.6809:', lb >= Fr('1.6809'))
S = 2918732888
log('[5] s = S/2^30 =', mp.nstr(mpf(S) / 2 ** 30, 15), ' e =', mp.nstr(mp.e, 15))

# ---------- 6. 얼린 용량 다항식: 전수 vs D의 네 재귀 ----------
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        t = 0
        for j in range(i - 1, -1, -1):
            if sig[j] > sig[i]: t = j + 1; break
        h.append(i + 1 - t)
    return h
def brute(n, k):
    """returns (A_{n,k-1}, K'(k), K''(k)=e_n, J_n(k-1))"""
    Asum = Kp = Kpp = J = 0
    for sig in itertools.permutations(range(1, n + 1)):
        h = caps(sig)
        Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
        light = prod(x for x in h if x <= k)          # prod_{h_i<=k} h_i
        lighter = prod(x for x in h if x < k)         # prod_{h_i<k} h_i
        Asum += light * k ** Z
        Kp += light * Z * k ** (Z - 1) if Z >= 1 else 0
        Kpp += light * Z * (Z - 1) * k ** (Z - 2) if Z >= 2 else 0
        J += H * k ** (H - 1) * (k - 1) ** Z * lighter if H >= 1 else 0
    return Asum, Kp, Kpp, J
def recursions(k, s):
    """D.central-gap-integer 의 네 재귀 (정확 Fraction, 정규화 n! s^n). returns dict n-> (A,d,z,j) 비정규화 값"""
    nmax = 2 * k
    r = [Fr(P[i] if i <= N else (i + 1) ** (i - 1), factorial(i) * s ** i) for i in range(nmax + 1)]
    Af = [Fr(0)] * (nmax + 1); d = [Fr(0)] * (nmax + 1); z = [Fr(0)] * (nmax + 1); j = [Fr(0)] * (nmax + 1)
    for i in range(k + 1): Af[i] = r[i]
    j[k] = r[k - 1] / (s * k)
    for n in range(k + 1, nmax + 1):
        R = n - k
        Af[n] = (sum((k + i + 1) * r[i] * Af[n - 1 - i] for i in range(0, R - 1)) + sum(min(i + 1, k) * r[i] * r[n - 1 - i] for i in range(R - 1, k + 1))) / (s * n)
        d[n] = (sum((k + i + 1) * r[i] * d[n - 1 - i] for i in range(0, R - 1)) + sum(r[i] * Af[n - 1 - i] for i in range(0, R))) / (s * n)
        z[n] = (sum((k + i + 1) * r[i] * z[n - 1 - i] for i in range(0, R - 1)) + 2 * sum(r[i] * d[n - 1 - i] for i in range(0, R - 1))) / (s * n)
        j[n] = (sum((k + i) * r[i] * j[n - 1 - i] for i in range(0, R)) + r[k - 1] * r[n - k]) / (s * n)
    res = {}
    for n in range(k + 1, nmax + 1):
        norm = factorial(n) * s ** n
        res[n] = (Af[n] * norm, d[n] * norm, z[n] * norm, j[n] * norm)
    return res
ok_all = True
for k in (3, 4, 5):
    rec = recursions(k, Fr(1))
    for n in range(k + 1, 2 * k + 1):
        if n > 9: continue
        bt = brute(n, k)
        rc = tuple(int(x) for x in rec[n])
        same = (bt == rc)
        ok_all &= same
        log('[6] k=%d n=%d brute (A,K\',K\'\',J)=%s  recursion=%s  same=%s' % (k, n, bt, rc, same))
log('[6] brute == D recursions for all tested:', ok_all)
# 기록 out_small 대조: k=8 비 e_n/J_n(k-1) n=15,16 ; k=9 n=17
s = Fr(S, 2 ** 30)
for k in (8, 9, 10):
    rec = recursions(k, s)
    for n in (2 * k - 1, 2 * k):
        _, _, e, J = rec[n]
        log('[6] k=%d n=%d  e_n/J_n(k-1) = %s   e>J: %s' % (k, n, mp.nstr(mpf(e.numerator) / e.denominator / (mpf(J.numerator) / J.denominator), 13), e > J))
log('[6] record out_small: k=8 -> 0.923427924629 (n=15), 1.016099321657 (n=16); min ratio n=17: 1.0068827')
# e_n = 2 E2 check vs d_{n,k} >= e_n - J_n(k-1) on the small table
for k in (8, 9):
    rec = recursions(k, Fr(1))
    for n in (2 * k - 1, 2 * k):
        Af, dd, e, J = rec[n]
        assert int(Af) == A[n][k - 1]
        dnk = b(n, k) - b(n, k - 1)
        log('[6] k=%d n=%d  A ok; d_{n,k}=%d  e_n-J=%d  d>=e-J: %s' % (k, n, dnk, int(e - J), dnk >= int(e - J)))

open(sys.argv[1] if len(sys.argv) > 1 else 'P12_장2-4_out.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
