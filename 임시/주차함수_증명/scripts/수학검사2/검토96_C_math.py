# -*- coding: utf-8 -*-
"""검토 C: 보조정리 5.73 (다) †의 두 상계(|1-ϱD|≤1, ≤8ϱ^{-2})와 지배함수의 적분 가능성, D.30 (7)(ㄱ)의 상대 차 상계 수치 확인."""
import sys
from mpmath import mp, mpf, exp, quad, sqrt, pi, inf
sys.stdout.reconfigure(encoding="utf-8")
mp.dps = 30
def D(r):  # Dawson e^{-r^2/2} ∫_0^r e^{u^2/2} du
    return exp(-r*r/2)*quad(lambda u: exp(u*u/2), [0, r])
worst1 = 0; worst2 = 0; worst_rD = 0
import numpy as np
for r in list(np.linspace(0.01, 12, 600)) + [mpf(10)**-3, mpf(10)**-6]:
    r = mpf(r); v = 1 - r*D(r)
    worst1 = max(worst1, abs(v)); worst2 = max(worst2, abs(v)*r*r/8); worst_rD = max(worst_rD, r*D(r))
print("sup|1-ϱD| (표본) =", worst1, " sup ϱD =", worst_rD, " (1.514 이하?)")
print("sup |1-ϱD|·ϱ²/8 (표본) =", worst2, " (1 이하면 (나) 성립)")
# 지배함수 적분 가능성 (m=0, j=0..3, η0=0.5)
for m in (0, 1):
    for j in range(0, 4):
        eta0 = mpf('0.5')
        f = lambda r: r**(2*m+2*j)*min(1, 8/(r*r))*exp(-eta0*r*r/2)
        print(f"m={m} j={j} ∫ 지배함수 =", quad(f, [0, sqrt(8), inf]))
# 옛 지배함수 m=0: 8ϱ^{-2}e^{-ηϱ²/2}는 원점에서 발산
print("옛 지배함수 m=0, [1e-6,1] 적분 =", quad(lambda r: 8/(r*r)*exp(-r*r/4), [mpf(10)**-6, 1]), "(1/ε 규모 → 발산)")
# 𝔧_m 항등식 수치 확인: 𝔧_1(η) = -2 𝔉'(η)
F = lambda s: sqrt(pi/2)*sqrt(s)/(s+1)
from mpmath import diff
eta = mpf('0.7')
j1 = quad(lambda r: r**2*(1-r*D(r))*exp(-eta*r*r/2), [0, 5, 20, inf])
print("𝔧_1(0.7) =", j1, " -2𝔉'(0.7) =", -2*diff(F, eta))
j0 = quad(lambda r: (1-r*D(r))*exp(-eta*r*r/2), [0, 5, 20, inf])
print("𝔧_0(0.7) =", j0, " 𝔉(0.7) =", F(eta))
mp.dps = 60  # 소거 손실을 피하려 자릿수 올림
# D.30 (ㄱ): 상대 차 ((e^z-1)/z - 1) ≤ z e^z/2, z = 𝔰 st ≤ 1e-14·0.3
z = mpf('1e-14')*mpf('0.3')
rel = (exp(z)-1)/z - 1
print("z=3e-15: 상대 차 =", rel, " 상계 z e^z/2 =", z*exp(z)/2, " < 2e-15?", rel < mpf('2e-15'))
z = mpf('1e-14')*mpf('0.29933')
print("z=(10.973+1)/40·1e-14: 상대 차 =", (exp(z)-1)/z - 1)
# 급수 확인: Σ_{n≥1} z^n/(n+1)! ≤ (z/2) e^z
for zz in (mpf('0.5'), mpf('1'), mpf('3')):
    print("z=",zz," (e^z-1)/z-1 =", (exp(zz)-1)/zz-1, " z e^z/2 =", zz*exp(zz)/2)
