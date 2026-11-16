# 명제 old-2-20의 유한 n 상계값(0.740, 0.317, 0.0658, 0.0115)을 본문 닫힌 꼴로 독립 재계산 (mpmath 50자리)
# 그리고 정리 old-2-5 마지막 문장(n<=6의 모든 섬유 행이 단봉)을 전수 확인
from mpmath import mp, mpf, factorial, binomial, log, exp
from itertools import permutations
mp.dps = 50
def v(k, Z, H):
    return (1+mpf(1)/k)**Z + (1-mpf(1)/k)**(Z+H) - 2
def bound(n, b):
    # 조건: 3<=i<=b, n/2<k<=n 에서 v_k(i-1,1)<0
    for i in range(3, b+1):
        for k in range(n//2+1, n+1):
            if not v(k, i-1, 1) < 0: return None
    s1 = mpf(0); s2 = mpf(0)
    for c in range(n//2+1, n+1):
        kap = n - c - b + 1
        if kap < 0: continue
        common = factorial(n)/factorial(c) * mpf(c)**(c-1) / (factorial(kap) * mpf(n+1)**(n-1))
        s1 += common * b * mpf(n-c+1)**(n-c-b)
        s2 += common * 2 * mpf(n-c-b+3)**(n-c-b)
    return 1 - s1 + s2
for n in [17, 100, 1000, 10**4]:
    best = None
    for b in range(3, 40):
        val = bound(n, b)
        if val is None: continue
        if best is None or val < best[0]: best = (val, b)
    print(n, 'min bound', mp.nstr(best[0], 6), 'at b =', best[1])
# n<=6 섬유 전수
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        z = 0
        for j in range(i):
            if sig[j] > sig[i]: z = j+1
        h.append(i+1-z)
    return h
def unimodal(seq):
    i = 0
    while i+1 < len(seq) and seq[i] <= seq[i+1]: i += 1
    while i+1 < len(seq) and seq[i] >= seq[i+1]: i += 1
    return i == len(seq)-1
for n in range(1, 8):
    bad = 0
    for sig in permutations(range(1, n+1)):
        h = caps(sig)
        A = [1]
        for l in range(n):
            p = 1
            for hi in h: p *= min(hi, l+1)
            A.append(p)
        row = [A[i+1]-A[i] for i in range(n)]
        if not unimodal(row): bad += 1
    print('n =', n, 'non-unimodal fibers:', bad)
