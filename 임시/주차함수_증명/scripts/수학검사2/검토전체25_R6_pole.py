# -*- coding: utf-8 -*-
# 7.3절의 극·갱신열·유한 크기 공식 (나)를 작은 열에서 수치로 확인한다(검토 25차 R6; 부동소수 대조용이며 인증이 아니다).
import sys, io
from fractions import Fraction as Fr
from math import factorial, log, exp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def p(m): return (m+1)**(m-1) if m > 0 else 1
NMAX = 260
for k in (2, 3, 5, 8):
    # a_m = A_{m,k-1}/m! : 마지막 차 재귀 n a_n = sum_j min(j,k) a_{j-1} a_{n-j}
    a = [Fr(1)]
    for n in range(1, NMAX+1):
        a.append(sum(min(j, k)*a[j-1]*a[n-j] for j in range(1, n+1))/n)
    # 소인 계수 c_n = C_{n,k}/n! : A = 1/(1-C)  =>  a_n = sum_{i>=1} c_i a_{n-i}
    c = [Fr(0)]
    for n in range(1, NMAX+1):
        c.append(a[n]-sum(c[i]*a[n-i] for i in range(1, n)))
    assert all(x >= 0 for x in c) and c[1] == 1
    cf = [float(x) for x in c]
    lo, hi = 1/exp(1), 1.0
    for _ in range(200):
        mid = (lo+hi)/2
        if sum(cf[n]*mid**n for n in range(1, NMAX+1)) < 1: lo = mid
        else: hi = mid
    rho = (lo+hi)/2
    Cp = sum(n*cf[n]*rho**(n-1) for n in range(1, NMAX+1))
    arho = [float(a[m])*rho**m for m in range(NMAX+1)]
    # 꼬리 핵 계수 K_j
    ao = [Fr(p(m), factorial(m)) for m in range(0, k)]
    K = [Fr(0)]*(NMAX+2)
    for j in range(1, NMAX+2):
        s = sum((k-m)*ao[m-1]*K[j-m] for m in range(1, k) if j-m >= 0)
        if j == k+1: s += 1
        K[j] = s/j
    Krho = sum(float(K[j])*rho**j for j in range(NMAX+2))
    Pinf = k*float(a[k-1])*Krho/rho
    def P(n):  # (가)의 식으로 E[H_k]를 구해 k/n을 곱한다
        return k*float((n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1, n+2))/a[n])/n
    print('k=%d rho_k=%.12f (log2=%.12f) C_k\'(rho)=%.9f  a^rho_250=%.12f 1/(k rho)=%.12f  max a^rho=%.6f' % (k, rho, log(2), Cp, arho[250], 1/(k*rho), max(arho)))
    print('     P_k(50)=%.9f P_k(250)=%.9f (1+1/250)^-1 P_k(250)=%.9f  P_k(inf)=%.9f' % (P(50), P(250), P(250)/(1+1/250), Pinf))
