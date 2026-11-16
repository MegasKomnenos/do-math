# -*- coding: utf-8 -*-
"""수학 검사 2 (태그 2) 검산 2: 2.6–2.9절. g의 성질, 동률–막힘 항등식, 얼린 용량 다항식, 경계 다항식 J_n(z)와 그 지수 생성함수,
(SM)(DM0)(SC), 계수 비 e, 자리 법칙 단조성, 수준 방문 보존, 나무 곡률, theta, Ren·Psi, 정리 2.38, 따름정리 2.39."""
from fractions import Fraction as Fr
from itertools import permutations, product
from math import comb, factorial, exp, log, cosh, sqrt, pi, lgamma
import sympy as sp
from mpmath import mp, mpf, quad

mp.dps = 30


def prod(it):
    r = 1
    for v in it:
        r *= v
    return r


def caps(sig):
    n = len(sig); h = []
    for i in range(1, n+1):
        z = 0
        for j in range(1, i):
            if sig[j-1] > sig[i-1]:
                z = j
        h.append(i - z)
    return h


def A_table(N):
    A = [[0]*(N+2) for _ in range(N+1)]
    for l in range(N+2):
        A[0][l] = 1
        for n in range(1, N+1):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A


NA = 60
A = A_table(NA)
p = lambda m: (m+1)**(m-1) if m >= 1 else 1


def b(n, l):
    if l < 0:
        return 0
    return A[n][l] - (A[n][l-1] if l >= 1 else 0)


def s(m, y):  # 생존 확률 s_m(y) = A_{m,y-1}/p_m, s_m(0)=0
    if y <= 0:
        return Fr(0)
    return Fr(A[m][y-1], p(m))


print("== 보조정리 2.26: g(x)=(x-1)log(1+1/x)")
g = lambda xx: (xx-1)*log(1+1/xx)
gp = lambda xx: log(1+1/xx) - (xx-1)/(xx*(xx+1))
xs = [1+i*0.05 for i in range(0, 400)]
assert all(gp(xx) >= (3*xx+1)/((2*xx+1)*xx*(xx+1)) - 1e-13 for xx in xs)
assert all(1-3/(2*xx)+1/(2*xx*xx) <= g(xx) <= 1-3/(2*xx)+5/(6*xx*xx) for xx in xs)
assert all(gp(xx) <= 3/(2*xx*xx)+1e-13 for xx in [0.2+i*0.01 for i in range(0, 2000)])
assert all(g(xx) < 1 for xx in [0.01*i for i in range(1, 5000)])
print(" (가)(다)(라) 격자 검사 OK;  (라) x=0.19:", gp(0.19) <= 3/(2*0.19**2), "(1/5 미만에서 깨지는지)")
for m in range(1, 30):
    Bm = lambda m: exp(-m + (m-1)*log(m) - lgamma(m+1))
    assert abs(Bm(m+1)/Bm(m) - exp(g(m)-1)) < 1e-12
    assert abs(p(m+1)/p(m) - (m+1)*exp(g(m+1))) < 1e-9*p(m+1)/p(m)
print(" (나) Bor(m+1)/Bor(m)=e^{g(m)-1}, p_{m+1}/p_m=(m+1)e^{g(m+1)} (m<30) OK")

print("== 2.7절: 동률–막힘 항등식, K''=2E2, 보조정리 2.30, 경계 다항식 (n<=7 전수)")
z, y = sp.symbols('z y')


def fiber_data(n):
    """결과 순열마다 용량과 섬유 전수(변위 벡터)."""
    out = []
    for sig in permutations(range(1, n+1)):
        h = caps(sig)
        out.append((sig, h))
    return out


