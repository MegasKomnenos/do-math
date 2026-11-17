# 검토전체25 R8: 보조정리 8:hazard-H1 (8.22)과 c_0(N) 하계의 배정밀도 수치 대조 (증명이 아니라 대조)
# s_n(k)는 정리 2:old-2-13(나)의 재귀 s_n = pi0_n + sum_{m=k+1}^n pi_n(m) (k/m) s_{m-1}  (n <= 2k+1)로 계산
import numpy as np, sys
from math import lgamma, log, exp, pi, sqrt, ceil, floor

def run(k):
    M = 2 * k + 3
    idx = np.arange(1, M + 1, dtype=np.float64)
    lb = -idx + (idx - 1) * np.log(idx) - np.array([lgamma(i + 1) for i in range(1, M + 1)])   # log Bor(m), m=1..M
    Bor = np.exp(lb)
    def surv(y, nmax):
        s = np.ones(nmax + 1)
        for n in range(y + 1, nmax + 1):
            m = np.arange(y + 1, n + 1)
            pin = np.exp(lb[m - 1] + lb[n - m] - lb[n])       # Bor(m)Bor(n+1-m)/Bor(n+1)
            s[n] = 1 - pin.sum() + (pin * (y / m) * s[m - 1]).sum()
        return s
    s = surv(k, 2 * k - 1)
    hz = 1 - s[1:] / s[:-1]            # hz[N] = 1 - s_{N+1}/s_N, N=0..2k-2
    cs = np.concatenate([[0.0], np.cumsum(hz)])   # cs[j] = sum_{N<j} hz[N]
    worst = (9e9, None)
    for nu in range(ceil(0.0537 * k), floor(0.49 * k) + 1):
        N = k + nu
        S = cs[2 * k - 1] - cs[N - 1]              # sum_{N'=N-1}^{2k-2}
        h = k / (k + nu) - k / (2 * k - 1)
        if S - h < worst[0]: worst = (S - h, nu, S, h)
    print(f"k={k}: min over nu in [0.0537k,0.49k] of (sum hz - h(k,nu)) = {worst[0]:.6f} at nu={worst[1]} (sum={worst[2]:.6f}, h={worst[3]:.6f})")
    # ratio sum/h at ends
    for nu in (ceil(0.0537 * k), floor(0.25 * k), floor(0.48 * k), floor(0.49 * k)):
        N = k + nu; S = cs[2 * k - 1] - cs[N - 1]; h = k / (k + nu) - k / (2 * k - 1)
        print(f"   nu={nu}: sum hz={S:.6f}, h={h:.6f}, ratio={S/h:.4f}")
    # c_0(N) <= s_N(k-1)/s_N(k), N in [k, 2k-2]
    s1 = surv(k - 1, 2 * k - 2)
    c2 = 1 / sqrt(2 * pi)
    wm = 9e9
    for N in range(k, 2 * k - 1):
        r = s1[N] / s[N]
        c0 = max((1 - 1 / k) ** (N - k + 1), 1 - exp(7 / 6) * N ** 1.5 / (4 * c2 * k * (2 * k - 1 - N)))
        wm = min(wm, r - c0)
    print(f"   min over k<=N<=2k-2 of s_N(k-1)/s_N(k) - c_0(N) = {wm:.6f}")
    # 8.2절 끝의 말: 창의 수준 질량 전체 >= 1 - s_{k+qmax}(k)
    qmax = int(floor(6 * k ** (2 / 3)))
    print(f"   s_(k+qmax)(k) = {s[k+qmax]:.5f}  (정리 6:old-8-25의 상계 1.15(k+qmax+1)/(qmax+1)^1.5 = {1.15*(k+qmax+1)/(qmax+1)**1.5:.5f})")

for k in [int(a) for a in sys.argv[1:]] or [6667, 6668]:
    run(k)
