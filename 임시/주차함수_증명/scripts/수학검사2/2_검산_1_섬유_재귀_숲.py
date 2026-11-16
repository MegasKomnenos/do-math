# -*- coding: utf-8 -*-
"""수학 검사 2 (태그 2) 검산 1: 2.1–2.5절. 섬유 행, 마지막 차 재귀, 역수 생성함수, 숲 일치, 최대 나무 사슬, 부호식, 사슬 구성 셈, Borel 질량."""
from fractions import Fraction as Fr
from itertools import permutations, product
from math import comb, factorial, exp, log, cosh, sqrt
import sympy as sp


def prod(it):
    r = 1
    for v in it:
        r *= v
    return r


def park(pref):
    n = len(pref); spots = [0]*(n+1); out = []
    for car, a in enumerate(pref, 1):
        s = a
        while s <= n and spots[s]:
            s += 1
        if s > n:
            return None
        spots[s] = car; out.append(s - a)
    return tuple(spots[1:]), max(out)


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
    """A[n][l] = A_{n,l} (정리 2.6 재귀), 0<=n<=N, 0<=l<=N."""
    A = [[0]*(N+1) for _ in range(N+1)]
    for l in range(N+1):
        A[0][l] = 1
        for n in range(1, N+1):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A


p = lambda m: (m+1)**(m-1) if m >= 1 else 1

print("== 정리 2.5: n=7, sigma=(1,2,3,5,4,6,7) 섬유 행 (직접 주차 vs 곱 공식)")
sig = (1, 2, 3, 5, 4, 6, 7); n = 7
row = [0]*n; fib = 0
for pref in product(range(1, n+1), repeat=n):
    r = park(pref)
    if r and r[0] == sig:
        row[r[1]] += 1; fib += 1
h = caps(sig)
Acum = [prod(min(hi, l+1) for hi in h) for l in range(n)]
prow = [Acum[0]] + [Acum[l]-Acum[l-1] for l in range(1, n)]
print(" h =", h, " A_l =", Acum, " 곱공식 행 =", prow, " 직접 행 =", row, " 합 =", sum(row), " 섬유 크기 prod h =", prod(h))
assert row == prow == [1, 31, 130, 222, 216, 264, 144] and sum(row) == 1008 == prod(h)
print(" 24(2l+1) at l=4,5:", [24*(2*l+1) for l in (4, 5)], " A_l=24(l+1)^2 at l=3,4,5:", [24*(l+1)**2 for l in (3, 4, 5)])
for N in (8, 9, 10):
    sp_ = tuple([N-6, N-5, N-4, N-2, N-3, N-1, N] + list(range(N-7, 0, -1)))
    hh = caps(sp_)
    print(f" sigma' n={N}: {sp_} h={hh}", " h[:7]==(1,2,3,4,1,6,7) & rest 1:", hh[:7] == [1, 2, 3, 4, 1, 6, 7] and all(v == 1 for v in hh[7:]))

print("== 정리 2.6 재귀 vs 직접 주차 (n<=6), 따름정리 2.4")
A = A_table(40)
for n in range(1, 7):
    cnt = {}; tot = 0
    for pref in product(range(1, n+1), repeat=n):
        r = park(pref)
        if r:
            cnt[r[1]] = cnt.get(r[1], 0)+1; tot += 1
    Ab = [sum(cnt.get(m, 0) for m in range(l+1)) for l in range(n)]
    Af = [sum(prod(min(v, l+1) for v in caps(s)) for s in permutations(range(1, n+1))) for l in range(n)]
    assert Ab == [A[n][l] for l in range(n)] == Af, (n, Ab, Af)
    assert tot == (n+1)**(n-1)
print(" n<=6: 재귀 = 직접 = 따름정리 2.4 합  OK;  n=7 행 (1.3절 표):", [A[7][0]]+[A[7][l]-A[7][l-1] for l in range(1, 7)])

