# 검토전체23 R8: 장8의 항등식·부등식을 작은 k에서 정확한 유리수로 대조한다.
# A_{n,l}: 최대 변위 <= l 인 길이 n 주차함수의 수 (2장의 재귀: 마지막 차의 자리 t').
from fractions import Fraction as F
from math import comb, exp, factorial
import sys

KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
NMAX = 3*KMAX + 2
LMAX = KMAX + 2

A = {}
for l in range(-1, LMAX+1):
    A[(0, l)] = 1
    for n in range(1, NMAX+1):
        if l < 0:
            A[(n, l)] = 0
            continue
        A[(n, l)] = sum(comb(n-1, t-1)*min(t, l+1)*A[(t-1, l)]*A[(n-t, l)] for t in range(1, n+1))


def p(n):
    return F(n+1)**(n-1) if n >= 1 else F(1)


for n in range(0, LMAX+2):
    assert A[(n, max(n-1, 0))] == p(n), n


def s(m, y):   # 생존 확률 Pr_m(M <= y-1)
    return F(A[(m, y-1)]) / p(m)


def c(m, y):   # 수준 질량 Pr_m(M = y)
    return s(m, y+1) - s(m, y)


def Bor(m):
    return F(m)**(m-1) / factorial(m)   # e^{-m} 인자는 비에서 지워지므로 뺀다(동차 차수 맞는 식에서만 씀)


def pi(n, m):  # 크기 m 나무 수의 기댓값
    return F(comb(n, m)) * F(m)**(m-1) * p(n-m) / p(n)


def pi0(n, y):  # 모든 나무 크기 <= y (n <= 2y+1 에서만)
    assert n <= 2*y+1
    return 1 - sum(pi(n, m) for m in range(y+1, n+1))


def sT(t, y):
    return F(min(t, y), t) * s(t-1, y)


bad = 0


def chk(cond, msg):
    global bad
    if not cond:
        bad += 1
        print('FAIL', msg)


