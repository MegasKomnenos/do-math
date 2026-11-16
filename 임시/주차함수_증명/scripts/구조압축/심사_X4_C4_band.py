# -*- coding: utf-8 -*-
"""심사 X4 — C4(이음 행 변경)의 조립 재계산.

부록 D.{{D:band-check}}의 다섯 포락선을 그대로 구현하되, 꼬리 창 폭의 상계 wid <= c y^{2/3} + c0 의 계수 (c, c0)와 w0 를 매개변수로 둔다.
  현행:  r_0(m)=floor(0.75 m^{2/3}) → wid <= 0.75(1.1y)^{2/3}+1  (c=0.75*1.1^{2/3}=0.79934, c0=1)
  F3:    a=.82               → c=.82*1.1^{2/3}=0.87393,  c0=1   (원고와 같은 유도)
  F7:    a=13/16             → c=0.8125*1.1^{2/3}=0.86594, c0=1
  F4:    t̃_0(y)=1+min{m>=y+1: y<=m-ceil(m^{2/3})} → wid <= 1.03 y^{2/3}+2 (이 스크립트의 유도; F4는 +1)
(가) λ∈[1/2,2/3]의 4000셀(n=50001)에서 (5.4)의 좌변 하계의 최솟값(=비).
(나) 오른쪽 부분(λ>2/3)의 네 상수와 Ψ_R 하계의 재계산(보조정리 5:right-part의 논법 그대로, wid 계수만 바꿈).
(다) 이음 상수의 기하 조건: a∈{.82, 13/16}에서 m>=25002일 때 r_a(m)=floor(a m^{2/3})가 598 이상이고 .73 < r_a^{3/2}/m <= 1.2 인지; r_a(m) <= 𝔪(m) 가 깨지는 m의 범위; F4의 ceil(m^{2/3}) > 𝔪(m) 확인.
"""
import mpmath as mp
from math import floor, ceil, isqrt
import sys

mp.mp.dps = 30
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

def bor(i):
    i = mp.mpf(i)
    return mp.e**(-i) * i**(i - 1) / mp.factorial(i)

def band_min(c, c0, w0, n=50001, cells=4000, report_first=True):
    n = mp.mpf(n)
    lo, hi = mp.mpf(1) / 2, mp.mpf(2) / 3
    best = None
    for i in range(cells):
        la = lo + (hi - lo) * i / cells
        lb = lo + (hi - lo) * (i + 1) / cells
        widb = c * (lb * n)**(mp.mpf(2) / 3) + c0
        # 조건 확인(따름정리 old-5-34): 0.4(1-λ)n >= 6(λn)^{2/3}+1 ; wid <= 0.7(n-y) (χ2 <= n-y-wid)
        cond1 = mp.mpf('0.4') * (1 - lb) * n >= 6 * (lb * n)**(mp.mpf(2) / 3) + 1
        cond2 = widb <= mp.mpf('0.7') * (1 - lb) * n
        # hov 하계
        chi_lb = mp.floor(mp.mpf('0.3') * (1 - lb) * n - 1) - 1
        rho = la - 1 / n
        hov = mp.mpf(0); z = 0
        while True:
            term = 1 - 2 / mp.sqrt(mp.pi) * mp.mpf(z)**1.5 / mp.sqrt(chi_lb)
            if term <= 0:
                break
            hov += rho**z * term; z += 1
        # 둘째 포락선
        sec = 1 - mp.sqrt(2 / mp.pi) * (mp.mpf('0.3') * (1 - lb) * n - 1)**(-0.5) \
            - mp.mpf('0.3') * (1 - la) * n * (2 * mp.pi)**(-0.5) * ((n + 1) / (la * n * ((1 - lb) * n - widb)))**1.5 * mp.e**(1 / (12 * (n + 1)))
        top = (2 * mp.pi)**(-0.5) * (1 + 1 / n)**1.5 * la**(-0.5) * (1 - lb)**(-1.5) * n**(-0.5) * mp.e**(1 / (12 * n))
        Kt = la * mp.e**(-(1 / (12 * (mp.mpf('0.4') * (1 - lb) * n - 6 * (lb * n)**(mp.mpf(2) / 3) + 1)) + 1 / (12 * la * n) + 1 / (12 * (n + 1))))
        c1 = mp.mpf('1.5') * ((2 * lb - 1) * n + 2 * widb) / (la * n * ((1 - lb) * n - widb))
        e0 = mp.mpf('1.5') * widb * ((2 * lb - 1) * n + 2 * widb) / ((la * n - 1) * ((1 - lb) * n - widb))
        W = (2 * mp.pi)**(-0.5) * mp.mpf(2) / 3 * (widb + 1)**1.5 * c1 * (1 + widb / (la * n))**1.5 * mp.e**(e0 + 1 / (12 * la * n))
        ratio = hov * w0 * Kt * (2 * sec - top) - W
        if best is None or ratio < best[0]:
            best = (ratio, i, hov, sec, top, Kt, W, cond1, cond2)
    return best

