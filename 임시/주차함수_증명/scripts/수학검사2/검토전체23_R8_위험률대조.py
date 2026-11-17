# 검토전체23 R8: 보조정리 8:hazard-H1 (8.22) 의 수치 대조 (배정밀도; 증명이 아니라 대조).
# 첫 층 생존 s_N(k) (k <= N <= 2k-1) 를 가장 큰 나무 사슬 재귀로 계산한다:
#   s_N(k) = pi0_N(k) + sum_{m=k+1}^N pi_N(m) (k/m) s_{m-1}(k),  pi_N(m)=Bor(m)Bor(N+1-m)/Bor(N+1).
import sys
import numpy as np
from math import lgamma, log

k = int(sys.argv[1]) if len(sys.argv) > 1 else 6667
M = 2*k+2
logBor = np.array([0.0]+[-m+(m-1)*log(m)-lgamma(m+1) for m in range(1, M+2)])
s = np.ones(2*k+1)        # s[m] = s_m(k), m <= k 에서 1
for N in range(k+1, 2*k):
    m = np.arange(k+1, N+1)
    piN = np.exp(logBor[m]+logBor[N+1-m]-logBor[N+1])
    pi0 = 1.0-piN.sum()
    s[N] = pi0+(piN*(k/m)*s[m-1]).sum()
hz = 1.0-s[1:2*k]/s[0:2*k-1]        # hz[N] = 1 - s_{N+1}/s_N, N = 0..2k-2
cum = np.cumsum(hz[::-1])[::-1]     # cum[N] = sum_{N'=N}^{2k-2} hz
worst = None
for nu in range(int(0.0537*k)+1, int(0.49*k)+1):
    N = k+nu
    lhs = cum[N-1]
    h = k/(k+nu)-k/(2*k-1)
    r = lhs/h
    if worst is None or r < worst[0]:
        worst = (r, nu, lhs, h)
print('k', k, 'min (sum hz)/h over 0.0537k<=nu<=0.49k:', worst)
# 점별 하계: k hz_k(N') >= 3/2 - 47/(24k) - (3/2 - 0.307(1-3/(2k))) k/(N'+1)
Np = np.arange(k, 2*k-1)
low = (1.5-47/(24*k)-(1.5-0.307*(1-1.5/k))*k/(Np+1))/k
print('pointwise min of hz - lower bound:', float((hz[Np]-low).min()), 'at N\'=', int(Np[(hz[Np]-low).argmin()]))
print('s_{2k-1}(k)=', s[2*k-1], ' k*hz at N=k, 1.5k, 2k-2:', k*hz[k], k*hz[int(1.5*k)], k*hz[2*k-2])
