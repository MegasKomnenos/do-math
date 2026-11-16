# -*- coding: utf-8 -*-
"""3_검산_극한법칙.py -- 3.1·3.2·3.3절의 식·상수를 mpmath로 다시 계산한다.

(1) Legendre 배가 공식 Γ(1/3)Γ(5/6) = 2^{1/3}√π Γ(2/3)
(2) 본문 (3.1절) 멜린 변환 식 vs Janson Theorem 1.12 셋째 식 (복소 σ 여러 점)
(3) 곱 표현의 세 기댓값을 밀도의 직접 적분으로 (σ 하나에서) 확인
(4) 본문 식에서 끌어낸 E[B^s] (Janson Lemma 1.11) vs Petersson Theorem 2.10 의 정수 모멘트, 그리고 E B = (2/3)√(2/π)
(5) σ=3/2 극 잔차 → 꼬리 상수 3/√(2π); ∫_ς^∞ (3/√(2π)) x^{-5/2} = √(2/π) ς^{-3/2}; (2^{-3/2})^2/3^{-3/2} = (3/4)^{3/2}
(6) 기울인 모수 (1+2ρ)/3, (7-2ρ)/6, (5-2ρ)/6 (sympy) 와 범위 -1/2<ρ<5/2
(7) K_ρ 의 로그 도함수 -3τ - (5/2)/(e^{3z}-1)
"""
from mpmath import mp, mpf, gamma, sqrt, pi, quad, exp, log, inf, mpc, beta as mbeta
import sympy as sp

mp.dps = 30

print("(1) Legendre:", gamma(mpf(1)/3)*gamma(mpf(5)/6), "vs", 2**(mpf(1)/3)*sqrt(pi)*gamma(mpf(2)/3))

def mellin_text(s):
    s = mpc(s)
    return (mpf(3)/2)**(s/3)*gamma(1+2*s/3)*gamma(mpf(5)/6-s/3)/gamma(mpf(5)/6) \
        * gamma(mpf(1)/2-s/3)*gamma(mpf(2)/3)/(gamma(mpf(1)/2)*gamma(mpf(2)/3-s/3))

def mellin_janson3(s):
    s = mpc(s)
    return gamma(mpf(1)/3)/(2**(mpf(1)/3)*pi)*gamma(1+2*s/3)*gamma(mpf(1)/2-s/3)*gamma(mpf(5)/6-s/3)/gamma(mpf(2)/3-s/3)*(mpf(3)/2)**(s/3)

def mellin_janson1(s):
    s = mpc(s)
    return gamma(1+2*s/3)*gamma(mpf(2)/3-2*s/3)*gamma(1-2*s/3)/(gamma(mpf(2)/3)*gamma(1-s))*(2/mpf(3)**(mpf(2)/3))**s

print("(2) 본문 식 vs Janson 1.12 셋째 식 / 첫째 식")
for s in [mpf('-1.4'), mpf('-0.5'), 0, mpf('0.5'), 1, mpf('1.4'), mpc('0.3','2.0'), mpc('-1','5')]:
    a, b = mellin_text(s), mellin_janson3(s)
    try:
        c = mellin_janson1(s)
    except ValueError:  # 첫째 식은 정수 s에서 Γ(1-s)/Γ(2/3-2s/3) 꼴의 제거 가능한 극을 가짐
        c = mellin_janson1(s + mpf('1e-12'))
    print("  s =", s, " 본문", a, " J3", b, " J1", c, " |차|", abs(a-b), abs(a-c))
print("  E X at s=1:", mellin_text(1), " Janson/Petersson 2Γ(1/3)/3^{2/3} =", 2*gamma(mpf(1)/3)/mpf(3)**(mpf(2)/3))

print("(3) 세 기댓값의 직접 적분, σ = 0.7")
s = mpf('0.7')
EE = quad(lambda z: z**(2*s/3)*exp(-z), [0, inf])
EH = quad(lambda z: z**(-s/3)*z**(mpf(5)/6-1)*exp(-z), [0, 1, inf])/gamma(mpf(5)/6)
# z = 1 - t^6 으로 바꿔 z=1 의 특이점을 없앤다: ∫_0^1 z^{a-1}(1-z)^{-5/6} dz = ∫_0^1 6 (1-t^6)^{a-1} dt
aV = -s/3 + mpf(1)/2
EV = quad(lambda t: 6*(1-t**6)**(aV-1), [0, mpf(1)/2, 1])/mbeta(mpf(1)/2, mpf(1)/6)
print("  E[E^{2σ/3}] =", EE, " Γ(1+2σ/3) =", gamma(1+2*s/3))
print("  E[H^{-σ/3}] =", EH, " Γ(5/6-σ/3)/Γ(5/6) =", gamma(mpf(5)/6-s/3)/gamma(mpf(5)/6))
print("  E[V^{-σ/3}] =", EV, " Γ(1/2-σ/3)Γ(2/3)/(Γ(1/2)Γ(2/3-σ/3)) =", gamma(mpf(1)/2-s/3)*gamma(mpf(2)/3)/(gamma(mpf(1)/2)*gamma(mpf(2)/3-s/3)))
print("  곱 =", (mpf(3)/2)**(s/3)*EE*EH*EV, " 본문 식 =", mellin_text(s))

