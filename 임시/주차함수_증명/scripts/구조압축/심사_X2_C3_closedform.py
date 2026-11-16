# -*- coding: utf-8 -*-
"""C3 보조: Abel 합 하계의 닫힌 꼴 변형(상수 C=3 / C=1.39 / 10.21 직접) — w_0=0.71216 를 넘는지. 실행: python -I 심사_X2_C3_closedform.py"""
import math
out=[]
def P(*a):
    s=" ".join(str(x) for x in a); out.append(s); print(s)
def exact(Y, sup):
    Q=int(math.floor(6*Y**(2/3))); a=lambda q: Y/(Y+q+1)
    return a(1)-a(Q)*sup(Q)+sum((a(q+1)-a(q))*sup(q) for q in range(1,Q))
def closed_C(Y, C):
    # s_q <= min(1, C Y q^{-3/2}); q1 = floor((CY)^{2/3}) 개는 1; 나머지는 중점 적분 비교; Abel 계수는 -1/Y 로 거칠게, a_Q 는 정확히
    Q=int(math.floor(6*Y**(2/3))); q1=int(math.floor((C*Y)**(2/3)))
    S = q1 + C*Y*2*((q1+0.5)**-0.5-(Q-0.5)**-0.5)
    return Y/(Y+2) - Y/(Y+Q+1)*C*Y*Q**-1.5 - S/Y
def closed_C_fine(Y, C):
    # Abel 계수를 Y/((Y+q+1)(Y+q+2)) 로 정확히, 합은 두 구간 적분 비교(수치 적분 대신 닫힌 꼴): 단조 감소 피합수 → 합 <= 적분 (왼쪽 끝)
    Q=int(math.floor(6*Y**(2/3))); q1=int(math.floor((C*Y)**(2/3)))
    # 구간 1: q<=q1, 항 Y/((Y+q+1)(Y+q+2)) = Y[1/(Y+q+1)-1/(Y+q+2)] → 망원: Y[1/(Y+2)-1/(Y+q1+2)]
    S1 = Y*(1/(Y+2)-1/(Y+q1+2))
    # 구간 2: q1<q<Q, 항 Y/((Y+q+1)(Y+q+2)) * C Y q^{-3/2} <= C Y^2 q^{-3/2}/(Y+q)^2 ; 감소 → <= ∫_{q1+1/2}^{Q-1/2} (근사: 수치 사다리꼴 아닌 상계용 적분을 Simpson으로)
    f=lambda x: C*Y*Y*x**-1.5/(Y+x)**2
    import numpy as np
    xs=np.linspace(q1+0.5,Q-0.5,20001); S2=float(np.trapezoid(f(xs),xs))
    return Y/(Y+2) - Y/(Y+Q+1)*C*Y*Q**-1.5 - S1 - S2
for Y in [25000, 40000, 10**5]:
    P(f"Y={Y}: 정확 유한합(6.1)={exact(Y, lambda q: min(1,3*Y*q**-1.5)):.5f}  닫힌꼴(C=3, 중점)={closed_C(Y,3):.5f}  닫힌꼴(C=3, Abel 계수 정확)={closed_C_fine(Y,3):.5f}")
    sup1021=lambda q: min(1,1.15*(Y+q+1)/(q+1)**1.5)
    P(f"        정확 유한합(10.21)={exact(Y,sup1021):.5f}  닫힌꼴(C=1.15*1.2=1.38)={closed_C(Y,1.38):.5f}  (w_0=0.71216)")
open(__file__.replace('.py','_out.txt'),'w',encoding='utf-8').write("\n".join(out)+"\n")
