# -*- coding: utf-8 -*-
# 검토전체24 R7b: 7.7절 끝 문단의 서술(n<3k에서 가벼운 뿌리의 첫 층 자식이 내는 몫)을 정확 유리수로 검산.
from fractions import Fraction as F
from math import comb
def p(m): return 1 if m == 0 else (m+1)**(m-1)
def tabA(l, N):
    if l < 0: return [1]+[0]*N
    a = [1]
    for mm in range(1, N+1):
        a.append(sum(comb(mm-1, j-1)*min(j, l+1)*a[j-1]*a[mm-j] for j in range(1, mm+1)))
    return a
for k in range(2, 9):
    N = 3*k
    T = {l: tabA(l, N) for l in (k-2, k-1, k)}
    A = lambda m, l: T[l][m]
    b = lambda m, y: A(m, y)-A(m, y-1)
    d = lambda m: b(m, k)-b(m, k-1)
    clp = lambda m: F(b(m, k), A(m, k-1)); clm = lambda m: F(b(m, k-1), A(m, k-1))
    mu = lambda m: F(d(m), A(m, k-1))
    ok = True
    for n in range(2*k+1, 3*k+1):
        Pk = lambda j: F(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), A(n, k-1))
        def chi(j):
            v = F(0)
            if j == k: v -= F(1, k)*(1-clm(n-k))
            if j > k: v += F(1, k)*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j))
            i = 1 if j > k else 0
            return v+(1+F(i, k))*clp(j-1)*clp(n-j)+(1-F(i, k))*clm(j-1)*clm(n-j)
        star = sum(Pk(j)*(chi(j)+(mu(j-1) if k <= j-1 <= 2*k else 0)+(mu(n-j) if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
        w = lambda m: F(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
        pp = lambda m: F((k+1)*b(m, k)-(k-1)*b(m, k-1), p(m))
        s = lambda m, y: F(A(m, y-1), p(m))
        Left = sum(w(m)*pp(m) for m in range(k, 2*k+1))
        RightHeavy = sum(w(m)*pp(m) for m in range(k, n-k))
        thr = w(n-k)*pp(n-k) - w(n-k)*s(n-k, k+1)
        light = sum((n-m)*w(m)*F(d(m), p(m)) for m in range(n-k+1, 2*k+1))
        Quad = sum(Pk(j)*((1+F(1, k))*clp(j-1)*clp(n-j)+(1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
        Stem = F(1, k)*sum(Pk(j)*(((clp(j-1)+clm(j-1)) if j-1 > 2*k else 0)+((clp(n-j)+clm(n-j)) if n-j > 2*k else 0)) for j in range(k+1, n+1))
        if star != Left+RightHeavy+thr+light+Quad+Stem:
            ok = False; print("FAIL k=%d n=%d" % (k, n))
        # 가벼운 뿌리 하나의 몫
        for m in range(n-k+1, 2*k+1):
            j = n-m
            if Pk(j)*mu(m) != (n-m)*w(m)*F(d(m), p(m)): ok = False; print("light FAIL", k, n, m)
    print("k=%d: 둘째 층 분해(왼쪽+무거운 뿌리 오른쪽+문턱+가벼운 뿌리+Quad+Stem) %s; d_{m,k} 부호(m=k..2k): %s"
          % (k, "ok" if ok else "FAILED", "".join("+" if d(m) > 0 else ("0" if d(m) == 0 else "-") for m in range(k, 2*k+1))))
