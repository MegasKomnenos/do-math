# 심사 A4 — C3·C4 가 조립(5.5.8)의 두 판정식에 남기는 여유의 추정 (배정밀도; 인증이 아니라 실익·타당성 가늠용)
#  (A) 조립 범위 λ∈[1/2,2/3], n=50001: 부록 D.band-check 의 다섯 포락선을 그대로 다시 구현해 현행값(최소 비 1.355874)을 재현한 뒤
#      창 폭 상계 wid_bar = cw*(cf*λ_b n)^{2/3} + c0 와 상수 w0 를 바꾸어 최소 비를 센다.
#  (B) 오른쪽 부분 λ>2/3: 보조정리 5:right-part 의 네 상수를 새 폭으로 다시 세고 Ψ_R(λ=2/3) 을 낸다.
#  (C) 격자 없는 조립 범위 논증: 떠돌기 인자의 둘째(닫힌 꼴) 하계로 λ 점별 하계를 내고, 거친 상수로 선형 하계 aλ-b 를 만든다.
#  (D) C3만 채택(폭 그대로)할 때: 비는 w0 에 대해 아핀이므로 1.3558 - (0.71216-w0)*A_lo 로 재인증 없이 닫히는지.
import math
from math import sqrt, pi, exp, floor
n = 50001

def envelopes(la, lb, cw, cf, c0, w0):
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
    A = hov*K*(2*B2-top)
    return A*w0 - W, A, dict(hov=hov, B2=B2, top=top, K=K, W=W, wid=wid)

def band_min(cw, cf, c0, w0, cells=4000):
    best = None
    for i in range(cells):
        la = 0.5 + (1/6)*i/cells; lb = 0.5 + (1/6)*(i+1)/cells
        v, A, d = envelopes(la, lb, cw, cf, c0, w0)
        if best is None or v < best[0]: best = (v, i, A, d)
    return best

print("(A) 조립 범위 4000셀, n=50001")
v, i, A, d = band_min(0.75, 1.1, 1, 0.71216)
print(f"  현행(0.75·(1.1y)^(2/3)+1, w0=0.71216): 최소 비 {v:.6f} (셀 {i}); hov={d['hov']:.4f} B2={d['B2']:.5f} top={d['top']:.5f} K={d['K']:.5f} W={d['W']:.5f}  — 부록 D 값 1.355874/1.957/0.9885/0.00714/0.49998/0.0169 재현")
variants = [("현행 폭", 0.75, 1.1, 1), ("F7 13/16", 0.8125, 1.1, 1), ("F3 .82", 0.82, 1.1, 1), ("F4 ceil(m^2/3): 1.03y^(2/3)+1", 1.03, 1.0, 1), ("W경계 이음(상계 y^(2/3)+2)", 1.0, 1.0, 2)]
for name, cw, cf, c0 in variants:
    row = []
    for w0 in (0.71216, 0.708, 0.7):
        v, i, A, d = band_min(cw, cf, c0, w0)
        row.append(f"w0={w0}: {v:.4f}(셀{i}, W≤{d['W']:.4f})")
    print(f"  {name}: " + " | ".join(row))

# (D) 아핀 논증: 비(w0) = A_lo*w0 - W_hi, 셀마다 A_lo 의 최댓값
Amax = max(envelopes(0.5+(1/6)*i/4000, 0.5+(1/6)*(i+1)/4000, 0.75, 1.1, 1, 0.71216)[1] for i in range(4000))
print(f"(D) 현행 폭에서 A_lo 의 셀 최댓값 {Amax:.4f} (해석적 상계 1/(1-2/3)·(2/3)·2 = 4);  1.3558-(0.71216-0.7)*{Amax:.3f} = {1.3558-(0.71216-0.7)*Amax:.4f} >= 1;  0.708 이면 {1.3558-(0.71216-0.708)*Amax:.4f}")