for n in range(1, 8):
    data = fiber_data(n)
    for k in range(1, n+1):
        E = E2 = B = 0; Eodd = 0
        bk = bk1 = 0
        for sig, h in data:
            # 변위 벡터 d_i in [0,h_i-1]; M=k 인 것, M#=개수
            for d in product(*[range(hi) for hi in h]):
                M = max(d); cnt = d.count(M)
                if M == k:
                    bk += 1
                    if cnt % 2 == 0:
                        E += 1
                    if cnt == 2:
                        E2 += 1
                if M == k-1:
                    bk1 += 1
                    if all(h[i] == k for i in range(n) if d[i] == M):
                        B += 1
        assert bk == b(n, k) and bk1 == b(n, k-1)
        assert b(n, k) - b(n, k-1) == 2*E - B, (n, k)
        # 얼린 용량 다항식
        K = sum(prod(hi for hi in h if hi <= k)*y**sum(1 for hi in h if hi > k) for sig, h in data)
        assert K.subs(y, k) == A[n][k-1] and K.subs(y, k+1) == A[n][k]
        assert sp.diff(K, y, 2).subs(y, k) == 2*E2
        assert K.subs(y, k-1) - (A[n][k-2] if k >= 2 else 0) == B
        # 보조정리 2.30 첫 식
        B2 = sum(prod(hi for hi in h if hi < k)*(k-1)**sum(1 for hi in h if hi > k)*(k**sum(1 for hi in h if hi == k)-(k-1)**sum(1 for hi in h if hi == k)) for sig, h in data)
        assert B2 == B
        J = sum(sum(1 for hi in h if hi == k)*k**(max(sum(1 for hi in h if hi == k)-1, 0))*z**sum(1 for hi in h if hi > k)*prod(hi for hi in h if hi < k) for sig, h in data)
        Jk1 = J.subs(z, k-1)
        if n <= 2*k-1:
            assert Jk1 == B, (n, k)
            assert all(sum(1 for hi in h if hi == k) <= 1 for sig, h in data)
        if n == 2*k:
            Xi = comb(2*k-1, k-1)*p(k-1)**2
            assert Jk1 - Xi == B, (n, k, Jk1, B, Xi)
        if k == n:
            assert B == b(n, n-1) and bk == 0
        if k == 1:
            assert B == 1
    print(f" n={n}: d=2E-B, K(k)=A, K(k+1)=A, K''(k)=2E2, K(k-1)-A_(k-2)=B, 보조정리 2.30 (B식, n<=2k-1 → B=J(k-1), n=2k → B=J(k-1)-Xi) OK")

print("== 보조정리 J-egf: (가) 재귀, (나) 생성함수 (k=1..4, n<=2k; J는 전수로)")
x = sp.symbols('x')
Jcache = {}
for k in range(1, 5):
    Js = {}
    for n in range(0, 2*k+1):
        if n == 0:
            Js[0] = sp.Integer(0); continue
        data = fiber_data(n)
        Js[n] = sp.expand(sum(sum(1 for hi in h if hi == k)*k**(max(sum(1 for hi in h if hi == k)-1, 0))*z**sum(1 for hi in h if hi > k)*prod(hi for hi in h if hi < k) for sig, h in data))
    for n in range(0, 2*k):
        rec = sum(comb(n, i)*(z+i+1)*p(i)*Js[n-i] for i in range(n+1)) + (comb(n, k-1)*p(k-1)*p(n-k+1) if n >= k-1 else 0)
        assert sp.expand(rec - Js[n+1]) == 0, (k, n)
    N = 2*k
    T = sum(sp.Rational(t**(t-1), factorial(t))*x**t for t in range(1, N+2))
    Gr = T - T**2/2
    ex = sp.series(sp.exp(T)*sp.exp(z*Gr), x, 0, N+1).removeO()
    inner = sp.series(sp.exp(-z*Gr)*x**(k-1)/factorial(k-1), x, 0, N+1).removeO()
    integ = sp.integrate(inner, x)
    Y = sp.expand(sp.series(p(k-1)*ex*integ, x, 0, N+1).removeO())
    for n in range(0, N+1):
        c = sp.Poly(Y, x).coeff_monomial(x**n)*factorial(n)
        assert sp.expand(c - Js[n]) == 0, (k, n, c, Js[n])
    # n=2k+1 에서 어긋나는지 (일치 범위 확인)
    print(f" k={k}: (가) 0<=n<=2k-1, (나) 0<=n<=2k 일치;  J_m=0 (m<k):", all(Js[m] == 0 for m in range(0, k)))
# (Gr)'=e^T
N = 10
T = sum(sp.Rational(t**(t-1), factorial(t))*x**t for t in range(1, N+2))
assert sp.expand(sp.series(sp.diff(T - T**2/2, x) - sp.exp(T), x, 0, N).removeO()) == 0
print(" (Gr)' = e^T (10차) OK")

print("== 정리 2.31 (SM)(DM0)(SC) n<=59, 따름정리 ratio-e")
for m in range(0, NA):
    for yv in range(1, NA):
        assert s(m+1, yv) <= s(m, yv), ("SM", m, yv)
        assert s(m, yv) <= s(m+1, yv+1), ("DM0", m, yv)
        l = yv-1
        assert Fr(A[m][l], p(m)) <= Fr(A[m+1][l+1], p(m+1))
        assert Fr(A[m+1][l], factorial(m+1)) <= Fr(A[m][l], factorial(m))*sp.E if False else Fr(A[m+1][l], factorial(m+1)) < Fr(A[m][l], factorial(m))*Fr(2718281829, 1000000000)
print(" OK (ratio-e는 e의 유리 상계 2.718281829로 검사)")

