# 심사 A3 — C5·C6·C7 검산 (정확 분수 / 절단 멱급수)
from fractions import Fraction as Fr
import math
N = 14  # 절단 차수

def trunc_mul(a, b):
    c = [Fr(0)]*N
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(N-i):
            c[i+j] += ai*b[j]
    return c
def deriv(a): return [ (i+1)*a[i+1] for i in range(N-1)] + [Fr(0)]
def zmul(a): return [Fr(0)] + a[:N-1]
def add(*xs): return [sum(t) for t in zip(*xs)]
def scal(c, a): return [c*x for x in a]
def inv_1mz(): return [Fr(1)]*N          # 1/(1-z)
def Ren(m): return Fr(m**m, math.factorial(m)) / Fr(math.e**0)  # placeholder, replaced below
# Ren(m)=m^m e^{-m}/m! 는 무리수이므로, 검산에서는 임의의 양의 유리 계수 급수 C로 (다)의 '순서 보존' 주장을 시험한다.
import random
random.seed(3)
def rand_series(const0):
    return [Fr(const0)] + [Fr(random.randint(1,9), random.randint(1,9)) for _ in range(N-1)]

def Y1(C):   # 5:marked-recursion (나) 초기식  Y_1 = (5/2) z (zC' - C)
    return scal(Fr(5,2), zmul(add(zmul(deriv(C)), scal(-1, C))))
def Zj(C, j):  # Z^{(2)}_j 재귀: Z_1 = zC,  Z_j = C z (Z_{j-1}' + 2 Z_{j-1}/(1-z))
    Z = zmul(C)
    for _ in range(2, j+1):
        Z = trunc_mul(C, zmul(add(deriv(Z), scal(2, trunc_mul(Z, inv_1mz())))))
    return Z
def Yj(C, j):
    Y = Y1(C); Z = zmul(C)
    for jj in range(2, j+1):
        A = add(zmul(deriv(C)) , scal(-1,C))                      # zC' - C  ... (j+3/2) z C' - C :
        A = add(scal(Fr(2*jj+3,2), zmul(deriv(C))), scal(-1, C))
        Y = add(trunc_mul(C, zmul(add(deriv(Y), scal(2, trunc_mul(Y, inv_1mz()))))),
                trunc_mul(A, zmul(add(deriv(Z), scal(2, trunc_mul(Z, inv_1mz()))))))
        Z = trunc_mul(C, zmul(add(deriv(Z), scal(2, trunc_mul(Z, inv_1mz())))))
    return Y

print("== C7: 5.28(다) 반례 — C_+ = C + a (상수항 a>0)")
C = rand_series(0)
a = Fr(1,3)
Cp = [C[0]+a] + C[1:]
d = add(Y1(Cp), scal(-1, Y1(C)))
print("   Y_1[C+a]-Y_1[C] =", [str(x) for x in d[:4]], " (예상: [0, -5a/2, 0, ...], -5a/2 =", -Fr(5,2)*a, ")")
assert d[1] == -Fr(5,2)*a and all(x == 0 for x in d[2:]) and d[0] == 0
# 상수항 0인 C_+ ⪰ C 에서는 순서 보존이 성립하는가 (j<=4, 무작위 20벌)
ok = True
for trial in range(20):
    C = rand_series(0)
    Cp = [Fr(0)] + [C[i] + Fr(random.randint(0,5), 7) for i in range(1, N)]
    for j in range(1, 5):
        for f in (Zj, Yj):
            A, B = f(C, j), f(Cp, j)
            if any(B[i] < A[i] for i in range(N)): ok = False
            if any(x < 0 for x in A): ok = False
print("   상수항 0인 C_+⪰C (무작위 20벌, j<=4): Z, Y 모두 계수별 상계 성립 =", ok)
# 상수항 있는 C_+에서 Y_j (j=2,3)도 실패하는가
C = rand_series(0); Cp = [Fr(1,5)] + C[1:]
bad = [j for j in range(1,4) if any(Yj(Cp,j)[i] < Yj(C,j)[i] for i in range(N))]
print("   상수항 1/5인 C_+에서 Y_j 상계가 깨지는 j:", bad)
# 실제 쓰는 C_-, C_+, (K1)의 상수항: w=sqrt(1-z) -> z=0에서 w=1
for name, val in [("C_-: o(w^-1 - 1)", 1-1), ("C_+: o(w^-1 - 11/12 - w/12)", Fr(1)-Fr(11,12)-Fr(1,12)), ("(K1): o(w^-1 - 24/25 - w/25)", Fr(1)-Fr(24,25)-Fr(1,25))]:
    print("   ", name, "상수항 =", val)

print("== C6: nf 로그 계수 lc_i(d) 의 상하계 2d^i/i <= lc_i <= 5d^i/(2i), 곱셈 항등식, 전달행렬 계수")
def lc(i, d): return Fr(1,i)*(Fr(d**(i+1), i+1) + 2*d**i - sum(Fr(u**i) for u in range(d)))
for d in range(0, 40):
    for i in range(1, 8):
        v = lc(i,d)
        assert Fr(2*d**i, i) <= v <= Fr(5*d**i, 2*i), (i,d,v)
