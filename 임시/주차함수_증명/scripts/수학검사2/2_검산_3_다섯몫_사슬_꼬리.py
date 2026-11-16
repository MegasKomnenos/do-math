# -*- coding: utf-8 -*-
"""수학 검사 2 (태그 2) 검산 3: 2.10–2.12절. 다섯 몫 분해, 쌍 항의 정수 꼴, Borel 갱신 집합, 무거운 사슬 전이·방문 확률, 갱신 다리,
지정 사슬 쌍 공식·사슬 전개, Bonferroni 잔차, 이동 꼬리 추정 (가)-(아), 사슬 가중치 정규화."""
from fractions import Fraction as Fr
from itertools import product
from math import comb, factorial, exp, log, cosh, sqrt, pi
import sympy as sp
from mpmath import mp, mpf

mp.dps = 30


def A_table(N):
    A = [[0]*(N+2) for _ in range(N+1)]
    for l in range(N+2):
        A[0][l] = 1
        for n in range(1, N+1):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A


NA = 24
A = A_table(NA)
p = lambda m: (m+1)**(m-1) if m >= 1 else 1


def b(n, l):
    if l < 0 or n < 0:
        return 0
    return A[n][l] - (A[n][l-1] if l >= 1 else 0)


Ncal = lambda l, t: min(t, l+1)*A[t-1][l] if t >= 1 else 0

print("== 정리 2.40 다섯 몫 분해 (k=2..8, 2k+1<=n<=3k-1), 명제 2.41 정수 꼴")
x = sp.symbols('x')
for k in range(2, 6):
    bT = lambda t, l: Ncal(l, t) - Ncal(l-1, t)
    delta = lambda t: bT(t, k) - bT(t, k-1)
    assert bT(k, k-1) == p(k-1) == k**(k-2) and delta(k) == -k**(k-2)
    for t in range(k+1, 3*k):
        assert bT(t, k) == (k+1)*A[t-1][k] - k*A[t-1][k-1] == A[t-1][k] + k*b(t-1, k)
        assert bT(t, k-1) == k*A[t-1][k-1] - (k-1)*A[t-1][k-2] == A[t-1][k-1] + (k-1)*b(t-1, k-1)
        assert delta(t) == (k+1)*b(t-1, k) - (k-1)*b(t-1, k-1) == k*(b(t-1, k)-b(t-1, k-1)) + b(t-1, k) + b(t-1, k-1)
    for t in range(1, k):
        assert bT(t, k) == 0 and bT(t, k-1) == 0
    assert bT(k, k) == 0
    Nmax = 3*k-1
    Ak1 = sum(sp.Rational(A[n][k-1], factorial(n))*x**n for n in range(Nmax+1))
    Bk = sum(sp.Rational(bT(t, k), factorial(t))*x**t for t in range(1, Nmax+1))
    Bk1 = sum(sp.Rational(bT(t, k-1), factorial(t))*x**t for t in range(1, Nmax+1))
    pair_ser = sp.expand(sp.series(sp.Rational(1, 2)*Ak1*(Bk**2+Bk1**2), x, 0, Nmax+1).removeO())
    for n in range(2*k+1, 3*k):
        Theta = comb(n, k)*k**(k-2)*A[n-k][k-1]
        FL = sum(comb(n, t)*delta(t)*A[n-t][k-1] for t in range(k+1, 2*k+2))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
        PAIR = sp.Poly(pair_ser, x).coeff_monomial(x**n)*factorial(n)
        d = b(n, k) - b(n, k-1)
        assert d == -Theta + FL + BV + KD + PAIR, (k, n, d, -Theta + FL + BV + KD + PAIR)
        PAIR2 = Fr(1, 2)*sum(Fr(factorial(n), factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1, k)*bT(t2, k)+bT(t1, k-1)*bT(t2, k-1))*p(n-t1-t2)
                             for t1 in range(1, n) for t2 in range(1, n-t1+1))
        assert PAIR2 == PAIR and PAIR >= 0
    print(f" k={k}: n=2k+1..3k-1 모두 d_(n,k) = -Theta+FL+BV+KD+PAIR, PAIR 정수 꼴 일치")
