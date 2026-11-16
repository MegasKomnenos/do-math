# -*- coding: utf-8 -*-
"""심사 A1 검산: G1(가중 분배 항등식), G2/G3(두 변수 닫힌 꼴, B의 EGF), R1/R2(전 차수 양성식, n=3k 항),
R4(사슬 셈의 일치), R7(질량 보존식), C6(nf 로그 계수). 정확 분수 산술(부동소수는 표시한 곳만)."""
import sys, io, itertools, random
from fractions import Fraction as Fr
from math import factorial, comb, exp, log
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
random.seed(20261117)

# ---------- 형식 멱급수 (보통 계수, 길이 N+1) ----------
def smul(a, b, N):
    c = [Fr(0)]*(N+1)
    for i, ai in enumerate(a[:N+1]):
        if ai == 0:
            continue
        for j, bj in enumerate(b[:N+1-i]):
            c[i+j] += ai*bj
    return c
def sderiv(a):
    return [(i+1)*a[i+1] for i in range(len(a)-1)] + [Fr(0)]
def sint(a, N):
    return [Fr(0)] + [a[i]/(i+1) for i in range(N)]
def sinv(a, N):
    b = [Fr(0)]*(N+1); b[0] = 1/a[0]
    for n in range(1, N+1):
        b[n] = -sum(a[i]*b[n-i] for i in range(1, n+1)) / a[0]
    return b
def sexp(a, N):
    e = [Fr(0)]*(N+1); e[0] = Fr(1)
    da = sderiv(a)
    for n in range(1, N+1):
        e[n] = sum(da[i]*e[n-1-i] for i in range(n)) / n
    return e
def slog(a, N):
    return sint(smul(sderiv(a), sinv(a, N), N), N)
def egf(seq, N):
    return [Fr(seq[n], factorial(n)) for n in range(N+1)]
def coef_n(series, n):
    return series[n]*factorial(n)

def A_table(N, L):
    A = [[Fr(0)]*(L+1) for _ in range(N+1)]
    for l in range(L+1):
        A[0][l] = Fr(1)
    for n in range(1, N+1):
        for l in range(L+1):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A
def p(n):
    return (n+1)**(n-1) if n >= 1 else 1

def capacities(sigma):
    n = len(sigma); h = []
    for i in range(n):
        z = 0
        for j in range(i-1, -1, -1):
            if sigma[j] > sigma[i]:
                z = j+1; break
        h.append(i+1-z)
    return h
def depth(par, v):
    d = 0
    while par[v-1] != 0:
        v = par[v-1]; d += 1
    return d
def forests(n):
    for par in itertools.product(range(n+1), repeat=n):
        ok = True
        for v in range(1, n+1):
            seen = {v}; u = par[v-1]
            while u != 0:
                if u in seen:
                    ok = False; break
                seen.add(u); u = par[u-1]
            if not ok:
                break
        if not ok:
            continue
        size = [1]*(n+1)
        for v in sorted(range(1, n+1), key=lambda v: -depth(par, v)):
            if par[v-1] != 0:
                size[par[v-1]] += size[v]
        yield [size[v] for v in range(1, n+1)]
def prod(xs):
    r = Fr(1)
    for x in xs:
        r *= x
    return r

print("== G1: 가중 분배 항등식 ==")
W = [Fr(random.randint(1, 9), random.randint(1, 5)) for _ in range(10)]
def Zperm(n):
    if n == 0:
        return Fr(1)
    return sum(prod([W[x-1] for x in capacities(s)]) for s in itertools.permutations(range(1, n+1)))
Zp = [Zperm(n) for n in range(8)]
for n in range(1, 6):
    Zf = sum(prod([W[t-1]/t for t in ts]) for ts in forests(n))
    print(f" n={n}: 순열합={Zp[n]} 숲합={Zf} 일치={Zp[n]==Zf}")
print(" 공통 재귀(n<=7):", all(Zp[n] == sum(comb(n-1, j)*W[j]*Zp[j]*Zp[n-1-j] for j in range(n)) for n in range(1, 8)))
N = 7
inner = [Fr(0)] + [W[t-1]*Zp[t-1]/factorial(t) for t in range(1, N+1)]
print(" EGF exp 꼴(n<=7):", all(coef_n(sexp(inner, N), n) == Zp[n] for n in range(N+1)))

