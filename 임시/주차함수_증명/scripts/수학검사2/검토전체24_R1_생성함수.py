# 검토전체24 R1: 2.7절 생성함수 항등식, 2.2·2.4·2.5절 숲 셈, 2.9·2.12절 부등식 수치 검산
import sys, itertools, math
from fractions import Fraction as Fr
C = math.comb
def p(n): return 1 if n == 0 else (n+1)**(n-1)
ok = True
def chk(name, cond):
    global ok
    print(("OK  " if cond else "FAIL"), name)
    if not cond: ok = False
# ---------- 멱급수 (보통 계수, Fraction) ----------
def mul(a, b, L):
    out = [Fr(0)]*(L+1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            if i+j > L: break
            if y != 0: out[i+j] += x*y
    return out
def integ(a, L):
    return ([Fr(0)] + [a[i]/(i+1) for i in range(L)])[:L+1]
def deriv(a, L):
    return [a[i+1]*(i+1) for i in range(L)] + [Fr(0)]
def expo(a, L):
    assert a[0] == 0
    out = [Fr(1)] + [Fr(0)]*L
    for n in range(1, L+1):
        out[n] = sum(k*a[k]*out[n-k] for k in range(1, n+1))/n
    return out
def inv(a, L):
    out = [Fr(0)]*(L+1); out[0] = 1/a[0]
    for n in range(1, L+1):
        out[n] = -sum(a[k]*out[n-k] for k in range(1, n+1))/a[0]
    return out
def add(a, b): return [x+y for x, y in zip(a, b)]
def sub(a, b): return [x-y for x, y in zip(a, b)]
def sc(c, a): return [c*x for x in a]
# ---------- 가중 분배함수 (재귀) ----------
def Apart(wg, L):
    A = [Fr(1)]
    for n in range(1, L+1):
        A.append(sum(C(n-1, j)*wg(j+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        z = 0
        for j in range(i-1, 0, -1):
            if sigma[j-1] > sigma[i-1]: z = j; break
        h.append(i - z)
    return h
# 순열 정의와 재귀의 일치 (정리 2:weighted-partition (나)), 임의 무게
wgt = lambda t: Fr(t*t+1, t+2)
A_rec = Apart(wgt, 7)
for n in range(1, 8):
    tot = Fr(0)
    for sg in itertools.permutations(range(1, n+1)):
        tot += math.prod(wgt(h) for h in caps(sg))
    if tot != A_rec[n]: chk(f"가중 분배 재귀 n={n}", False)
chk("가중 분배함수: 순열 합 = 마지막 차 재귀 (n<=7)", True)
# ---------- 2.7: 두 변수 얼린 다항식 ----------
L = 16
fact = [math.factorial(i) for i in range(L+3)]
T = [Fr(0)] + [Fr(t**(t-1), fact[t]) for t in range(1, L+1)]
eT = expo(T, L)
chk("e^T 계수 = p_n/n!", all(eT[n] == Fr(p(n), fact[n]) for n in range(L+1)))
Gr = sub(T, sc(Fr(1, 2), mul(T, T, L)))
chk("Gr' = e^T", deriv(Gr, L)[:L] == eT[:L])
for k in (1, 2, 3, 4):
    for (eta, y) in ((Fr(5, 7), Fr(3, 2)), (Fr(k), Fr(k-1)), (Fr(k), Fr(k+1)), (Fr(k), Fr(k)), (Fr(2), Fr(0))):
        wg = lambda t: Fr(t) if t < k else (eta if t == k else y)
        Kn = Apart(wg, L)
        Kser = [Kn[n]/fact[n] for n in range(L+1)]
        adj = [Fr(0)]*(L+1)
        for t in range(1, k): adj[t] = (t-y)*p(t-1)/fact[t]
        adj[k] = (eta-y)*p(k-1)/fact[k]
        ea = expo(adj, L)
        den = [Fr(1)] + [Fr(0)]*L
        den = sub(den, sc(y, integ(ea, L)))
        closed = mul(ea, inv(den, L), L)
        if closed != Kser: chk(f"두 변수 닫힌 꼴 k={k} eta={eta} y={y}", False)
    chk(f"따름정리 two-variable-frozen (ㄱ) k={k}", True)
    # 한 변수판 K_k(y;x), 조각 차이, 연쇄 해, 잔차
    for y in (Fr(3, 2), Fr(k-1), Fr(k+1), Fr(1, 3)):
        wg = lambda t: Fr(t) if t <= k else y
        Kn = Apart(wg, L)
        Kser = [Kn[n]/fact[n] for n in range(L+1)]
        E = [Fr(p(j), fact[j]) if j < k else Fr(0) for j in range(L+1)]
        Tle = [T[t] if t <= k else Fr(0) for t in range(L+1)]
        Tgt = sub(T, Tle)
        pd = sub(sc(y, integ(sub(Kser, E), L)), Tgt)
        chk(f"k={k} y={y}: K = e^T e^pd", mul(eT, expo(pd, L), L) == Kser)
        pdc = all(pd[t] == (y*Kn[t-1]-t**(t-1))/fact[t] for t in range(k+1, L+1)) and all(pd[t] == 0 for t in range(0, k+1))
        chk(f"k={k} y={y}: pd 계수 꼴, x^(k+1) 아래 없음", pdc)
        one = [Fr(1)] + [Fr(0)]*L
        sm = mul(sub(one, T), sub(eT, E), L)
        eyG = expo(sc(y, Gr), L); emyG = expo(sc(-y, Gr), L)
        Gstar = add(add(E, sm), sc(y, mul(mul(eT, eyG, L), integ(mul(sm, emyG, L), L), L)))
        X = sub(Kser, Gstar)
        lowest = next((i for i, v in enumerate(X) if v != 0), None)
        chk(f"k={k} y={y}: 잔차 최저 차수 >= 2k+2 (실제 {lowest})", lowest is None or lowest >= 2*k+2)
        rhs = mul(eT, sub(add(sc(y, integ(X, L)), expo(pd, L)), add(one, pd)), L)
        chk(f"k={k} y={y}: 잔차 항등식", rhs == X)
        eTle = expo(Tle, L)
        lim = min(L, 2*k+1)
        chk(f"k={k}: E+sm == e^(T<=k) mod x^(2k+2)", add(E, sm)[:lim+1] == eTle[:lim+1])
        lim3 = min(L, 3*k+2)
        rhs2 = mul(eTle, add(sc(y, integ(X, L)), sc(Fr(1, 2), mul(pd, pd, L))), L)
        chk(f"k={k} y={y}: (ㄴ) mod x^(3k+3)", rhs2[:lim3+1] == X[:lim3+1])
        # 경계 다항식 J_n(y)
        Jn = []
        for n in range(0, L+1):
            Jn.append(None)
        # J_n(y) = d/d eta K_{n,k}(eta,y) at eta=k : 수치 미분 대신 eta 다항식 보간 (차수<=n/k)
        def Kval(eta):
            wg2 = lambda t: Fr(t) if t < k else (eta if t == k else y)
            return Apart(wg2, L)
        deg = L//k
        xs = [Fr(k)+i for i in range(deg+1)]
        vals = [Kval(x0) for x0 in xs]
        J = []
        for n in range(L+1):
            # 뉴턴 전진 차분으로 eta=k 에서의 도함수
            f = [vals[i][n] for i in range(deg+1)]
            diffs = []; cur = f[:]
            for i in range(deg+1):
                diffs.append(cur[0]); cur = [cur[j+1]-cur[j] for j in range(len(cur)-1)]
            # f(k+s) = sum diffs[i]*C(s,i);  d/ds C(s,i) at s=0 = (-1)^(i-1)/i
            J.append(sum(diffs[i]*Fr((-1)**(i-1), i) for i in range(1, deg+1)))
        Y = sc(Fr(p(k-1)), mul(mul(eT, eyG, L), integ(mul(emyG, [Fr(1, fact[k-1]) if i == k-1 else Fr(0) for i in range(L+1)], L), L), L))
        Jser = [J[n]/fact[n] for n in range(L+1)]
        agree = [n for n in range(L+1) if Jser[n] == Y[n]]
        first_diff = next((n for n in range(L+1) if Jser[n] != Y[n]), None)
        chk(f"k={k} y={y}: J_n = p_(k-1) G_(y,k-1,n) for n<=2k (처음 다른 n = {first_diff})", all(Jser[n] == Y[n] for n in range(min(L, 2*k)+1)))
        if 0 <= y <= k+1:
            chk(f"k={k} y={y}: J_n(y) <= p_(k-1) G (모든 n<={L})", all(Jser[n] <= Y[n] for n in range(L+1)))
        # ODE (ㄷ)
        adjk = [Fr(0)]*(L+1)
        for t in range(1, k+1): adjk[t] = (t-y)*p(t-1)/fact[t]
        lhs = deriv(Jser, L)
        inh = [Fr(0)]*(L+1)
        for i in range(L+1-(k-1)): inh[i+k-1] = Fr(p(k-1), fact[k-1])*Kser[i]
        rhs = add(mul(add(sc(2*y, Kser), deriv(adjk, L)), Jser, L), inh)
        chk(f"k={k} y={y}: J 의 일차 선형 방정식", lhs[:L] == rhs[:L])
# B, J, Xi 순열 무차별
for n in range(1, 8):
    perms = [caps(sg) for sg in itertools.permutations(range(1, n+1))]
    for k in range(1, n+1):
        Bv = 0; Jv = 0; Xi = 0
        for h in perms:
            Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            pr = math.prod(x for x in h if x < k)
            Bv += pr*(k-1)**Z*(k**H-(k-1)**H)
            Jv += pr*(k-1)**Z*H*(k**(H-1) if H >= 1 else 0)
            if H == 2: Xi += pr*(k-1)**Z
        if not (Bv <= Jv): chk(f"B<=J n={n} k={k}", False)
        if n <= 2*k-1 and Bv != Jv: chk(f"B=J n<=2k-1 n={n} k={k}", False)
        if n == 2*k and not (Bv == Jv - C(2*k-1, k-1)*p(k-1)**2 and Xi == C(2*k-1, k-1)*p(k-1)**2): chk(f"Xi n=2k k={k}", False)
        if any(sum(1 for x in h if x == k)*k > n for h in perms): chk("H_k k <= n", False)
chk("B<=J(k-1), n<=2k-1 등호, B_(2k,k-1)=J-Xi (n<=7 무차별)", True)
# ---------- 숲 무차별: 정리 2.10, 지정 사슬 공식 ----------
def forests(n):
    # 부모 함수 par: {1..n}->{0..n}, 순환 없음
    for par in itertools.product(range(0, n+1), repeat=n):
        good = True
        for v in range(1, n+1):
            seen = 0; u = v
            while u != 0 and seen <= n:
                u = par[u-1]; seen += 1
            if seen > n: good = False; break
        if good: yield par
def stats(par, n):
    anc = {v: [] for v in range(1, n+1)}
    for v in range(1, n+1):
        u = par[v-1]
        while u != 0:
            anc[v].append(u); u = par[u-1]
    t = [1]*(n+1); I = [0]*(n+1)
    for v in range(1, n+1):
        for u in anc[v]:
            t[u] += 1
            if v < u: I[u] += 1
    return anc, t, I
import collections
def last_car_A(n, l):
    col = [1]
    for m in range(1, n+1):
        col.append(sum(C(m-1, j)*min(j+1, l+1)*col[j]*col[m-1-j] for j in range(m)))
    return col[n]
for n in range(1, 7):
    cnt = collections.Counter(); nf = 0
    Hexp = collections.Counter(); chain2 = collections.Counter(); chain2c = collections.Counter(); rootsz = collections.Counter()
    pairs = collections.Counter()
    for par in forests(n):
        nf += 1
        anc, t, I = stats(par, n)
        cnt[max(I[1:])] += 1
        for v in range(1, n+1):
            Hexp[t[v]] += 1
            if par[v-1] == 0: rootsz[t[v]] += 1
            for u in anc[v]:
                chain2[(t[u], t[v])] += 1          # 자손 고리-자손 고리
                if par[v-1] == u and par[u-1] == 0: chain2c[(t[u], t[v])] += 1   # 자식-자식
        comps_ = [v for v in range(1, n+1) if par[v-1] == 0]
        for a in comps_:
            for b_ in comps_:
                if a != b_: pairs[(t[a], t[b_])] += 1
    chk(f"숲의 수 n={n} = (n+1)^(n-1)", nf == p(n))
    cum = 0; good = True
    for l in range(n):
        cum += cnt[l]
        if cum != last_car_A(n, l): good = False
    chk(f"정리 2.10: #(M(F)<=l) = A_(n,l), n={n}", good)
    # (가) j=1 자손 고리: E[H_t] = theta_{n+1}(t) = C(n+1,t) t^(t-1) (n+1-t)^(n+1-t) / (n+1)^n
    good = all(Fr(Hexp[t_], nf) == Fr(C(n+1, t_)*t_**(t_-1)*(n+1-t_)**(n+1-t_), (n+1)**n) for t_ in range(1, n+1))
    chk(f"theta_(n+1)(t) n={n}", good)
    good = all(Fr(rootsz[m], nf) == Fr(C(n, m)*m**(m-1)*p(n-m), p(n)) for m in range(1, n+1))
    chk(f"pi_n(m) n={n}", good)
    # (가) j=2: 쌍의 수 = n!/((g1-1)! g2! t2!) * t2^(t2-1) * [g1^(g1-1) or g1^(g1-2)] * [g2^g2 or g2^(g2-1)]
    good = True
    for t1 in range(2, n+1):
        for t2 in range(1, t1):
            g1 = n+1-t1; g2 = t1-t2
            base = Fr(math.factorial(n), math.factorial(g1-1)*math.factorial(g2)*math.factorial(t2))*t2**(t2-1)
            dd = base*g1**(g1-1)*g2**g2
            cc = base*Fr(g1)**(g1-2)*g2**(g2-1)
            if chain2[(t1, t2)] != dd or chain2c[(t1, t2)] != cc: good = False
    chk(f"지정 사슬 공식 (가) j=2 (자손·자손, 자식·자식) n={n}", good)
    good = True
    for a in range(1, n):
        for b_ in range(1, n-a+1):
            exp = Fr(math.factorial(n), math.factorial(a)*math.factorial(b_)*math.factorial(n-a-b_))*a**(a-1)*b_**(b_-1)*p(n-a-b_)
            if pairs[(a, b_)] != exp: good = False
    chk(f"지정 사슬 공식 (나) j=2 n={n}", good)
# ---------- 실수 부등식 수치 ----------
Bor = lambda m: math.exp(-m + (m-1)*math.log(m) - math.lgamma(m+1))
Ren = lambda j: 1.0 if j == 0 else j*Bor(j)
g = lambda x: (x-1)*math.log(1+1/x)
chk("g 상하계 (다)", all(1-1.5/x+0.5/x**2 <= g(x)+1e-15 and g(x) <= 1-1.5/x+5/(6*x*x)+1e-15 for x in [1+0.37*i for i in range(3000)]))
chk("Bor 이웃비 = e^(g(m)-1)", all(abs(Bor(m+1)/Bor(m)-math.exp(g(m)-1)) < 1e-12 for m in range(1, 200)))
Psi = [0.0]
for j in range(1, 20001): Psi.append(Psi[-1]+Ren(j))
c2pi = (2*math.pi)**-0.5
chk("Psi(q) <= (2pi)^-1/2 (2 sqrt q - 1)", all(Psi[q] <= c2pi*(2*math.sqrt(q)-1) for q in range(1, 20001)))
z12, zm12, z32 = -1.4603545088095868, -0.2078862249773546, 2.612375348685488
cPsi = -z12+z32/12
chk("c_Psi in (1.5, 1.6781)", 1.5 < cPsi < 1.6781)
Plow = lambda x: c2pi*(2*math.sqrt(x)-cPsi+0.5/math.sqrt(x)-x**-1.5/24)
chk("Psi(q) >= Psi_low(q)", all(Psi[q] >= Plow(q) for q in range(1, 20001)))
s1 = 0.0; s2 = 0.0; good = True
for q in range(1, 20001):
    s1 += q**-0.5; s2 += q**0.5
    if not (2*math.sqrt(q)+z12+0.5*q**-0.5-q**-1.5/24 <= s1+1e-9 and s1 <= 2*math.sqrt(q)+z12+0.5*q**-0.5+1e-9): good = False
    if not (2/3*q**1.5+0.5*q**0.5+zm12 <= s2+1e-6 and s2 <= 2/3*q**1.5+0.5*q**0.5+zm12+q**-0.5/24+1e-6): good = False
chk("거듭제곱 합 Euler-Maclaurin 상하계", good)
tail = sum(Bor(m) for m in range(1, 200001))
good = True; acc = 0.0
for q in range(0, 3000):
    if q >= 1: acc += Bor(q)
    tl = 1-acc
    lo = 2*c2pi*math.exp(-1/(12*(q+1)))*(q+1)**-0.5
    if not (lo <= tl+1e-12): good = False
    if q >= 1 and not (tl <= 2*c2pi*(q+0.5)**-0.5+1e-12): good = False
chk("Borel 꼬리 상하계", good)
# 갱신 방정식
good = all(abs(Ren(j)-(Bor(j)+sum(Bor(m)*Ren(j-m) for m in range(1, j)))) < 1e-12 for j in range(1, 80))
chk("갱신 방정식 (가)", good)
# 합집합 상계의 닫힌 꼴과 실제 1-s_n(y)
def Acol(nmax, l):
    col = [1]
    for m in range(1, nmax+1):
        col.append(sum(C(m-1, j)*min(j+1, l+1)*col[j]*col[m-1-j] for j in range(m)))
    return col
good = True
for y in range(1, 30):
    col = Acol(60, y-1)
    for n in range(y+1, 61):
        lhs = 1-col[n]/p(n)
        q = n-y
        ub0 = sum(Ren(n+1-t)*Bor(t)/Bor(n+1)*(t-y)/t for t in range(y+1, n+1))
        ub1 = ((n+1)/(y+1))**1.5/(y+1)*sum(Psi[i] for i in range(1, q+1))
        ub2 = c2pi*((n+1)/(y+1))**1.5/(y+1)*(4/3*q**1.5+math.sqrt(q)-q-1/3)
        if not (lhs <= ub0+1e-12 and ub0 <= ub1+1e-12 and ub1 <= ub2+1e-12): good = False
chk("합집합 상계와 닫힌 꼴 (y<30, n<=60)", good)
# nf 상하계, 로그 계수
def nf(n, d): return math.exp(d + math.lgamma(n+1)-math.lgamma(n-d+1)+(n-d-2)*math.log(n-d)-(n-2)*math.log(n))
good = all((n/(n-d))**2 <= nf(n, d)*(1+1e-12) and nf(n, d) <= (n/(n-d))**2.5*(1+1e-12) for n in range(2, 200) for d in range(0, n))
chk("nf 상하계", good)
def lcterm(i, d, n): return (d*(d/n)**i/(i+1)+2*(d/n)**i-sum((r/n)**i for r in range(d)))/i
good = all(abs(math.log(nf(n, d))-sum(lcterm(i, d, n) for i in range(1, 400))) < 1e-9 for n in (50, 77, 200) for d in range(0, n//3))
chk("log nf = sum lc_i(d) n^-i", good)
# Ren 합성곱 상계
good = all(sum(Ren(a)*Ren(j-a) for a in range(1, j)) <= 0.5 for j in range(2, 400))
chk("sum Ren Ren <= 1/2", good)
good = all(math.e*Ren(r+1) <= 1+1e-15 and (r == 0 or math.e*Ren(r+1) >= math.exp(-0.5)*r**-0.5) for r in range(0, 2000))
chk("(바) e Ren(r+1)", good)
# h-변환 항등식 (무작위 핵)
import random
random.seed(1)
good = True
for trial in range(200):
    d = random.randint(2, 7); y = random.uniform(0.5, 9)
    hf = {q: random.uniform(0.2, 2) for q in range(1, d+1)}
    k0 = {}
    for q in range(1, d+1):
        w = [random.random() for _ in range(q-1)]
        # sum k0(q,q') hf(q') <= hf(q), sum k0 <= 1
        tot = sum(w) if w else 1
        scale = random.uniform(0, 1)/tot if w else 0
        row = [x*scale for x in w]
        hsum = sum(row[i]*hf[i+1] for i in range(q-1))
        if hsum > hf[q]: row = [x*hf[q]/hsum*0.9 for x in row]
        for i in range(q-1): k0[(q, i+1)] = row[i]
    ker = {(q, q2): k0[(q, q2)]*hf[q2]/hf[q] for (q, q2) in k0}
    def term(kern):
        memo = {}
        def f(q):
            if q in memo: return memo[q]
            v = 1-sum(kern[(q, q2)] for q2 in range(1, q))
            v += sum(kern[(q, q2)]*y/(y+q2)*f(q2) for q2 in range(1, q))
            memo[q] = v; return v
        return f(d)
    vm = {d: 1.0}
    for q in range(d-1, 0, -1):
        vm[q] = sum(vm[q1]*k0[(q1, q)] for q1 in range(q+1, d+1))*y/(y+q)
    rhs = -sum(q/y*vm[q]*(hf[q]/hf[d]-1) for q in range(1, d))
    if abs(term(ker)-term(k0)-rhs) > 1e-10: good = False
chk("h-변환 항등식 (무작위 핵 200회)", good)
print("ALL OK" if ok else "SOME FAIL")
