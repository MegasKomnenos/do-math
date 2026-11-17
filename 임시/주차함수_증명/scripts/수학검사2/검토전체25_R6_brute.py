# -*- coding: utf-8 -*-
# 장7A의 진술을 작은 크기에서 전수 열거로 다시 센다(검토 25차 R6).
import itertools, random, sys, io
from fractions import Fraction as Fr
from math import comb, factorial
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

def park(a):
    n = len(a); occ = [0]*(n+2); pos = []
    for c, p in enumerate(a):
        q = p
        while q <= n and occ[q]: q += 1
        if q > n: return None
        occ[q] = c+1; pos.append(q)
    sigma = [occ[i] for i in range(1, n+1)]
    disp = [pos[c]-a[c] for c in range(n)]
    return sigma, disp, pos

def caps(sigma):
    n = len(sigma); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and sigma[j] < sigma[i]: j -= 1
        h.append(i-j)
    return h

PF = {}
for n in range(1, 8):
    L = []
    for a in itertools.product(range(1, n+1), repeat=n):
        r = park(a)
        if r: L.append((a, r[0], r[1], r[2]))
    PF[n] = L
    assert len(L) == (n+1)**(n-1)

def A(n, l):  # M<=l
    if n == 0: return 1
    if l < 0: return 0
    return sum(1 for (a, s, d, p) in PF[n] if max(d) <= l)

# (1) 정리 7:old-6-2, 보조정리 7:old-6-3, 명제 7:old-6-7(결합 부등식)
import math
for n in range(1, 8):
    for k in range(2, n+2):
        Ak, Ak1, Ak2 = A(n, k), A(n, k-1), A(n, k-2)
        Rs, Rf = Fr(Ak, Ak1), Fr(Ak2, Ak1)
        xf = 1-1/k; o = -2*math.log(1-1/k)/math.log(1+1/k)
        assert float(Rf) > xf*float(Rs)**(-o) - 1e-15, (n, k)
        # 모멘트 표현
        tot = Fr(0); T = Fr(0)
        for sig in itertools.permutations(range(1, n+1)):
            h = caps(sig); w = 1
            for x in h: w *= min(x, k)
            Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            tot += w*((1+Fr(1, k))**Z + (1-Fr(1, k))**(Z+H) - 2)
            T += w*(Z*(Z-1) - k*H)
        d = Ak - 2*Ak1 + Ak2
        assert tot == d, (n, k)
        assert d*k*k >= T, (n, k)
print('(1) 모멘트 표현·모멘트 판정·결합 부등식: n<=7 통과')

# (2) 정리 7:old-6-6: 무작위 대칭 가중치와 첫째 사실
random.seed(1)
for n in range(1, 7):
    for trial in range(40):
        wt = {}
        tot = Fr(0); num = {y: Fr(0) for y in range(n+1)}; posn = {y: Fr(0) for y in range(n+1)}
        for (a, s, d, p) in PF[n]:
            key = tuple(sorted(d))
            if key not in wt:
                if trial == 0: wt[key] = 1
                elif trial < 8: wt[key] = 1 if max(d) <= trial-1 else 0
                else: wt[key] = random.choice([0, 0, 1, 2, 5, 17])
            w = wt[key]
            if not w: continue
            h = caps(s); tot += w
            for y in range(n+1):
                num[y] += w*sum(1 for x in h if x > y)
                if p[n-1] <= y: posn[y] += w
        if tot == 0: continue
        for y in range(n+1):
            assert num[y]/tot >= Fr(n-y, y+1), (n, y, trial)
            assert posn[y]/tot <= Fr(y, n), (n, y, trial)
print('(2) 평균 하계와 Pr(pos_n<=y)<=y/n: n<=6, 가중치 40종 통과')

# (3) 소인 주차함수: C_{n,n}=(n-1)^{n-1}, A=1/(1-C), C'=k-Q'(1-C), C_{n,2}=1
def prime(a):
    n = len(a)
    return all(sum(1 for x in a if x <= b) != b for b in range(1, n))
C = {}
for n in range(1, 8):
    for k in range(1, 9):
        C[(n, k)] = sum(1 for (a, s, d, p) in PF[n] if prime(a) and max(d) <= k-1)
    assert C[(n, n)] == (n-1)**(n-1) if n > 1 else C[(1, 1)] == 1
    assert C[(n, 2)] == 1
for k in range(1, 8):
    for n in range(1, 8):
        # 조합 공식
        def comps(m):
            if m == 0: yield (); return
            for g in range(1, m+1):
                for rest in comps(m-g): yield (g,)+rest
        s = 0
        for cp in comps(n):
            t = factorial(n)
            for g in cp: t //= factorial(g)
            for g in cp: t *= C[(g, k)]
            s += t
        assert s == A(n, k-1), (n, k)
    # C' = k - Q'(1-C) 계수 비교: C_{n+1,k}/n! = [n=0]k - sum_j q_j [x^{n-j}](1-C)
    p = lambda m: (m+1)**(m-1) if m > 0 else 1
    qd = [Fr((k-1-j)*p(j), factorial(j)) for j in range(0, k-1)]  # Q'_{k-1} 계수
    oneC = [Fr(1)] + [-Fr(C[(n, k)], factorial(n)) for n in range(1, 8)]
    for n in range(0, 7):
        lhs = Fr(C[(n+1, k)], factorial(n))
        rhs = (k if n == 0 else 0) - sum(qd[j]*oneC[n-j] for j in range(len(qd)) if n-j >= 0)
        assert lhs == rhs, (n, k)
print('(3) 소인 분해: C_{n,n}, C_{n,2}=1, A=1/(1-C), C\'=k-Q\'(1-C): n<=7 통과')

# (4) 초승법성
for k in range(1, 6):
    for m in range(0, 8):
        for m2 in range(0, 8-m):
            if m+m2 == 0: continue
            assert A(m+m2, k-1) >= comb(m+m2, m)*A(m, k-1)*A(m2, k-1)
print('(4) 초승법성 통과')

# (5) 유한 크기 공식 (가): E[H_k] = (n+1) a_{k-1} sum_j K_j a_{n+1-j}/a_n
for k in range(2, 6):
    a = [Fr(A(m, k-1), factorial(m)) for m in range(0, 8)]
    ao = [Fr(p(m), factorial(m)) for m in range(0, 8)]
    K = [Fr(0)]*9
    for j in range(1, 9):
        s = sum((k-m)*ao[m-1]*K[j-m] for m in range(1, k) if j-m >= 0)
        if j == k+1: s += 1
        K[j] = s/j
    assert all(K[j] == 0 for j in range(0, k+1)) and K[k+1] == Fr(1, k+1)
    for n in range(1, 8):
        EH = Fr(0)
        for sig in itertools.permutations(range(1, n+1)):
            h = caps(sig); w = 1
            for x in h: w *= min(x, k)
            EH += w*sum(1 for x in h if x == k)
        EH /= A(n, k-1)
        rhs = (n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1, n+2))/a[n]
        assert EH == rhs, (n, k, EH, rhs)
print('(5) 유한 크기 공식 (가): k=2..5, n<=7 통과')

# (6) k=1: b_{n,1} >= (n-1) n!/2
for n in range(2, 8):
    b1 = A(n, 1)-A(n, 0)
    print('   n=%d b_{n,1}=%d  (n-1)n!/2=%d  n!=%d' % (n, b1, (n-1)*factorial(n)//2, factorial(n)))
    assert b1 >= (n-1)*factorial(n)//2