print("\n== G2: 두 변수 F_{n,k}(u,z)의 닫힌 꼴 (k=2,3; n<=7) ==")
def F_bf(n, k, u, z):
    if n == 0:
        return Fr(1)
    tot = Fr(0)
    for s in itertools.permutations(range(1, n+1)):
        pr = Fr(1)
        for x in capacities(s):
            pr *= x if x < k else (u if x == k else z)
        tot += pr
    return tot
def F_closed(k, u, z, N):
    C = [Fr(0)]*(N+1)
    for j in range(0, k-1):
        if j <= N:
            C[j] += (j+1-z)*Fr(p(j), factorial(j))
    if k-1 <= N:
        C[k-1] += (u-z)*Fr(p(k-1), factorial(k-1))
    eR = sexp(sint(C, N), N); I = sint(eR, N)
    den = [Fr(1)] + [-z*I[i] for i in range(1, N+1)]
    return smul(eR, sinv(den, N), N)
A = A_table(8, 4)
for k in (2, 3):
    for (u, z) in [(Fr(7, 3), Fr(5, 2)), (Fr(k), Fr(k-1)), (Fr(k-1), Fr(k-1)), (Fr(k), Fr(k)), (Fr(k), Fr(k+1))]:
        Fc = F_closed(k, u, z, 7)
        print(f" k={k} (u,z)=({u},{z}): 닫힌 꼴 == 전수 열거(n<=7): {all(coef_n(Fc, n) == F_bf(n, k, u, z) for n in range(8))}")
    print(f" k={k}: F(k,k)=A_(n,k-1):", all(F_bf(n, k, Fr(k), Fr(k)) == A[n][k-1] for n in range(8)),
          "| F(k,k+1)=A_(n,k):", all(F_bf(n, k, Fr(k), Fr(k+1)) == A[n][k] for n in range(8)),
          "| F(k-1,k-1)=A_(n,k-2):", all(F_bf(n, k, Fr(k-1), Fr(k-1)) == A[n][k-2] for n in range(8)))

print("\n== G3: 막힘 수 B_{n,k-1}의 EGF (k=2) ==")
def B_direct(n, k):
    tot = 0
    for s in itertools.permutations(range(1, n+1)):
        small = 1; nk = 0
        for x in capacities(s):
            if x < k:
                small *= x
            elif x == k:
                nk += 1
            else:
                small *= (k-1)
        if nk:
            tot += small*(k**nk - (k-1)**nk)
    return tot
Bser = [coef_n(F_closed(2, Fr(2), Fr(1), 7), n) - coef_n(F_closed(2, Fr(1), Fr(1), 7), n) for n in range(8)]
Bdir = [B_direct(n, 2) for n in range(8)]
print(" F(2,1)-F(1,1) 계수:", Bser)
print(" 직접 셈 B_(n,1):   ", Bdir, "| 일치:", Bser == Bdir)
eR = sexp([Fr(0), Fr(0), Fr(1, 2)] + [Fr(0)]*5, 7); I = sint(eR, 7)
f4 = smul(eR, sinv([Fr(1)] + [-I[i] for i in range(1, 8)], 7), 7)
print(" F4의 식 e^{x^2/2}/(1-∫e^{t^2/2}) - 1/(1-x) 계수 일치:", [coef_n(f4, n) - factorial(n) for n in range(8)] == Bdir)

