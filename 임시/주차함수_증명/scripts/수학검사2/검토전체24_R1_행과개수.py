# 검토전체24 R1: 1장·2장의 수치와 개수 항등식 검산 (정확 정수)
import sys, itertools, math
from fractions import Fraction as Fr
N = 90
C = math.comb
def p(n): return 1 if n == 0 else (n+1)**(n-1)
# 마지막 차 재귀로 A[n][l]
A = [[0]*(N+2) for _ in range(N+1)]
for l in range(N+2):
    col = [1]
    for n in range(1, N+1):
        s_ = 0
        for j in range(n):
            s_ += C(n-1, j)*min(j+1, l+1)*col[j]*col[n-1-j]
        col.append(s_)
    for n in range(N+1): A[n][l] = col[n]
def Aval(n, l):
    if l < 0: return 0
    if l > N+1: return p(n)
    return A[n][l]
def b(n, l): return Aval(n, l) - Aval(n, l-1)
ok = True
def chk(name, cond):
    global ok
    print(("OK  " if cond else "FAIL"), name)
    if not cond: ok = False
# 1.3 표
table = {1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296],
7:[5040,42253,62145,57398,46142,32359,16807],8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
sums = {1:1,2:3,3:16,4:125,5:1296,6:16807,7:262144,8:4782969,9:100000000,10:2357947691}
for n in range(1, 11):
    row = [b(n, l) for l in range(n)]
    chk(f"1.3 표 n={n}", row == table[n] and sum(row) == sums[n] == p(n))
# 무차별 대입 (n<=7) 으로 재귀 자체 검증 + E, E2, B
def park(pref):
    n = len(pref); occ = [0]*(n+2); disp = []; pos = []
    for a in pref:
        q = a
        while q <= n and occ[q]: q += 1
        if q > n: return None
        occ[q] = 1; disp.append(q-a); pos.append(q)
    return disp, pos
def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        z = 0
        for j in range(i-1, 0, -1):
            if sigma[j-1] > sigma[i-1]: z = j; break
        h.append(i - z)
    return h
brute = {}
for n in range(1, 8):
    cnt = [0]*n; E = [0]*(n+1); E2 = [0]*(n+1); B = [0]*(n+1)
    for pref in itertools.product(range(1, n+1), repeat=n):
        r = park(pref)
        if r is None: continue
        disp, pos = r
        M = max(disp); cnt[M] += 1
        ties = [i for i in range(n) if disp[i] == M]
        if len(ties) % 2 == 0: E[M] += 1
        if len(ties) == 2: E2[M] += 1
        sigma = [0]*n
        for car, q in enumerate(pos): sigma[q-1] = car+1
        h = caps(sigma)
        if all(h[pos[i]-1] == M+1 for i in ties): B[M] += 1
    brute[n] = (cnt, E, E2, B)
    chk(f"무차별 n={n} 행 = 재귀", cnt == [b(n, l) for l in range(n)])
    good = all(b(n, k) - b(n, k-1) == 2*E[k] - B[k-1] for k in range(1, n+1))
    chk(f"동률-막힘 항등식 n={n}, 1<=k<=n", good)
    chk(f"B_(n,0)=1, B_(n,n-1)=b_(n,n-1) n={n}", B[0] == 1 and B[n-1] == b(n, n-1))
    chk(f"2E2-B<=d n={n}", all(2*E2[k]-B[k-1] <= b(n,k)-b(n,k-1) for k in range(1, n+1)))
chk("n=3 세 무리 6,7,3", brute[3][0] == [6,7,3])
def witness(n):
    row = [b(n, l) for l in range(n)]
    for w in range(n):
        if all(row[i] <= row[i+1] for i in range(w)) and all(row[i] >= row[i+1] for i in range(w, n-1)): return w
    return None
