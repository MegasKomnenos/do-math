# 검토전체22 R1 검산 1: 1.3절 표, 1.4절 수치 주장, 2장 재귀·항등식(정확 정수/유리수)
from fractions import Fraction as Fr
from math import comb, factorial
import itertools

NMAX = 90
def p(n): return 1 if n == 0 else (n + 1) ** (n - 1)

# A[l][n] = A_{n,l}, 정리 2:old-2-6 의 마지막 차 재귀
def build_A(l, nmax):
    A = [1] + [0] * nmax
    for n in range(1, nmax + 1):
        s = 0
        for j in range(n):
            s += comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j]
        A[n] = s
    return A
Acol = {l: build_A(l, NMAX) for l in range(0, NMAX + 1)}
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    if l >= n - 1: return p(n)
    return Acol[l][n]
def b(n, l): return A(n, l) - A(n, l - 1)
def d(n, k): return b(n, k) - b(n, k - 1)
ok = True
def check(name, cond):
    global ok
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: ok = False

# 재귀 자체의 일관성: l>=n-1 에서 p_n
check("recursion gives p_n when l>=n-1", all(Acol[l][n] == p(n) for l in range(0, 30) for n in range(1, l + 2)))

# --- 1.3 표
table = {1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],
 6:[720,3963,4594,3688,2546,1296],7:[5040,42253,62145,57398,46142,32359,16807],
 8:[40320,505515,929856,979430,865970,702292,497442,262144],
 9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
 10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
psum = {1:1,2:3,3:16,4:125,5:1296,6:16807,7:262144,8:4782969,9:100000000,10:2357947691}
check("1.3 table rows n<=10", all([b(n,l) for l in range(n)] == table[n] for n in table))
check("1.3 table sums p_n", all(sum(table[n]) == psum[n] == p(n) for n in table))
def unimodal_witnesses(row):
    m = len(row) - 1; w = []
    for s in range(m + 1):
        if all(row[i] <= row[i+1] for i in range(s)) and all(row[i] >= row[i+1] for i in range(s, m)): w.append(s)
    return w