print("== 명제 2.7: 자리 법칙 합=1, 극한식")
for n in (5, 10, 20):
    s = sum(Fr(comb(n-1, j)*(j+1)*p(j)*p(n-1-j), p(n)) for j in range(n))
    assert s == 1
    for rho in (0, 1, 3):
        v = Fr(comb(n-1, rho)*(n-rho)**(n-rho-1)*p(rho), (n+1)**(n-1))
        v2 = Fr(comb(n-1, n-1-rho)*(n-rho)*p(n-1-rho)*p(rho), p(n))
        assert v == v2
        lim = exp(-(rho+1))*(rho+1)**(rho-1)/factorial(rho)
        print(f" n={n} rho={rho}: Pr={float(v):.6f}  극한 Bor(rho+1)={lim:.6f}")

print("== 명제 2.8: A' = (l+1)A^2 - Q'A 와 닫힌 꼴 (형식 멱급수, sympy)")
x = sp.symbols('x')
for l in range(0, 4):
    N = 12
    Aser = sum(sp.Rational(A[n][l], factorial(n))*x**n for n in range(N+1))
    Q = sum((l-j)*p(j)*x**(j+1)/sp.factorial(j+1) for j in range(l))
    lhs = sp.series(sp.diff(Aser, x), x, 0, N).removeO()
    rhs = sp.series((l+1)*Aser**2 - sp.diff(Q, x)*Aser, x, 0, N).removeO()
    assert sp.expand(lhs - rhs) == 0, l
    closed = sp.exp(-Q)/(1-(l+1)*sp.integrate(sp.exp(-Q), (x, 0, x)))
    cs = sp.series(closed, x, 0, N+1).removeO()
    assert sp.expand(cs - Aser) == 0, l
    print(f" l={l}: 미분방정식·닫힌 꼴 모두 {N}차까지 일치")
print(" l=0: 1/(1-x) 계수 n! =", [factorial(n) for n in range(6)], "A_{n,0} =", [A[n][0] for n in range(6)])
s1 = sp.series(1/(2-sp.exp(x)), x, 0, 8).removeO()
print(" l=1: 1/(2-e^x) 계수*n! =", [sp.Poly(s1, x).coeff_monomial(x**n)*factorial(n) for n in range(8)], "A_{n,1} =", [A[n][1] for n in range(8)])

print("== 정리 2.10/2.11: 뿌리 숲 전수 (n<=6)")


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


def subtree_sizes_and_I(par, n):
    ch = {v: [] for v in range(0, n+1)}
    for v in range(1, n+1):
        ch[par[v-1]].append(v)
    t = {}; I = {}

    def rec(v):
        desc = []
        for c in ch[v]:
            desc += rec(c)
        t[v] = len(desc)+1; I[v] = sum(1 for d in desc if d < v)
        return desc + [v]
    for r in ch[0]:
        rec(r)
    return t, I


for n in range(1, 7):
    cnt = 0; byM = [0]*(n+1); sumprod = [Fr(0)]*(n+1)
    for par in forests(n):
        cnt += 1
        t, I = subtree_sizes_and_I(par, n)
        M = max(I.values()); byM[M] += 1
        for l in range(n):
            pr = Fr(1)
            for v in t:
                pr *= min(1, Fr(l+1, t[v]))
            sumprod[l] += pr
    assert cnt == (n+1)**(n-1)
    cum = [sum(byM[:l+1]) for l in range(n)]
    assert cum == [A[n][l] for l in range(n)], (n, cum)
    assert all(sumprod[l] == A[n][l] for l in range(n))
    print(f" n={n}: 숲 {cnt}개, M(F)<=l 개수 = A_(n,l) OK, 정리 2.11 둘째 식 OK")
for t in range(1, 7):
    for l in range(t):
        c = 0
        for par in forests(t):
            if par.count(0) == 1:
                tt, I = subtree_sizes_and_I(par, t)
                if max(I.values()) <= l:
                    c += 1
        assert c == min(t, l+1)*A[t-1][l]
print(" N_l(t)=min(t,l+1)A_{t-1,l} (t<=6) OK")

print("== 2.4절: 일곱 꼭짓점 나무 (크기 1,2,3,4,1,6,7) 라벨 배정의 M 개수열")
parent = {0: None, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 1}
nodes = list(range(7))
desc = {v: [] for v in nodes}
for v in nodes:
    u = parent[v]
    while u is not None:
        desc[u].append(v); u = parent[u]
sizes = [len(desc[v])+1 for v in nodes]
cnt = [0]*7
for lab in permutations(range(1, 8)):
    M = max(sum(1 for d in desc[v] if lab[d] < lab[v]) for v in nodes)
    cnt[M] += 1
