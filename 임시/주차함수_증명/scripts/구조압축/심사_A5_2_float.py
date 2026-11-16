# -*- coding: utf-8 -*-
"""심사 A5 — 배정밀도 재귀 (큰 k). 생존 확률 s_m(cap) 을 (6.1) 마지막 차 재귀로 모든 m<=2k+1 에서 계산.
S13 수치 관찰(6.1의 상수 3 대 참값, V_k(k) 참값, 생존 상계 비 표), S1·S2·S12 큰 k 확인, 판정 V (61<=k<=249).
실행: python -I 심사_A5_2_float.py > 심사_A5_2_float_out.txt
"""
import numpy as np
from math import lgamma, log, exp, sqrt, pi
import sys

def logp(n):  # log p_n, p_n=(n+1)^{n-1}, p_0=1
    return (n-1)*np.log(n+1.0) if n >= 1 else 0.0

def surv(cap, M):
    """s_m(cap) = Pr_m(M <= cap-1), m=0..M (배정밀도). (6.1): s_m = sum_j P_m(j) min(j,cap)/j s_{j-1} s_{m-j}."""
    s = np.ones(M+1)
    lp = np.array([logp(n) for n in range(M+1)])
    lg = np.array([lgamma(n+1) for n in range(M+1)])  # log n!
    for m in range(cap, M+1):   # m<=cap-1 → s=1 (최대 변위 <= m-1 <= cap-2)
        j = np.arange(1, m+1)
        # log P_m(j) = log j + log C(m-1,j-1) + logp(j-1) + logp(m-j) - logp(m)
        lP = np.log(j) + (lg[m-1] - lg[j-1] - lg[m-j]) + lp[j-1] + lp[m-j] - lp[m]
        w = np.exp(lP) * np.minimum(j, cap)/j
        s[m] = np.dot(w, s[j-1]*s[m-j])
    return s

def Bor(n):
    n = np.asarray(n, dtype=float)
    return np.exp(-n + (n-1)*np.log(n) - np.vectorize(lgamma)(n+1))

def Ren(n):
    return n*Bor(n)

def g(x):
    return (x-1)*np.log(1+1/x)

sB = exp(1)/sqrt(2*pi)
gamma_W = 2*exp(0.0031)/exp(1)

