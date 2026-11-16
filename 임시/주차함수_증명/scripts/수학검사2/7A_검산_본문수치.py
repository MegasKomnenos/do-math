# -*- coding: utf-8 -*-
"""7A 검산: 장7A.md 본문의 소수·정수 상수를 정의대로 다시 계산한다(mpmath 50자리).
대상: 71행(𝗍_k 범위), 157행(𝔬_k>2), 336–342행(열 인증 (가)의 사슬), 547·551행(따름정리 S′의 수치),
627행(비의 극한), 715행(ς_k>0), 862행(보조정리 polar-N), 883행(명제 polar-W의 ψ_V(n°_k)>0 사슬), 599행(Riccati 반례).
실행: python -I scripts/수학검사2/7A_검산_본문수치.py"""
import mpmath as mp
from fractions import Fraction as Fr
from math import comb, factorial
mp.mp.dps = 50
e = mp.e

def tk(k):
    j = 0
    while (k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) < 2 * k ** (2 * j + 1):
        j += 1
    return j
print("[71행] 𝗍_k (k=2..10, 100, 500, 2001):", [(k, tk(k)) for k in [2, 3, 4, 5, 10, 100, 500, 2001]], " 𝗍_k/k≈", mp.nstr(mp.mpf(tk(2001)) / 2001, 4))
# e^t+e^{-2t}=2 의 근
print("  연속 극한 t*: ", mp.nstr(mp.findroot(lambda t: mp.e ** t + mp.e ** (-2 * t) - 2, 0.5), 6))
for k in [2, 41, 501]:
    ok = -2 * mp.log(1 - mp.mpf(1) / k) / mp.log(1 + mp.mpf(1) / k)
    print(f"[157행] k={k}: 𝔬_k={mp.nstr(ok, 8)} (>2: {ok > 2}); 2(k+1)/(k-1)={mp.nstr(mp.mpf(2*(k+1))/(k-1), 6)}")
# 336–342행
print("[336행] k=41: 2(k+1)/(k-1)=", Fr(84, 40), "=", float(Fr(84, 40)), "≤21/10:", Fr(84, 40) <= Fr(21, 10), "; 𝔵♭=40/41:", Fr(40, 41))
print("[338행] 1-(21/10)(10/17)^3 =", mp.nstr(1 - mp.mpf(21) / 10 * (mp.mpf(10) / 17) ** 3, 6), ">0")
v = mp.mpf(40) / 41 * (mp.mpf(10) / 17) ** (mp.mpf(21) / 10)
print("[340행] (40/41)(10/17)^{21/10} =", mp.nstr(v, 8), "> 3/10:", v > 0.3, "; ϕ♯(17/10)+2 ≥ 17/10+그 값 =", mp.nstr(mp.mpf(17) / 10 + v, 6))
L = 10 ** 21 * 400 ** 10; Rr = 17 ** 21 * 123 ** 10
print("[342행] 10^21·400^10 =", L, "=", mp.nstr(mp.mpf(L), 8), "; 17^21·123^10 =", Rr, "=", mp.nstr(mp.mpf(Rr), 8), "; 좌>우:", L > Rr)
print("   동치 확인: (40/41)^10 (10/17)^21 > (3/10)^10 ⟺ 10^31·40^10 > 17^21·41^10·3^10 =", 10 ** 31 * 40 ** 10 > 17 ** 21 * 41 ** 10 * 3 ** 10, "; 41·3=123, 40^10·10^10=400^10:", 40 ** 10 * 10 ** 10 == 400 ** 10)
print("   사슬: 17^4=", 17 ** 4, "<8.36e4:", 17 ** 4 < 8.36e4, "; 17·8.36^5·1e20=", mp.nstr(17 * mp.mpf(8.36) ** 5 * 1e20, 6), "; 8.36^5=", mp.nstr(mp.mpf(8.36) ** 5, 6), "<40836:", mp.mpf(8.36) ** 5 < 40836, "; 17·40836e20=", 17 * 40836e20, "<6.95e25:", 17 * 40836e20 < 6.95e25)
print("   123^2=", 123 ** 2, "<1.513e4:", 123 ** 2 < 1.513e4, "; 1.513^5=", mp.nstr(mp.mpf(1.513) ** 5, 6), "<7.93:", mp.mpf(1.513) ** 5 < 7.93, "; 6.95e25·7.93e20=", mp.nstr(mp.mpf(6.95e25) * 7.93e20, 6), "<5.52e46:", 6.95e25 * 7.93e20 < 5.52e46, "; 실제 17^21=", mp.nstr(mp.mpf(17 ** 21), 6), " 123^10=", mp.nstr(mp.mpf(123 ** 10), 6))
# 547·551행
for (k0, y, B0, c1, c2) in [(501, Fr(13, 100), Fr("0.098505"), "0.0030", "0.0495"), (1855, Fr(2, 25), Fr("0.060259"), "0.0009", "0.0302"), (6098, Fr(11, 200), Fr("0.0422"), "0.0003", "0.0212")]:
    xi = Fr(1, k0)
    a = (3 * xi + xi * xi) / 2; b = (1 + xi) ** 2 * B0 / 2
    print(f"[547/551행] k0={k0}: 𝗒k0²-2k0-1={float(y*k0*k0-2*k0-1):.1f}>0; (3ξ+ξ²)/2={float(a):.7f}<{c1}: {a < Fr(c1)}; (1+ξ)²𝔅0/2={float(b):.7f}<{c2}: {b < Fr(c2)}; 합<𝗒: {a + b < y}")
    for B0b in [Fr("0.098504"), Fr("0.0985043")]:
        if k0 == 501:
            print(f"    참고: 𝔅0={B0b}일 때 (1+ξ)²𝔅0/2={float((1+xi)**2*B0b/2):.7f}")