P("== (가) 조립 범위 4000셀 최소 비 (n=50001)")
variants = [("현행 a=3/4 (c=0.75*1.1^(2/3), c0=1)", mp.mpf('0.75') * mp.mpf('1.1')**(mp.mpf(2) / 3), 1),
            ("F7 a=13/16", mp.mpf(13) / 16 * mp.mpf('1.1')**(mp.mpf(2) / 3), 1),
            ("F3 a=.82", mp.mpf('0.82') * mp.mpf('1.1')**(mp.mpf(2) / 3), 1),
            ("F4 ceil(m^{2/3}) (c=1.03, c0=2)", mp.mpf('1.03'), 2),
            ("F4 ceil(m^{2/3}) (c=1.03, c0=1; F4 표기)", mp.mpf('1.03'), 1)]
cells = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
for name, c, c0 in variants:
    for w0 in [mp.mpf('0.71216'), mp.mpf('0.7')]:
        b = band_min(c, c0, w0, cells=cells)
        P(f"{name}, w0={w0}: 최소 비 {mp.nstr(b[0],7)} (셀 {b[1]}); hov>={mp.nstr(b[2],6)}, 둘째>={mp.nstr(b[3],6)}, top<={mp.nstr(b[4],6)}, K>={mp.nstr(b[5],6)}, W<={mp.nstr(b[6],6)}; 조건(0.4(1-λ)n>=6(λn)^(2/3)+1)={b[7]}, wid<=0.7(n-y)={b[8]}")

P("== (나) 오른쪽 부분(λ>2/3) 상수 재계산 — y>=33334, r>=10357, 10 y^{2/3} < r+1")
def right_part(c, c0, w0):
    # wid <= c y^{2/3} + c0 ;  10 y^{2/3} < r+1 → wid <= (c/10)(r+1) + c0
    y = mp.mpf(33334); r = mp.mpf(10357)
    frac = c / 10
    # 둘째 상수: n+2-t0 = r+1-wid >= (1-frac)(r+1) - c0 ; (n+1)/y <= 1.50003
    # pi_n(t0-1) <= (2pi)^{-1/2} [ (n+1)/(y (n+2-t0)) ]^{3/2} e^{1/(12(n+1))}
    n1 = 50002
    k1 = (2 * mp.pi)**(-0.5) * (mp.mpf('1.50003') / ((1 - frac) - c0 / (r + 1)))**1.5 * mp.e**(1 / (12 * n1))  # (r+1)^{-3/2} 배
    chi2pi = mp.mpf('0.3') * k1 * (r + 1)**(-0.5)   # χ2 <= 0.3 r <= 0.3(r+1)
    chi_w = mp.mpf('0.2') * r - mp.mpf('7.3')
    sec = 1 - mp.sqrt(2 / mp.pi) * chi_w**(-0.5) - chi2pi
    # 넷째 상수: (r+1)/y * W
    wid_r = frac * (r + 1) + c0         # r 기준 상계
    wid_y = c * y**(mp.mpf(2) / 3) + c0  # y 기준 상계
    c1 = mp.mpf('1.5') / (r - wid_r)      # 2 wid <= r 가정 하 c1 <= 1.5/(r-wid)
    ratio_r = (r + 1) / (r - wid_r)
    pow32 = (c * y**(mp.mpf(2) / 3) + c0 + 1)**1.5 / y   # (wid+1)^{3/2} <= (c y^{2/3}+c0+1)^{3/2} ; /y 로 정규화
    eps0 = mp.mpf('1.5') * wid_r / (r + 1 - wid_r)
    onep = (1 + wid_y / y)**1.5
    Wr = (2 * mp.pi)**(-0.5) * mp.mpf(2) / 3 * pow32 * mp.mpf('1.5') * ratio_r * onep * mp.e**(eps0 + 1 / (12 * y))
    # 첫째 상수 ε_hov=0.1573, top_pi<=0.0232 (wid 무관), e^{-c4}>=0.9936
    eps_hov = mp.mpf('0.1573'); top_pi = mp.mpf('0.0232'); ec4 = mp.mpf('0.9936')
    coefA = (1 - eps_hov) * w0 * ec4 * (2 * sec - top_pi) - Wr
    PsiR_at_23 = coefA * mp.mpf(2) / 3 - mp.mpf(1) / 3 - mp.mpf('2.5e-5')
    return sec, Wr, coefA, PsiR_at_23, wid_r / (r + 1)