def u_of(k, C=3.0):
    return (C/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5

def analyze(k, verbose=True):
    M = 2*k+1
    s_km1 = surv(k-1, M); s_k = surv(k, M); s_kp1 = surv(k+1, M)
    c_k = s_kp1 - s_k          # c_m(k)
    c_km1 = s_k - s_km1        # c_m(k-1)
    m = np.arange(M+1)
    out = {}
    # 판정 V
    terms = (k+1)*c_k - (k-1)*c_km1
    V = np.array([terms[mm:2*k+1].sum() for mm in range(k, 2*k+1)])
    out['V_k(k)'] = V[0]; out['minV'] = V.min(); out['argminV_m'] = k+int(V.argmin())
    # 6.1 비: max_q s_{k+q}(k) q^{3/2}/k
    q = np.arange(1, k+1)
    ratio61 = s_k[k+q]*q**1.5/k
    out['max s q^1.5/k'] = ratio61.max(); out['argmax q'] = int(q[ratio61.argmax()])
    # 중앙 행 질량
    out['k c_2k(k-1)'] = k*c_km1[2*k]; out['(k-1)c_2k(k)'] = (k-1)*c_k[2*k]; out['u(k)'] = u_of(k)
    # W0 참값과 상계
    d = np.arange(1, k+1)
    W0 = (Bor(k+d)*c_km1[k-1+d]).sum()
    out['W0'] = W0; out['W0/new'] = W0/(2/sqrt(2*pi)*k**-1.5); out['W0/old'] = W0/(gamma_W*sB*k**-1.5)
    # S1 부등식 (큰 k): c_{k-1+d}(k-1) <= U_d c_{2k-1}(2k-1-d). c_{2k-1}(2k-1-d) 는 용량 2k-d, 2k-1-d 의 생존이 필요 → 여기서는 d<=2 만(용량 k+1,k,k-1 보유)
    #   d=1: c_{2k-1}(2k-2) = s_{2k-1}(2k-1)-s_{2k-1}(2k-2) — 보유하지 않음 → 생략(정확 스크립트가 작은 k 전수).
    # S2: min_n D_{n,k}/(Bor(n)c_{n-1}(k-1))
    n = np.arange(k+1, 2*k+1)
    D = (k+1)*Bor(n+1)*c_k[n] - (k-1)*Bor(n)*c_km1[n-1]
    base = Bor(n)*c_km1[n-1]
    out['min D/(Bor c)'] = (D/base).min(); out['min -(k-1)/(2n)'] = (-(k-1)/(2*n)).min()
    # S12: (k-1)/(R+1)(1-s_R(k-1)) - (k-1)c_2k(k-1), R=floor(3(k-1)/2)
    R = (3*(k-1))//2
    out['S12 참값하계'] = (k-1)/(R+1)*(1-s_km1[R]) - (k-1)*c_km1[2*k]
    qR = R-(k-1)
    for C in (3.0, 3.2):
        sR_up = min(1.0, C*(k-1)*qR**-1.5)
        out['S12 C=%.1f 하계' % C] = (k-1)/(R+1)*(1-sR_up) - u_of(k, C)
    # 생존 상계 비 표 (F6): 위치 xi=q/k^{2/3} in 1,2,4; q=k/2; q=k  — 6.1 / 10.21 / 8.10(가) 대 참값 s_{k+q}(k)
    def b61(q): return min(1.0, 3*k*q**-1.5)
    def b1021(q): return min(1.0, 1.15*(k+q+1)/(q+1)**1.5)
    def b810(q):
        N = k+q; mm = np.arange(k+1, N+1)
        theta = Bor(mm)*Ren(N+1-mm)/Bor(N+1)
        B = (theta*(mm-k)/mm).sum()
        return 1/(1+B)
    tab = []
    for name, qq in (('xi=1', round(k**(2/3))), ('xi=2', round(2*k**(2/3))), ('xi=4', round(4*k**(2/3))), ('q=k/2', k//2), ('q=k', k)):
        tv = s_k[k+qq]
        tab.append((name, qq, tv, b61(qq)/tv, b1021(qq)/tv, b810(qq)/tv))
    out['table'] = tab
    # 수준 질량 하계 비 표 (F6 (2)): k c_{k+q}(k) 참값 대 Psi(q)/(2m)*k (6.48), 9.7 하계, 6.53 Low
    def Psi(dd): return Ren(np.arange(1, dd+1)).sum()
    def lo97(mm, dd):
        w = mm-dd; gg = ((mm+1)/(mm-dd+1))**1.5*exp(1/(12*(mm-dd+1)))
        P = Psi(dd)
        return P/w*exp(-(gg*(2*pi)**-0.5*(4/3*dd**1.5+2*sqrt(dd)) + gg**2*(5/8*dd**2+dd))/(w*P))
    def low653(kk, dd):
        rho = dd/kk**(2/3); eps = kk**(-1/3)
        br = 2*sqrt(rho)-2.218*eps
        if br <= 0: return float('nan')
        return (2*pi)**-0.5*kk**(1/3)*br/(1+rho*eps)*exp(-1/(12*(kk+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(kk+1)))/((2*pi)**-0.5*br))/(kk+1)
    tab2 = []
    for name, dd in (('q=20', 20), ('xi=.5', round(0.5*k**(2/3))), ('xi=1', round(k**(2/3))), ('xi=2', round(2*k**(2/3))), ('xi=4', round(4*k**(2/3)))):
        mm = k+dd; tv = c_k[mm]
        b648 = Psi(dd)/(2*mm) if dd <= mm**(2/3)/2 else float('nan')
        tab2.append((name, dd, tv*k, b648/tv if b648 == b648 else float('nan'), lo97(mm, dd)/tv, low653(k, dd)/tv))
    out['table2'] = tab2
    if verbose:
        print("\n==== k=%d ====" % k)
        for key in ('V_k(k)', 'minV', 'argminV_m', 'max s q^1.5/k', 'argmax q', 'k c_2k(k-1)', '(k-1)c_2k(k)', 'u(k)', 'W0', 'W0/new', 'W0/old', 'min D/(Bor c)', 'min -(k-1)/(2n)', 'S12 참값하계', 'S12 C=3.0 하계', 'S12 C=3.2 하계'):
            print("  %-18s %s" % (key, out[key]))
        print("  생존 상계/참값: 위치 q 참값 | 6.1 | 10.21(y>=4000꼴) | 8.10(가)")
        for row in tab: print("   %-6s q=%5d s=%.5e | %7.3f | %7.3f | %7.3f" % row)
        print("  수준 질량 하계/참값: 위치 d k*c참값 | 6.48(나) | 9.7 | 6.53")
        for row in tab2: print("   %-6s d=%5d kc=%.5f | %7.4f | %7.4f | %7.4f" % row)
    return out

if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1:]] or [249, 2001, 3131, 6668]
    for k in ks:
        analyze(k)
    # 판정 V: 61..249 (배정밀도)
    if not sys.argv[1:]:
        print("\n# 판정 V, 61<=k<=249 (배정밀도): 최소 V_k(m)")
        worst = (1e9, None, None)
        for k in range(61, 250):
            o = analyze(k, verbose=False)
            if o['minV'] < worst[0]:
                worst = (o['minV'], k, o['argminV_m'])
        print("min_k min_m V_k(m) =", worst)