chk("증인 n=1..10", [witness(n) for n in range(1, 11)] == [0,0,1,1,1,2,2,3,3,4])
chk("모든 행 n<=90 단봉", all(witness(n) is not None for n in range(1, N+1)))
kn = lambda n: -(-n//2)
neg = [n for n in range(2, N+1) if b(n, kn(n)) - b(n, kn(n)-1) < 0]
pos_ = [n for n in range(2, N+1) if b(n, kn(n)) - b(n, kn(n)-1) > 0]
chk("d_(n,k_n)<0 정확히 2<=n<=15, >0 for 16<=n<=90", neg == list(range(2, 16)) and pos_ == list(range(16, N+1)))
def lc_fail(n):
    return [l for l in range(1, n-1) if b(n, l)**2 < b(n, l-1)*b(n, l+1)]
fails = [n for n in range(1, N+1) if lc_fail(n)]
print("로그오목 실패 행(<=90):", fails[:12], " n=80 실패 수준:", lc_fail(80))
chk("로그오목 처음 실패 n=80, l=40", fails[0] == 80 and 40 in lc_fail(80))
chk("b_(k,k-1)=p_(k-1)", all(b(k, k-1) == p(k-1) for k in range(1, 40)))
h = caps([1,2,3,5,4,6,7])
Asig = [math.prod(min(x, l+1) for x in h) for l in range(7)]
bs = [Asig[0]] + [Asig[l]-Asig[l-1] for l in range(1, 7)]
chk("명제 2.5 섬유", h == [1,2,3,4,1,6,7] and Asig == [1,32,162,384,600,864,1008] and bs == [1,31,130,222,216,264,144])
for n in (8, 9, 12):
    s2 = [n-6,n-5,n-4,n-2,n-3,n-1,n] + list(range(n-7, 0, -1))
    h2 = caps(s2)
    A2 = [math.prod(min(x, l+1) for x in h2) for l in range(n)]
    b2 = [A2[0]] + [A2[l]-A2[l-1] for l in range(1, n)]
    chk(f"sigma-prime n={n}", b2 == bs + [0]*(n-7))
chk("A_(n,0)=n!", all(Aval(n, 0) == math.factorial(n) for n in range(0, 20)))
fub = [1]
for n in range(1, 15): fub.append(sum(C(n, j)*fub[n-j] for j in range(1, n+1)))
chk("A_(n,1) = n![x^n] 1/(2-e^x)", all(Aval(n, 1) == fub[n] for n in range(15)))
def pi0num(n, y):
    return p(n) - sum(C(n, m)*m**(m-1)*p(n-m) for m in range(y+1, n+1))
good = True
for l in range(0, 12):
    for n in range(1, 2*l+4):
        rhs = pi0num(n, l+1) + sum(C(n, m)*(l+1)*Aval(m-1, l)*p(n-m) for m in range(l+2, n+1))
        if rhs != Aval(n, l): good = False
chk("정리 2.13(가) n<=2l+3", good)
def s(m, y): return Fr(Aval(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(m, Y), p(m))
def pin(n, m): return Fr(C(n, m)*m**(m-1)*p(n-m), p(n))
good = True
for y in range(1, 10):
    for n in range(1, 2*y+2):
        rhs = sum(pin(n, m)/m*(s(m-1, y+1) + y*c(m-1, y)) for m in range(y+1, n+1))
        if rhs != c(n, y): good = False
chk("한 나무 재귀 n<=2y+1", good)
chk("(SM)", all(s(m+1, y) <= s(m, y) for m in range(0, 60) for y in range(1, 60)))
chk("(DM0)", all(s(m, y) <= s(m+1, y+1) for m in range(0, 60) for y in range(1, 60)))
good = True
for m in range(0, 40):
    for y in range(1, 12):
        for y2 in range(y, 14):
            lhs = s(m, y)/s(m, y2)
            rhs = math.prod(Fr(min(i, y), min(i, y2)) for i in range(1, m+1))
            if lhs < rhs: good = False
chk("용량 이동 비", good)
def P(m, j): return Fr(j*C(m-1, j-1)*p(j-1)*p(m-j), p(m))
chk("P_m 합=1", all(sum(P(m, j) for j in range(1, m+1)) == 1 for m in range(1, 30)))
chk("2.32(ㄱ)", all(P(m+1, m+1-r) <= P(m, m-r) for r in range(0, 20) for m in range(r+1, 40)))
chk("2.32(ㄴ)", all((m+1)*P(m+1, j) <= m*P(m, j) for j in range(1, 30) for m in range(j, 40)))
def F(m, x): return sum(P(m, j) for j in range(1, x+1))
chk("2.33 분포함수", all(F(m+1, x) <= F(m, x) <= F(m+1, x+1) for m in range(1, 25) for x in range(0, m+1)))
def NT(l, t): return min(t, l+1)*Aval(t-1, l)
good = True
for k in range(2, 9):
    for n in range(1, 2*k+2):
        v = sum(C(n, t)*(NT(k, t)-NT(k-1, t))*Aval(n-t, k-1) for t in range(k+1, n+1))
        if v != b(n, k): good = False
    for n in range(1, 2*k):
        v = sum(C(n, t)*(NT(k-1, t)-NT(k-2, t))*Aval(n-t, k-1) for t in range(k, n+1))
        if v != b(n, k-1): good = False
chk("표시 나무 전개 (다) 절단", good)
# 표시 나무 전개 (가) 전 차수: 계수 비교 (EGF 를 n! 곱한 정수로)
def egf_mul(a, bb, L):
    out = [Fr(0)]*(L+1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(bb):
            if i+j > L: break
            out[i+j] += x*y
    return out
L = 20
good = True
for k in range(2, 6):
    Ak = [Fr(Aval(n, k), math.factorial(n)) for n in range(L+1)]
    Ak1 = [Fr(Aval(n, k-1), math.factorial(n)) for n in range(L+1)]
    Ak2 = [Fr(Aval(n, k-2), math.factorial(n)) for n in range(L+1)]
    Bk = [Fr(0)] + [Fr(NT(k, t)-NT(k-1, t), math.factorial(t)) for t in range(1, L+1)]
    Bk1 = [Fr(0)] + [Fr(NT(k-1, t)-NT(k-2, t), math.factorial(t)) for t in range(1, L+1)]
    lhs = [Ak[n]-2*Ak1[n]+Ak2[n] for n in range(L+1)]
    term1 = egf_mul(Ak1, [x-y for x, y in zip(Bk, Bk1)], L)
    s2 = [Fr(0)]*(L+1); pw = Bk[:]
    j = 2; pw = egf_mul(pw, Bk, L)
    while any(pw):
        s2 = [x+y/math.factorial(j) for x, y in zip(s2, pw)]
        pw = egf_mul(pw, Bk, L); j += 1
    s3 = [Fr(0)]*(L+1); pw = egf_mul(Bk1, Bk1, L); j = 2
    while any(pw):
        s3 = [x+y*(j-1)/math.factorial(j) for x, y in zip(s3, pw)]
        pw = egf_mul(pw, Bk1, L); j += 1
    rhs = [x+y+z for x, y, z in zip(term1, egf_mul(Ak1, s2, L), egf_mul(Ak2, s3, L))]
    if lhs != rhs: good = False
chk("표시 나무 전개 (가) 전 차수 (n<=20, k=2..5)", good)
good = True
for D in range(2, 4):
    n0 = math.ceil(20*D**1.5)
    for n in range(n0, N+1):
        if not all(b(n, n-r-1) > b(n, n-r) for r in range(1, D)): good = False
chk("이동 꼬리 (아) (D=2: n>=57, D=3: n>=104 가운데 n<=90)", good)
# 지정 사슬 전개: -d_{n,n-r} = sum_j (-1)^{j+1} Q_{n,r,j}
def Wpair(n, gam):
    # (숲, 지정 사슬) 쌍의 수, 모든 고리 자손 고리
    j = len(gam); tj = n+1-sum(gam)
    if tj < 1: return 0
    num = Fr(math.factorial(n), math.factorial(gam[0]-1)*math.prod(math.factorial(g) for g in gam[1:])*math.factorial(tj))
    val = num*tj**(tj-1)*Fr(gam[0])**(gam[0]-1)
    for g in gam[1:]: val *= g**g
    return val
def comps(total_max, j):
    # gam_1..gam_j >=1, sum <= total_max
    if j == 0:
        yield (); return
    for g in range(1, total_max-(j-1)+1):
        for rest in comps(total_max-g, j-1):
            yield (g,)+rest
def Q(n, r, j):
    tot = Fr(0)
    for gam in comps(r+1, j):
        ts = []; acc = 0
        for g in gam:
            acc += g; ts.append(n+1-acc)
        def f(d):
            v = Fr(1); acc2 = 0
            for g, t in zip(gam, ts):
                acc2 += g
                v *= Fr(max(d-acc2, 0), t)
            return v
        tot += Wpair(n, gam)*(f(r+2)-2*f(r+1)+f(r))
    return tot
good = True; good2 = True; good3 = True
for r in range(1, 6):
    for n in range(2*r+1, 2*r+8):
        Qs = [Q(n, r, j) for j in range(1, r+2)]
        lhs = b(n, n-r-1) - b(n, n-r)
        if lhs != sum((-1)**(j) * q for j, q in enumerate(Qs)): good = False
        if Qs[0] != C(n, r)*(n-r)**(n-r-2)*(r+1)**r: good2 = False
        if not (Qs[0]-(Qs[1] if len(Qs) > 1 else 0) <= lhs <= Qs[0]): good3 = False
chk("지정 사슬 전개 (다) 교대합 = -d", good)
chk("Q_(n,r,1) 닫힌 꼴", good2)
chk("이동 꼬리 (가) Q1-Q2 <= -d <= Q1", good3)
print("ALL OK" if ok else "SOME FAIL")