print("   lc_i(d) 상하계: d<40, i<8 전부 성립 (원문의 하계 0보다 강한 2d^i/i 성립)")
def nf(n, d): return Fr(math.e**0)  # placeholder
# nf(n,d) = e^d n!/(n-d)! (n-d)^{n-d-2}/n^{n-2}: e^d 는 공통이므로 e^{-d} nf 로 정확 분수 비교
def nf_rat(n, d): return Fr(math.factorial(n), math.factorial(n-d)) * Fr((n-d)**(n-d-2) if n-d>=2 else 1, 1) / Fr(n**(n-2)) if n-d>=2 else None
okm = True
for n in range(6, 30):
    for a_ in range(0, n-4):
        for b_ in range(0, n-a_-3):
            L = nf_rat(n, a_+b_); R = nf_rat(n, a_)*nf_rat(n-a_, b_)
            if L is None or R is None: continue
            if L != R: okm = False
print("   nf(n,a+b) = nf(n,a) nf(n-a,b) (e^d 인자 제외, n<30 전수):", okm)
# 전달행렬 계수: K_{j,γ}(ε) = exp(Σ lc_i(γ) ε^i) (1-(γ-1)ε)^{-1} (1-γε)^{-(j-2)};  [ε]K = b_j, [ε^2]K = c_j, [ε](K(1-γε)^{-1}) = a_j
def series_exp(a):  # exp of series with a[0]=0
    out = [Fr(0)]*N; out[0] = Fr(1)
    term = [Fr(1)] + [Fr(0)]*(N-1)
    for m in range(1, N):
        term = scal(Fr(1,m), trunc_mul(term, a))
        out = add(out, term)
    return out
def geom(c, p):  # (1 - c ε)^{-p}
    out = [Fr(1)] + [Fr(0)]*(N-1)
    g = [Fr(c)**i for i in range(N)]
    for _ in range(p): out = trunc_mul(out, g)
    return out
okT = True
for j in range(2, 7):
    for g in range(1, 9):
        logK = [Fr(0)] + [lc(i, g) for i in range(1, N)]
        K = trunc_mul(trunc_mul(series_exp(logK), geom(g-1, 1)), geom(g, j-2))
        b = Fr(2*j+3, 2)*g - 1
        a = Fr(2*j+5, 2)*g - 1
        c = Fr(1,2)*Fr(2*j+3,2)*Fr(2*j+5,2)*g*g - (j + Fr(31,12))*g + 1
        Ka = trunc_mul(K, geom(g, 1))
        if not (K[1] == b and K[2] == c and Ka[1] == a): okT = False
        if any(x < 0 for x in K): okT = False
print("   전달행렬 0·1·2차 계수 = (j+3/2)γ-1, (j+5/2)γ-1, c_j(γ)  (j<7, γ<9):", okT, " / K의 계수 모두 비음")
# j=1 초기값: [ε^2] nf(ε^{-1}, γ-1) = 35/8 (γ-1)^2 - (γ-1)/12
ok1 = all(series_exp([Fr(0)]+[lc(i, g-1) for i in range(1,N)])[2] == Fr(35,8)*(g-1)**2 - Fr(g-1,12) for g in range(1,12))
print("   j=1: [ε^2] nf = 35/8(γ-1)^2-(γ-1)/12 :", ok1)

print("== C5: Rm_j(r/n) <= er_j((r+3)/n) 와 F2 §3.5의 사슬 (EI 범위 r>=529, rq_*<1/12)")
import math
def Rm(j, q): a = j+1.5; return (1-q)**(-a) - 1 - a*q
def er(j, q): return q*q/2*((j+1.5)**2/(1-q)**2*math.exp((j+1.5)*q/(1-q)) + (j+4)/(1-q))
def mid(j, Q): a=j+1.5; return Q*Q/2*(a*a/(1-Q)**2*math.exp(a*Q/(1-Q)) + a/(1-Q))
worst = 1.0
for r in [529, 600, 1000, 5000, 10**5]:
    for x32 in [0.64, 0.645, 0.65]:
        n = r**1.5/x32
        q, Q = r/n, (r+3)/n
        for j in range(1, 13):
            assert Rm(j,q) <= Rm(j,Q) <= mid(j,Q) <= er(j,Q), (r,x32,j)
            worst = min(worst, Rm(j,q)/er(j,Q))
print("   모든 표본에서 Rm_j(q) <= Rm_j(Q) <= [F2 중간식] <= er_j(Q);  Rm_j(q)/er_j(Q) 최소 =", round(worst,4))
# 일반 Q<1/2에서도 (1-Q)^{-a}-1-aQ <= Q^2/2[a^2/(1-Q)^2 e^{aQ/(1-Q)} + a/(1-Q)] ?
okg = all(Rm(j,Q) <= mid(j,Q)*(1+1e-12) for j in range(1,30) for Q in [i/1000 for i in range(1,500)])
print("   Q<1/2, j<30 격자에서 Rm_j(Q) <= F2 중간식:", okg)