print("== 보조정리 2.32: 두 비의 닫힌 꼴, (ㄱ) 비증가·극한, (ㄴ) (m+1)P_{m+1}(j)<=mP_m(j)")
P = lambda m, j: Fr(j*comb(m-1, j-1)*p(j-1)*p(m-j), p(m))
for m in range(1, 40):
    assert sum(P(m, j) for j in range(1, m+1)) == 1
    for rho in range(0, m):
        lhs = P(m+1, m+1-rho)/P(m, m-rho)
        rhs = Fr(m, m-rho)*Fr((m-rho+1)**(m-rho), (m-rho)**(m-rho-1))*Fr((m+1)**(m-1), (m+2)**m)
        assert lhs == rhs
        assert lhs < 1
        assert P(m, m-rho) == Fr(comb(m-1, rho)*(m-rho)**(m-rho-1)*p(rho), (m+1)**(m-1))
    for j in range(1, m+1):
        rho = m-j+1
        lhs = P(m+1, j)/P(m, j)
        rhs = Fr(m, rho)*Fr((rho+1)**(rho-1), rho**(rho-2) if rho >= 2 else Fr(1, rho**(2-rho)))*Fr((m+1)**(m-1), (m+2)**m) if rho >= 2 else Fr(m, 1)*Fr(1, Fr(1, 1))*Fr((m+1)**(m-1), (m+2)**m)
        if rho >= 2:
            assert lhs == rhs, (m, j)
        assert (m+1)*P(m+1, j) <= m*P(m, j)
        if rho == 1:
            assert lhs == Fr(m)*Fr(1, 1)*Fr((m+1)**(m-1), (m+2)**m)  # (rho+1)^{rho-1}/rho^{rho-2} = 1/1 = 1 at rho=1
print(" OK; 극한 P_m(m-rho)->Bor(rho+1):", float(P(400, 400-2)), exp(-3)*3/2)
# 보조정리 2.33 분포함수 부등식
for m in range(1, 40):
    F = lambda mm, chi: sum(P(mm, j) for j in range(1, min(chi, mm)+1))
    for chi in range(0, m+1):
        assert F(m+1, chi) <= F(m, chi) <= F(m+1, chi+1)
print(" 보조정리 2.33 F_{m+1}(chi)<=F_m(chi)<=F_{m+1}(chi+1) OK")

print("== 보조정리 2.34 수준 방문 보존 (Y<=20, K<=59)")
c = lambda m, Y: s(m, Y+1) - s(m, Y)
for Y in range(1, 21):
    for K in range(Y+1, NA):
        assert sum(c(m, Y) for m in range(Y+1, K+1)) >= 1 - s(K, Y)
        w = lambda m: Fr(1, m)  # 비증가 무게 보기
        assert sum(w(m)*c(m, Y) for m in range(Y+1, K+1)) >= sum(w(m)*(s(m-1, Y)-s(m, Y)) for m in range(Y+1, K+1))
print(" OK (무게 1/m 보기 포함)")

print("== 2.9절: 나무 곡률 x_t(y), theta_t(k), Ren, Psi")
Ncal = lambda l, t: min(t, l+1)*A[t-1][l] if t >= 1 else 0
for yv in range(2, 20):
    for t in range(yv, 40):
        xt = Fr(Ncal(yv, t) - 2*Ncal(yv-1, t) + Ncal(yv-2, t), t**(t-1))
        if t == yv:
            assert xt == Fr(-1, yv)
        else:
            assert xt == Fr((yv+1)*b(t-1, yv) - (yv-1)*b(t-1, yv-1), t**(t-1))
print(" x_y(y)=-1/y, x_t(y) 닫힌 꼴 OK")
# theta_t(k) 직접 (나무 전수 t<=6)


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


def sizes(par, n):
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
    return t


theta = lambda t, k: Fr(comb(t, k)*k**(k-1)*(t-k)**(t-k), t**(t-1))
for t in range(2, 7):
    for k in range(2, t+1):
        tot = 0; trees = 0
        for par in forests(t):
            if par.count(0) == 1:
                trees += 1
                tt = sizes(par, t)
                tot += sum(1 for v in tt if tt[v] == k)
        assert trees == t**(t-1) and Fr(tot, trees) == theta(t, k), (t, k)
    # 정리 chain-expansion (가): E_n[H_t(F)] = theta_{n+1}(t), n=t
    n = t
    for tsz in range(1, n+1):
        tot = 0
        for par in forests(n):
            tt = sizes(par, n)
            tot += sum(1 for v in tt if tt[v] == tsz)
        assert tot == comb(n, tsz)*tsz**(tsz-1)*(n+1-tsz)**(n-tsz)
        assert Fr(tot, p(n)) == Fr(comb(n+1, tsz)*tsz**(tsz-1)*(n+1-tsz)**(n+1-tsz), (n+1)**n)
