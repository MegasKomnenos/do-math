# -*- coding: utf-8 -*-
"""구조 압축 심사 X5 — R1·R2·R3·R4·R5·R7·R8의 정확 산술 검산.
python -I 로 실행. 출력은 같은 폴더의 심사_X5_재생_3k_사슬_출력.txt 로도 저장한다.
"""
from fractions import Fraction as Fr
from math import comb, factorial, lgamma, log, pi, sqrt, exp
import itertools, os, random

OUT = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.append(s)

# ---------- A_{n,l} (마지막 차 재귀, 정리 2.6) ----------
A = {}
def Acount(n, l):
    if (n, l) in A: return A[(n, l)]
    if n == 0: v = 1
    else:
        v = sum(comb(n-1, t-1)*min(t, l+1)*Acount(t-1, l)*Acount(n-t, l) for t in range(1, n+1))
    A[(n, l)] = v; return v
def p(n): return (n+1)**(n-1) if n >= 1 else 1

# ---------- 형식적 멱급수(x^n 계수, Fraction) ----------
def series_from_egf(coefs, N):
    return [Fr(coefs[n], factorial(n)) if n < len(coefs) else Fr(0) for n in range(N+1)]
def mul(a, b, N):
    c = [Fr(0)]*(N+1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(N+1-i):
            if b[j]: c[i+j] += ai*b[j]
    return c
def add(a, b): return [x+y for x, y in zip(a, b)]
def scal(a, s): return [x*s for x in a]
def powS(a, j, N):
    r = [Fr(1)]+[Fr(0)]*N
    for _ in range(j): r = mul(r, a, N)
    return r
def expS(a, N):
    r = [Fr(1)]+[Fr(0)]*N; term = r[:]
    for j in range(1, N+1):
        term = scal(mul(term, a, N), Fr(1, j)); r = add(r, term)
    return r
def egf(s, n): return s[n]*factorial(n)
def one(N): return [Fr(1)]+[Fr(0)]*N

def check_R1_R2_R3(k, N):
    say(f"=== k={k}, n<= {N} ===")
    Ak  = series_from_egf([Acount(n, k)   for n in range(N+1)], N)
    Ak1 = series_from_egf([Acount(n, k-1) for n in range(N+1)], N)
    Ak2 = series_from_egf([Acount(n, k-2) for n in range(N+1)], N)
    def T(l): return series_from_egf([0]+[min(t, l+1)*Acount(t-1, l) for t in range(1, N+1)], N)
    for l, S in ((k, Ak), (k-1, Ak1), (k-2, Ak2)):
        assert expS(T(l), N) == S, "exp(T_l) != A_l"
    F, G = Ak1, Ak2
    U = add(T(k), scal(T(k-1), -1)); V = add(T(k-1), scal(T(k-2), -1))
    assert mul(F, expS(U, N), N) == Ak and mul(F, expS(scal(V, -1), N), N) == Ak2
    D = add(add(Ak, scal(Ak1, -2)), Ak2)
    # (i) 전 차수 양성식
    S1 = [Fr(0)]*(N+1)
    for j in range(1, N+1):
        S1 = add(S1, scal(add(powS(U, j, N), scal(powS(V, j, N), (-1)**j)), Fr(1, factorial(j))))
    assert mul(F, S1, N) == D; say("(R1) D = F*sum_j (U^j+(-1)^j V^j)/j!  : 확인")
    # (v) 비음 나머지
    R = add(D, scal(mul(F, add(U, scal(V, -1)), N), -1))
    S2 = [Fr(0)]*(N+1); S3 = [Fr(0)]*(N+1)
    for j in range(2, N+1):
        S2 = add(S2, scal(powS(U, j, N), Fr(1, factorial(j))))
        S3 = add(S3, scal(powS(V, j, N), Fr(j-1, factorial(j))))
    assert R == add(mul(F, S2, N), mul(G, S3, N)); say("(R1) D-F(U-V) = F sum_{j>=2} U^j/j! + G sum_{j>=2} (j-1)V^j/j! : 확인")
    assert all(x >= 0 for x in R); say("(R1) 교차항 O_n >= 0 (모든 n<=N) : 확인")
    O2 = add(mul(F, add(add(expS(U, N), scal(one(N), -1)), scal(U, -1)), N),
             mul(G, add(add(one(N), scal(expS(V, N), -1)), mul(V, expS(V, N), N)), N))
    assert O2 == R; say("(R1) 9.25(나) 꼴 F(e^U-1-U)+G(1-e^V+Ve^V) = 위 나머지 : 확인")
    # (ii) O_n = PAIR_n (n<=3k-1), 3k 경계
    PAIR = scal(mul(F, add(powS(U, 2, N), powS(V, 2, N)), N), Fr(1, 2))
    for n in range(0, 3*k):
        assert egf(R, n) == egf(PAIR, n)
    say(f"(R1) O_n = PAIR_n for 0<=n<=3k-1={3*k-1} : 확인")
    n = 3*k
    corr = Fr(factorial(3*k)*k**(3*(k-2)), 6*factorial(k)**3)
    say(f"(R2) n=3k={n}: O={egf(R,n)}  PAIR={egf(PAIR,n)}  (3k)!k^(3k-6)/(6 k!^3)={corr}  PAIR-corr={egf(PAIR,n)-corr}")
    assert egf(R, n) == egf(PAIR, n) - corr; say("(R2) O_{3k} = PAIR_{3k} - (3k)! k^{3(k-2)}/(6(k!)^3) : 확인")
    if N >= 3*k+1:
        n = 3*k+1
        say(f"(R2) n=3k+1: O-PAIR = {egf(R,n)-egf(PAIR,n)}  (= -(3k+1)![x^(3k+1)] F V^3/6 )")
        FV3 = scal(mul(F, powS(V, 3, N), N), Fr(-1, 6))
        say(f"      -(3k+1)![x^(3k+1)]FV^3/6 = {egf(FV3,n)}")
    # (iii) 9.25(가)(다)
    def delta(t):
        return min(t, k+1)*Acount(t-1, k) - 2*min(t, k)*Acount(t-1, k-1) + min(t, k-1)*Acount(t-1, k-2) if t >= 1 else 0
    def d(n): return Acount(n, k)-2*Acount(n, k-1)+Acount(n, k-2)
    def b2(m): return Acount(m, k)-Acount(m, k-2)
    for t in range(k+2, N+1): assert delta(t) == k*d(t-1)+b2(t-1)
    assert delta(k+1) == -(k-1)*k**(k-2) and delta(k) == -k**(k-2); say("(R3) 9.25(가) : 확인")
    ok_all, first_fail_26 = True, None
    for n in range(2*k+1, N+1):
        On = egf(R, n)
        Theta = comb(n, k)*k**(k-2)*Acount(n-k, k-1)
        FL = sum(comb(n, t)*delta(t)*Acount(n-t, k-1) for t in range(k+1, min(2*k+1, n)+1))
        Kr = sum(k*comb(n, m+1)*Acount(n-m-1, k-1)*d(m) for m in range(2*k+1, n))
        BVa = sum(comb(n, t)*Acount(n-t, k-1)*b2(t-1) for t in range(2*k+2, n+1))
        if d(n) != On - Theta + FL + Kr + BVa: ok_all = False
        BV = sum(comb(n, m+1)*p(n-1-m)*b2(m) for m in range(2*k+1, n))
        regen = d(n) - Kr
        if regen != FL - Theta + BV + On and first_fail_26 is None: first_fail_26 = n
    say(f"(R3) 9.25(다) 항등식, 2k+1<=n<={N} (상한 3k-1 없이) : {'확인' if ok_all else '실패'}")
    say(f"(R3) 9.26 첫 등식(BV에 p_(n-1-m) 치환)의 첫 실패 n = {first_fail_26} (F1 예상: 3k+2까지 성립, 3k+3={3*k+3}에서 실패)")
    # (vi) 9.21 흡수, 포함배제
    FV = mul(F, V, N); FV2 = scal(mul(F, powS(V, 2, N), N), Fr(1, 2))
    for m in range(2*k+1, 3*k):
        assert egf(FV, m) == (Acount(m, k-1)-Acount(m, k-2)) + egf(FV2, m)
    say("(R1) 9.21: V_m = b_{m,k-1} + Pcor^-_m (2k+1<=m<=3k-1) : 확인")
    IE = [Fr(0)]*(N+1)
    for j in range(1, N+1): IE = add(IE, scal(mul(F, powS(V, j, N), N), Fr((-1)**(j+1), factorial(j))))
    assert IE == add(Ak1, scal(Ak2, -1)) == mul(G, add(expS(V, N), scal(one(N), -1)), N)
    say("(R1) b_{.,k-1} egf = F sum_j (-1)^{j+1}V^j/j! = G(e^V-1) (양의 꼴) : 확인")

for k, N in ((2, 12), (3, 14), (4, 17), (5, 20)):
    check_R1_R2_R3(k, N)

# ---------- R4 ----------
say("\n=== R4: 2.49(다) 닫힌 수 / p_n  ==  Bor(t_j)/Bor(n+1) * prod Ren(gamma_i)  (e 지수 소거 후 정확 유리수) ===")
def BorT(m): return Fr(m**(m-1), factorial(m))
def RenT(j): return Fr(j**j, factorial(j))
def W_closed(n, gam):
    tj = n+1-sum(gam)
    num = factorial(n)*tj**(tj-1)*gam[0]**(gam[0]-1)
    den = factorial(tj)*factorial(gam[0]-1)
    for g in gam[1:]:
        num *= g**g; den *= factorial(g)
    return Fr(num, den)
bad = 0; tot = 0
for n in range(1, 13):
    for j in range(1, 5):
        for gam in itertools.product(range(1, n+1), repeat=j):
            if sum(gam) > n: continue
            tj = n+1-sum(gam); tot += 1
            lhs = W_closed(n, gam)/p(n)
            rhs = BorT(tj)/BorT(n+1)
            for g in gam: rhs *= RenT(g)
            if lhs != rhs: bad += 1
say(f"(R4) 대조 {tot}건, 어긋남 {bad}건 (n<=12, j<=4)")
# 뿌리 붙임 변형: 첫 인자 Ren(gamma_1) -> Bor(gamma_1) 이면 가장 큰 나무 핵 pi_n(t) = Bor(t)Bor(n+1-t)/Bor(n+1)
bad = 0
for n in range(1, 30):
    for t in range(1, n+1):
        lhs = Fr(comb(n, t)*t**(t-1)*p(n-t), p(n))
        rhs = BorT(t)*BorT(n+1-t)/BorT(n+1)
        if lhs != rhs: bad += 1
say(f"(R4) 뿌리 변형 j=1: pi_n(t) = Bor(t)Bor(n+1-t)/Bor(n+1), 어긋남 {bad}건 (n<30)")
# 2.18 사슬 구성 수 / p_n = Bor(u+1) prod Bor(o_j+1) Bor(c)/Bor(n+1)  (모두 D 변형)
bad = 0
for n in range(2, 12):
    for b in range(1, 4):
        for parts in itertools.product(range(0, n), repeat=b):
            u, os_ = parts[0], parts[1:]
            c = n - u - (b-1) - sum(os_)
            if c <= n/2 or c < 1: continue
            num = factorial(n)*(u+1)**(u-1 if u >= 1 else 0)*c**(c-1)
            den = factorial(u)*factorial(c)
            for o in os_:
                num *= (o+1)**(o-1) if o >= 1 else 1; den *= factorial(o)
            lhs = Fr(num, den)/p(n)
            rhs = BorT(u+1)*BorT(c)/BorT(n+1)
            for o in os_: rhs *= BorT(o+1)
            if lhs != rhs: bad += 1
say(f"(R4) 2.18 사슬 구성 확률 = Bor(u+1) prod Bor(o_j+1) Bor(c)/Bor(n+1), 어긋남 {bad}건")
# 브루트포스: 숲 전수(Prüfer)로 2.49(다) j=1,2 검증
def prufer_to_tree(seq, m):
    deg = [1]*m
    for s in seq: deg[s] += 1
    edges = []
    for s in seq:
        for leaf in range(m):
            if deg[leaf] == 1:
                edges.append((leaf, s)); deg[leaf] -= 1; deg[s] -= 1; break
    u = [i for i in range(m) if deg[i] == 1]; edges.append((u[0], u[1]))
    return edges
def forest_counts(n):
    m = n+1; cnt = {}
    seqs = itertools.product(range(m), repeat=m-2) if m >= 3 else [()]
    for seq in seqs:
        edges = prufer_to_tree(seq, m) if m >= 3 else [(0, 1)]
        adj = [[] for _ in range(m)]
        for a, b in edges: adj[a].append(b); adj[b].append(a)
        par = [-1]*m; order = []; st = [0]; seen = [False]*m; seen[0] = True
        while st:
            v = st.pop(); order.append(v)
            for w in adj[v]:
                if not seen[w]: seen[w] = True; par[w] = v; st.append(w)
        size = [1]*m
        for v in reversed(order):
            if par[v] >= 0: size[par[v]] += size[v]
        anc = [set() for _ in range(m)]
        for v in order[1:]:
            anc[v] = anc[par[v]] | {par[v]}
        for v in range(1, m):
            key = (size[v],); cnt[key] = cnt.get(key, 0)+1
            for u in range(1, m):
                if v in anc[u]:
                    key = (size[v], size[u]); cnt[key] = cnt.get(key, 0)+1
    return cnt
for n in (4, 5, 6):
    cnt = forest_counts(n); bad = 0; tot = 0
    for key, c in cnt.items():
        gam = (n+1-key[0],) if len(key) == 1 else (n+1-key[0], key[0]-key[1])
        tot += 1
        if W_closed(n, gam) != c: bad += 1
    say(f"(R4) n={n}: 숲 전수({(n+1)**(n-1)}개)로 2.49(다) j=1,2 대조 — 키 {tot}개, 어긋남 {bad}")

# ---------- R5 ----------
say("\n=== R5 ===")
def caps2(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and sig[j] < sig[i]: j -= 1
        h.append(i-j)
    return h
for n in range(2, 8):
    for k in range(2, n+1):
        Kink = Fr(0); Jk = Fr(0)
        for sig in itertools.permutations(range(1, n+1)):
            h = caps2(sig)
            Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            Ak1s = 1
            for x in h: Ak1s *= min(x, k)
            Kink += Fr(Ak1s*H, k)
            pr = 1
            for x in h:
                if x < k: pr *= x
            Jk += H*k**(H-1)*k**Z*pr if H >= 1 else 0
        assert Kink == Jk
    for l in range(0, n):
        s = 0
        for sig in itertools.permutations(range(1, n+1)):
            pr = 1
            for x in caps2(sig): pr *= min(x, l+1)
            s += pr
        assert s == Acount(n, l)
say("(R5) Kink_{n,k} = sum_sigma A^sigma_{k-1} H_k/k = J_n(k) (n<=7, 모든 k) : 확인;  따름정리 2.4 전수 확인")
random.seed(1)
for _ in range(2000):
    y = random.randint(3, 30); z = random.randint(0, 6); H = random.randint(0, 1)
    S = sorted(random.sample(range(y+1, y+40), z), reverse=True)
    if H: S = S+[y]
    def Pi(Y):
        r = Fr(1)
        for s_ in S:
            if s_ > Y: r *= Fr(Y, s_)
        return r
    lhs = Pi(y+1)-2*Pi(y)+Pi(y-1)
    v = (Fr(y+1, y))**z + (Fr(y-1, y))**(z+H) - 2
    assert lhs == Pi(y)*v
    prodS = 1
    for s_ in S[:z]: prodS *= s_
    rhs544 = Fr((y+1)**z-2*y**z+(y-1)**z, prodS) - (Fr((y-1)**z, y*prodS) if H else 0)
    assert lhs == rhs544
say("(R5) 5.44의 식 = Pi(y)*v_y(z,H) (2.15의 특수화) : 무작위 2000건 확인")

# ---------- R7 ----------
say("\n=== R7 ===")
def s(m, y): return Fr(Acount(m, y-1), p(m))
def c(m, Y): return s(m, Y+1)-s(m, Y)
def vs(m, l): return s(m+1, l+1)-s(m, l)
bad = 0
for Y in range(1, 9):
    for K in range(Y+1, 2*Y+6):
        lhs = sum(c(m, Y) for m in range(Y+1, K+1))
        rhs = 1 - s(K, Y) + sum(vs(m-1, Y) for m in range(Y+1, K+1))
        rhs2 = s(Y+1, Y+1) - s(K+1, Y+1) + sum(vs(m, Y) for m in range(Y+1, K+1))
        if lhs != rhs or lhs != rhs2: bad += 1
        assert all(vs(m, Y) >= 0 for m in range(Y, K+1))
say(f"(R7) sum c_m(Y) = 1 - s_K(Y) + sum varsigma_(m-1)(Y)  와 10.4 꼴, 어긋남 {bad}건; varsigma>=0 확인")

# ---------- R8 ----------
say("\n=== R8 ===")
z12, z32 = -1.4603545088, 2.6123753487
cPsi = -z12 + z32/12
say(f"(R8) c_Psi = -z_1/2 + z_3/2/12 = {cPsi:.6f}  (9.43의 1.678, 8.6(라)의 c_Psi)")
def Ren(j): return exp(j*log(j)-j-lgamma(j+1))
def Psi(d): return sum(Ren(j) for j in range(1, d+1))
def lb98(d): return 0.7978*sqrt(d)-0.8848
def lb943(d): return 0.3989*(2*sqrt(d)-1.678)
def lb86(d): return (2*pi)**-0.5*(2*sqrt(d)-cPsi+0.5/sqrt(d)-d**-1.5/24)
order_ok = all(lb98(d) <= lb943(d) <= lb86(d) <= Psi(d) for d in range(1, 20001))
say(f"(R8) 9.8 <= 9.43 <= 8.6(라) <= Psi(d), d<=20000 : {order_ok}")
say(f"(R8) d=100: Psi={Psi(100):.5f} 9.8={lb98(100):.5f} 9.43={lb943(100):.5f} 8.6라={lb86(100):.5f}")
def rb(m): return lgamma(m+1)-(m+0.5)*log(m)+m-0.5*log(2*pi)
mono = all(rb(m) > rb(m+1) for m in range(1, 3000))
say(f"(R8) Robbins 나머지 rb_m 감소(m<3000 수치; 일반은 rb_m>1/(12m+1)>1/(12m+12)>rb_(m+1)로 해석적) : {mono}  -> Bor(a)/Bor(b) <= (b/a)^(3/2) (a<b); 9.7의 e^(1/(12(m-d+1))) 인자 불필요")
def logBor(m): return (m-1)*log(m)-m-lgamma(m+1)
worst = max(logBor(m-i)-logBor(m+1)-1.5*log((m+1)/(m-i)) for m in (50, 500, 5000, 50000) for i in range(0, m//2))
say(f"(R8) max[log(Bor(m-i)/Bor(m+1)) - 3/2 log((m+1)/(m-i))] = {worst:.3e} (<=0 이면 2.40(iv)꼴 성립)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "심사_X5_재생_3k_사슬_출력.txt")
with open(out, "w", encoding="utf-8") as f: f.write("\n".join(OUT)+"\n")
say("saved:", out)