for k in range(2, KMAX+1):
    # (8.1)
    for n in range(2*k+1, 3*k+1):
        N = n-k
        Theta = F(comb(n, k)) * F(k)**(k-2) * A[(N, k-1)]
        BV = sum(F(comb(n, m+1)) * p(n-1-m) * (A[(m, k)] - A[(m, k-2)]) for m in range(2*k+1, n))
        chk(Theta/p(n) == pi(n, k)*s(N, k)/k, ('8.1 Theta', k, n))
        chk(BV/p(n) == sum(pi(n, m+1)/(m+1)*(c(m, k)+c(m, k-1)) for m in range(2*k+1, n)), ('8.1 BV', k, n))
    # (8.2) 두 수준
    for m in range(k+1, 2*k+2):
        chk(c(m, k) == sum(pi(m, t)/t*(s(t-1, k+1)+k*c(t-1, k)) for t in range(k+1, m+1)), ('8.2', k, m))
    for m in range(k, 2*k):
        chk(c(m, k-1) == sum(pi(m, t)/t*(s(t-1, k)+(k-1)*c(t-1, k-1)) for t in range(k, m+1)), ('8.2 level k-1', k, m))
    # (8.2)가 범위 밖에서 깨지는지(등식이 아님)와 보조정리 old-6-23
    for m in range(2*k+2, 3*k+2):
        rhs = sum(pi(m, t)/t*s(m-t, k)*(s(t-1, k+1)+k*c(t-1, k)) for t in range(k+1, m+1))
        chk(c(m, k) >= rhs, ('old-6-23', k, m))
    for m in range(2*k, 3*k+1):
        rhs = sum(pi(m, t)/t*s(m-t, k-1)*(s(t-1, k)+(k-1)*c(t-1, k-1)) for t in range(k, m+1))
        chk(c(m, k-1) >= rhs, ('old-6-23 level k-1', k, m))
    # 정리 escape-lower (y=k, k+1 <= N <= 2k+1)
    for N in range(k+1, 2*k+2):
        km = sum(pi(N, m)*F(k, m) for m in range(k+1, N+1))
        p0 = pi0(N, k)
        chk(s(N, k) == p0 + sum(pi(N, m)*F(k, m)*s(m-1, k) for m in range(k+1, N+1)), ('heavy path rec', k, N))
        chk(s(N, k) >= p0/(1-km) >= p0/(1-F(k, N)+F(k, N)*p0), ('escape-lower', k, N))
    # 보조정리 old-6-30
    for N in range(k, 2*k):
        ratio = s(N, k-1)/s(N, k)
        ga = 1 - max(1/(k*pi0(Np, k-1)) for Np in range(k, N+1))
        chk(ratio >= ga, ('old-6-30 (ga)', k, N))
        chk(ratio >= (1-F(1, k))**(N-k+1), ('capacity-shift', k, N))
        if N <= 2*k-2:
            # (나)의 pi0 하계: 4(2pi)^{-1/2} e^{-7/6} (2k-1-N) N^{-3/2}
            low = 4*(2*3.141592653589793)**-0.5*exp(-7/6)*(2*k-1-N)*N**-1.5
            chk(float(pi0(N, k-1)) >= low, ('old-6-30 (na) pi0', k, N))
    # 보조정리 old-6-31 (가)(나)(다)
    for m in range(2, 3*k+1):
        for t in range(1, m):
            if 2*t >= m:
                chk(pi(m, t+1) >= pi(m, t), ('old-6-31 (ga)', m, t))
        for t in range(1, m+1):
            chk(pi(m+1, t) <= pi(m, t), ('old-6-31 (na)', m, t))
            chk(pi(m, t) == pi(m, m+1-t), ('pi symmetry', m, t))
    for N in range(2, 2*k+1):
        for j in range(N//2+1, N+1):
            # pi0_N(j) - pi0_{N+1}(j) <= pi_N(j);  N/2 < j <= N
            a = 1 - sum(pi(N, i) for i in range(j+1, N+1))
            b = 1 - sum(pi(N+1, i) for i in range(j+1, N+2))
            chk(a - b <= pi(N, j), ('old-6-31 (da)', N, j))
    # 보조정리 old-6-32 와 eps_cap 의 꼴
    for t in range(k+1, 2*k+2):
        ecap = sT(t, k+1) - sT(t, k)
        esize = sT(t, k) - sT(t+1, k)
        chk(ecap == (s(t-1, k+1)+k*c(t-1, k))/t, ('eps_cap form', k, t))
        chk(ecap >= esize/2, ('old-6-32', k, t))
        chk(esize >= 0, ('eps_size>=0', k, t))
    # s_N(k) = E[s^T_G(k)] (N <= 2k+1)
    for N in range(1, 2*k+2):
        # G = 가장 큰 나무; N<=2k+1 이면 크기 >k 인 나무는 많아야 하나
        val = pi0(N, k) + sum(pi(N, j)*sT(j, k) for j in range(k+1, N+1)) if N >= k+1 else F(1)
        chk(s(N, k) == val, ('s=E sT', k, N))
    # (8.5): R_q >= k/(k+q) sum Bor(j)[s_{k+q-j}(k+1)+R_{q-j}]  (Borel 질량은 e^{-j} 포함해야 하므로 float)
    import math
    def BorF(m):
        return math.exp(-m)*m**(m-1)/math.factorial(m)
    R = [0.0]+[k*float(c(k+q, k)) for q in range(1, k+2)]
    Psi = [0.0]
    for q in range(1, k+2):
        Psi.append(Psi[-1]+q*BorF(q))
    for q in range(1, k+2):
        rhs = k/(k+q)*sum(BorF(j)*(float(s(k+q-j, k+1))+R[q-j]) for j in range(1, q+1))
        chk(R[q] >= rhs-1e-13, ('8.5', k, q))
        # (8.6) with s_low = exact
        D = [Psi[i]-R[i] for i in range(q+1)]
        src = q/(k+q)*Psi[q]+k/(k+q)*sum(BorF(j)*(1-float(s(k+q-j, k+1))) for j in range(1, q+1))
        chk(D[q] <= src+k/(k+q)*sum(BorF(j)*D[q-j] for j in range(1, q))+1e-13, ('8.6', k, q))
    # 보조정리 envelope-H 첫 주장: s_{k+q}(k+1) >= exp(-J(q,k))
    kk = k+1
    for q in range(1, k+4):
        if k+q > NMAX:
            break
        J = sum((q-r)*r*BorF(r)*BorF(kk+q-r)/BorF(kk+q) for r in range(1, q))/kk
        chk(float(s(k+q, k+1)) >= math.exp(-J)-1e-13, ('Jensen', k, q))
        # 정리 escape-lower 를 y=k+1, N=k+q 에 (2<=q<=k+3)
        if 2 <= q <= k+3 and k+q <= 2*(k+1)+1:
            N = k+q
            p0 = 1 - sum(pi(N, m) for m in range(kk+1, N+1))
            km = sum(pi(N, m)*F(kk, m) for m in range(kk+1, N+1))
            chk(s(N, kk) >= p0/(1-km), ('escape at k+1', k, q))
    # 수준 방문 보존 (가): sum_{m=k+1}^K c_m(k) >= 1 - s_K(k)
    for K in range(k+1, 2*k+2):
        chk(sum(c(m, k) for m in range(k+1, K+1)) >= 1-s(K, k), ('level-visit', k, K))

print('KMAX', KMAX, 'failures', bad)
# 참고: R_q/Psi(q) 의 크기(작은 k)
