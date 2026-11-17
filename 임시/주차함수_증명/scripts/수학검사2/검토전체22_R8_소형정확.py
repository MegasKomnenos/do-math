# 검토 22차 R8: 장8의 일반-k 진술을 작은 k에서 정확 유리수로 확인
from fractions import Fraction as Fr
from math import comb, factorial, exp
import sys
NMAX = 40
def build(l):
    A = [1]
    for n in range(1, NMAX+1):
        A.append(sum(comb(n-1, t-1)*min(t, l+1)*A[t-1]*A[n-t] for t in range(1, n+1)))
    return A
Acache = {}
def A(n, l):
    if l < 0: return 1 if n == 0 else 0
    if l not in Acache: Acache[l] = build(l)
    return Acache[l][n]
def p(n): return (n+1)**(n-1) if n >= 1 else 1
def s(m, y): return Fr(A(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return s(m, Y+1)-s(m, Y)
def pi(n, m): return Fr(comb(n, m)*m**(m-1)*p(n-m), p(n))
def pi0(n, y):  # Pr(G<=y): 숲의 모든 나무 크기 <= y
    # 수: 지수 공식으로 크기 <=y 나무만
    F = [1]
    for nn in range(1, n+1):
        F.append(sum(comb(nn-1, t-1)*t**(t-1)*F[nn-t] for t in range(1, min(nn, y)+1)))
    return Fr(F[n], p(n))
assert all(A(n, n-1) == p(n) for n in range(1, 12))
bad = 0
for k in range(2, 11):
    # (8.2) 등식과 보조정리 old-6-23 하계
    for m in range(k+1, min(3*k+1, NMAX)+1):
        rhs = sum(pi(m, t)/t*s(m-t, k)*(s(t-1, k+1)+k*c(t-1, k)) for t in range(k+1, m+1))
        if m <= 2*k+1:
            if c(m, k) != sum(pi(m, t)/t*(s(t-1, k+1)+k*c(t-1, k)) for t in range(k+1, m+1)): bad += 1; print("8.2 fail", k, m)
        if c(m, k) < rhs: bad += 1; print("old-6-23 fail", k, m)
    for m in range(k, min(3*k, NMAX)+1):
        rhs = sum(pi(m, t)/t*s(m-t, k-1)*(s(t-1, k)+(k-1)*c(t-1, k-1)) for t in range(k, m+1))
        if c(m, k-1) < rhs: bad += 1; print("old-6-23 level k-1 fail", k, m)
        if m <= 2*k-1 and c(m, k-1) != sum(pi(m, t)/t*(s(t-1, k)+(k-1)*c(t-1, k-1)) for t in range(k, m+1)): bad += 1; print("8.2' fail", k, m)
    # (8.1)
    for n in range(2*k+1, min(3*k, NMAX)+1):
        Theta = comb(n, k)*k**(k-2)*A(n-k, k-1)
        BV = sum(comb(n, m+1)*p(n-1-m)*(A(m, k)-A(m, k-2)) for m in range(2*k+1, n))
        if Fr(Theta, p(n)) != pi(n, k)*s(n-k, k)/k: bad += 1; print("8.1 Theta fail")
        if Fr(BV, p(n)) != sum(pi(n, m+1)/(m+1)*(c(m, k)+c(m, k-1)) for m in range(2*k+1, n)): bad += 1; print("8.1 BV fail")
    # escape-lower (8.8): y=k, y+1<=N<=2y+1
    for N in range(k+1, min(2*k+1, NMAX)+1):
        km = sum(pi(N, m)*Fr(k, m) for m in range(k+1, N+1)); q0 = pi0(N, k)
        if not (s(N, k) >= q0/(1-km) >= q0/(1-Fr(k, N)+Fr(k, N)*q0)): bad += 1; print("escape fail", k, N)
    # old-6-30 (가)(나)
    for N in range(k, 2*k):
        ratio = s(N, k-1)/s(N, k)
        ga = 1-max(1/(k*pi0(Np, k-1)) for Np in range(k, N+1))
        if ratio < ga: bad += 1; print("old-6-30(가) fail", k, N)
        if N <= 2*k-2:
            gb = 1-exp(7/6)*N**1.5/(4*(2*3.141592653589793)**-0.5*k*(2*k-1-N))
            if float(ratio) < gb: bad += 1; print("old-6-30(나) fail", k, N)
        if ratio < Fr(k-1, k)**(N-k+1): bad += 1; print("cap-shift fail", k, N)
    # old-6-31 (다)
    for N in range(1, min(2*k+2, NMAX-1)):
        for j in range(N//2+1, N+1):
            if pi0(N, j)-pi0(N+1, j) > pi(N, j): bad += 1; print("old-6-31(다) fail", N, j)
    # old-6-32
    def sT(t, y): return Fr(min(t, y), t)*s(t-1, y)
    for t in range(k+1, 2*k+2):
        cap = sT(t, k+1)-sT(t, k); size = sT(t, k)-sT(t+1, k)
        if cap != (s(t-1, k+1)+k*c(t-1, k))/t: bad += 1; print("eps_cap 꼴 fail")
        if cap < size/2: bad += 1; print("old-6-32 fail", k, t)
    # s_N(k)=E[s^T_G(k)] (N<=2k+1)
    # envelope-H 첫 주장: s_{k+q}(k+1) >= exp(-J(q,k))
    def Bor(m): return exp(-m)*m**(m-1)/factorial(m)
    def Ren(m): return m*Bor(m)
    for q in range(1, min(k+3, NMAX-k)+1):
        J = sum((q-r)*Ren(r)*Bor(k+1+q-r)/Bor(k+1+q) for r in range(1, q))/(k+1)
        if float(s(k+q, k+1)) < exp(-J)-1e-12: bad += 1; print("envelope-H fail", k, q)
    # R_q 재귀 (8.4), (8.5), 그리고 k c_{k+q}(k) <= Psi(q)?
    R = {0: Fr(0)}
    for q in range(1, k+2):
        if k+q > NMAX: break
        R[q] = k*c(k+q, k)
        rhs = sum(pi(k+q, k+j)*Fr(k, k+j)*(s(k+j-1, k+1)+R[j-1]) for j in range(1, q+1))
        if R[q] != rhs: bad += 1; print("8.4 fail", k, q)
        low = Fr(k, k+q)*sum(Bor(j)*(float(s(k+q-j, k+1))+float(R[q-j])) for j in range(1, q+1))
        if float(R[q]) < low-1e-12: bad += 1; print("8.5 fail", k, q)
print("실패 수:", bad)