# 627행
for n in [10, 100, 1000]:
    r = mp.mpf(n) ** n / (mp.mpf(n - 1) ** (n - 1) * (n + 1))
    print(f"[627행] n={n}: n^n/((n-1)^(n-1)(n+1)) = {mp.nstr(r, 8)} → e={mp.nstr(e, 8)}")
# 862행
k = 2001
print("[862행] 2/√2001 =", mp.nstr(2 / mp.sqrt(2001), 6), "<0.0448")
ee = mp.mpf("0.0448")
print("   𝔢⁴/(12(1-𝔢²))/𝔢² at 𝔢=0.0448:", mp.nstr(ee ** 2 / (12 * (1 - ee ** 2)), 6), "≤0.0002; 2(cosh𝔢-1)/𝔢²=", mp.nstr(2 * (mp.cosh(ee) - 1) / ee ** 2, 8), "≤1.001")
xk = (mp.mpf(k) / (k + 1)) ** (k - 1)
print("   𝗑_2001 =", mp.nstr(xk, 8), "; e^{-1+2/2002}=", mp.nstr(mp.e ** (-1 + mp.mpf(2) / 2002), 8), "<0.3683; e^{-1}=", mp.nstr(1 / e, 8), ">0.3678")
print("   0.3683(2/√k+1/k²) at k=2001:", mp.nstr(mp.mpf("0.3683") * (2 / mp.sqrt(k) + mp.mpf(1) / k ** 2), 6), "; 0.75/√2001=", mp.nstr(mp.mpf("0.75") / mp.sqrt(2001), 6), "≤0.017")
print("   e^{-0.0448}=", mp.nstr(mp.e ** (-ee), 6), "≥0.955; (1-0.0085)=0.9915≥0.991; 0.955·0.991·0.3678=", mp.nstr(mp.mpf("0.955") * mp.mpf("0.991") * mp.mpf("0.3678"), 6), ">0.348")
print("   0.348/1.001=", mp.nstr(mp.mpf("0.348") / mp.mpf("1.001"), 6), "≥0.3476; 2·2001^{3/2}+1=", mp.nstr(2 * mp.mpf(2001) ** 1.5 + 1, 8), "≤179021; 0.3476·2001²=", mp.nstr(mp.mpf("0.3476") * 2001 ** 2, 8), "≥1.39e6")
print("   ⌈2·2001^{3/2}⌉ =", int(mp.ceil(2 * mp.mpf(2001) ** 1.5)))
# 883행
k = mp.mpf(10) ** 7; V = mp.mpf("0.9") / mp.sqrt(k); nck = mp.ceil(2 * k ** 1.5)
msh = (nck - k) / (k + 1); nu = V * nck / k
print("[883행] k=1e7: n°=", nck, " 𝔪♯=", mp.nstr(msh, 10), " 2√k-1.001=", mp.nstr(2 * mp.sqrt(k) - 1.001, 10), " 2√k=", mp.nstr(2 * mp.sqrt(k), 10), " ν=", mp.nstr(nu, 6), "≤1.81")
print("   (1+0.91/√k)^3·8=", mp.nstr(8 * (1 + mp.mpf("0.91") / mp.sqrt(k)) ** 3, 8), "≤8.01; 8.01/6=", mp.nstr(mp.mpf("8.01") / 6, 5), "≤1.34; (4.004+3+1.34)/√k=", mp.nstr(mp.mpf("8.344") / mp.sqrt(k), 6), "≤0.0027")
lgp = mp.log(1 + 1 / k); lgm = -mp.log(1 - 1 / k)
psi = mp.e ** (msh * lgp) - 1 - (1 - mp.e ** (-(msh + nu) * lgm))
print("   실제 ψ_V(n°_k)·k =", mp.nstr(psi * k, 8), " (하계 (4-1.81-0.0027)=", 4 - 1.81 - 0.0027, ")")
# 599행 Riccati 반례 (k,z,n)=(3,1,2)
# 좌변: Σ_σ ∏min(h_i,3)·η_1(σ) over S_2
import itertools
def caps(s):
    h = []
    for i, v in enumerate(s):
        j = i - 1
        while j >= 0 and s[j] < v: j -= 1
        h.append(i - j)
    return h
lhs = 0
for s in itertools.permutations([1, 2]):
    h = caps(s); w = 1
    for x in h: w *= min(x, 3)
    lhs += w * sum(1 for x in h if x == 1)
# 우변: 2![x^2](A_2 γ̂_1 + 3 Ex 𝔧_1/Δ²), Q_2'=2+x
x = mp.mpf(0)
import sympy as sp
X = sp.symbols('x')
Q2 = 2 * X + X ** 2 / 2
Ex = sp.exp(-Q2)
Delta = 1 - 3 * sp.integrate(Ex, (X, 0, X))
A2 = Ex / Delta
j1 = sp.integrate(X * Ex, (X, 0, X))
rhs_series = sp.series(A2 * X + 3 * Ex * j1 / Delta ** 2, X, 0, 3).removeO()
print("[599행] (k,z,n)=(3,1,2): 좌변 n!계수 =", lhs, "; 우변 2![x^2] =", 2 * rhs_series.coeff(X, 2))
# 715행: ς_k>0 ⟺ ρ_k>1/e ; ρ_2=log2
print("[631행] ρ_2=log2=", mp.nstr(mp.log(2), 8), "; ς_2=2log(e·log2)=", mp.nstr(2 * mp.log(mp.e * mp.log(2)), 8), ">0")
