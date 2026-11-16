# -*- coding: utf-8 -*-
"""결정 K1 검산 (2b) — 판정 V 를 2001 아래로 더 내릴 수 있는가(A7 통찰 (ㄴ)의 상한 탐색; K0·K2 에 넘길 경계 사실).
가정: 생존 상계가 10.21 꼴 s_{y+q}(y) ≤ min(1, C₀(y+q+1)/(q+1)^{3/2}) 로 용량 y ≥ y₀ 에서 선다고 할 때(C₀∈{1.15,1.2,1.3}),
세 줄 하계(합집합 상계 포함)가 d ≤ (k+d)^{2/3}/2 를 덮는지, small-k-bulk 의 분할점 ρk^{2/3} 을 바꾼 (가)·(나) 조건이 서는지를
k ∈ {501, 841, 1000, 1368} 에서 본다. 배정밀도 관찰.
"""
import os, math
import numpy as np
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def P(s=""): out.append(s)
def lbor(w): return -w + (w-1)*math.log(w) - math.lgamma(w+1)
def lren(j): return 0.0 if j == 0 else (j-1)*math.log(j) - j - math.lgamma(j)
def union_ub(k, m):
    return sum(math.exp(lren(m-t)+lbor(t)-lbor(m))*(t-k+1)/t for t in range(k, m))
def surv(C0, y, q):
    d = q+1; return min(1.0, C0*(y+d)/d**1.5)
def u_bound(C0, k):
    Nn = int(0.35*k); K = k+Nn+1; q = 2*k-K
    return k*surv(C0, K, q)/(Nn+2), K
def wp(mp): return 1.99 + 0.59963*(mp+1)**(2/3) + 1.24847*(mp+1)**(1/3)
def Low(k, rho):
    eps = k**(-1/3); sB = (2*math.pi)**-0.5
    num = sB*k**(1/3)*(2*math.sqrt(rho)-2.218*eps)
    if num <= 0: return float('nan')
    return num/(1+rho*eps)*math.exp(-1/(12*(k+1)))*math.exp(-rho**2*(1+rho*eps)**1.5*math.exp(1/(4*(k+1)))/(sB*(2*math.sqrt(rho)-2.218*eps)))
for k in (501, 841, 1000, 1368):
    R = (3*(k-1))//2; q = R-(k-1)
    d_b = max(d for d in range(0, 2000) if d <= (k+d)**(2/3)/2)
    P(f"\n==== k={k}: R={R}, q={q}, d_b={d_b}, 𝗎 를 쓸 용량 K={k+int(0.35*k)+1}")
    for C0 in (1.15, 1.2, 1.3):
        sR = surv(C0, k-1, q); uC, K = u_bound(C0, k)
        lbs = [(k-1)/(R+1)*((1-(union_ub(k, k+d) if d else 0.0)) - sR) - uC for d in range(0, 400)]
        d0 = 0
        while d0+1 < len(lbs) and lbs[d0+1] > 0: d0 += 1
        if lbs[0] <= 0: d0 = -1
        P(f"  C₀={C0}: s_R 상계={sR:.4f}, 𝗎={uC:.4f}; 하계 m=k: {lbs[0]:.4f}, d_b: {lbs[d_b]:.4f}; d°={d0} (≥d_b: {d0>=d_b})")
        for rho in (0.75, 0.85, 0.95, 1.0, 1.1):
            dfrak = (2/math.e)*(0.5+2.5/k+0.25/k**2) + uC/(math.e*2**1.5)
            dr = rho*k**(2/3)
            Obar = dfrak*math.exp(1+1/(12*k))*(1+(dr+1)/k)**1.5
            cond_ga = dr >= wp(k+dr)-1
            P(f"     분할 ρ={rho}: (나) Low(k,ρ)={Low(k,rho):.4f} > 𝒪̄={Obar:.4f}: {Low(k,rho)>Obar};  (가) ρk^(2/3)={dr:.1f} ≥ wp(k+ρk^(2/3))-1={wp(k+dr)-1:.1f}: {cond_ga};  d_b ≤ ρk^(2/3): {d_b <= dr}")
P("\n(가)의 조건은 5.1(행 ≤20000)·명제 5.3(증인 위치)만 쓰므로 2k-2 ≤ 20000 인 모든 k 에서 분할점만 맞으면 된다. 생존 상계의 용량 범위 y₀ 가 결정적이다(K2·S3).")
with open(os.path.join(ROOT, r"scripts\구조압축\결정_K1_V확장_저열_out.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out)+"\n")
print("\n".join(out))