# n=3k 에서는 B_{k-1}^3 항이 끼어 분해가 어긋나는지 (범위 확인)
k = 3; n = 9
Nmax = 9
Ak1 = sum(sp.Rational(A[m][k-1], factorial(m))*x**m for m in range(Nmax+1))
bT = lambda t, l: Ncal(l, t) - Ncal(l-1, t)
Bk = sum(sp.Rational(bT(t, k), factorial(t))*x**t for t in range(1, Nmax+1))
Bk1 = sum(sp.Rational(bT(t, k-1), factorial(t))*x**t for t in range(1, Nmax+1))
full = sp.Poly(sp.expand(sp.series(Ak1*(sp.exp(Bk)-1-Bk+sp.exp(-Bk1)-1+Bk1), x, 0, Nmax+1).removeO()), x).coeff_monomial(x**n)*factorial(n)
pair = sp.Poly(sp.expand(sp.series(sp.Rational(1, 2)*Ak1*(Bk**2+Bk1**2), x, 0, Nmax+1).removeO()), x).coeff_monomial(x**n)*factorial(n)
print(" k=3, n=3k=9: 둘째 항 전체 vs PAIR:", full, pair, "(다르면 n<=3k-1 제한이 필요함)")

print("== 보조정리 2.45/2.46: 전이 확률 합=1, 방문 확률 = tilt*Ren, 갱신 다리 (정확 유리수)")
BorF = lambda m: Fr(m**(m-1), factorial(m))   # e^{-m} 인자 제외 (비에서 상쇄되는 경우에만 쓴다)
# pi^0_{n}(y) * p_n = 크기<=y 나무들만의 숲 수
pi0 = {}
for yv in range(1, 16):
    # 크기<=y 나무들만의 숲 수: 라벨 1을 담은 나무의 크기 t로 재귀
    F = [1]
    for n in range(1, 2*yv+2):
        F.append(sum(comb(n-1, t-1)*t**(t-1)*F[n-t] for t in range(1, min(yv, n)+1)))
    for n in range(0, 2*yv+2):
        pi0[(n, yv)] = Fr(F[n], p(n))
RenF = lambda j: Fr(1) if j == 0 else Fr(j**j, factorial(j))  # e^{-j} 제외
for yv in range(1, 12):
    for q0 in range(1, yv+3):
        n = yv+q0-1
        # 전이: q -> q' (1<=q'<q) 확률 Bor(q-q')Bor(y+q')/Bor(y+q); e 인자: e^{-(q-q')-(y+q')+(y+q)} = 1
        trans = lambda q, qp: BorF(q-qp)*BorF(yv+qp)/BorF(yv+q)
        for q in range(1, q0+1):
            tot = sum(trans(q, qp) for qp in range(1, q)) + pi0[(yv+q-1, yv)]
            assert tot == 1, (yv, q0, q, tot)
            # 2.5절 pi_{n'}(m) 과 같음
            npr = yv+q-1
            for qp in range(1, q):
                m = yv+qp
                assert trans(q, qp) == Fr(comb(npr, m)*m**(m-1)*p(npr-m), p(npr))
        # 방문 확률: Markov 연쇄 직접
        visit = {q0: Fr(1)}
        for q in range(q0-1, 0, -1):
            visit[q] = sum(visit[qq]*trans(qq, q) for qq in range(q+1, q0+1))
        for q in range(1, q0):
            # tilt*Ren: e 인자 e^{-(y+q)+(y+q0)-(q0-q)} = 1
            assert visit[q] == BorF(yv+q)/BorF(yv+q0)*RenF(q0-q), (yv, q0, q)
        # 갱신 다리
        for qp in range(1, q0):
            for q in range(qp+1, q0):
                both = visit[q]*(BorF(yv+qp)/BorF(yv+q)*RenF(q-qp))
                assert both/visit[qp] == RenF(q0-q)*RenF(q-qp)/RenF(q0-qp)
print(" y<=11, q0<=y+2: OK")
print("== 명제 2.44: Pr(j in H_B(q)) = Ren(j) (Borel 보행 직접, j<=12)")
BT = lambda i, m: Fr(i, m)*Fr(m**(m-i), factorial(m-i))
for j in range(1, 13):
    assert sum(BT(i, j) for i in range(1, j+1)) == RenF(j)
