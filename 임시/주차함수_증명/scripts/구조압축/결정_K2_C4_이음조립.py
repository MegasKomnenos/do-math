# -*- coding: utf-8 -*-
# 결정 K2 — C4: W 경계 이음 t0^W(y) := 1 + min{m >= y+1 : m - y >= 𝔪(m)+1} 와 그 폭 wid^W := t0^W(y)-y-1 <= y^{2/3}+2 (y>=20001; 표본),
#   𝔪(m) < m^{2/3} - 4.5 m^{1/3} (m >= 20001; 표본) ; 오른쪽 부분(5.64) 상수 네 개를 새 폭·w0=4/5 로 다시 셈 ;
#   조립 범위 λ∈[1/2,2/3] 의 닫힌 꼴 선형 하계 (5.62 둘째 하계 hov >= (1-ρ)^{-1}(1-hv/(1-ρ)) 사용; 모든 n>=50001 에 대해 n=50001 상수가 최악) ;
#   참고로 4000셀 띠 최소 비(5.63 꼴).  실행: python -I 결정_K2_C4_이음조립.py
import sys
from math import sqrt, pi, exp, floor, ceil
sys.stdout.reconfigure(encoding='utf-8')

def frak_m(n):
    # max({170} ∪ {m>=171 : m^{3/2}+9m <= n})  (정수 산술; 조건은 m 에 단조)
    lo, hi = 171, int(n**(2/3))+2
    if 9*lo > n or lo**3 > (n-9*lo)**2:
        return 170
    while lo < hi:
        mid = (lo+hi+1)//2
        if 9*mid <= n and mid**3 <= (n-9*mid)**2:
            lo = mid
        else:
            hi = mid-1
    return lo

def t0W(y):
    m = y+1
    while m - y < frak_m(m) + 1:
        m += 1
    return m + 1

print("(1) W 경계 이음 폭 wid^W(y)=t0^W(y)-y-1 <= y^(2/3)+2 와 𝔪(m) < m^(2/3)-4.5m^(1/3)")
viol = 0; worst = (-1e9, None, None)
ys = list(range(20001, 20101)) + list(range(20101, 200001, 613)) + list(range(200001, 2_000_001, 9973)) + [10**7, 10**8]
for y in ys:
    w = t0W(y) - y - 1
    gap = w - (y**(2/3)+2)
    if gap > 0: viol += 1
    if gap > worst[0]: worst = (gap, y, w)
print(f"   표본 {len(ys)}개(20001..1e8): 위반 {viol}; 최대 (wid^W - y^(2/3) - 2) = {worst[0]:.3f} at y={worst[1]} (wid^W={worst[2]});  wid^W(25000)={t0W(25000)-25001}, wid^W(33334)={t0W(33334)-33335}, wid^W(50001)={t0W(50001)-50002}")
viol2 = 0
for m in list(range(20001, 20201)) + list(range(20201, 3_000_001, 7919)) + [10**7, 10**8, 10**9]:
    if not frak_m(m) < m**(2/3) - 4.5*m**(1/3): viol2 += 1
print(f"   𝔪(m) < m^(2/3) - 4.5 m^(1/3) 위반(표본): {viol2}")
ok = all(((y + ceil(y**(2/3)) + 1) - y >= frak_m(y + ceil(y**(2/3)) + 1) + 1) for y in ys)
print(f"   m=y+ceil(y^(2/3))+1 이 조건 m-y >= 𝔪(m)+1 을 만족(=> t0^W <= y+ceil(y^(2/3))+2, wid^W <= ceil(y^(2/3))+1 <= y^(2/3)+2): {ok}")

# ---------- 오른쪽 부분 (5.64) 상수 ----------
def right_part(cw, cf, c0, w0):
    y0, r0 = 33334, 10357
    a = cw*cf**(2/3)/10;  cy = cw*cf**(2/3)
    eps_hov = 1.6932*(y0**(1/3)/10+1)*(2*y0**(2/3)-7.5)**-0.5
    def chi2pi(r):
        return 0.3*r*(2*pi)**-0.5*(1.50003/((1-a)*(r+1)-c0))**1.5*exp(1/(12*50002))
    sq = sqrt(2/pi)*(0.2*r0-7.3)**-0.5
    B2 = 1 - sq - chi2pi(r0)
    top = 0.0232
    wid_y = cy*y0**(2/3)+c0
    assert 2*(a*(r0+1)+c0) <= r0
    t1 = (wid_y+1)**1.5/y0
    t2 = (r0+1)/(r0-(a*(r0+1)+c0))
    e0 = 1.5*(a*(r0+1)+c0)/((r0+1)-(a*(r0+1)+c0))
    t3 = (1+wid_y/y0)**1.5
    W4 = (2*pi)**-0.5*(2/3)*t1*1.5*t2*t3*exp(e0+1/(12*y0))
    c4 = 1/156 + 1/(12*y0) + 1/(12*50002)
    coef = (1-eps_hov)*w0*exp(-c4)*(2*B2-top) - W4
    Psi = coef*(2/3) - (1/3) - 2.5e-5
    return dict(eps_hov=eps_hov, B2=B2, W4=W4, coef=coef, Psi=Psi, t1=t1, t2=t2, e0=e0, t3=t3, chi2pi=chi2pi(r0), sq=sq)

