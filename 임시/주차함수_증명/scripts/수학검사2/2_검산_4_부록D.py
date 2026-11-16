# -*- coding: utf-8 -*-
"""수학 검사 2 (태그 2) 검산 4: 부록 D 두 항목. 섬유 전수(n<=7)의 결과 수치와, 단봉 섬유 비율 상계의 식·허용 조건·네 값·여유를 독립 구현으로 다시 계산한다."""
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial
from mpmath import mp, mpf, nstr

mp.dps = 30


def caps(sig):
    n = len(sig); h = []
    for i in range(1, n+1):
        z = 0
        for j in range(1, i):
            if sig[j-1] > sig[i-1]:
                z = j
        h.append(i - z)
    return h


def unimodal(b):
    i = 0
    while i+1 < len(b) and b[i] <= b[i+1]:
        i += 1
    while i+1 < len(b) and b[i] >= b[i+1]:
        i += 1
    return i == len(b)-1


print("== D.fiber-enumeration: 용량 다중집합 수, 비단봉 섬유 수 (n<=7)")
for n in range(1, 8):
    seen = set(); bad = []
    for s in permutations(range(1, n+1)):
        h = caps(s); key = tuple(sorted(h))
        seen.add(key)
        A = [1]
        for l in range(n):
            v = 1
            for hi in h:
                v *= min(hi, l+1)
            A.append(v)
        A = A[1:]; b = [A[0]]+[A[l]-A[l-1] for l in range(1, n)]
        if not unimodal(b):
            bad.append((s, tuple(h), tuple(b)))
    print(f" n={n}: 다중집합 {len(seen)}개, 비단봉 섬유 {len(bad)}개", (" 첫째: "+str(bad[0])) if bad else "")

print("== D.fiber-nonunimodal-bound: 허용 조건이 처음 깨지는 b, 상계값, 여유")
v_int = lambda k, i: (k+1)**(i-1)*k + (k-1)**i - 2*k**i   # k^i v_k(i-1,1)


def first_bad_b(n):
    b = 3
    while True:
        if any(v_int(k, i) >= 0 for i in range(3, b+1) for k in range(n//2+1, n+1)):
            return b
        b += 1


def bound_mp(n, b):
    NP = mpf(n+1)**(n-1)
    P = Q = mpf(0)
    lognfac = mp.loggamma(n+1)
    for c in range(n//2+1, n+1):
        L = n-c-b+1
        if L < 0:
            continue
        base = mp.e**(lognfac - mp.loggamma(c+1) + (c-1)*mp.log(c) - mp.loggamma(L+1) - (n-1)*mp.log(n+1))
        if L == 0:
            P += base; Q += base
        else:
            P += base*b*mpf(b+L)**(L-1)
            Q += base*2*mpf(2+L)**(L-1)
    return 1-P+Q


def bound_exact(n, b):
    P = Q = Fr(0)
    for c in range(n//2+1, n+1):
        L = n-c-b+1
        if L < 0:
            continue
        base = Fr(factorial(n), factorial(c))*c**(c-1)/Fr(factorial(L)*(n+1)**(n-1))
        if L == 0:
            P += base; Q += base
        else:
            P += base*b*Fr(b+L)**(L-1)
            Q += base*2*Fr(2+L)**(L-1)
    return 1-P+Q


claims = {17: mpf('0.740'), 100: mpf('0.317'), 1000: mpf('0.0658'), 10000: mpf('0.0115')}
reported = {17: (3, '0.7395086877'), 100: (4, '0.3168484270'), 1000: (6, '0.06573317522'), 10000: (8, '0.01142155148')}
for n in (17, 100, 1000, 10000):
    fb = first_bad_b(n)
    bs = list(range(3, fb))
    vals = {b: bound_mp(n, b) for b in bs} if n < 10000 else {reported[n][0]: bound_mp(n, reported[n][0])}
    bmin = min(vals, key=lambda b: vals[b])
    print(f" n={n}: 허용 조건 첫 실패 b={fb}; 최소 b={bmin}, 상계={nstr(vals[bmin], 12)}; 보고값 b={reported[n][0]} {reported[n][1]}; 진술값 {claims[n]}; 여유={nstr(claims[n]-vals[bmin], 6)}; 상계<=진술값: {vals[bmin] <= claims[n]}")
    if n == 17:
        ex = bound_exact(17, 3)
        print("   n=17 정확 유리수 b=3:", float(ex), " 분모 자릿수", len(str(ex.denominator)))
    if n == 10000:
        print("   (n=10^4는 보고된 최소 b=8만 평가; 이웃 b=7,9:", nstr(bound_mp(n, 7), 8), nstr(bound_mp(n, 9), 8), ")")
print(" 기록 exposition §2.3는 1000에서 0.0657, 10^4에서 0.0114(내림)로 적고, 이 글은 0.0658, 0.0115(올림)로 적는다: 상계이므로 올림이 바른 방향.")