wit = {n: unimodal_witnesses([b(n,l) for l in range(n)]) for n in range(1, NMAX+1)}
check("all rows n<=90 unimodal", all(len(wit[n]) > 0 for n in wit))
print("   least witnesses n=1..10:", [wit[n][0] for n in range(1, 11)])
check("least witness values of 1.3", [wit[n][0] for n in range(1, 11)] == [0,0,1,1,1,2,2,3,3,4])
kn = lambda n: -(-n // 2)
check("3장 머리: n<=10 증인 < ceil(n/2)", all(max(wit[n]) < kn(n) for n in range(1, 11)))
# --- 1.4: 가운데 비교
check("d_{n,k_n}<0 for 2<=n<=15", all(d(n, kn(n)) < 0 for n in range(2, 16)))
check("d_{n,k_n}>0 for 16<=n<=90", all(d(n, kn(n)) > 0 for n in range(16, NMAX+1)))
def logconc(n): return all(b(n,l)**2 >= b(n,l-1)*b(n,l+1) for l in range(1, n-1))
check("log-concave for n<=79", all(logconc(n) for n in range(1, 80)))
check("log-concavity fails at n=80 (l=40)", (not logconc(80)) and b(80,40)**2 < b(80,39)*b(80,41) and b(80,39) < b(80,40) < b(80,41))
# --- 2.3 역수 생성함수 작은 수준
check("A_{n,0}=n!", all(A(n,0) == factorial(n) for n in range(0, 20)))
fub = [1]
for n in range(1, 15): fub.append(sum(comb(n, j) * fub[n - j] for j in range(1, n + 1)))
check("A_{n,1}=Fubini (1/(2-e^x))", all(A(n,1) == fub[n] for n in range(0, 15)))
check("b_{k,k-1}=p_{k-1}", all(b(k, k-1) == p(k-1) for k in range(1, 40)))
# --- 정리 2:old-2-13 (가)
def forests_small(nmax, y):
    f = [1] + [0]*nmax
    for n in range(1, nmax+1):
        f[n] = sum(comb(n-1, t-1) * t**(t-1) * f[n-t] for t in range(1, min(y, n)+1))
    return f
good = True
for l in range(0, 20):
    y = l + 1; f = forests_small(2*y+1, y)
    for n in range(1, 2*l+4):
        rhs = f[n] + sum(comb(n, m) * (l+1) * A(m-1, l) * p(n-m) for m in range(l+2, n+1))
        if rhs != A(n, l): good = False
check("Thm 2.13(가) largest-tree chain formula, l<20", good)
def s(m, y): return Fr(A(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(m, Y), p(m))
def pi(n, m): return Fr(comb(n, m) * m**(m-1) * p(n-m), p(n))
good = True
for y in range(1, 20):
    for n in range(1, 2*y+2):
        rhs = sum(pi(n, m) / m * (s(m-1, y+1) + y * c(m-1, y)) for m in range(y+1, n+1))
        if rhs != c(n, y): good = False
check("Cor one-tree-recursion", good)
check("(SM) s_{m+1}(y)<=s_m(y)", all(s(m+1, y) <= s(m, y) for m in range(0, 60) for y in range(1, 40)))
check("(DM0) s_m(y)<=s_{m+1}(y+1)", all(s(m, y) <= s(m+1, y+1) for m in range(0, 60) for y in range(1, 40)))
good = True
for m in range(0, 40):
    for y in range(1, 12):
        for y2 in range(y, 14):
            pr = Fr(1)
            for i in range(1, m+1): pr *= Fr(min(i, y), min(i, y2))
            if s(m, y) < pr * s(m, y2): good = False
check("Lemma capacity-shift-ratio", good)
def P(m, j): return Fr(j * comb(m-1, j-1) * p(j-1) * p(m-j), p(m))
check("P_m sums to 1", all(sum(P(m, j) for j in range(1, m+1)) == 1 for m in range(1, 40)))
check("Lemma 2.32(ㄱ) P_m(m-rho) nonincreasing in m", all(P(m+1, m+1-r) <= P(m, m-r) for r in range(0, 25) for m in range(r+1, 50)))
check("Lemma 2.32(ㄴ) (m+1)P_{m+1}(j)<=mP_m(j)", all((m+1)*P(m+1, j) <= m*P(m, j) for j in range(1, 30) for m in range(j, 50)))
# --- 순열 전수 n<=7
def capacities(sig):
    n = len(sig); h = []
    for i in range(n):
        z = 0
        for j in range(i-1, -1, -1):
            if sig[j] > sig[i]: z = j+1; break
        h.append(i+1 - z)
    return h
def pw(a, e): return 1 if e == 0 else a**e
good = goodB = goodXi = goodFib = True
for n in range(1, 8):
    hs = [capacities(sg) for sg in itertools.permutations(range(1, n+1))]
    for l in range(0, n):
        tot = 0
        for h in hs:
            pr = 1
            for x in h: pr *= min(x, l+1)
            tot += pr
        if tot != A(n, l): goodFib = False
    for k in range(1, n+1):
        E = 0; E2 = 0; B = 0; J = 0; Xi2 = 0
        for h in hs:
            Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            low = 1
            for x in h:
                if x < k: low *= x
            for i in range(2, Z+1, 2):
                E += low * pw(k, H) * comb(Z, i) * pw(k, Z-i)
            if Z >= 2: E2 += low * pw(k, H) * comb(Z, 2) * pw(k, Z-2)
            B += low * pw(k-1, Z) * (pw(k, H) - pw(k-1, H))
            if H >= 1: J += low * H * pw(k, H-1) * pw(k-1, Z)
            if H == 2: Xi2 += low * pw(k-1, Z)
        if d(n, k) != 2*E - B: good = False
        if not (2*E2 - B <= d(n, k)): good = False
        if B > J: goodB = False
        if n <= 2*k-1 and B != J: goodB = False
        if n == 2*k:
            if B != J - Xi2 or Xi2 != comb(2*k-1, k-1) * p(k-1)**2: goodXi = False
        if k == 1 and B != 1: goodB = False
        if k == n and B != b(n, n-1): goodB = False
check("Cor 2.4 A_{n,l}=sum_sigma prod min(h_i,l+1), n<=7", goodFib)
check("Thm 2.28 d=2E-B and Cor 2.29, n<=7", good)
check("B<=J(k-1), equality n<=2k-1, B_{n,0}=1, B_{n,n-1}=b_{n,n-1}", goodB)
check("B_{2k,k-1}=J-Xi, Xi=C(2k-1,k-1)p_{k-1}^2 (k<=3)", goodXi)
h = capacities((1,2,3,5,4,6,7))
Asig = []
for l in range(7):
    pr = 1
    for x in h: pr *= min(x, l+1)
    Asig.append(pr)
row = [Asig[0]] + [Asig[i]-Asig[i-1] for i in range(1, 7)]
check("Prop 2.5 capacities and fiber row", h == [1,2,3,4,1,6,7] and Asig == [1,32,162,384,600,864,1008] and row == [1,31,130,222,216,264,144])
for n in (8, 9):
    sg = tuple([n-6,n-5,n-4,n-2,n-3,n-1,n] + list(range(n-7, 0, -1)))
    check("Prop 2.5 sigma-prime capacities n=%d" % n, capacities(sg) == [1,2,3,4,1,6,7] + [1]*(n-7))
# --- 보조정리 b-top, 정리 tree-expansion (가)
def Ntree(l, t): return min(t, l+1) * A(t-1, l) if l >= 0 else 0
def bT(t, l): return Ntree(l, t) - Ntree(l-1, t)
good = True
for k in range(2, 8):
    N = 3*k + 3
    for t in range(1, N+1):
        dl = bT(t, k) - bT(t, k-1)
        if t >= k+1 and dl != k*d(t-1, k) + b(t-1, k) + b(t-1, k-1): good = False
        if t >= k+1 and dl != (k+1)*b(t-1, k) - (k-1)*b(t-1, k-1): good = False
        if t == k and dl != -k**(k-2): good = False
        if t <= k-1 and dl != 0: good = False
    def ser_mul(u, v): return [sum(u[i]*v[n-i] for i in range(n+1)) for n in range(N+1)]
    def ser(f): return [Fr(f(n), factorial(n)) for n in range(N+1)]
    Ak = ser(lambda n: A(n, k)); Ak1 = ser(lambda n: A(n, k-1)); Ak2 = ser(lambda n: A(n, k-2))
    Bk = ser(lambda t: bT(t, k) if t >= 1 else 0); Bk1 = ser(lambda t: bT(t, k-1) if t >= 1 else 0)
    lhs = [Ak[n] - 2*Ak1[n] + Ak2[n] for n in range(N+1)]
    term1 = ser_mul(Ak1, [Bk[n]-Bk1[n] for n in range(N+1)])
    def powsum(Bs, coef):
        out = [Fr(0)]*(N+1); pwr = Bs[:]
        j = 1
        while True:
            j += 1; pwr = ser_mul(pwr, Bs)
            if all(x == 0 for x in pwr): break
            cj = coef(j)
            out = [out[n] + cj*pwr[n] for n in range(N+1)]
        return out
    c1 = ser_mul(Ak1, powsum(Bk, lambda j: Fr(1, factorial(j))))
    c2 = ser_mul(Ak2, powsum(Bk1, lambda j: Fr(j-1, factorial(j))))
    if any(lhs[n] != term1[n] + c1[n] + c2[n] for n in range(N+1)): good = False
    if any(lhs[n]*factorial(n) != d(n, k) for n in range(1, N+1)): good = False
check("Lemma b-top (다) and Thm tree-expansion (가), k<=7", good)
print("ALL OK" if ok else "SOME FAIL")