for name, c, c0 in variants:
    for w0 in [mp.mpf('0.71216'), mp.mpf('0.7')]:
        sec, Wr, A, Psi, wf = right_part(c, c0, w0)
        P(f"{name}, w0={w0}: 둘째상수>={mp.nstr(sec,5)}, (r+1)/y·W<={mp.nstr(Wr,5)}, Ψ_R 계수 {mp.nstr(A,5)}λ-(1-λ), Ψ_R(λ=2/3)>={mp.nstr(Psi,5)}; wid/(r+1)<={mp.nstr(wf,5)}")

P("== (다) 이음 상수의 기하 조건 (m>=25002)")
def mfrak(n):
    # 𝔪(n) = max({170} ∪ {m>=171: m^{3/2}+9m <= n}) ; 정수 비교 m^3 <= (n-9m)^2
    lo, hi = 171, int(n**(2 / 3)) + 2
    best = 170
    for m in range(171, hi + 1):
        if n - 9 * m > 0 and m**3 <= (n - 9 * m)**2:
            best = m
    return best
for a_name, a in [("13/16", mp.mpf(13) / 16), (".82", mp.mpf('0.82')), ("3/4(현행)", mp.mpf('0.75'))]:
    worst_x = None; first_ok = None
    for m in [25002, 25003, 26000, 30000, 50001, 100000, 10**6, 10**7]:
        ra = int(mp.floor(a * mp.mpf(m)**(mp.mpf(2) / 3)))
        x32 = mp.mpf(ra)**1.5 / m
        mm = mfrak(m) if m <= 10**6 else None
        P(f"  a={a_name} m={m}: r_a={ra} (>=598: {ra>=598}) x^(3/2)={mp.nstr(x32,6)} (.73<x<=1.2: {mp.mpf('0.73')<x32<=mp.mpf('1.2')}); 𝔪(m)={mm}; r_a<=𝔪: {None if mm is None else ra<=mm}")
    # r_a(m) <= 𝔪(m) 가 처음 성립하는 m (a^{3/2} + 9 a m^{-1/3} <= 1 근사)
    mstar = ((9 * a) / (1 - a**1.5))**3
    P(f"  a={a_name}: r_a(m)<=𝔪(m) 근사 문턱 m >= {mp.nstr(mstar,6)}")
P("  F4: ceil(m^{2/3}) > 𝔪(m) ? (𝔪(m) < m^{2/3} 는 5.2.2절에서 n>=20001에 증명됨)")
for m in [25002, 50001, 100000, 10**6]:
    P(f"   m={m}: ceil(m^(2/3))={ceil(m**(2/3))}, 𝔪(m)={mfrak(m)}")
# F4 폭 상수: wid <= c y^{2/3}+2 with c >= (1 + c y^{-1/3} + 2/y)^{2/3} at y=25000
y = mp.mpf(25000)
for cc in [mp.mpf('1.03'), mp.mpf('1.025')]:
    P(f"  F4 폭 계수 c={cc}: (1 + c y^(-1/3) + 2/y)^(2/3) = {mp.nstr((1 + cc * y**(-mp.mpf(1)/3) + 2/y)**(mp.mpf(2)/3),6)} <= c ? {(1 + cc * y**(-mp.mpf(1)/3) + 2/y)**(mp.mpf(2)/3) <= cc}")
# 현행 wid 상계의 실제 여유: 0.75(1+0.75 y^{-1/3}+...)^{2/3}
P(f"  현행 c=0.75·1.1^(2/3)={mp.nstr(mp.mpf('0.75')*mp.mpf('1.1')**(mp.mpf(2)/3),6)}; a=.82 → {mp.nstr(mp.mpf('0.82')*mp.mpf('1.1')**(mp.mpf(2)/3),6)}; a=13/16 → {mp.nstr(mp.mpf(13)/16*mp.mpf('1.1')**(mp.mpf(2)/3),6)}")

open(__file__.replace('.py', '_out.txt'), 'w', encoding='utf-8').write("\n".join(out) + "\n")