print("(2) 오른쪽 부분(λ>2/3) 상수 — 폭 상계 y^(2/3)+2, w0=4/5  (현행 본문: 0.1573 / 0.9799 / 0.0232 / 0.3678 / 계수 0.7869 / Ψ_R(2/3)>0.191)")
for (name, cw, cf, c0, w0) in (("현행 폭·현행 w0", 0.75, 1.1, 1, 0.71216), ("W경계 폭·w0=0.8", 1.0, 1.0, 2, 0.8), ("W경계 폭·w0=0.71216(참고)", 1.0, 1.0, 2, 0.71216)):
    d = right_part(cw, cf, c0, w0)
    print(f"   {name}: eps_hov<={d['eps_hov']:.4f}, 둘째>=1-{d['sq']:.5f}-{d['chi2pi']:.5f}={d['B2']:.4f}, (r+1)/y*W<={d['W4']:.4f} [(wid+1)^1.5/y<={d['t1']:.4f}, (r+1)/(r-wid)<={d['t2']:.4f}, eps0<={d['e0']:.4f}, (1+wid/y)^1.5<={d['t3']:.4f}], 계수={d['coef']:.4f}, Psi_R(2/3)>={d['Psi']:.4f}")

# ---------- 조립 범위 λ∈[1/2,2/3] 닫힌 꼴 선형 하계 ----------
# (5.4)×(r+1)/n : Ψ(λ) := (1-ε) w0 e^{-c4} λ (2 B2 - top) - (r+1)/n·W - (1-λ+1/n) >= 0 이면 (5.4).
#  거친 상수(모두 n=50001 에서 최악, λ∈[1/2,2/3], 폭 wid <= y^{2/3}+2 <= (2n/3)^{2/3}+2):
#   χ_w=χ_2=floor(0.3 r), r = n-y ∈ [n/3, n/2] ; ε = hv_χ · n/(r+1)
#   B2 >= 1 - sqrt(2/π) χ^{-1/2} - 0.3 r (2π)^{-1/2} ((n+1)/(y (r+1-wid)))^{3/2} e^{1/(12(n+1))}
#   top <= (2π)^{-1/2}(1+1/n)^{3/2} λ^{-1/2}(1-λ)^{-3/2} n^{-1/2} e^{1/(12n)}
#   c4 = 1/(12(0.4 r - 6 y^{2/3} + 1)) + 1/(12 y) + 1/(12(n+1))
#   (r+1)/n·W = (2π)^{-1/2} (wid+1)^{3/2}/(λn) · [(2λ-1) + 2 wid/n] · (r+1)/(r-wid) · (1+wid/y)^{3/2} e^{ε0 + 1/(12y)}
#       (wid+1)^{3/2} <= (y^{2/3}+3)^{3/2} = y (1+3 y^{-2/3})^{3/2}  =>  (wid+1)^{3/2}/(λn) <= (1+3y^{-2/3})^{3/2}
def crude_constants(n, w0):
    lam_lo, lam_hi = 0.5, 2/3
    y_lo = lam_lo*n; y_hi = lam_hi*n
    r_lo = n - y_hi; r_hi = n - y_lo
    wid = y_hi**(2/3) + 2
    chi_lo = floor(0.3*r_lo)
    hv = chi_lo**-0.5*((2/sqrt(pi))*(1+1/chi_lo) + 1/sqrt(pi))
    eps = hv*n/(r_lo+1)
    B2 = 1 - sqrt(2/pi)*chi_lo**-0.5 - 0.3*r_hi*(2*pi)**-0.5*((n+1)/(y_lo*(r_lo+1-wid)))**1.5*exp(1/(12*(n+1)))
    top = (2*pi)**-0.5*(1+1/n)**1.5*lam_lo**-0.5*(1-lam_hi)**-1.5*n**-0.5*exp(1/(12*n))
    c4 = 1/(12*(0.4*r_lo - 6*y_hi**(2/3) + 1)) + 1/(12*y_lo) + 1/(12*(n+1))
    A = (1-eps)*w0*exp(-c4)*(2*B2 - top)
    k1 = (1+3*y_lo**(-2/3))**1.5
    k2 = (r_lo+1)/(r_lo-wid)
    k3 = (1+wid/y_lo)**1.5
    e0 = 1.5*wid*(2*y_hi+2*wid-2-n)/((y_lo+wid-1)*(r_lo-wid+1))
    K = (2*pi)**-0.5*k1*k2*k3*exp(e0+1/(12*y_lo))
    b = K*2*wid/n
    slope = A - 2*K + 1; icpt = K - b - 1 - 1/n
    return dict(eps=eps, B2=B2, top=top, c4=c4, A=A, K=K, b=b, slope=slope, icpt=icpt, wid=wid, chi_lo=chi_lo,
                k1=k1, k2=k2, k3=k3, e0=e0, Psi_half=slope*0.5+icpt, Psi_23=slope*(2/3)+icpt)