print(" OK")

print("== 정리 chain-expansion (나)(다)(라): W_n(gamma) 전수 (n<=6), 사슬 전개 항등식 (n<=50)")


def forests(n):
    for par in product(range(0, n+1), repeat=n):
        ok = True
        for v in range(1, n+1):
            if par[v-1] == v:
                ok = False; break
            seen = {v}; u = par[v-1]
            while u:
                if u in seen:
                    ok = False; break
                seen.add(u); u = par[u-1]
            if not ok:
                break
        if ok:
            yield par


def sizes_anc(par, n):
    ch = {v: [] for v in range(0, n+1)}
    for v in range(1, n+1):
        ch[par[v-1]].append(v)
    t = {}

    def rec(v):
        tot = 1
        for cc in ch[v]:
            tot += rec(cc)
        t[v] = tot
        return tot
    for r in ch[0]:
        rec(r)
    anc = {}
    for v in range(1, n+1):
        a = []; u = par[v-1]
        while u:
            a.append(u); u = par[u-1]
        anc[v] = set(a)
    return t, anc


def Wn(n, gam):
    j = len(gam); tj = n+1-sum(gam)
    val = Fr(factorial(n)*tj**(tj-1)*gam[0]**(gam[0]-1), factorial(tj)*factorial(gam[0]-1))
    for gi in gam[1:]:
        val *= Fr(gi**gi, factorial(gi))
    return val


for n in range(2, 7):
    cnt = {}
    for par in forests(n):
        t, anc = sizes_anc(par, n)
        for v1 in range(1, n+1):
            cnt[(t[v1],)] = cnt.get((t[v1],), 0)+1
            for v2 in range(1, n+1):
                if v1 in anc[v2]:
                    cnt[(t[v1], t[v2])] = cnt.get((t[v1], t[v2]), 0)+1
                    for v3 in range(1, n+1):
                        if v2 in anc[v3]:
                            cnt[(t[v1], t[v2], t[v3])] = cnt.get((t[v1], t[v2], t[v3]), 0)+1
    for key, m in cnt.items():
        gam = [n+1-key[0]] + [key[i-1]-key[i] for i in range(1, len(key))]
        assert Wn(n, gam) == m, (n, key, gam, Wn(n, gam), m)
    # (나) 꼴
    for key, m in cnt.items():
        if len(key) == 2:
            g1 = n+1-key[0]; g2 = key[0]-key[1]; t2 = key[1]
            assert m == Fr(factorial(n), factorial(g1-1)*factorial(g2)*factorial(t2))*t2**(t2-1)*g1**(g1-1)*g2**g2
print(" W_n(gamma) 길이 1,2,3 전수 일치 (n<=6)")


def Q(n, r, j):
    """정리 chain-expansion (라)의 Q_{n,r,j}: 간격 수열 합, d에 대한 둘째 차분."""
    tot = Fr(0)
    def rec(prefix, rem):
        nonlocal tot
        if len(prefix) == j:
            ts = []; acc = 0
            for gi in prefix:
                acc += gi; ts.append(n+1-acc)
            f = lambda d: Fr(1) if True else None
            def F(d):
                v = Fr(1)
                for ti in ts:
                    v *= Fr(max(d-(n+1-ti), 0), ti)
                return v
            tot += Wn(n, prefix)*(F(r+2)-2*F(r+1)+F(r))
            return
        for gi in range(1, rem+1):
            rec(prefix+[gi], rem-gi)
    rec([], r+1)
    return tot


