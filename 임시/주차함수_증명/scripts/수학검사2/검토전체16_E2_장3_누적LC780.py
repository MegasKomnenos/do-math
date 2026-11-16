# 검토전체16 E2: 정리 3-5 (누적 로그오목성의 실패) 검산.
# A_{n,l} (n<=780) 을 정리 2-6 재귀(l<389)와 정리 2-13 공식(l>=389)으로 정확 정수로 계산하고
# 모든 n<=780 에서 A_{n,.} 의 로그오목성을 검사한다. n<760 은 log 근사(절대오차 ~1e-12)로,
# n>=760 은 정확 정수로 검사한다.
from math import comb, log
import sys, time
N = 780
def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1
P = [p(n) for n in range(N + 1)]
C = [[comb(m, j) for j in range(m + 1)] for m in range(N + 1)]
LOGA = [[0.0] * N for _ in range(N + 1)]   # LOGA[n][l] = log A_{n,l}
EXACT = {n: [0] * N for n in range(760, N + 1)}
t0 = time.time()
for l in range(N):
    A = [0] * (N + 1)
    for m in range(min(l + 1, N) + 1):
        A[m] = P[m]
    if l < 389:
        for m in range(l + 1, N):
            Cm = C[m]; lp1 = l + 1
            s = 0
            for j in range(m + 1):
                s += Cm[j] * min(j + 1, lp1) * A[j] * A[m - j]
            A[m + 1] = s
    else:
        for n in range(l + 2, N + 1):
            Cn = C[n]
            s = 0
            for m in range(l + 2, n + 1):
                s += Cn[m] * P[n - m] * (m ** (m - 1) - (l + 1) * A[m - 1])
            A[n] = P[n] - s
    for n in range(N + 1):
        LOGA[n][l] = log(A[n])
        if n >= 760: EXACT[n][l] = A[n]
    if l % 20 == 0:
        print(f"l={l} done, {time.time()-t0:.0f}s", flush=True)
# 교차 검증: l=389,390 를 두 방법으로 (작은 n 범위)
l = 389
A2 = [0] * (N + 1)
for m in range(l + 2): A2[m] = P[m]
for m in range(l + 1, N):
    A2[m + 1] = sum(C[m][j] * min(j + 1, l + 1) * A2[j] * A2[m - j] for j in range(m + 1))
print("교차검증 l=389 n=780:", A2[780] == EXACT[780][389], flush=True)
# 로그오목성 검사
fails = {}
for n in range(3, N + 1):
    bad = []
    for l in range(1, n - 1):
        if n >= 760:
            a = EXACT[n]
            if a[l] ** 2 < a[l - 1] * a[l + 1]: bad.append(l)
        else:
            d = 2 * LOGA[n][l] - LOGA[n][l - 1] - LOGA[n][l + 1]
            if d < 1e-10: bad.append((l, d))
    if bad: fails[n] = bad
print("LC 실패/근접 행:", {n: v for n, v in fails.items()})
a = EXACT[780]
for l in range(570, 585):
    num = a[l] ** 2 - a[l - 1] * a[l + 1]
    print(l, "ok" if num >= 0 else "FAIL", f"{num / a[l]**2:.3e}")
# 위반 수준에서의 상대 크기 범위
rel = [(a[l] ** 2 - a[l - 1] * a[l + 1]) / a[l] ** 2 for l in range(1, 779) if a[l] ** 2 < a[l - 1] * a[l + 1]]
print("n=780 위반 수준 수:", len(rel), "상대 크기 min/max:", min(rel) if rel else None, max(rel) if rel else None)
print("총 시간", time.time() - t0)
