# -*- coding: utf-8 -*-
"""7A 검산: 정리 self-consistent-S (다)의 표와 따름정리 cor-S-prime의 세 값을
본문 정의(장7A.md 452-555행)대로 정확 유리수 + mpmath(e^{-i} 구간)로 다시 계산한다.
기록 rad00a59의 cert_S.py와 독립으로 정의에서 짰다. 실행: python -I scripts/수학검사2/7A_검산_selfconsistent.py"""
from fractions import Fraction as Fr
from math import factorial
import mpmath as mp
from mpmath import iv

iv.dps = 60
mp.mp.dps = 60

def a_circ(m):  # 𝔞°_m=(m+1)^{m-1}/m!
    return Fr(1) if m == 0 else Fr((m + 1) ** (m - 1), factorial(m))

def free_ratio(m):  # e^{g(m+1)}=𝔞°_{m+1}/𝔞°_m
    return a_circ(m + 1) / a_circ(m)

def jstar(c):
    m = 0
    while free_ratio(m) < c:
        m += 1
    return m - 1

def kR(c):
    J = jstar(c)
    need = c ** (J + 2) / a_circ(J + 1)
    return max(2 * J + 2, -((-need.numerator) // need.denominator)), J

def I(x):
    return iv.mpf(x.numerator) / iv.mpf(x.denominator)

def tier(c, JS, k0, y):
    kr, J = kR(c)
    assert k0 >= kr and 1 <= JS <= J
    # 𝔈̲_J(k0)=Σ_{i=1}^{k0-J*} (𝔞°_{J+i}/𝔞°_J) e^{-i}
    El = iv.mpf(0)
    for i in range(1, k0 - J + 1):
        El += I(a_circ(JS + i) / a_circ(JS)) * iv.exp(-i)
    ci = I(c)
    Einf = (ci / iv.e) * (1 - (ci / iv.e) ** k0) / (1 - ci / iv.e)
    R_true_hi = max((1 / (1 + El)).b, (1 / (1 + Einf)).b)   # 참 𝔑_J의 상단
    R_true_lo = max((1 / (1 + El)).a, (1 / (1 + Einf)).a)
    # 기록 cert_S.py와 같은 올림: 40자리 십진으로 적고 1e-25를 더한다
    R = Fr(mp.nstr(mp.mpf(R_true_hi), 40, strip_zeros=False)) + Fr(1, 10 ** 25)
    xbar = [a_circ(t) / c ** (t + 1) for t in range(JS)]
    qlow = []; cum = Fr(0)
    for t in range(JS):
        qlow.append(max(Fr(0), 1 - cum)); cum += xbar[t]
    Xi = sum(max(Fr(0), xbar[t] - R * qlow[t]) for t in range(JS))
    xk0 = Fr(k0, k0 + 1) ** (k0 - 1)
    Xik = sum(max(Fr(0), a_circ(t) * xk0 / c ** t - R * qlow[t]) for t in range(JS))
    A0 = xk0 + Xik / (c * (1 - Xi)); B0 = R * (1 + Xik / (1 - Xi))
    xi = Fr(1, k0)
    g = (y - xi) * (y - 2 * xi - xi * xi) - (1 + xi) ** 2 * (A0 * xi + B0 * y)
    vert = (3 * xi + xi * xi) / 2 + (1 + xi) ** 2 * B0 / 2
    f = lambda q, d=10: mp.nstr(mp.mpf(q.numerator) / q.denominator, d)
    print(f"층 ς={c} J^S={JS} k0={k0} 𝗒={y}: 𝔧*={J} k_R={kr}")
    print(f"  참 𝔑_J 구간 [{mp.nstr(mp.mpf(R_true_lo),12)}, {mp.nstr(mp.mpf(R_true_hi),12)}], 1/(1+𝔈̲)={mp.nstr(mp.mpf((1/(1+El)).b),10)}, 1/(1+𝔈∞)={mp.nstr(mp.mpf((1/(1+Einf)).b),10)}")
    print(f"  올린 𝔑_J={f(R,12)}  Ξ={f(Xi)}  Ξ^(k0)={f(Xik)}  𝔄0={f(A0)}  𝔅0={f(B0)}")
    print(f"  𝗑_k0={f(xk0)}  𝔤_S(𝗒k0^2)/k0^4={mp.nstr(mp.mpf(g.numerator)/g.denominator, 6)}  꼭짓점/k0^2={f(vert,6)}  Ξ<1:{Xi<1}  g>0:{g>0}  꼭짓점≤𝗒:{vert<=y}")
    print(f"  꼭짓점 두 조각: (3ξ+ξ^2)/2={f((3*xi+xi*xi)/2,6)}  (1+ξ)^2𝔅0/2={f((1+xi)**2*B0/2,6)}")
    print(f"  𝗒k0^2-2k0-1={float(y*k0*k0-2*k0-1):.1f}")
    return dict(R=R, Xi=Xi, Xik=Xik, A0=A0, B0=B0, g=g)

tiers = [(Fr(267, 100), 25, 501, Fr(13, 100)), (Fr(27, 10), 70, 1855, Fr(2, 25)), (Fr(271, 100), 100, 6098, Fr(11, 200))]
stated = [  # 표(장7A 507-509행; 부록 D 53행): R≤, Ξ, Ξ^(k0), A0≤, B0≤, g
    (Fr("0.024991"), Fr("0.749711"), Fr("0.736245"), Fr("1.4708"), Fr("0.098504"), "3.250e-4"),
    (Fr("0.008802"), Fr("0.854757"), Fr("0.849132"), Fr("2.5335"), Fr("0.060259"), "7.808e-5"),
    (Fr("0.005691"), Fr("0.865504"), Fr("0.862859"), Fr("2.7354"), Fr("0.0422"), "2.275e-4"),
]
for (c, JS, k0, y), st in zip(tiers, stated):
    r = tier(c, JS, k0, y)
    print(f"  적힌 값 대조: 𝔑_J≤{st[0]}: {'성립' if r['R'] <= st[0] else '위반(참값이 더 큼)'}; "
          f"Ξ={st[1]}: 차={float(r['Xi']-st[1]):.2e}; Ξ^(k0)={st[2]}: 차={float(r['Xik']-st[2]):.2e}; "
          f"𝔄0≤{st[3]}: {'성립' if r['A0'] <= st[3] else '위반'}; 𝔅0≤{st[4]}: {'성립' if r['B0'] <= st[4] else '위반(참값이 더 큼)'}; g≈{st[5]}")
    print()

# 보조정리 lemma-R-sc 대표값과 2<ς<e, 자유 비 증가 확인
print("자유 비 e^{g(m+1)} 처음 다섯:", [float(free_ratio(m)) for m in range(5)], "증가?", all(free_ratio(m) < free_ratio(m + 1) for m in range(300)))
# 따름정리 cor-S-prime 547행의 세 수
for k0, y in [(501, Fr(13, 100)), (1855, Fr(2, 25)), (6098, Fr(11, 200))]:
    print(f"k0={k0}: 𝗒k0^2-2k0-1 = {float(y*k0**2-2*k0-1):.1f} (>0)")