print("(4) E[B^s] = E X^{-3s/2}/Γ(1-s) 의 해석적 연속 vs Petersson Thm 2.10")
def EB_from_text(sv):
    sv = mpf(sv)
    return (mpf(3)/2)**(-sv/2)*gamma(mpf(5)/6+sv/2)/gamma(mpf(5)/6)*gamma(mpf(1)/2+sv/2)*gamma(mpf(2)/3)/(gamma(mpf(1)/2)*gamma(mpf(2)/3+sv/2))
def EB_petersson(n):
    from mpmath import factorial
    return factorial(n)*gamma(n+mpf(2)/3)/(gamma(mpf(2)/3)*gamma(mpf(3)*n/2+1))*(3*sqrt(2)/4)**n
for n in [1, 2, 3, 4]:
    print("  n =", n, " 본문→", EB_from_text(n), " Petersson", EB_petersson(n))
print("  E B 직접: ∫_0^1 √(2t/π) dt = (2/3)√(2/π) =", mpf(2)/3*sqrt(2/pi))
# 범위 안의 비정수 s 에서도 (Lemma 1.11 그대로) 확인: s = 0.4 → σ = -0.6
sv = mpf('0.4')
print("  s=0.4: E X^{-3s/2}/Γ(1-s) =", mellin_text(-3*sv/2).real/gamma(1-sv), " 닫힌 식 =", EB_from_text(sv))

print("(5) 꼬리 상수")
for eps in [mpf('1e-4'), mpf('1e-6'), mpf('1e-8')]:
    print("  (3/2-σ)·E X^σ at σ=3/2-eps:", (eps*mellin_text(mpf(3)/2-eps)).real, " 3/√(2π) =", 3/sqrt(2*pi))
print("  해석: Pr(X>x)~c x^{-3/2} ⇒ (3/2-σ)E X^σ → (3/2)c, f~(3/2)c x^{-5/2}; 곧 밀도 상수 = 잔차 = 3/√(2π), c = √(2/π) =", sqrt(2/pi))
vs = mpf(7)
print("  ∫_ς^∞ 3/√(2π) x^{-5/2} dx (ς=7) =", quad(lambda x: 3/sqrt(2*pi)*x**(-mpf(5)/2), [vs, inf]), " √(2/π) ς^{-3/2} =", sqrt(2/pi)*vs**(-mpf(3)/2))
print("  (2^{-3/2})^2/3^{-3/2} =", (mpf(2)**(-mpf(3)/2))**2/mpf(3)**(-mpf(3)/2), " (3/4)^{3/2} =", (mpf(3)/4)**(mpf(3)/2))

print("(6) 기울인 모수 (sympy)")
z, r = sp.symbols('z rho', positive=True)
# Gamma(1): e^{-z} · z^{2(ρ-1)/3} → z^{a-1}, a = ?
a1 = sp.simplify(2*(r-1)/3 + 1)
a2 = sp.simplify(-sp.Rational(1, 6) - (r-1)/3 + 1)
a3 = sp.simplify(-sp.Rational(1, 2) - (r-1)/3 + 1)
print("  Gamma(1) 기울임 모수:", a1, " 본문 (1+2ρ)/3:", sp.simplify(a1 - (1+2*r)/3) == 0)
print("  Gamma(5/6) 기울임 모수:", a2, " 본문 (7-2ρ)/6:", sp.simplify(a2 - (7-2*r)/6) == 0)
print("  Beta 첫 모수:", a3, " 본문 (5-2ρ)/6:", sp.simplify(a3 - (5-2*r)/6) == 0)
print("  양수 범위:", sp.solve([a1 > 0, a2 > 0, a3 > 0], r))
print("  ρ-1 범위 -3/2<ρ-1<3/2 ⇔ -1/2<ρ<5/2 (일치)")

print("(7) K_ρ 로그 도함수")
tau = sp.symbols('tau', positive=True)
K = sp.exp(-3*tau*z)*(1-sp.exp(-3*z))**sp.Rational(-5, 6)
dlogK = sp.simplify(sp.diff(sp.log(K), z))
target = -3*tau - sp.Rational(5, 2)/(sp.exp(3*z)-1)
print("  (log K)' - 본문 =", sp.simplify(dlogK - target))
# V = e^{-3Z} 변수 변환: V 밀도 v^{τ-1}(1-v)^{-5/6}, |dV/dz| = 3 e^{-3z}
v_dens = (sp.exp(-3*z))**(tau-1)*(1-sp.exp(-3*z))**sp.Rational(-5, 6)*3*sp.exp(-3*z)
print("  Z 밀도 / K_ρ =", sp.simplify(v_dens/K))
# (log η)' 와 ∫_0^φ η
phi = sp.symbols('phi', positive=True)
eta = phi**sp.Rational(-1, 2)*(1-phi)**sp.Rational(-3, 2)
print("  (log η)' =", sp.simplify(sp.diff(sp.log(eta), phi)), "; 영점:", sp.solve(sp.diff(sp.log(eta), phi), phi))
dd = sp.diff(2*sp.sqrt(phi/(1-phi)), phi) - eta
print("  d/dφ 2√(φ/(1-φ)) - η at φ=0.1,0.3,0.7:", [sp.N(dd.subs(phi, v), 20) for v in (sp.Rational(1, 10), sp.Rational(3, 10), sp.Rational(7, 10))])
# log-Gamma 밀도의 로그 이계도함수
b = sp.symbols('beta', positive=True)
print("  (log exp(βz-e^z))'' =", sp.diff(b*z-sp.exp(z), z, 2))