print(" theta_t(k) (t<=6 전수), chain-expansion(가) E_n[H_t]=theta_{n+1}(t) (n<=6) OK")
Bor = lambda m: mpf(m)**(m-1)*mp.e**(-m)/mp.factorial(m)
Ren = lambda j: mpf(1) if j == 0 else mpf(j)**j*mp.e**(-j)/mp.factorial(j)
Psi = lambda q: sum(Ren(j) for j in range(1, q+1))
for j in range(1, 60):
    assert abs(Ren(j) - j*Bor(j)) < mpf(10)**-25
    assert Ren(j) <= (2*pi*j)**-0.5
    assert Psi(j) <= 2*(2*pi)**-0.5*sqrt(j) <= 0.7979*sqrt(j)
print(" (가)(라) OK; 2(2pi)^{-1/2} =", 2*(2*pi)**-0.5)
# (나) Ren(j) = sum_i Bor^{*i}(j)
BT = lambda j, m: Fr(j, m)*Fr(m**(m-j), factorial(m-j))  # e^{-m} 제외
for j in range(1, 15):
    assert sum(BT(i, j) for i in range(1, j+1)) == Fr(j**j, factorial(j))
# (다) G1
for q in range(1, 40):
    lhs = sum(Bor(m)*Psi(q-m) for m in range(1, q+1)); rhs = Psi(q) - sum(Bor(m) for m in range(1, q+1))
    assert abs(lhs-rhs) < mpf(10)**-25
# (마)
for k in range(2, 20):
    for t in range(k, 40):
        assert abs(Ren(t-k)*Bor(k)/Bor(t) - mpf(theta(t, k).numerator)/theta(t, k).denominator) < mpf(10)**-25
print(" (나)(다)(마) OK")

print("== 정리 2.38 (ii)(iii)(iv), q=1 닫힌 꼴, 따름정리 2.39 (a)-(d)")
xt = lambda t, k: Fr(Ncal(k, t) - 2*Ncal(k-1, t) + Ncal(k-2, t), t**(t-1))
for k in range(2, 30):
    for t in range(k, NA+1):
        kx = k*xt(t, k)
        assert kx >= -theta(t, k), (k, t)
        q = t-k
        if t <= 2*k:
            assert float(kx) <= float(-theta(t, k)) + (2*q*q+q)*cosh(q/k)/k + 1e-12, (k, t)
        assert Ren(q) - mpf(10)**-20 <= mpf(theta(t, k).numerator)/theta(t, k).denominator <= Ren(q)*(1+mpf(q)/k)**1.5 + mpf(10)**-20
    assert k*xt(k+1, k) == Fr(-(k-1)*k**(k-1), (k+1)**k) == -Fr(k-1, k+1)*theta(k+1, k)
    Pt = lambda t: sum(xt(tp, k) for tp in range(k, t+1))
    for q in range(0, min(k, NA-k)+1):
        kP = k*Pt(k+q)
        assert kP >= -sum(theta(k+qq, k) for qq in range(0, q+1))
        assert abs(float(kP) + float(sum(theta(k+qq, k) for qq in range(0, q+1)))) <= cosh(1)/k*sum(2*qq*qq+qq for qq in range(q+1)) + 1e-12
        assert abs(float(kP) + 1 + float(Psi(q))) <= cosh(1)/k*sum(2*qq*qq+qq for qq in range(q+1)) + 3*q**1.5/k + 1e-12
        assert float(kP) >= -(1+q/k)**1.5*(1+float(Psi(q))) - 1e-12 >= -(1+q/k)**1.5*(1+0.7979*sqrt(q)) - 1e-12
print(" OK (k<30, t<=60); (1+u)^{3/2}-1<=3u on [0,1]:", all((1+u)**1.5-1 <= 3*u for u in [i/1000 for i in range(1001)]))
print(" q=1 극한 -(k-1)k^{k-1}/(k+1)^k at k=10^4:", -(1e4-1)/(1e4+1)*(1e4/(1e4+1))**(1e4-1), " -1/e =", -1/exp(1))
print(" Robbins: Bor(m)=(2pi)^{-1/2}m^{-3/2}e^{-rb_m}; rb_m in (1/(12m+1),1/(12m)):",
      all(1/(12*m+1) < float(mp.log(mp.factorial(m)) - (m+0.5)*mp.log(m) + m - 0.5*mp.log(2*mp.pi)) < 1/(12*m) for m in range(1, 200)))
