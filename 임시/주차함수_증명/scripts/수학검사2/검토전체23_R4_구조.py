# 검토전체23 R4: 장5B의 구조 식(열 재귀, Abel 환원, 기저량 하계, 창 항 항별 상계,
# 꼭대기 행 하계)을 작은 크기에서 정확 유리수로 다시 센다.
import itertools
import sys
from fractions import Fraction as Fr
from math import comb, exp, factorial, floor, pi, sqrt


def table(nmax, levels):
    """A[l][n] = 최대 변위 <= l 인 길이 n 주차함수의 수 (마지막 차 재귀)."""
    A = {}
    for l in levels:
        a = [1]
        for n in range(1, nmax + 1):
            s = 0
            for j in range(1, n + 1):
                s += comb(n - 1, j - 1) * min(j, l + 1) * a[j - 1] * a[n - j]
            a.append(s)
        A[l] = a
    return A


def brute(n):
    cnt = [0] * n
    for pref in itertools.product(range(1, n + 1), repeat=n):
        occ = [False] * (n + 2)
        M = 0
        ok = True
        for a in pref:
            s = a
            while s <= n and occ[s]:
                s += 1
            if s > n:
                ok = False
                break
            occ[s] = True
            M = max(M, s - a)
        if ok:
            cnt[M] += 1
    return cnt


def p(n):
    return 1 if n == 0 else (n + 1) ** (n - 1)


# (a) 마지막 차 재귀를 직접 열거로 확인
NM = 60
A = table(NM, range(-1, NM + 1))
for n in range(1, 7):
    bc = brute(n)
    for l in range(n):
        b = A[l][n] - A[l - 1][n]
        assert b == bc[l], (n, l)
    assert A[n - 1][n] == p(n)
print('(a) 마지막 차 재귀 = 직접 열거, n<=6: OK')


def s(m, Y):  # s_m(Y) = A_{m,Y-1}/p_m
    if Y <= 0:
        return Fr(0)
    return Fr(A[min(Y - 1, NM)][m], p(m))


def c(m, Y):
    return s(m, Y + 1) - s(m, Y)


def pik(n, t):
    return Fr(comb(n, t) * t ** (t - 1) * p(n - t), p(n))


def x(t, y):
    if t <= y - 1:
        return Fr(0)
    if t == y:
        return Fr(-1, y)
    return ((y + 1) * c(t - 1, y) - (y - 1) * c(t - 1, y - 1)) / t


def theta(t, k):
    return Fr(comb(t, k) * k ** (k - 1) * (t - k) ** (t - k), t ** (t - 1))