print(" 부분나무 크기(정렬) =", sorted(sizes), " 개수열 =", cnt, " 5*행 =", [5*b for b in [1, 31, 130, 222, 216, 264, 144]], " 7!/1008 =", factorial(7)//1008)
assert cnt == [5*b for b in [1, 31, 130, 222, 216, 264, 144]]

print("== 정의 2.21/나무 함수/Borel–Tanner/[x^m]e^{vT}")
from math import lgamma
Bor = lambda m: exp(-m + (m-1)*log(m) - lgamma(m+1))
print(" sum_{m<=400} Bor(m) =", sum(Bor(m) for m in range(1, 401)), " (꼬리 ~ m^{-3/2}; T(1/e)=1)")
N = 12
T = sum(sp.Rational(t**(t-1), factorial(t))*x**t for t in range(1, N+1))
assert sp.expand(sp.series(T - x*sp.exp(T), x, 0, N+1).removeO()) == 0
for j in (1, 2, 3):
    ser = sp.series(T**j, x, 0, N+1).removeO()
    for m in range(j, N+1):
        c = sp.Poly(ser, x).coeff_monomial(x**m)
        assert c == sp.Rational(j, m)*sp.Rational(m**(m-j), factorial(m-j)), (j, m)
for j in (2, 3):
    base = [Fr(0)]+[Fr(m**(m-1), factorial(m)) for m in range(1, N+1)]
    cur = base[:]
    for _ in range(j-1):
        new = [Fr(0)]*(N+1)
        for a in range(1, N+1):
            for b in range(1, N+1-a):
                new[a+b] += cur[a]*base[b]
        cur = new
    for m in range(j, N+1):
        assert cur[m] == Fr(j, m)*Fr(m**(m-j), factorial(m-j))
print(" Bor^{*j}(m) = (j/m) e^{-m} m^{m-j}/(m-j)!  (j<=3, m<=12) OK (급수·합성곱)")
v = sp.symbols('v')
ser = sp.expand(sp.series(sp.exp(v*T), x, 0, N+1).removeO())
for m in range(1, N+1):
    c = sp.Poly(ser, x).coeff_monomial(x**m)
    assert sp.expand(c - v*(v+m)**(m-1)/sp.factorial(m)) == 0, m
print(" [x^m]e^{vT} = v(v+m)^{m-1}/m! (m<=12) OK;  v=1: p_m/m!")
for n in (6, 11):
    for m in range(n//2+1, n+1):
        a = Fr(comb(n, m)*m**(m-1)*p(n-m), p(n))
        b = Fr(m**(m-1), factorial(m))*Fr((n+1-m)**(n-m), factorial(n+1-m))/Fr((n+1)**n, factorial(n+1))
        assert a == b
print(" pi_n(m) = Bor(m)Bor(n+1-m)/Bor(n+1) (e 상쇄) OK")

print("== 정리 2.13: 최대 나무 사슬 공식 (n<=2l+3)")
for l in range(0, 6):
    for n in range(1, 2*l+4):
        y = l+1
        Ty = sum(sp.Rational(t**(t-1), factorial(t))*x**t for t in range(1, y+1))
        P0 = sp.Poly(sp.series(sp.exp(Ty), x, 0, n+1).removeO(), x).coeff_monomial(x**n)*factorial(n)
        rhs = P0 + sum(comb(n, m)*(l+1)*A[m-1][l]*p(n-m) for m in range(l+2, n+1))
        assert rhs == A[n][l], (l, n, rhs, A[n][l])
print(" l<=5, n<=2l+3 OK")

print("== 보조정리 2.14: 부호식과 v_k 성질")
vk = lambda k, Z, H: (1+1/k)**Z + (1-1/k)**(Z+H) - 2
for n in range(2, 7):
    for s in permutations(range(1, n+1)):
        h = caps(s)
        Acum = [prod(min(hi, l+1) for hi in h) for l in range(n)]
        b = [Acum[0]]+[Acum[l]-Acum[l-1] for l in range(1, n)]
        for k in range(1, n):
            Z = sum(1 for hi in h if hi > k); H = sum(1 for hi in h if hi == k)
            lhs = Fr(b[k]-b[k-1]); rhs = Acum[k-1]*((1+Fr(1, k))**Z + (1-Fr(1, k))**(Z+H) - 2)
            assert lhs == rhs, (s, k)
print(" 부호식 (n<=6, 1<=k<=n-1) OK")
for k in range(1, 40):
    for Z in range(0, 12):
        v0 = vk(k, Z, 0)
        ser = 2*sum(comb(Z, 2*i)*k**(-2*i) for i in range(1, Z//2+1))
        assert abs(v0-ser) < 1e-12
        assert v0 <= (Z/k)**2*cosh(Z/k)+1e-12
        for H in range(1, 6):
            assert vk(k, Z, H) <= (Z/k)**2*cosh(Z/k) - (1-Z/k)/k + 1e-12
            if k >= 4*Z*Z:
                assert vk(k, Z, H) < 0
print(" v_k(Z,0) 급수·상계, H>=1 상계, k>=4Z^2 => v<0  OK;  cosh(1/4)/4 =", cosh(0.25)/4)
print(" v_k(2,1) = -1/k+4/k^2-1/k^3:", all(abs(vk(k, 2, 1)-(-1/k+4/k**2-1/k**3)) < 1e-12 for k in range(1, 30)), " 부호 k=3,4:", vk(3, 2, 1), vk(4, 2, 1), " 2+sqrt3 =", 2+sqrt(3))

print("== 보조정리 2.18/2.20: 사슬 구성 수 vs 숲 전수 (n<=6), 닫힌 꼴")


def chain_config(par, n):
    t, I = subtree_sizes_and_I(par, n)
    ch = {v: [] for v in range(0, n+1)}
    for v in range(1, n+1):
        ch[par[v-1]].append(v)
    roots = ch[0]; big = max(roots, key=lambda v: t[v]); S = [t[big]]
    v = big
    while ch[v]:
        c = max(ch[v], key=lambda u: t[u])
        S.append(t[c]); v = c
    return S


for n in range(3, 7):
    for bb in range(1, 4):
        cnt = {}
        for par in forests(n):
            S = chain_config(par, n)
            if len(S) >= bb and S[bb-1] > n/2:
                u = n - S[0]; o = tuple(S[j]-1-S[j+1] for j in range(bb-1)); c = S[bb-1]
                cnt[(u, o, c)] = cnt.get((u, o, c), 0)+1
        for (u, o, c), m in cnt.items():
            f = Fr(factorial(n), factorial(u)*factorial(c))
            for oj in o:
                f /= factorial(oj)
            f *= (u+1)**(u-1) if u else 1
            for oj in o:
                f *= (oj+1)**(oj-1) if oj else 1
            f *= c**(c-1)
            assert f == m, (n, bb, u, o, c, f, m)
        for c in range(n//2+1, n+1):
            tot = sum(m for (u, o, cc), m in cnt.items() if cc == c)
            kap = n-c-bb+1
            if kap < 0:
                assert tot == 0; continue
            closed = Fr(factorial(n), factorial(c))*c**(c-1)*Fr(bb*(n-c+1)**(n-c-bb) if kap > 0 else 1, factorial(kap))
            assert closed == tot, (n, bb, c, closed, tot)
            tot0 = sum(m for (u, o, cc), m in cnt.items() if cc == c and all(v == 0 for v in o[1:]))
            closed0 = Fr(factorial(n), factorial(c))*c**(c-1)*Fr(2*(n-c-bb+3)**(n-c-bb) if kap > 0 else 1, factorial(kap))
            if bb >= 2:  # e^{2T} 꼴은 u+o_1 합이므로 b>=2에서만 뜻이 있다(본문은 b>=3)
                assert closed0 == tot0, (n, bb, c, closed0, tot0)
print(" 보조정리 2.18 구성 수, 명제 2.20 두 닫힌 꼴 (n<=6, b<=3) OK (kappa=0 항은 1)")
print("== 따름정리 2.19 극한 인자 보기 (n=2000, c=n-5)")
n = 2000; c = n-5
print(" n!/(c! n^{n-c}) =", exp(sum(log(1-i/n) for i in range(n-c))), " c^{c-1}/(n^{c-1}e^{-(n-c)}) =", exp((c-1)*log(c/n)+(n-c)), " (n+1)^{n-1}/(e n^{n-1}) =", exp((n-1)*log((n+1)/n)-1))
