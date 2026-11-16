# -*- coding: utf-8 -*-
"""심사 A10 — E6 보충: F4 닫힌 꼴의 마지막 단계(log(3j) <= log(3k))를 적분 비교로 바꾼 정제 상계
   R(k) := (42/(5 sqrt(pi) k)) [ (2 sqrt(k)(log 3k - 1) + 1.902)/6 + 1/sqrt(3) ]
         = 14(log 3k - 1)/(5 sqrt(pi k)) + (7*1.902 + 42/sqrt(3))/(5 sqrt(pi) k)
   유도: sum_{j<=k} (1+log 3j)/sqrt(j) <= (1+log 3) + int_1^k (1+log 3x)/sqrt(x) dx = 2 sqrt(k)(log 3k - 1) + 3 - log 3  (피적분함수 (1+log 3x)/sqrt x 는 x > e/3 에서 감소; int log(3x)/sqrt x = 2 sqrt x log 3x - 4 sqrt x)
   확인: (a) R(k) >= 유한 합-적분 상계 U_finite(k) (E6 스크립트의 것), (b) R 감소, (c) R(6667) 값, (d) 1a 여유.
"""
import math, numpy as np
def U_finite(k):
    j = np.arange(1, k + 1, dtype=float); M = k + 1 - j; x0 = k / np.sqrt(3 * j)
    integ = np.where(M <= x0, M**2*np.sqrt(j)/(2*k*k), 1/(6*np.sqrt(j)) + np.log(np.maximum(M/x0, 1))/(3*np.sqrt(j)))
    return 2*21/(5*math.sqrt(math.pi)*k) * np.sum(integ + 1/(math.sqrt(3)*k))
def S_exact(k):
    j = np.arange(1, k + 1, dtype=float)
    return np.sum((1+np.log(3*j))/np.sqrt(j))
def S_bound(k):
    return 2*math.sqrt(k)*(math.log(3*k)-1) + 3 - math.log(3)
def R(k):
    return 42/(5*math.sqrt(math.pi)*k) * (S_bound(k)/6 + 1/math.sqrt(3))
def F4(k):
    return 14*(1+math.log(3*k))/(5*math.sqrt(math.pi*k)) + 42/(5*math.sqrt(3*math.pi)*k)
print(f"  3 - log 3 = {3-math.log(3):.4f} (1.902 로 올림)")
for k in (6667, 6668, 8065, 9551, 9705, 20000, 10**5, 10**6):
    print(f"  k={k}: sum (1+log3j)/sqrt j = {S_exact(k):.3f} <= 적분 상계 {S_bound(k):.3f}: {S_exact(k)<=S_bound(k)};  R(k) = {R(k):.6f} >= U_finite = {U_finite(k):.6f}: {R(k)>=U_finite(k)};  F4 = {F4(k):.6f}")
ks = np.arange(6667, 200000)
Rv = np.array([R(int(k)) for k in ks[::97]])
print(f"  R 감소(표본 97 간격): {np.all(np.diff(Rv) < 0)}; (log3k-1)/sqrt k 감소 조건 log 3k > 3: {math.log(3*6667)>3}")
print(f"  R(6667) = {R(6667):.5f} < 0.18: {R(6667)<0.18};  1a (나) 여유 0.2047101516 - (0.18 - 0.1132841417) = {0.2047101516-(0.18-0.1132841417):.4f};  1a (가)(a) 0.2354722037 -> {0.2354722037-(0.18-0.1132841417):.4f}")
