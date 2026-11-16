# 검토전체16 E2: 보조정리 borel-tail-arc (가) 증명의 두 조각 상수 확인 (binary64, 상대오차 ~1e-12)
from math import lgamma, log, exp, sqrt, pi
def Bor(j): return exp(-j + (j-1)*log(j) - lgamma(j+1))
c = (2*pi)**-0.5
for k in [1000, 10000, 100000]:
    eps = k**-0.5
    S1 = sum(j*Bor(j) for j in range(1, k+1))
    d1 = S1 - (2*c*sqrt(k) - 2/3)
    tail = sum(Bor(j) for j in range(k+1, 40*k))  # 꼬리 근사 (j<40k) + 적분 보정
    tail += 2*c*(40*k)**-0.5  # 나머지 꼬리 ~ int
    d0 = 2*c*eps - tail
    print(f"k={k}: sum jBor - (2c sqrt k - 2/3) = {d1:.3e}  in [0, {2/3*c*eps:.3e}]: {0 <= d1 <= 2/3*c*eps};  2c eps - tail = {d0:.3e} in [0,{5/9*c*eps**3:.3e}]: {0<=d0<=5/9*c*eps**3}")
# 전변동 상계: h(w) = w^{-3/2}(e^{-phi w} - 1 + phi w), |phi| <= 2(-Re phi)
import cmath
def TV(phi, N=20000):
    ws = [i/N for i in range(1, N+1)]
    hs = [w**-1.5*(cmath.exp(-phi*w) - 1 + phi*w) for w in ws]
    return sum(abs(hs[i+1]-hs[i]) for i in range(N-1)) + abs(hs[0])
for phi in [-0.5, -2, -8, -20, complex(-1, 2), complex(-4, 6), complex(-10, 17)]:
    print(f"phi={phi}: TV={TV(phi):.4f}  bound |phi|^2 e^{{-Re phi}}={abs(phi)**2*exp(-phi.real):.4f}  ok={TV(phi) <= abs(phi)**2*exp(-phi.real)}  cond |phi|<=2(-Re): {abs(phi) <= -2*phi.real}")
