# -*- coding: utf-8 -*-
"""외부 지적 검증: 보조정리 5.41(조립 5.77)의 C_I(eta) 정의(본문 646행)를 직접 수치 적분하고,
부록 D.21 식 줄의 두 판(υ^5·υ^6 / υ^10·υ^12)과 지적의 닫힌 꼴 √π(6−23√2)를 비교한다."""
from mpmath import mp, mpf, quad, sqrt, pi, exp, inf

mp.dps = 30


def body(eta):
    # ∫_R ∫_0^1 υ^4 ρ^2 Q0 e^{-ηυ^2/2 - ρ^2υ^2/2} [4/3 ρ^2 υ^2 - (1+η)/3 ρ υ^4] dρ dυ,  Q0 = μυ^2 + μ^2υ^4/4, μ = 1-ρ^2
    def f(u, r):
        mu = 1 - r * r
        Q0 = mu * u * u + mu * mu * u ** 4 / 4
        return u ** 4 * r * r * Q0 * exp(-eta * u * u / 2 - r * r * u * u / 2) * (mpf(4) / 3 * r * r * u * u - (1 + eta) / 3 * r * u ** 4)
    return quad(lambda u: quad(lambda r: f(u, r), [0, 1]), [-inf, 0, inf])


def I(i, u):
    return quad(lambda r: r * (1 - r) ** i * exp(-u * u * r / 2), [0, 1])


def appendix(eta, powers):
    a, b = powers
    first = 8 * sqrt(2 * pi) * eta ** -3 * (1 + eta) ** mpf(-1.5)
    # (ㄴ)으로 적분한 ... : 여기서는 Gauss 무게 e^{-ηυ^2/2}로 υ∈[0,∞) 적분(짝함수의 절반 → 계수 2(1+η)/3)
    neg = quad(lambda u: mpf(1) / 2 * (u ** a * I(1, u) + u ** b / 4 * I(2, u)) * exp(-eta * u * u / 2), [0, inf])
    return first - 2 * (1 + eta) / 3 * neg


def positive_part(eta):
    def f(u, r):
        mu = 1 - r * r
        Q0 = mu * u * u + mu * mu * u ** 4 / 4
        return u ** 4 * r * r * Q0 * exp(-eta * u * u / 2 - r * r * u * u / 2) * (mpf(4) / 3 * r * r * u * u)
    return quad(lambda u: quad(lambda r: f(u, r), [0, 1]), [-inf, 0, inf])


for eta in (mpf(1), mpf("0.5"), mpf(2)):
    print("eta =", eta)
    print("  본문 정의 직접 적분      :", body(eta))
    print("  양의 부분만              :", positive_part(eta), " 대 8√(2π)η^-3(1+η)^-3/2 =", 8 * sqrt(2 * pi) * eta ** -3 * (1 + eta) ** mpf(-1.5))
    print("  부록 식(υ^5, υ^6)        :", appendix(eta, (5, 6)))
    print("  부록 식(υ^10, υ^12)      :", appendix(eta, (10, 12)))
print("지적의 닫힌 꼴 √π(6−23√2) =", sqrt(pi) * (6 - 23 * sqrt(2)))