print("\n== R1/R2: 전 차수 양성식과 n=3k 항 (k=2,3) ==")
for k in (2, 3):
    N = 3*k+2
    A = A_table(N, k+1)
    Ak, Ak1, Ak2 = (egf([A[n][l] for n in range(N+1)], N) for l in (k, k-1, k-2))
    Tk, Tk1, Tk2 = slog(Ak, N), slog(Ak1, N), slog(Ak2, N)
    U = [a-b for a, b in zip(Tk, Tk1)]; V = [a-b for a, b in zip(Tk1, Tk2)]
    F, G = Ak1, Ak2
    D = [a-2*b+c for a, b, c in zip(Ak, Ak1, Ak2)]
    eU = sexp(U, N); emV = sexp([-v for v in V], N)
    O = smul(F, [eU[i]-(1 if i == 0 else 0)-U[i] + emV[i]-(1 if i == 0 else 0)+V[i] for i in range(N+1)], N)
    lin = smul(F, [a-b for a, b in zip(U, V)], N)
    print(f" k={k}: D = F(U-V)+O (n<={N}):", all(D[n] == lin[n]+O[n] for n in range(N+1)), "| O 계수 비음:", all(O[n] >= 0 for n in range(N+1)))
    Uj = [Fr(1)]+[Fr(0)]*N; Vj = [Fr(1)]+[Fr(0)]*N; S1 = [Fr(0)]*(N+1); S2 = [Fr(0)]*(N+1)
    for j in range(1, N+1):
        Uj = smul(Uj, U, N); Vj = smul(Vj, V, N)
        if j >= 2:
            S1 = [S1[i]+Uj[i]/factorial(j) for i in range(N+1)]
            S2 = [S2[i]+(j-1)*Vj[i]/factorial(j) for i in range(N+1)]
    rhs = [a+b for a, b in zip(smul(F, S1, N), smul(G, S2, N))]
    print(f"   D-F(U-V) = F·Σ_{{j>=2}}U^j/j! + G·Σ_{{j>=2}}(j-1)V^j/j!:", all(D[n]-lin[n] == rhs[n] for n in range(N+1)))
    PAIR = smul(F, [(smul(U, U, N)[i] + smul(V, V, N)[i])/2 for i in range(N+1)], N)
    print(f"   O_n = PAIR_n (n<=3k-1):", all(O[n] == PAIR[n] for n in range(3*k)))
    On, Pn = coef_n(O, 3*k), coef_n(PAIR, 3*k)
    corr = Fr(factorial(3*k), 6*factorial(k)**3)*k**(3*(k-2))
    print(f"   n=3k={3*k}: O={On}, PAIR={Pn}, 보정항={corr}, O=PAIR-보정: {On == Pn-corr}")
    def bT(t, l):
        return min(t, l+1)*A[t-1][l] - (min(t, l)*A[t-1][l-1] if l >= 1 else 0)
    ok43 = True
    for n in range(2*k+1, 3*k):
        Th = comb(n, k)*k**(k-2)*A[n-k][k-1]
        FL = sum(comb(n, t)*(bT(t, k)-bT(t, k-1))*A[n-t][k-1] for t in range(k+1, 2*k+2) if t <= n)
        BV = sum(comb(n, m+1)*p(n-1-m)*(A[m][k]-A[m][k-2]) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*(A[m][k]-2*A[m][k-1]+A[m][k-2]) for m in range(2*k+1, n))
        ok43 &= (coef_n(D, n) == -Th+FL+BV+KD+coef_n(PAIR, n))
    print(f"   정리 2.43 다섯 몫 항등식 (2k+1<=n<=3k-1):", ok43)

print("\n== R4: 사슬 셈의 일치 ==")
def Bor(m):
    return exp(-m)*m**(m-1)/factorial(m)
def Ren(j):
    return 1.0 if j == 0 else j**j*exp(-j)/factorial(j)
ok = True
for t in range(2, 14):
    for k in range(1, t):
        th = Fr(comb(t, k)*k**(k-1)*(t-k)**(t-k), t**(t-1))
        n = t-1
        ok &= (th == Fr(comb(n, k)*k**(k-1)*(n+1-k)**(n-k), p(n)))
print(" 2.37 θ_t(k) == 2.49(가) E_{t-1}[H_k(F)] (t<=13, 정확):", ok)
def W249(n, gam):
    tj = n+1-sum(gam)
    num = factorial(n)*tj**(tj-1)*gam[0]**(gam[0]-1); den = factorial(tj)*factorial(gam[0]-1)
    for g in gam[1:]:
        num *= g**g; den *= factorial(g)
    return Fr(num, den)
mx = 0.0
for n in range(3, 16):
    for j in range(1, 4):
        for gam in itertools.product(range(1, 5), repeat=j):
            if sum(gam) > n:
                continue
            tj = n+1-sum(gam)
            rhs = Bor(tj)/Bor(n+1)
            for g in gam:
                rhs *= Ren(g)
            mx = max(mx, abs(float(W249(n, gam)/p(n))-rhs)/rhs)
print(f" 2.49(다)/p_n == Bor(t_j)/Bor(n+1)·ΠRen(γ_i): 최대 상대오차 {mx:.1e}")
mx = 0.0
for n in range(5, 16):
    for b in range(1, 4):
        for u in range(0, 3):
            for os_ in itertools.product(range(0, 3), repeat=b-1):
                c = n-u-(b-1)-sum(os_)
                if c <= n/2:
                    continue
                num = factorial(n)*((u+1)**(u-1) if u else 1)*c**(c-1); den = factorial(u)*factorial(c)
                for o in os_:
                    num *= ((o+1)**(o-1) if o else 1); den *= factorial(o)
                lhs = float(Fr(num, den)/p(n))
                rhs = Bor(c)/Bor(n+1)*Bor(u+1)
                for o in os_:
                    rhs *= Bor(o+1)
                mx = max(mx, abs(lhs-rhs)/rhs)
