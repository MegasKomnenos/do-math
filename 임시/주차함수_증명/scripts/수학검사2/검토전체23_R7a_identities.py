# R7a: 7.4·7.5절의 항등식을 작은 크기에서 정확 유리수로 검사
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial
import sympy as sp

def caps(perm):
    # 자리 i(1..n)의 용량 h_i = i - (왼쪽으로 가장 가까운 더 큰 값의 자리; 없으면 0)
    n = len(perm); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and perm[j] < perm[i]: j -= 1
        h.append(i - j)
    return h

def A_table(N, ell):
    # 정리 2:old-2-6
    A = [1]
    for n in range(1, N+1):
        A.append(sum(comb(n-1, j)*min(j+1, ell+1)*A[j]*A[n-1-j] for j in range(n)) if ell >= 0 else 0)
    return A

ok = True
# (a) 결과 순열 합과 재귀의 일치, 모멘트 재귀 (7.2)
for k in (2, 3):
    N = 8
    A = A_table(N, k-1)
    EZ = [Fr(0)]; EH = [Fr(0)]; EZZ = [Fr(0)]
    for n in range(1, N+1):
        tot = 0; sz = 0; sh = 0; szz = 0
        for p in permutations(range(1, n+1)):
            h = caps(p); w = 1
            for x in h: w *= min(x, k)
            Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            tot += w; sz += w*Z; sh += w*H; szz += w*Z*(Z-1)
        assert tot == A[n], (k, n)
        EZ.append(Fr(sz, tot)); EH.append(Fr(sh, tot)); EZZ.append(Fr(szz, tot))
    for n in range(1, N+1):
        P = [None] + [Fr(min(j, k)*comb(n-1, j-1)*A[j-1]*A[n-j], A[n]) for j in range(1, n+1)]
        assert sum(P[1:]) == 1
        r1 = sum(P[j]*((1 if j > k else 0) + EZ[j-1] + EZ[n-j]) for j in range(1, n+1))
        r2 = sum(P[j]*((1 if j == k else 0) + EH[j-1] + EH[n-j]) for j in range(1, n+1))
        r3 = sum(P[j]*(EZZ[j-1] + EZZ[n-j] + 2*EZ[j-1]*EZ[n-j] + 2*(1 if j > k else 0)*(EZ[j-1] + EZ[n-j])) for j in range(1, n+1))
        if not (r1 == EZ[n] and r2 == EH[n] and r3 == EZZ[n]): ok = False; print("FAIL (7.2)", k, n)
print("(7.1)·(7.2) brute force k=2,3, n<=8:", ok)

# (b) 한 걸음 항등식 (7.10)
ok = True
for k in range(2, 9):
    N = 5*k+6
    Am2 = A_table(N, k-2); Am1 = A_table(N, k-1); A0 = A_table(N, k)
    clp = [Fr(A0[m]-Am1[m], Am1[m]) for m in range(N+1)]
    clm = [Fr(Am1[m]-Am2[m], Am1[m]) for m in range(N+1)]
    mu = [clp[m]-clm[m] for m in range(N+1)]
    for m in range(0, k):
        assert clp[m] == 0 and clm[m] == 0
    assert clp[k] == 0 and mu[k] == -Fr((k)**(k-2), (k+1)**(k-1))
    for m in range(1, N+1):
        src = Fr(0); rest = Fr(0)
        for j in range(1, m+1):
            P = Fr(min(j, k)*comb(m-1, j-1)*Am1[j-1]*Am1[m-j], Am1[m])
            hv = 1 if j > k else 0
            chi = Fr(1, k)*(-(1 if j == k else 0)*(1-(clm[m-k] if m >= k else 0)) + hv*(clp[j-1]+clm[j-1]+clp[m-j]+clm[m-j])) \
                  + (1+Fr(hv, k))*clp[j-1]*clp[m-j] + (1-Fr(hv, k))*clm[j-1]*clm[m-j]
            src += P*chi; rest += P*(mu[j-1]+mu[m-j])
        if mu[m] != src+rest: ok = False; print("FAIL (7.10)", k, m)
        if m <= k-1 and (src != 0 or mu[m] != 0): ok = False; print("FAIL start", k, m)
print("(7.10) exact, 2<=k<=8, m<=5k+6:", ok)

