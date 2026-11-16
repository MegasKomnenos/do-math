# -*- coding: utf-8 -*-
"""심사 A5 추가 발견 — 세 줄 하계식으로 절단점 m>=k 의 V_k(m) 을 직접 아래에서 막기.
V_k(m) >= (k-1)/(R+1) * [ s_{m-1}(k-1) - s_R(k-1) ] - (k-1) c_{2k}(k-1),  R=floor(3(k-1)/2)   (6.20 재배열, 6.21, 2.34 항별)
입력: s_{m-1}(k-1) 의 하계 = 1 - 합집합 상계 sum_{t>y} theta_{N+1}(t)(t-y)/t  (y=k-1, N=m-1; 첫 층 밖 가정 없음),
      s_R(k-1) 의 상계 = C (k-1) q^{-3/2}  (q=R-k+1),  (k-1)c_{2k}(k-1) <= u_C(k) (6.18 꼴).
참값(배정밀도 재귀)과 나란히 적는다.  실행: python -I 심사_A5_4_vcut.py > 심사_A5_4_vcut_out.txt
"""
import numpy as np, sys, importlib.util
from math import lgamma, exp, sqrt, pi, log
spec = importlib.util.spec_from_file_location('f2', __file__.replace('_4_vcut', '_2_float'))
f2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f2)
Bor, Ren, surv = f2.Bor, f2.Ren, f2.surv

def u_of(k, C): return (C/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5

def union_lower_surv(N, y):
    """s_N(y) >= 1 - sum_{t=y+1}^{N} theta_{N+1}(t) (t-y)/t  (꼭짓점별 실패확률의 합집합 상계; 모양 조건부 독립성)"""
    if N <= y: return 1.0
    t = np.arange(y+1, N+1)
    theta = Bor(t)*Ren(N+1-t)/Bor(N+1)
    return 1 - (theta*(t-y)/t).sum()

for k, C in ((3131, 3.2), (4001, 3.0), (6668, 3.0), (10001, 3.0)):
    M = 2*k+1
    s_km1 = surv(k-1, M); s_k = surv(k, M); s_kp1 = surv(k+1, M)
    c_k = s_kp1-s_k; c_km1 = s_k-s_km1
    R = (3*(k-1))//2; q = R-(k-1)
    sR_up = min(1.0, C*(k-1)*q**-1.5); u = u_of(k, C)
    terms = (k+1)*c_k-(k-1)*c_km1
    print("\n==== k=%d (C=%.1f): R=%d q=%d s_R참=%.4f s_R상계=%.4f  (k-1)c_2k(k-1)참=%.4f u_C=%.4f" % (k, C, R, q, s_km1[R], sR_up, (k-1)*c_km1[2*k], u))
    print("  m-k | V_k(m)참값 | 하계(참 s) | 하계(증명가능: 합집합 하계·C 상계·u_C)")
    last_pos = None
    for d in list(range(0, 14)) + [20, 40, 80, 120, 160, 200, 300, 400]:
        m = k+d
        if m > 2*k: break
        V = terms[m:2*k+1].sum()
        lb_true = (k-1)/(R+1)*(s_km1[m-1]-s_km1[R]) - (k-1)*c_km1[2*k]
        lb_prov = (k-1)/(R+1)*(union_lower_surv(m-1, k-1)-sR_up) - u
        if lb_prov > 0: last_pos = d
        print("  %4d | %.5f | %.5f | %.5f" % (d, V, lb_true, lb_prov))
    # 증명가능 하계가 양인 최대 d (연속 탐색)
    dmax = 0
    for d in range(0, k):
        m = k+d
        if (k-1)/(R+1)*(union_lower_surv(m-1, k-1)-sR_up) - u > 0: dmax = d
        else: break
    print("  증명가능 하계>0 인 연속 범위: 0<=m-k<=%d  (k^{2/3}=%.0f, 6.55의 d<=m^{2/3}/2 경계=%.0f)" % (dmax, k**(2/3), (k+dmax)**(2/3)/2))
    # 1.15 꼴 생존 상계로 u 를 바꾸면
    u115 = (1.15/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5  # 10.21 꼴 min(1,1.15(y+d)/d^{3/2}) 을 6.18 증명에 넣은 근사 (y+d<=2k, d>=0.65k: 1.15*2k/(0.65k)^{1.5} 와 비교)
    sR115 = min(1.0, 1.15*(k-1+q+1)/(q+1)**1.5)
    dmax2 = 0
    for d in range(0, k):
        m = k+d
        if (k-1)/(R+1)*(union_lower_surv(m-1, k-1)-sR115) - u115 > 0: dmax2 = d
        else: break
    print("  10.21(1.15) 꼴 상계를 쓰면: s_R상계=%.4f u=%.4f, 양인 범위 0<=m-k<=%d" % (sR115, u115, dmax2))