print(f" 2.19 셈/p_n == 2.47 경로 확률 Bor(c)/Bor(n+1)·Bor(u+1)·ΠBor(o_j+1): 최대 상대오차 {mx:.1e}")

print("\n== R7: 질량 보존식 (정확) ==")
A = A_table(40, 40)
def s(m, y):
    return Fr(A[m][y-1], p(m)) if 1 <= y <= 41 else Fr(0)
def c(m, Y):
    return Fr(A[m][Y]-(A[m][Y-1] if Y >= 1 else 0), p(m))
ok = True; nonneg = True
for Y in range(1, 12):
    for K in range(Y+1, 36):
        sig = [s(m, Y+1)-s(m-1, Y) for m in range(Y+1, K+1)]
        nonneg &= all(x >= 0 for x in sig)
        ok &= (sum(c(m, Y) for m in range(Y+1, K+1)) == 1-s(K, Y)+sum(sig))
print(" Σ_{m=Y+1}^K c_m(Y) = 1-s_K(Y)+Σς_{m-1}(Y), ς_{m-1}(Y)=s_m(Y+1)-s_{m-1}(Y):", ok, "| ς>=0 (DM0):", nonneg)

print("\n== C6: nf 로그 계수 ==")
def ell(r, d):
    return Fr(1, r)*(Fr(d**(r+1), r+1) + 2*d**r - sum(u**r for u in range(d)))
print(" 2d^r/r <= ℓ_r(d) <= 5d^r/(2r) (r<=7, d<60):", all(Fr(2*d**r, r) <= ell(r, d) <= Fr(5*d**r, 2*r) for r in range(1, 8) for d in range(1, 60)))
print(" ℓ_1(d)=5d/2:", all(ell(1, d) == Fr(5*d, 2) for d in range(1, 60)), "| ℓ_2(d)=(15d^2-d)/12:", all(ell(2, d) == Fr(15*d*d-d, 12) for d in range(1, 60)))
def lognf(n, d):
    return d + sum(log(i) for i in range(n-d+1, n+1)) + (n-d-2)*log(n-d) - (n-2)*log(n)
mx = 0.0
for n in range(2, 80):
    for d in range(1, n):
        if d/n < 0.6:
            mx = max(mx, abs(lognf(n, d) - sum(float(ell(r, d))/n**r for r in range(1, 60))))
print(f" log nf = Σℓ_r n^-r (d/n<0.6, 60항까지): 최대 절대오차 {mx:.1e}")
print(" (1-d/n)^-2 <= nf <= (1-d/n)^-5/2 (n<300):", all(-2*log(1-d/n)-1e-12 <= lognf(n, d) <= -2.5*log(1-d/n)+1e-12 for n in range(2, 300) for d in range(1, n)))
print(" nf(n,a+b)=nf(n,a)·nf(n-a,b) (n<60):", all(abs(lognf(n, a+b)-lognf(n, a)-lognf(n-a, b)) < 1e-9 for n in range(3, 60) for a in range(1, n-1) for b in range(1, n-a)))
# F2의 전달행렬 계수 b_j, a_j, c_j (ε 전개)와 내 손계산 비교
def Kcoef(j, g, order=2):
    N = order
    lnf = [Fr(0)] + [ell(r, g) for r in range(1, N+1)]
    s1 = sexp(lnf, N)
    s2 = sinv([Fr(1), -Fr(g-1)] + [Fr(0)]*(N-1), N)
    s3 = [Fr(1)] + [Fr(0)]*N
    base = sinv([Fr(1), -Fr(g)] + [Fr(0)]*(N-1), N)
    for _ in range(j-2):
        s3 = smul(s3, base, N)
    return smul(smul(s1, s2, N), s3, N), base
okT = True
for j in range(2, 7):
    for g in range(1, 8):
        K, base = Kcoef(j, g)
        b = K[1]; a = smul(K, base, 2)[1]; cc = K[2]
        okT &= (b == Fr(2*j+3, 2)*g-1) and (a == Fr(2*j+5, 2)*g-1) and (cc == Fr(1, 2)*Fr(2*j+3, 2)*Fr(2*j+5, 2)*g*g - (j+Fr(31, 12))*g + 1)
print(" F2 §3.2 전달행렬 계수 b_j=(j+3/2)γ-1, a_j=(j+5/2)γ-1, c_j=½(j+3/2)(j+5/2)γ²-(j+31/12)γ+1 (j<=6, γ<=7):", okT)