for n in range(3, 17):
    for r in range(1, (n-1)//2+1):
        lhs = b(n, n-r-1) - b(n, n-r)
        Qs = [Q(n, r, j) for j in range(1, r+2)]
        assert all(q >= 0 for q in Qs)
        rhs = sum((-1)**(j+1)*Qs[j-1] for j in range(1, r+2))
        assert lhs == rhs, (n, r, lhs, rhs)
        assert Qs[0] == comb(n, r)*(n-r)**(n-r-2)*(r+1)**r
        if r >= 1:
            Q2 = sum(Fr(2*Wn(n, [g1, g2]), (n+1-g1)*(n+1-g1-g2)) for g1 in range(1, r) for g2 in range(1, r-g1+1)) + \
                sum(Fr((g2+1)*Wn(n, [g1, g2]), (n+1-g1)*(n+1-g1-g2)) for g1 in range(1, r+1) for g2 in [r+1-g1] if g2 >= 1)
            assert (len(Qs) < 2) or Q2 == Qs[1], (n, r, Q2, Qs[1])
        # (가) Bonferroni 양쪽
        for m in range(1, r+2):
            part = sum((-1)**(j+1)*Qs[j-1] for j in range(1, m+1))
            assert (-1)**m*(lhs - part) >= 0, (n, r, m)
print(" 사슬 전개 항등식, Q_1 닫힌 꼴, Q_2 꼴, (가) Bonferroni 교대 부등식 (n<=16, r<=(n-1)/2) OK")

print("== 정리 moving-tail (다)(라)(마)(바)(사)(아)")
nf = lambda n, d: mpf(mp.e)**d*mp.factorial(n)/mp.factorial(n-d)*mpf(n-d)**(n-d-2)/mpf(n)**(n-2)
Ren = lambda j: mpf(1) if j == 0 else mpf(j)**j*mp.e**(-j)/mp.factorial(j)
for n in range(3, 200, 7):
    for d in range(0, n):
        v = nf(n, d)
        assert (mpf(n)/(n-d))**2 - mpf(10)**-20 <= v <= (mpf(n)/(n-d))**3 + mpf(10)**-20, (n, d)
print(" (다) (n/(n-d))^2 <= nf <= (n/(n-d))^3 OK (n<200)")
for n in range(3, 25):
    for r in range(1, (n-1)//2+1):
        Q1 = comb(n, r)*(n-r)**(n-r-2)*(r+1)**r
        assert abs(mpf(Q1)/mpf(n)**(n-2) - nf(n, r)*mp.e*Ren(r+1)) < mpf(10)**-20
        for g1 in range(1, r+1):
            for g2 in range(1, r+2-g1):
                t1 = n+1-g1; t2 = t1-g2
                lhs = mpf(Wn(n, [g1, g2]).numerator)/Wn(n, [g1, g2]).denominator/(t1*t2*mpf(n)**(n-2))
                rhs = mp.e*nf(n, g1+g2-1)/t1*Ren(g1)*Ren(g2)
                assert abs(lhs-rhs) < mpf(10)**-20*max(1, lhs)
        d = b(n, n-r) - b(n, n-r-1)
        mid = nf(n, r)*mp.e*Ren(r+1) + mpf(d)/mpf(n)**(n-2)
        assert 0 <= mid <= mp.e*(5*r-1)/(4*n*(1-mpf(r)/n)**4) + mpf(10)**-20, (n, r, mid)
        assert abs(-mpf(d)/mpf(n)**(n-2) - mp.e*Ren(r+1)) <= 60*(r+1)/mpf(n)
print(" (라) 두 등식, (마) 0<=...<=e(5r-1)/(4n(1-r/n)^4), (사) |..|<=60(r+1)/n  (n<=24) OK")
for m in range(2, 200):
    s1 = sum(Ren(g)*Ren(m-g) for g in range(1, m)); s2 = sum((m-g)*Ren(g)*Ren(m-g) for g in range(1, m))
    assert s1 <= 0.5 and s2 <= mpf(m)/4
print(" (라) 두 합 상계 (m<200) OK; m=2:", float(sum(Ren(g)*Ren(2-g) for g in range(1, 2))), " 최대 s1:", max(float(sum(Ren(g)*Ren(m-g) for g in range(1, m))) for m in range(2, 200)))
for r in range(0, 300):
    v = mp.e*Ren(r+1)
    assert v <= 1
    if r >= 1:
        assert v >= mp.e**-0.5*mpf(r)**-0.5 > 1/(2*mp.sqrt(r+1))
print(" (바) OK; 4(r+1)>er:", all(4*(r+1) > exp(1)*r for r in range(1, 1000)))
print(" (사) 상수: (1-1/2)^{-4} =", 16, " 4e(5r-1)/n < 20e(r+1)/n, 20e =", 20*exp(1), " ((1-s)^{-3}-1)/s at s=1/2 =", (8-1)/0.5,
      " 증가성:", all(((1-s)**-3-1)/s <= ((1-s-1e-6)**-3-1)/(s+1e-6) for s in [0.001*i for i in range(1, 499)]))
print(" (아) 상수: e(20/19)^4 =", exp(1)*(20/19)**4, " r/(20(r+1)^{3/2}) < 1/20:", all(r/(20*(r+1)**1.5) < 1/20 for r in range(1, 1000)))
# (아) 직접: D=2,3, n>=20 D^{3/2}, n<=50
A60 = A_table(110)
b60 = lambda n, l: A60[n][l] - (A60[n][l-1] if l >= 1 else 0)
for D in (2, 3):
    nmin = int(mp.ceil(20*mpf(D)**1.5))
    for n in range(nmin, 111):
        seq = [b60(n, n-rr) for rr in range(D, 0, -1)]
        assert all(seq[i] > seq[i+1] for i in range(len(seq)-1)), (D, n, seq)
    print(f" (아) D={D}: n>=ceil(20D^1.5)={nmin} (<=110) 에서 b_(n,n-D)>...>b_(n,n-1) OK")
# 실제로는 훨씬 작은 n부터 성립하는지 참고
print(" 참고: n=110 꼬리 b_{n,n-3..n-1} =", [b60(110, 110-rr) for rr in range(3, 0, -1)], "(엄격 증가 꼬리)")

print("== 보조정리 chain-normalization (가)(나)(다) (n<=16)")
for n in range(4, 17):
    for r in range(1, (n-1)//2+1):
        for j in range(1, 4):
            def rec(prefix, rem):
                if len(prefix) == j:
                    ts = []; acc = 0
                    for gi in prefix:
                        acc += gi; ts.append(n+1-acc)
                    W = nf(n, n-ts[-1])
                    for ti in ts[:-1]:
                        W *= mpf(n)/ti
                    lhs = mpf(Wn(n, prefix).numerator)/Wn(n, prefix).denominator/(mpf(n)**(n-2))
                    for ti in ts:
                        lhs /= ti
                    rhs = mp.e*mpf(n)**(1-j)*W
                    for gi in prefix:
                        rhs *= Ren(gi)
                    assert abs(lhs-rhs) < mpf(10)**-18*max(1, lhs), (n, prefix)
                    assert 1 - mpf(10)**-20 <= W <= (1-mpf(r)/n)**(-j-2) + mpf(10)**-20, (n, r, prefix, W)
                    return
                for gi in range(1, rem+1):
                    rec(prefix+[gi], rem-gi)
            rec([], r+1)
print(" (가) 등식, (나) 1<=W<=(1-r/n)^{-j-2} OK")
# (다) iota=0..3
for n in range(5, 17):
    for r in range(1, 6):
        for iota in range(0, 4):
            if n < max(2*r+1, 2*r+2*iota-3) or r+iota > n:
                continue
            lhs = sum((-1)**(iota-i)*comb(iota, i)*(p(n)-A[n][n-(r+i)]) for i in range(iota+1))
            box = [Fr(0)]
            for j in range(1, r+iota):
                def rec(prefix, rem):
                    if len(prefix) == j:
                        ts = []; acc = 0
                        for gi in prefix:
                            acc += gi; ts.append(n+1-acc)
                        def F(d):
                            v = Fr(1)
                            for ti in ts:
                                v *= Fr(max(d-(n+1-ti), 0), ti)
                            return v
                        box[0] += (-1)**(j+1)*Wn(n, prefix)*sum((-1)**(iota-i)*comb(iota, i)*F(r+i) for i in range(iota+1))
                        return
                    for gi in range(1, rem+1):
                        rec(prefix+[gi], rem-gi)
                rec([], r+iota-1)
            tot = box[0]
            assert tot == lhs, (n, r, iota, tot, lhs)
            if iota == 1:
                assert lhs == b(n, n-r)
            if iota == 2:
                assert lhs == b(n, n-r-1) - b(n, n-r)
            if iota == 3:
                assert lhs == b(n, n-r-2) - 2*b(n, n-r-1) + b(n, n-r)
print(" (다) iota=0..3 전개 항등식과 좌변의 네 값 OK (n<=16, r<6)")