print("(3) 조립 범위 λ∈[1/2,2/3] 닫힌 꼴 선형 하계 (5.62 둘째 하계; w0=4/5, 폭 <= y^(2/3)+2)")
for n in (50001, 10**5, 10**6, 10**7, 10**9):
    d = crude_constants(n, 0.8)
    print(f"   n={n:>10}: eps<={d['eps']:.4f}, B2>={d['B2']:.4f}, top<={d['top']:.4f}, c4<={d['c4']:.5f}, A>={d['A']:.4f}, K<={d['K']:.4f} [k1={d['k1']:.4f},k2={d['k2']:.4f},k3={d['k3']:.4f},e0={d['e0']:.4f}], b<={d['b']:.4f} => Ψ(λ) >= {d['slope']:.4f}λ {d['icpt']:+.4f};  Ψ(1/2)>={d['Psi_half']:.4f}, Ψ(2/3)>={d['Psi_23']:.4f}")
d = crude_constants(50001, 0.8)
print(f"   => n=50001 상수로 모든 n>=50001: Ψ(λ) >= {d['slope']:.3f}λ {d['icpt']:+.3f} >= {d['Psi_half']:.3f} > 0  (λ>=1/2; 기울기 양)")
for w0 in (0.71216, 0.75):
    d2 = crude_constants(50001, w0)
    print(f"   (참고) w0={w0}: Ψ(1/2) >= {d2['Psi_half']:.4f}, Ψ(2/3) >= {d2['Psi_23']:.4f}")
ns = [50001, 60000, 10**5, 3*10**5, 10**6, 10**7, 10**8]
seq = [crude_constants(n, 0.8) for n in ns]
mono = all(seq[i]['eps'] >= seq[i+1]['eps'] and (1-seq[i]['B2']) >= (1-seq[i+1]['B2']) and seq[i]['top'] >= seq[i+1]['top'] and seq[i]['c4'] >= seq[i+1]['c4'] and seq[i]['K'] >= seq[i+1]['K'] and seq[i]['b'] >= seq[i+1]['b'] for i in range(len(ns)-1))
print(f"   여섯 상수(eps, 1-B2, top, c4, K, b)의 n-감소(표본 {ns[0]}..{ns[-1]}): {mono}")

# ---------- 참고: 4000셀 띠 최소 비 (심사 A4 (A) 재현, 새 폭·w0) ----------
def envelopes(la, lb, cw, cf, c0, w0, n=50001):
    wid = cw*(cf*lb*n)**(2/3) + c0
    chi_lo = floor(0.3*(1-lb)*n - 1)
    hov = 0.0; z = 0
    while True:
        t = 1 - (2/sqrt(pi))*z**1.5*(chi_lo-1)**-0.5
        if t <= 0: break
        hov += (la-1/n)**z * t; z += 1
    B2 = 1 - sqrt(2/pi)*(0.3*(1-lb)*n-1)**-0.5 - 0.3*(1-la)*n*(2*pi)**-0.5*((n+1)/(la*n*((1-lb)*n-wid)))**1.5*exp(1/(12*(n+1)))
    top = (2*pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb)**-1.5*n**-0.5*exp(1/(12*n))
    K = la*exp(-1/(12*(0.4*(1-lb)*n-6*(lb*n)**(2/3)+1)) - 1/(12*la*n) - 1/(12*(n+1)))
    c1 = 1.5*((2*lb-1)*n+2*wid)/(la*n*((1-lb)*n-wid))
    e0 = 1.5*wid*((2*lb-1)*n+2*wid)/((la*n-1)*((1-lb)*n-wid))
    W = (2*pi)**-0.5*(2/3)*(wid+1)**1.5*c1*(1+wid/(la*n))**1.5*exp(e0+1/(12*la*n))
    return hov*K*(2*B2-top)*w0 - W

def band_min(cw, cf, c0, w0, cells=4000):
    return min((envelopes(0.5+(1/6)*i/cells, 0.5+(1/6)*(i+1)/cells, cw, cf, c0, w0), i) for i in range(cells))

v, i = band_min(0.75, 1.1, 1, 0.71216); v2, i2 = band_min(1.0, 1.0, 2, 0.8)
print(f"(4) 참고 — 4000셀 띠 최소 비(5.63 꼴): 현행 {v:.4f}(셀 {i}) ; W경계 폭·w0=0.8: {v2:.4f}(셀 {i2})  [채택안은 셀 없이 (3)으로 닫는다]")
