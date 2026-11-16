# 검토전체16 E2: 정리 4-8(나) 의 20<=n<=1000 에서 b_{n,k_n} < b_{n,k_n+1}, 정리 4-9 의 3<=n<=15 Q_L(n),
# 정리 4-8(가) 관련: n>=16 d>0 (이미 확인). 정확 정수 (n<=80) + binary64 (n<=1000, 여유 보고)
from math import comb, ceil, lgamma, log, exp
import numpy as np
def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1
N = 80
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
print("Q_L(n), 3<=n<=15:")
for n in range(3, 16):
    ok = True
    for l in range(0, n - 2):
        if 2 * l <= n - 2 and b(n, l) > b(n, l + 1):
            if b(n, l + 1) ** 2 < b(n, l) * b(n, l + 2): ok = False
    print(n, ok, end="; ")
print()
print("20<=n<=80: b_{n,k_n} < b_{n,k_n+1} 모두:", all(b(n, ceil(n/2)) < b(n, ceil(n/2) + 1) for n in range(20, 81)))
print("n<=19: ", [(n, b(n, ceil(n/2)) < b(n, ceil(n/2)+1)) for n in range(4, 20)])
# binary64: a_{m,l} = A_{m,l}/p_m, a_{m+1} = sum_j w_{m,j} min(j+1,l+1) a_j a_{m-j}, w = C(m,j) p_j p_{m-j} / p_{m+1}
def logp(n): return (n - 1) * log(n + 1) if n >= 1 else 0.0
def col_float(l, M):
    a = np.zeros(M + 1); a[0] = 1.0
    for m in range(M):
        j = np.arange(m + 1)
        lw = np.array([lgamma(m + 1) - lgamma(jj + 1) - lgamma(m - jj + 1) + logp(jj) + logp(m - jj) - logp(m + 1) for jj in j])
        w = np.exp(lw) * np.minimum(j + 1, l + 1)
        a[m + 1] = np.dot(w, a[:m + 1] * a[m::-1][:m + 1][::-1] if False else a[:m+1] * a[m - j])
    return a
worst = (None, 1e9)
for n in range(81, 1001):
    k = ceil(n / 2)
    a_km1 = col_float(k - 1, n)[n]; a_k = col_float(k, n)[n]; a_kp1 = col_float(k + 1, n)[n]
    bk = a_k - a_km1; bk1 = a_kp1 - a_k
    rel = (bk1 - bk) / bk
    if rel < worst[1]: worst = (n, rel)
    if bk >= bk1: print("FAIL", n, bk, bk1)
    if n % 100 == 0: print(f"n={n} 상대 여유 (b_{{k+1}}-b_k)/b_k = {rel:.4e}", flush=True)
print("81<=n<=1000 최소 상대 여유:", worst)
