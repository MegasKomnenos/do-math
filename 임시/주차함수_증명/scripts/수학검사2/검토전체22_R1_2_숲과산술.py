# 검토전체22 R1 검산 2: 숲 전수(n<=6), Borel 산술, 2.9 닫힌 꼴, 2.12 이동 꼬리 (분수 + 부동소수점)
from fractions import Fraction as Fr
from math import comb, factorial, exp, log, sqrt, pi as PI, e as E
import itertools

NMAX = 70
def p(n): return 1 if n == 0 else (n + 1) ** (n - 1)
def build_A(l, nmax):
    A = [1] + [0] * nmax
    for n in range(1, nmax + 1):
        A[n] = sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j] for j in range(n))
    return A
Acol = {l: build_A(l, NMAX) for l in range(0, NMAX + 1)}
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    if l >= n - 1: return p(n)
    return Acol[l][n]
def b(n, l): return A(n, l) - A(n, l - 1)
def d(n, k): return b(n, k) - b(n, k - 1)
def s(m, y): return Fr(A(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(m, Y), p(m))
ok = True
def check(name, cond):
    global ok
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: ok = False

def Bor(m): return Fr(m**(m-1), factorial(m))            # e^{-m} 인자는 따로
def BorF(m): return exp(-m + (m-1)*log(m) - sum(log(i) for i in range(1, m+1)))
def RenF(j): return 1.0 if j == 0 else j * BorF(j)
def theta(t, k):  # 이항계수 꼴
    return Fr(comb(t, k) * k**(k-1) * (t-k)**(t-k), t**(t-1))

# ---------- 숲 전수: {1..n} 위 뿌리 숲 = 부모 배열(0=보조 뿌리), n<=6
def forests(n):
    for par in itertools.product(range(0, n+1), repeat=n):
        good = True
        for v in range(1, n+1):
            u = v; steps = 0
            while u != 0 and steps <= n:
                u = par[u-1]; steps += 1
            if u != 0: good = False; break
        if good: yield par
def stats(par, n):
    # 부분나무 크기 t_v, 국소 역전 수 I_v
    anc = {}
    t = [0]*(n+1); I = [0]*(n+1)
    for v in range(1, n+1):
        u = v
        while u != 0:
            t[u] += 1
            if u != v and v < u: I[u] += 1
            u = par[u-1]
    return t, I
for n in range(1, 7):
    cnt = 0; Mdist = {}; H = {}; pairs = {}
    wsum = Fr(0); prodsum = {l: Fr(0) for l in range(n)}
    chain2 = {}
    for par in forests(n):
        cnt += 1
        t, I = stats(par, n)
        M = max(I[1:])
        Mdist[M] = Mdist.get(M, 0) + 1
        for v in range(1, n+1):
            H[t[v]] = H.get(t[v], 0) + 1
        for l in range(n):
            pr = Fr(1)
            for v in range(1, n+1): pr *= Fr(min(t[v], l+1), t[v])
            prodsum[l] += pr
        # (v, 자손 w) 쌍: 크기 (t_v, t_w)
        for w in range(1, n+1):
            u = par[w-1]
            first = True
            while u != 0:
                key = (t[u], t[w], first)   # first: w 가 u 의 자식
                chain2[key] = chain2.get(key, 0) + 1
                first = False
                u = par[u-1]
    check("n=%d: forest count = p_n" % n, cnt == p(n))
    check("n=%d: Thm 2.10 #{M(F)<=l}=A_{n,l}" % n, all(sum(v for m, v in Mdist.items() if m <= l) == A(n, l) for l in range(n)))
    check("n=%d: Thm 2.11 A_{n,l}=sum_F prod min(1,(l+1)/t_v)" % n, all(prodsum[l] == A(n, l) for l in range(n)))
    check("n=%d: E_n[H_t(F)]=theta_{n+1}(t)" % n, all(Fr(H.get(t, 0), p(n)) == theta(n+1, t) for t in range(1, n+1)))
    # 지정 사슬 공식 (가) j=2: 자손 고리/자식 고리. e 인자는 소거되므로 분수로.
    good = True
    for t1 in range(2, n+1):
        for t2 in range(1, t1):
            g1 = n+1-t1; g2 = t1-t2
            tot_desc = sum(v for (a, b_, f), v in chain2.items() if a == t1 and b_ == t2)
            tot_child = sum(v for (a, b_, f), v in chain2.items() if a == t1 and b_ == t2 and f)
            # 기대 수 = Bor(t2)/Bor(n+1) * Ren(g1) * (Ren(g2) 또는 Bor(g2)), 첫 고리 자손
            base = Bor(t2) / Bor(n+1)
            exp_desc = base * (g1 * Bor(g1)) * (g2 * Bor(g2))
            exp_child = base * (g1 * Bor(g1)) * Bor(g2)
            if Fr(tot_desc, p(n)) != exp_desc or Fr(tot_child, p(n)) != exp_child: good = False
    check("n=%d: chain-law (가) j=2 (descendant/child second link)" % n, good)

# ---------- 보조정리 union-bound, 따름정리 union-bound-closed
def Psi(q): return sum(RenF(j) for j in range(1, q+1))
good1 = good2 = good3 = True
for n in range(2, 61):
    for y in range(1, n):
        lhs = float(1 - s(n, y))
        ub = sum(float(theta(n+1, t)) * (t-y)/t for t in range(y+1, n+1))
        q = n - y
        mid = ((n+1)/(y+1))**1.5 / (y+1) * sum(Psi(i) for i in range(1, q+1))
        rhs = (2*PI)**-0.5 * ((n+1)/(y+1))**1.5 / (y+1) * (4/3*q**1.5 + sqrt(q) - q - 1/3)
        if lhs > ub*(1+1e-12): good1 = False
        if ub > mid*(1+1e-12): good2 = False
        if mid > rhs*(1+1e-12): good3 = False
check("Lemma union-bound (n<=60)", good1)
check("Cor union-bound-closed first inequality", good2)
check("Cor union-bound-closed second inequality", good3)

# ---------- Borel 산술 (ㄱ)-(ㄹ), power-sum-renewal
def rb(m): return sum(log(i) for i in range(1, m+1)) - (m+0.5)*log(m) + m - 0.5*log(2*PI)
check("Robbins 1/(12m+1)<rb_m<1/(12m), m<=100 (binary64로는 m이 크면 1/(360m^3) 여유가 반올림 아래)", all(1/(12*m+1) < rb(m) < 1/(12*m) for m in range(1, 101)))
z12, zm12, z32 = -1.4603545088095868, -0.20788622497735457, 2.612375348685488
check("zeta intervals", -1.46036 <= z12 <= -1.46035 and -0.20789 <= zm12 <= -0.20788 and 2.61237 <= z32 <= 2.61238)
g1 = g2 = g3 = g4 = g5 = True
S1 = S2 = S3 = 0.0; psi = 0.0
cPsi = -z12 + z32/12
for q in range(1, 20001):
    S1 += q**-0.5; S2 += q**0.5; S3 += q**-1.5; psi += RenF(q) if q < 600 else (2*PI*q)**-0.5*exp(-rb(q))
    lo1 = 2*sqrt(q) + z12 + 0.5*q**-0.5 - q**-1.5/24; hi1 = 2*sqrt(q) + z12 + 0.5*q**-0.5
    lo2 = 2/3*q**1.5 + 0.5*q**0.5 + zm12; hi2 = lo2 + q**-0.5/24
    if not (lo1 - 1e-9 <= S1 <= hi1 + 1e-9): g1 = False
    if not (lo2 - 1e-7 <= S2 <= hi2 + 1e-7): g2 = False
    if S3 > z32: g3 = False
    low = (2*PI)**-0.5 * (2*sqrt(q) - cPsi + 0.5/sqrt(q) - q**-1.5/24)
    if not (psi >= low - 1e-9 and low >= 0.3989*(2*sqrt(q) - 1.678) and 0.3989*(2*sqrt(q)-1.678) >= 0.7978*sqrt(q) - 0.8848): g4 = False
    if not (psi <= (2*PI)**-0.5*(2*sqrt(q)-1) + 1e-9): g5 = False
check("power sums (ㄱ) j^{-1/2}", g1); check("power sums (ㄱ) j^{1/2}", g2); check("sum j^{-3/2}<=zeta(3/2)", g3)
check("Psi lower chain (ㄴ)", g4); check("Psi upper (ㄷ)", g5)
print("   c_Psi = %.7f ; 0.3989*1.678 = %.5f (본문 마지막 상수 0.8848과 비교)" % (cPsi, 0.3989*1.678))
# Borel 꼬리
tail = 1.0; gt = True
for q in range(0, 400):
    if q >= 1: tail -= BorF(q)
    lo = 2*(2*PI)**-0.5*exp(-1/(12*(q+1)))*(q+1)**-0.5
    hi = 2*(2*PI)**-0.5*(q+0.5)**-0.5
    if not (lo <= tail + 1e-12 and (q == 0 or tail <= hi + 1e-12)): gt = False
check("Borel tail bounds (ㄷ)", gt)
# 갱신 방정식 (가), (다)
gr = True
for j in range(1, 60):
    if abs(RenF(j) - (BorF(j) + sum(BorF(m)*RenF(j-m) for m in range(1, j)))) > 1e-12: gr = False
check("renewal equation (가)", gr)
gg = True
def g(x): return (x-1)*log(1+1/x)
for i in range(1, 500):
    if not (1.5/i - 5/(6*i*i) - 1e-15 <= 1-g(i) <= 1.5/i + 1e-15): gg = False
    if abs(BorF(i+1)/BorF(i) - exp(g(i)-1)) > 1e-12: gg = False
check("g bounds, Bor ratio", gg)

# ---------- 정리 2:old-2-38: k x_t(k) >= -theta_t(k); 보조정리 curvature-level-mass
def sT(t, y): return Fr(min(t, y) * A(t-1, y-1), t**(t-1))
def xcurv(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)
gc = gk = True
for k in range(2, 20):
    for t in range(1, 60):
        x = xcurv(t, k)
        if t >= k+1 and x != Fr(1, t)*((k+1)*c(t-1, k) - (k-1)*c(t-1, k-1)): gc = False
        if t == k and x != Fr(-1, k): gc = False
        if t <= k-1 and x != 0: gc = False
        if t >= k and k*x < -theta(t, k): gk = False
check("Lemma curvature-level-mass", gc); check("Thm 2.38 k x_t(k)>=-theta_t(k)", gk)

# ---------- 보조정리 supersolution (나): s_{y+q-1}(y) <= phi_1(q)
gs = True
for y in range(2, 25):
    for q in range(1, y+3):
        if y+q-1 > NMAX: continue
        phi1 = 1 - sum(BorF(j)*(q-j)/(y+q-j) for j in range(1, q))
        if float(s(y+q-1, y)) > phi1 + 1e-12: gs = False
check("Lemma supersolution (나)", gs)

# ---------- 2.12: 이동 꼬리
def nf(n, dd): return exp(dd + sum(log(n-i) for i in range(dd)) + (n-dd-2)*log(n-dd) - (n-2)*log(n))
gm = [True]*8
def Wcal(n, gam):  # (숲, 지정 사슬) 쌍의 수 / n^{n-2}: 정리 chain-law (가)
    tj = n + 1 - sum(gam)
    val = float(Fr(p(n)) * Bor(tj) / Bor(n+1))  # e 인자: e^{-tj+n+1} 과 Ren 의 e^{-gam}: 합 0
    for gmm in gam: val *= float(gmm * Bor(gmm))
    return val
for n in range(3, 61):
    for r in range(1, (n-1)//2 + 1):
        lhs = b(n, n-r-1) - b(n, n-r)
        Q1 = comb(n, r) * (n-r)**(n-r-2) * (r+1)**r
        # Q2 by (나)
        Q2 = 0.0
        for g1_ in range(1, r+1):
            for g2_ in range(1, r+2-g1_):
                t1 = n+1-g1_; t2 = t1-g2_
                W = Wcal(n, (g1_, g2_))
                Q2 += (2 if g1_+g2_ <= r else (g2_+1)) * W / (t1*t2)
        if not (Q1 - Q2 <= lhs*(1+1e-9) + 1e-9*Q1 and lhs <= Q1): gm[0] = False
        nn = float(n)**(n-2)
        if abs(Q1/nn - nf(n, r)*E*RenF(r+1)) > 1e-9*(Q1/nn): gm[1] = False
        v = nf(n, r)*E*RenF(r+1) + d(n, n-r)/nn
        if not (-1e-12 <= v <= E*(5*r-1)/(4*n*(1-r/n)**4) + 1e-12): gm[2] = False
        if abs(-d(n, n-r)/nn - E*RenF(r+1)) > 60*(r+1)/n: gm[3] = False
    for dd in range(0, n):
        v = nf(n, dd)
        if not ((n/(n-dd))**2*(1-1e-12) <= v <= (n/(n-dd))**2.5*(1+1e-12)): gm[4] = False
for r in range(0, 300):
    if E*RenF(r+1) > 1+1e-12: gm[5] = False
    if r >= 1 and not (E*RenF(r+1) >= exp(-0.5)*r**-0.5 > 1/(2*sqrt(r+1))): gm[5] = False
for D in range(2, 4):
    n0 = int(20*D**1.5) + 1
    for n in range(n0, NMAX+1):
        if not all(b(n, n-D+i) > b(n, n-D+i+1) for i in range(D-1)): gm[6] = False
for j in range(2, 400):
    sm = sum(RenF(a)*RenF(j-a) for a in range(1, j))
    if sm > 0.5: gm[7] = False
check("moving-tail (가) Q1-Q2<=..<=Q1", gm[0]); check("moving-tail (라) Q1/n^{n-2}", gm[1]); check("moving-tail (마)", gm[2])
check("moving-tail (사)", gm[3]); check("moving-tail (다) nf bounds", gm[4]); check("moving-tail (바)", gm[5]); check("moving-tail (아) D=2,3", gm[6]); check("moving-tail (라) convolution<=1/2", gm[7])

# ---------- 2.7: J_n(z) = p_{k-1} G_{z,k-1,n} (n<=2k), K ≡ G_* mod x^{2k+2}
def series_ops(N):
    def mul(u, v): return [sum(u[i]*v[n-i] for i in range(n+1)) for n in range(N+1)]
    def integ(u): return [Fr(0)] + [u[n-1]/n for n in range(1, N+1)]
    def expo(u):  # u[0]=0
        out = [Fr(1)] + [Fr(0)]*N
        for n in range(1, N+1):
            out[n] = sum(i*u[i]*out[n-i] for i in range(1, n+1)) / n
        return out
    return mul, integ, expo
def capacities(sig):
    n = len(sig); h = []
    for i in range(n):
        z = 0
        for j in range(i-1, -1, -1):
            if sig[j] > sig[i]: z = j+1; break
        h.append(i+1 - z)
    return h
gJ = gK = True
for k in range(1, 4):
    N = 2*k + 2
    if N > 7: N = 7
    mul, integ, expo = series_ops(N)
    T = [Fr(0)] + [Fr(t**(t-1), factorial(t)) for t in range(1, N+1)]
    eT = [Fr(p(m), factorial(m)) for m in range(N+1)]
    Gr = [T[n] - mul(T, T)[n]/2 for n in range(N+1)]
    hsn = {n: [capacities(sg) for sg in itertools.permutations(range(1, n+1))] for n in range(0, N+1)}
    for z in (Fr(k-1), Fr(2), Fr(5, 3)):
        ezG = expo([z*x for x in Gr]); emzG = expo([-z*x for x in Gr])
        mono = [Fr(0)]*(N+1)
        if k-1 <= N: mono[k-1] = Fr(1, factorial(k-1))
        Y = mul(mul(eT, ezG), integ(mul(emzG, mono)))
        for n in range(0, min(2*k, N)+1):
            J = Fr(0)
            for h in hsn[n]:
                Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
                low = 1
                for x in h:
                    if x < k: low *= x
                if H >= 1: J += low * H * Fr(k)**(H-1) * z**Z
            if J != p(k-1) * Y[n] * factorial(n): gJ = False
        # K_k(y;x) 와 연쇄 해
        y = z
        Kser = []
        for n in range(0, N+1):
            tot = Fr(0)
            for h in hsn[n]:
                Z = sum(1 for x in h if x > k)
                low = 1
                for x in h:
                    if x <= k: low *= x
                tot += low * y**Z
            Kser.append(tot / factorial(n))
        Elt = [eT[n] if n < k else Fr(0) for n in range(N+1)]
        oneT = [(1 if n == 0 else 0) - T[n] for n in range(N+1)]
        sm = mul(oneT, [eT[n]-Elt[n] for n in range(N+1)])
        eyG = expo([y*x for x in Gr]); emyG = expo([-y*x for x in Gr])
        Gst = [Elt[n] + sm[n] + y*mul(mul(eT, eyG), integ(mul(sm, emyG)))[n] for n in range(N+1)]
        lim = min(2*k+1, N)
        if any(Kser[n] != Gst[n] for n in range(0, lim+1)): gK = False
check("Lemma J-egf: J_n(z)=p_{k-1}G_{z,k-1,n}, n<=2k (k<=3)", gJ)
check("Cor volterra-residual (ㄱ): K ≡ G_* mod x^{2k+2} (k<=3, n<=7)", gK)
print("ALL OK" if ok else "SOME FAIL")
