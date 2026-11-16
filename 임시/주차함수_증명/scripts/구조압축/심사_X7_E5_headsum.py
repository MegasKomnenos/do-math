# -*- coding: utf-8 -*-
# 심사 X7 — E5 검산: 9:head-sum-1 / 9:H-star-plus 의 실변수 함수 Phi, L, G 를 그대로 구현해
#   (i)  G/L 의 모양(xi에 대한 단조성 여부)과 영역 A의 최댓값 자리,
#   (ii) xi > 1 로 넓혔을 때 Phi<=L (head-sum-1), G<=L (H-star-plus) 가 어디까지 서는지,
#   (iii) 5:witness-position-bound 를 재사용해 m_1(k) 를 막으면 필요한 xi 가 얼마인지 (D:m1-column-reading 대체 가능성)
import math, sys

def funcs(xi, ups):
    inv = 1/(1-ups**3)                      # 1+1/ell
    c1 = (1+xi*ups*inv)**1.5*math.exp(inv*ups**3/12)
    uq = inv**2*(xi*ups+ups**3)**2/2
    Phi = inv*c1*math.exp(uq)*(0.11399*xi**3.5+0.15958*xi**2.5*ups**2+0.85108*xi**3*ups)
    den = 0.7978*math.sqrt(xi)-0.8848*ups
    if den <= 0: return Phi, float('nan'), float('nan'), c1
    E = c1*inv*(0.5320*xi**1.5*ups+0.7979*math.sqrt(xi)*ups**3+c1*(0.625*xi**2+xi*ups**2))/den
    L = den*math.exp(-E)/(1+(xi*ups+ups**3)*inv)
    G = Phi + ups*(0.5320*c1*xi**1.5+0.2)
    return Phi, L, G, c1

out = []
for k in (3132, 6668, 10000, 19404, 38887):
    ups = k**(-1/3)
    out.append(f"--- k={k}, upsilon={ups:.5f} ---")
    # (i) 모양: G/L on a grid
    grid = [2*ups**2, 0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 0.9, 1.0, 1.03, 1.05, 1.07, 1.1, 1.2]
    row = []
    for xi in grid:
        Phi, L, G, c1 = funcs(xi, ups)
        row.append(f"xi={xi:.4f}: Phi/L={Phi/L:.4f} G/L={G/L:.4f}")
    out.extend(row)
    # (ii) 최대 xi with Phi<=L and with G<=L (scan)
    xmaxP = None; xmaxG = None
    xi = 0.03
    while xi <= 1.5:
        Phi, L, G, c1 = funcs(xi, ups)
        if Phi <= L: xmaxP = xi
        if G <= L: xmaxG = xi
        xi += 0.001
    out.append(f"(ii) Phi<=L 가 서는 최대 xi(0.03부터 연속 구간 아님—마지막 성립점) = {xmaxP:.3f};  G<=L 마지막 성립점 = {xmaxG if xmaxG is None else round(xmaxG,3)}")
    # 조건 t-1-k <= ell/6  <=>  xi k^{2/3} - 1 <= (k-1)/6
    out.append(f"     xi 상한(조건 q-1<=ell/6): {((k-1)/6+1)/k**(2/3):.3f}")
    # (iii) witness bound requirement
    M = min(2*k, 20000)
    need = 0.99 + 0.59963*(M+1)**(2/3) + 1.24847*(M+1)**(1/3)
    out.append(f"(iii) 5:witness-position-bound 로 m_1(k)-k <= ceil({need:.1f}) -> xi_need = {math.ceil(need)/k**(2/3):.4f}  (원고: 0.75 for k<=19403 via readout; 1.0 for k>=19404)")
with open(sys.argv[1] if len(sys.argv) > 1 else 'scripts/구조압축/심사_X7_E5_headsum_out.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out)+'\n')
print('\n'.join(out))