# (B) 오른쪽 부분 상수 (보조정리 5:right-part 의 네 단계; y>=33334, r>=10357, 10y^{2/3}<r+1)
def right_part(cw, cf, c0, w0):
    y0, r0 = 33334, 10357
    a = cw*cf**(2/3)/10          # wid <= a (r+1) + c0   (y^{2/3} < (r+1)/10)
    cy = cw*cf**(2/3)            # wid <= cy y^{2/3} + c0
    eps_hov = 1.6932*(y0**(1/3)/10+1)*(2*y0**(2/3)-7.5)**-0.5   # 폭과 무관
    # 둘째: n+2-t0 = r+1-wid >= (1-a)(r+1)-c0 ;  π_n(t0-1) <= (2π)^{-1/2}[1.50003/((1-a)(r+1)-c0)]^{3/2} e^{1/(12(n+1))}; χ2<=0.3r
    def chi2pi(r):
        return 0.3*r*(2*pi)**-0.5*(1.50003/((1-a)*(r+1)-c0))**1.5*exp(1/(12*50002))
    B2 = 1 - sqrt(2/pi)*(0.2*r0-7.3)**-0.5 - chi2pi(r0)   # 두 항 모두 r 에 감소 → r0 에서 최악
    top = 0.0232
    # 넷째: (r+1)/y·W <= (2π)^{-1/2}(2/3)(wid+1)^{3/2}/y · 1.5 (r+1)/(r-wid) · (1+wid/y)^{3/2} e^{ε0+1/(12y)},  (y-r+2wid)/y <= 1 (2wid<=r)
    wid_y = cy*y0**(2/3)+c0
    assert 2*(a*(r0+1)+c0) <= r0
    t1 = (wid_y+1)**1.5/y0                         # y 에 감소
    t2 = (r0+1)/(r0-(a*(r0+1)+c0))                 # r 에 감소
    e0 = 1.5*(a*(r0+1)+c0)/((r0+1)-(a*(r0+1)+c0))  # r 에 감소
    t3 = (1+wid_y/y0)**1.5
    W4 = (2*pi)**-0.5*(2/3)*t1*1.5*t2*t3*exp(e0+1/(12*y0))
    c4 = 1/156 + 1/(12*y0) + 1/(12*50002)
    coef = (1-eps_hov)*w0*exp(-c4)*(2*B2-top) - W4
    lam = 2/3
    Psi = coef*lam - (1-lam) - 2.5e-5
    return dict(eps_hov=eps_hov, B2=B2, W4=W4, coef=coef, Psi_at_2_3=Psi)
print("(B) 오른쪽 부분(λ>2/3) 상수")
for name, cw, cf, c0 in variants:
    for w0 in (0.71216, 0.708, 0.7):
        d = right_part(cw, cf, c0, w0)
        print(f"  {name}, w0={w0}: ε_hov={d['eps_hov']:.4f} B2={d['B2']:.4f} (r+1)/y·W<={d['W4']:.4f} 계수={d['coef']:.4f} Ψ_R(2/3)>={d['Psi_at_2_3']:.4f}   (현행 본문: 0.1573/0.9799/0.3678/0.7869/0.191)")

# (C) 격자 없는 조립 범위: 둘째 떠돌기 하계 (r+1)/n·hov >= 1-ε, ε = hv_χ·n/(r+1), χ=floor(0.3r), r>=n/3
print("(C) 조립 범위의 닫힌 꼴 점별 하계 (n=50001; 모든 n>=50001 로 넓히려면 각 항의 n-단조성을 따로 확인해야 함)")
def closed_form(lam, cw, cf, c0, w0, n=50001):
    y = lam*n; r = n - y
    chi = floor(0.3*r)
    hv = chi**-0.5*((2/sqrt(pi))*(1+1/chi) + 1/sqrt(pi))
    eps = hv*n/(r+1)
    wid = cw*(cf*y)**(2/3)+c0
    B2 = 1 - sqrt(2/pi)*chi**-0.5 - 0.3*r*(2*pi)**-0.5*((n+1)/(y*(r+1-wid)))**1.5*exp(1/(12*(n+1)))
    top = (2*pi)**-0.5*(1+1/n)**1.5*lam**-0.5*(1-lam+1/n)**-1.5*n**-0.5*exp(1/(12*(n+1)))
    c4 = 1/(12*(r-2*chi-6*y**(2/3)+1)) + 1/(12*y) + 1/(12*(n+1))
    c1 = 1.5*(2*y+2*wid-n)/(y*(r-wid))
    e0 = 1.5*wid*(2*y+2*wid-2-n)/((y+wid-1)*(r-wid+1))
    W = (2*pi)**-0.5*(2/3)*(wid+1)**1.5*c1*(1+wid/y)**1.5*exp(e0+1/(12*y))
    # (5.4)에 (r+1)/n 을 곱한 꼴: Ψ = (1-ε) w0 e^{-c4} λ (2B2-top) - (r+1)/n·W - (1-λ+1/n)
    return (1-eps)*w0*exp(-c4)*lam*(2*B2-top) - (r+1)/n*W - (1-lam+1/n)
for name, cw, cf, c0 in variants:
    for w0 in (0.708, 0.7):
        vals = [(closed_form(0.5+(1/6)*i/2000, cw, cf, c0, w0), 0.5+(1/6)*i/2000) for i in range(2001)]
        m = min(vals)
        print(f"  {name}, w0={w0}: Ψ(λ) 최솟값 {m[0]:.4f} at λ={m[1]:.4f};  Ψ(1/2)={vals[0][0]:.4f}, Ψ(2/3)={vals[-1][0]:.4f}")
# 거친 상수 선형 하계(F4 폭, w0=0.7): ε<=0.0718, B2>=1-0.0113-0.0040, top<=0.0133, e^{-c4}>=0.99, (r+1)/y·W <= 0.499((2λ-1)/λ+0.064)
lamv = [0.5, 2/3]
for lam in lamv:
    print(f"  거친 선형 하계(F4, w0=0.7) λ={lam:.3f}: {(1-0.0718)*0.7*0.99*(2*(1-0.0113-0.0040)-0.0133)*lam - 0.499*(2*lam-1+0.064*lam) - (1-lam) - 2.5e-5:.4f}")