# (c) (7.3)·(7.4)·Neumann 전개·(7.6)
z, x = sp.symbols('z x')
def ser_mul(a, b, N):
    c = [0]*(N+1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j, bj in enumerate(b):
            if i+j > N: break
            c[i+j] += ai*bj
    return [sp.expand(t) for t in c]
def ser_int(a, N):
    return [0] + [a[i]/sp.Integer(i+1) for i in range(N)]
def ser_exp(a, N):
    # a[0]=0
    e = [sp.Integer(1)] + [0]*N
    for n in range(1, N+1):
        e[n] = sp.expand(sum(sp.Integer(i)*a[i]*e[n-i] for i in range(1, n+1))/n)
    return e
ok = True
for k in (2, 3):
    N = 3*k+2
    # K_{n,k}(z): 가중 분배함수 재귀, wg_t = t (t<=k), z (t>k)
    K = [sp.Integer(1)]
    for n in range(1, N+1):
        K.append(sp.expand(sum(comb(n-1, j)*(sp.Integer(j+1) if j+1 <= k else z)*K[j]*K[n-1-j] for j in range(n))))
    # 순열 전수 대조 (n<=7)
    for n in range(1, min(N, 7)+1):
        s = 0
        for p in permutations(range(1, n+1)):
            h = caps(p); w = sp.Integer(1)
            for hh in h: w *= (hh if hh <= k else z)
            s += w
        assert sp.expand(s-K[n]) == 0
    p_ = lambda m: sp.Integer(m+1)**(m-1) if m >= 1 else sp.Integer(1)
    Kx = [K[n]/sp.factorial(n) for n in range(N+1)]           # K_k(z;x) 보통 계수
    eT = [p_(n)/sp.factorial(n) for n in range(N+1)]
    Tle = [0]+[sp.Integer(t)**(t-1)/sp.factorial(t) if t <= k else 0 for t in range(1, N+1)]
    Tgt = [0]+[sp.Integer(t)**(t-1)/sp.factorial(t) if t > k else 0 for t in range(1, N+1)]
    Elt = [eT[n] if n < k else 0 for n in range(N+1)]
    # (7.3)
    inner = [Tle[n] + z*ser_int([Kx[i]-Elt[i] for i in range(N+1)], N)[n] for n in range(N+1)]
    E73 = ser_exp(inner, N)
    assert all(sp.expand(E73[n]-Kx[n]) == 0 for n in range(N+1)), "7.3"
    # pd
    pd = [0]*(N+1)
    for t in range(k+1, N+1):
        pd[t] = sp.expand(z*K[t-1]-sp.Integer(t)**(t-1))/sp.factorial(t)
    # 연쇄 해: G = e^T (1 - T^{>k} + z∫(G - E_{<k})) 를 계수별로 푼다
    G = [0]*(N+1)
    for n in range(N+1):
        # G_n = sum_{i} eT[i]*B[n-i], B = 1 - Tgt + z*int(G-E); B[m]은 G[<m]만 쓴다
        B = [0]*(n+1)
        for m in range(n+1):
            B[m] = (1 if m == 0 else 0) - Tgt[m] + (z*(G[m-1]-Elt[m-1])/m if m >= 1 else 0)
        G[n] = sp.expand(sum(eT[i]*B[n-i] for i in range(n+1)))
    X = [sp.expand(Kx[n]-G[n]) for n in range(N+1)]
    assert all(X[n] == 0 for n in range(2*k+2)), "X starts at 2k+2"
    assert X[2*k+2] != 0
    # (7.4)
    eTle = ser_exp(Tle, N)
    rhs = ser_mul(eTle, [z*ser_int(X, N)[n] + ser_mul(pd, pd, N)[n]/2 for n in range(N+1)], N)
    assert all(sp.expand(X[n]-rhs[n]) == 0 for n in range(N+1)), "7.4"
    # Neumann 전개와 X''(k)
    def Neu(f): return ser_mul(eTle, ser_int(f, N), N)
    term = ser_mul(eTle, [t/2 for t in ser_mul(pd, pd, N)], N)
    tot = [0]*(N+1); cur = term
    for j in range(0, N+1):
        tot = [sp.expand(tot[n] + z**j*cur[n]) for n in range(N+1)]
        cur = Neu(cur)
    assert all(sp.expand(X[n]-tot[n]) == 0 for n in range(N+1)), "Neumann"
    # X''(k) via Q_j
    d = lambda f, r: [sp.diff(t, z, r) for t in f]
    at = lambda f: [sp.nsimplify(sp.sympify(t).subs(z, k)) for t in f]
    pd0, pd1, pd2 = at(pd), at(d(pd, 1)), at(d(pd, 2))
    X2 = at(d(X, 2))
    tot2 = [0]*(N+1)
    for j in range(0, N+1):
        Qj = [sp.Rational(j*(j-1), 2*k*k)*a + sp.Rational(2*j, k)*b + c + e for a, b, c, e in
              zip(ser_mul(pd0, pd0, N), ser_mul(pd0, pd1, N), ser_mul(pd1, pd1, N), ser_mul(pd0, pd2, N))]
        cur = ser_mul(at(eTle), Qj, N)
        for _ in range(j): cur = [sp.nsimplify(t) for t in Neu(cur)]
        tot2 = [tot2[n] + k**j*cur[n] for n in range(N+1)]
    assert all(sp.simplify(X2[n]-tot2[n]) == 0 for n in range(N+1)), "X''"
    # (7.6)의 값: pd_t(k), pd'_t(k), pd''_t(k)
    A = A_table(N, k-1)
    for t in range(k+1, min(N, 8)+1):
        m = t-1; sz = 0; szz = 0; tot_ = 0
        for p in permutations(range(1, m+1)):
            h = caps(p); w = 1
            for hh in h: w *= min(hh, k)
            Z = sum(1 for hh in h if hh > k); tot_ += w; sz += w*Z; szz += w*Z*(Z-1)
        EZ = sp.Rational(sz, tot_); EZZ = sp.Rational(szz, tot_)
        ex = sp.Rational(t*(t**(t-2)), A[m]) - k
        f = sp.factorial(t)
        assert pd0[t]*f == -A[m]*ex and pd1[t]*f == A[m]*(1+EZ) and pd2[t]*f == sp.Rational(A[m], k)*(2*EZ+EZZ), ("7.6 values", k, t)
        q = t-k
        assert 0 <= EZ <= q-1 and 0 <= EZZ <= (q-1)*(q-2) and ex >= q
    print("k =", k, ": (7.3), 잔차 시작 차수, (7.4), Neumann, X''(k), (7.6) 값 일치; X''_n(k), n=2k+2..3k+2:",
          [sp.nsimplify(X2[n]*sp.factorial(n)) for n in range(2*k+2, N+1)])