cnt = [0, 0, 0, 0, 0]
for n in range(3, NM + 1):
    for y in range((n + 2) // 2, n):  # (n+1)/2 <= y <= n-1
        assert 2 * y >= n + 1
        lhs = c(n, y) - c(n, y - 1)
        xs = {t: x(t, y) for t in range(y, n + 1)}
        # (b) 보조정리 old-5-19
        assert lhs == sum(pik(n, t) * xs[t] for t in range(y, n + 1)), (n, y)
        cnt[0] += 1
        # 핵의 단조성
        for t in range(y, n):
            assert pik(n, t + 1) > pik(n, t)
        # (c) 따름정리 cor-L
        P = sum(xs.values())
        top = Fr(y * (y - 1)) * c(n - 1, y - 1) / n
        assert P >= -(1 + top) / y, (n, y)
        cnt[1] += 1
        # (e) 보조정리 old-5-25 의 항별 상계
        for t in range(y, n + 1):
            assert max(-xs[t], 0) <= theta(t, y) / y, (n, y, t)
            cnt[2] += 1
        # (d) 명제 old-5-22: IH 가 성립하는 모든 t0 in [y+2, n]
        for t0 in range(y + 2, n + 1):
            if all(c(m, y) >= c(m, y - 1) for m in range(t0 - 1, n)):
                win = sum((pik(n, t) - pik(n, y)) * max(-xs[t], 0) for t in range(y + 1, t0))
                pos = sum((pik(n, m + 1) - pik(n, t0 - 1)) * (c(m, y) + c(m, y - 1)) / (m + 1)
                          for m in range(t0 - 1, n))
                assert lhs >= pik(n, y) * P - win + pos, (n, y, t0)
                cnt[3] += 1
                # (5.1)
                assert lhs >= pos - win - pik(n, y) / y * (1 + top)
                # 흡수 항등식 (old-5-30 (가))
                tp = (y - 1) * pik(n, y)
                posp = sum((pik(n, m + 1) - pik(n, t0 - 1)) * (c(m, y) + c(m, y - 1)) / (m + 1)
                           for m in range(t0 - 1, n - 1))
                posp += (pik(n, n) - pik(n, t0 - 1)) * c(n - 1, y) / n
                posp += (pik(n, n) - pik(n, t0 - 1) - tp) * c(n - 1, y - 1) / n
                assert pos - pik(n, y) / y * top == posp
                cnt[4] += 1
print('(b) 열 재귀 등식 %d건, (c) 기저량 하계 %d건, (e) 항별 상계 %d건, (d) Abel 환원·(5.1)·흡수 %d건: OK'
      % (cnt[0], cnt[1], cnt[2], cnt[3]))

# (f) 정리 old-5-33 의 꼴을 Y=300 근처에서 확인 (진술의 범위 Y>=25000 밖이지만 증명은 같은 꼴)
if len(sys.argv) > 1 and sys.argv[1] == 'top':
    from mpmath import mp, mpf
    mp.dps = 30
    for Y in (300, 400):
        qm = floor(6 * Y ** (2 / 3) + 1e-9)
        nmax = 2 * Y + 1
        B = table(nmax, [Y - 1, Y, Y + 1])

        def sY(m, T):
            return mpf(B[T - 1][m]) / mpf(p(m))

        def cY(m):
            return sY(m, Y + 1) - sY(m, Y)

        lam = sum(mpf(Y) / (Y + q + 1) * cY(Y + q) for q in range(1, qm + 1))
        # 보조정리 2:old-2-34(다) 를 쓴 첫 단계(정확한 생존 확률로)
        rhs = (1 - mpf(qm + 1) / Y) * (1 - sY(Y + qm, Y)) + sum(1 - sY(Y + q, Y) for q in range(1, qm)) / Y
        print('Y=%d q_max=%d  Lambda=%s  Abel 하계=%s  %s' % (Y, qm, mp.nstr(lam, 10), mp.nstr(rhs, 10),
                                                         'OK' if lam >= rhs else 'FAIL'))

        def bor(i):
            return mp.exp(-i) * mpf(i) ** (i - 1) / mp.factorial(i)

        for chi in (2, 3, 5):
            # hov(rho, chi) = sum_z rho^z Pr(R_z <= chi-1); R_z >= z 이므로 z <= chi-1
            # Pr(R_z <= chi-1) 을 합성곱으로
            dist = {0: mpf(1)}
            probs = [mpf(1)]
            for z in range(1, chi):
                nd = {}
                for a, pa in dist.items():
                    for i in range(1, chi - a):
                        nd[a + i] = nd.get(a + i, mpf(0)) + pa * bor(i)
                dist = nd
                probs.append(sum(nd.values()))
            for m in range(Y + qm + chi + 1, 2 * Y + 2):
                rho = mpf(Y) / (m + 1)
                hov = sum(rho ** z * probs[z] for z in range(chi))
                V = (1 / mp.sqrt(2 * mp.pi)) * (mpf(m + 1) / ((Y + 1) * (m - Y))) ** mpf('1.5') * mp.exp(
                    -mpf(1) / (12 * (m - chi - Y - qm + 1)) - mpf(1) / (12 * (Y + 1)))
                low = hov * V * lam
                val = cY(m)
                if not val >= low:
                    print('FAIL', Y, chi, m, val, low)
                if m in (Y + qm + chi + 1, 2 * Y + 1):
                    print('  chi=%d m=%d  c_m(Y)=%s >= hov*V*Lambda=%s (비 %s)' % (
                        chi, m, mp.nstr(val, 8), mp.nstr(low, 8), mp.nstr(val / low, 6)))
    print('(f) 꼭대기 행 하계의 꼴: 끝')
