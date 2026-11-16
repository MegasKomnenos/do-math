# 검토전체16 E2: 4장 수치 검산 1 (정확 정수·유리수)
# (1) 정리 4-5 진술: d_{n,k_n} 부호 (n<=80), 2<=n<=15 에서 오른쪽 절반 비증가, n>=16 양수
# (2) e_n = K''_{n,k}(k) = 2 E2_{n,k} 와 J_n(k-1) (보조정리 2:J-egf (가) 재귀), n in {2k-1,2k}, e_n > J_n(k-1) for 16<=n<=80
# (3) 보조정리 2-30: B_{n,k-1} = J_n(k-1) - Xi_{n,k} 에서 d_{n,k} = 2E_{n,k} - B 확인은 불가(E 필요); 대신 d >= e_n - J_n(k-1) 확인
# (4) 경계 응답 다항식 Gamma_d(y;n) 의 계수 비음수 (작은 n)
from fractions import Fraction as Fr
from math import comb, ceil
import sys
sys.setrecursionlimit(10000)

def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1
N = 80
# A_{n,l} 열
def column(l, N):
    A = [0] * (N + 1); A[0] = 1
    for m in range(N):
        A[m + 1] = sum(comb(m, j) * min(j + 1, l + 1) * A[j] * A[m - j] for j in range(m + 1))
    return A
cols = [column(l, N) for l in range(N)]
def A(n, l):
    if l < 0: return 0
    if l >= n - 1: return p(n)
    return cols[l][n]
def b(n, l): return A(n, l) - A(n, l - 1)
def d(n, k): return b(n, k) - b(n, k - 1)

print("== 정리 4-5 진술 ==")
for n in range(2, N + 1):
    kn = ceil(n / 2)
    dn = d(n, kn)
    right_noninc = all(b(n, j) >= b(n, j + 1) for j in range(kn, n - 1))
    if n <= 15:
        ok = dn < 0 and right_noninc
    else:
        ok = dn > 0
    if not ok or n <= 17:
        print(n, kn, "d=", dn if abs(dn) < 10**6 else ("+" if dn > 0 else "-"), "right_noninc=", right_noninc, "OK" if ok else "FAIL")
print("n=16..80 모두 d>0:", all(d(n, ceil(n/2)) > 0 for n in range(16, N + 1)))

# 얼린 용량 다항식 K_{n,k}(y) 를 y 의 다항식(계수 리스트)으로 재귀 계산 (4장 (4.99행) 재귀)
def polymul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r
def polyadd(a, b):
    r = [0] * max(len(a), len(b))
    for i, x in enumerate(a): r[i] += x
    for i, x in enumerate(b): r[i] += x
    return r
def polyscale(a, c): return [c * x for x in a]
def polyeval(a, y): return sum(c * y**i for i, c in enumerate(a))
def polyderiv(a): return [i * a[i] for i in range(1, len(a))] or [0]

def K_table(k, N):
    K = [[1]]  # K_{0,k} = 1
    for n in range(1, N + 1):
        s = [0]
        for j in range(n):
            W = [j + 1] if j + 1 <= k else [0, 1]  # W(j+1): j+1<=k -> j+1 ; else y
            term = polymul(polymul(W, K[j]), K[n - 1 - j])
            s = polyadd(s, polyscale(term, comb(n - 1, j)))
        K.append(s)
    return K

def J_table(k, N):
    # J-egf (가): J_0=0, J_m=0 (m<k), J_{n+1}(z) = sum_i C(n,i)(z+i+1)p_i J_{n-i}(z) + 1[n>=k-1] C(n,k-1) p_{k-1} p_{n-k+1}, 0<=n<=2k-1
    # z 의 다항식으로.
    J = [[0]]
    for n in range(0, N):
        if n + 1 < k:
            J.append([0]); continue
        s = [0]
        for i in range(n + 1):
            term = polymul([i + 1, 1], J[n - i])  # (z+i+1) J_{n-i}
            s = polyadd(s, polyscale(term, comb(n, i) * p(i)))
        if n >= k - 1:
            s = polyadd(s, [comb(n, k - 1) * p(k - 1) * p(n - k + 1)])
        J.append(s)
    return J

print("== e_n 과 J_n(k-1), 2-30 검사 ==")
for n in range(2, 41):
    k = ceil(n / 2)
    K = K_table(k, n)
    J = J_table(k, n)  # 유효 범위 n<=2k: 여기서 n in {2k-1,2k} OK
    # 검사: K_{n,k}(k) = A_{n,k-1}, K(k+1) = A_{n,k}
    assert polyeval(K[n], k) == A(n, k - 1) and polyeval(K[n], k + 1) == A(n, k), n
    e_n = polyeval(polyderiv(polyderiv(K[n])), k)
    Jn = polyeval(J[n], k - 1)
    Xi = comb(2 * k - 1, k - 1) * p(k - 1) ** 2 if n == 2 * k else 0
    B = polyeval(K[n], k - 1) - A(n, k - 2)  # B_{n,k-1} = K(k-1) - A_{n,k-2}
    dn = d(n, k)
    # 2-30: B = J - Xi ; 2-28: d = 2E - B  => 2E = d + B; e_n <= 2E
    ok30 = (B == Jn - Xi)
    ok_lower = dn >= e_n - Jn
    twoE = dn + B
    print(f"n={n} k={k} e_n>J: {e_n > Jn} (e_n-J={e_n-Jn if abs(e_n-Jn)<10**8 else ('+' if e_n>Jn else '-')}) 2-30 B=J-Xi: {ok30} d>=e-J: {ok_lower} e_n<=2E: {e_n <= twoE}")

# (4) Gamma_d(y;n) 계수 비음수
def Gamma(d, n, memo={}):
    if d == 0: return [1]
    key = (d, n)
    if key in memo: return memo[key]
    s = [comb(n, d) * p(d)]
    inner = [0]
    for j in range(d):
        inner = polyadd(inner, polyscale(Gamma(d - 1 - j, n), comb(n - d + j, j) * p(j)))
    s = polyadd(s, polymul([0, 1], inner))
    memo[key] = s
    return s
print("Gamma 계수 비음수 (n<=30):", all(all(c >= 0 for c in Gamma(dd, n)) for n in range(1, 31) for dd in range(0, n)))
