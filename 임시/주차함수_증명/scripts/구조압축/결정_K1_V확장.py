# -*- coding: utf-8 -*-
"""결정 K1 검산 (2) — 판정 V 의 k≥2001 확장 가능성 (S12 길 A, 6장 V 문턱 3131 의 처분).
(가) 세 열 A_{·,k-2},A_{·,k-1},A_{·,k} 를 볼츠만 척도 양수항 재귀로 구해(배정밀도; 관찰) 𝒱_k(m) 참값.
(나) 세 줄 하계식 𝒱_k(m) ≥ (k-1)/(R+1)[s_{m-1}(k-1) - s_R(k-1)] - (k-1)c_{2k}(k-1), R=⌊3(k-1)/2⌋ 의
     (i) 참 s 를 넣은 값(부등식 자체의 점검), (ii) 증명 가능한 꼴: s_{m-1}(k-1) ≥ 1 - UB(m) (합집합 상계),
     s_R(k-1) ≤ 생존 상계(6.1 꼴 C·y·q^{-3/2} 또는 10.21 꼴 1.15(y+d)/d^{3/2}), (k-1)c_{2k}(k-1) ≤ 𝗎(k)(6.18 증명을 같은 생존 상계로).
     양인 연속 범위 d° 와 경계 d_b = max{d : d ≤ (k+d)^{2/3}/2} (critical-front/small-k-bulk 의 경계) 비교.
(다) small-k-bulk (나) 의 입력: Low(k,3/4) (6.48) 대 𝒪̄(k,0.75k^{2/3}) ; (6.49) ; lemma-M(나) 상수 ; old-8-11 전제.
python -I. 출력 결정_K1_V확장_out.txt. 배정밀도 관찰이지 증명이 아니다.
"""
import os, math
import numpy as np
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def P(s=""): out.append(s)

def lbor(w):   # log Bor(w) = -w + (w-1)log w - log w!
    return -w + (w-1)*math.log(w) - math.lgamma(w+1)
def lren(j):   # log Ren(j) ; Ren(0)=1
    return 0.0 if j == 0 else (j-1)*math.log(j) - j - math.lgamma(j)
def bor(w): return math.exp(lbor(w))

def cols(k):
    """ã^{(c)}_n = e^{-n}A_{n,c-1}/n!  (c = k+1, k, k-1), n ≤ 2k  — 양수항 재귀 n ã_n = e^{-1} Σ_{j<n} min(j+1,c) ã_j ã_{n-1-j}."""
    N = 2*k; res = {}
    for c in (k+1, k, k-1):
        a = np.zeros(N+1); a[0] = 1.0
        w = np.minimum(np.arange(0, N+1)+1, c).astype(float)
        for n in range(1, N+1):
            a[n] = math.exp(-1)*np.dot(w[:n]*a[:n], a[n-1::-1][:n]) / n
        res[c] = a
    return res

def union_ub(k, m):
    """1 - s_{m-1}(k-1) ≤ Σ_{t=k}^{m-1} θ_m(t)(t-k+1)/t, θ_m(t)=Ren(m-t)Bor(t)/Bor(m)."""
    s = 0.0
    for t in range(k, m):
        s += math.exp(lren(m-t)+lbor(t)-lbor(m))*(t-k+1)/t
    return s

def surv_bound(form, y, q):
    """s_{y+q}(y) 의 상계. form='6.1': C y q^{-3/2}; form='10.21': 1.15 (y+d)/d^{3/2}, d=q+1."""
    if form[0] == '6':
        C = float(form.split(':')[1]); return min(1.0, C*y*q**-1.5)
    d = q+1; return min(1.0, 1.15*(y+d)/d**1.5)

def u_bound(form, k):
    """old-8-11 의 증명: (k-1)c_{2k}(k-1) ≤ k c_{2k}(k-1) ≤ s_{2k}(K)/(𝒩+2)·k, K=k+𝒩+1, 𝒩=⌊0.35k⌋, 2k=K+q."""
    Nn = int(0.35*k); K = k+Nn+1; q = 2*k-K
    return k*surv_bound(form, K, q)/(Nn+2), K, q

def wp(mp): return 1.99 + 0.59963*(mp+1)**(2/3) + 1.24847*(mp+1)**(1/3)

def Low(k, rho):
    eps = k**(-1/3); sB = (2*math.pi)**-0.5
    num = sB*k**(1/3)*(2*math.sqrt(rho)-2.218*eps)
    return num/(1+rho*eps)*math.exp(-1/(12*(k+1)))*math.exp(-rho**2*(1+rho*eps)**1.5*math.exp(1/(4*(k+1)))/(sB*(2*math.sqrt(rho)-2.218*eps)))

forms = ['6.1:3', '6.1:3.2', '10.21']
for k in (841, 1000, 1368, 2001, 2500, 3130, 3131, 4001, 6668):
    A = cols(k)
    eb = np.array([math.e*bor(m+1) for m in range(0, 2*k+1)])
    cK = (A[k+1]-A[k])/eb; cKm = (A[k]-A[k-1])/eb
    sKm = A[k-1]/eb                      # s_m(k-1)
    p_ = (k+1)*cK - (k-1)*cKm
    V = np.cumsum(p_[k:2*k+1][::-1])[::-1]   # V_k(m), m = k..2k
    R = (3*(k-1))//2; q = R-(k-1)
    P(f"\n==== k={k}: 𝒱_k(k)={V[0]:.5f}, min_m 𝒱_k(m)={V.min():.3e} (m={int(np.argmin(V))+k}), R={R}, q=R-(k-1)={q}, s_R(k-1)참={sKm[R]:.5f}, (k-1)c_2k(k-1)참={(k-1)*cKm[2*k]:.5f}")
    d_b = max(d for d in range(0, 2000) if d <= (k+d)**(2/3)/2)
    # (i) 부등식 자체: 참 s 를 넣은 하계 ≤ 참값?
    viol = 0; dmax_chk = min(k, 600)
    for d in range(0, dmax_chk):
        m = k+d
        lb_true = (k-1)/(R+1)*(sKm[m-1]-sKm[R]) - (k-1)*cKm[2*k]
        if lb_true > V[d] + 1e-9: viol += 1
    P(f"  세 줄 하계식(참 s)이 참값을 넘는 d(0..{dmax_chk-1}): {viol}건;  경계 d_b=max{{d: d≤(k+d)^(2/3)/2}} = {d_b}")
    for form in forms:
        sR_ub = surv_bound(form, k-1, q)
        uC, K, qq = u_bound(form, k)
        lbs = []
        for d in range(0, 700):
            m = k+d
            ub = union_ub(k, m) if d > 0 else 0.0
            lbs.append((k-1)/(R+1)*((1-ub) - sR_ub) - uC)
        d0 = 0
        while d0+1 < len(lbs) and lbs[d0+1] > 0: d0 += 1
        if lbs[0] <= 0: d0 = -1
        P(f"  [{form:>7}] s_R 상계={sR_ub:.4f}, 𝗎={uC:.4f} (K={K}, 2k-K={qq}); 하계(m=k)={lbs[0]:.4f}; d=13: {lbs[13]:.4f}; d=d_b={d_b}: {lbs[d_b]:.4f}; 양인 연속 범위 0..d°={d0}  → d°≥d_b: {d0 >= d_b}")
    # (다) small-k-bulk (나): Low(k,3/4) vs 𝒪̄(k, 0.75 k^{2/3})
    for form in forms:
        uC, K, qq = u_bound(form, k)
        for gW in (0.7380432, 2/math.e):
            ups = 0.5 + 2.5/k + 0.25/k**2
            dfrak = gW*ups + uC/(math.e*2**1.5)
            d75 = 0.75*k**(2/3)
            Obar = dfrak*math.exp(1+1/(12*k))*(1+(d75+1)/k)**1.5
            P(f"  small-k-bulk(나) [{form:>7}, γ_W={gW:.4f}]: 𝔡(k)={dfrak:.4f}, 𝒪̄(k,0.75k^(2/3))={Obar:.4f}, Low(k,3/4)={Low(k,0.75):.4f} → Low>𝒪̄: {Low(k,0.75) > Obar}")
    lhs = 0.75*k**(2/3); rhs = wp(k+0.75*k**(2/3))-1
    P(f"  (6.49) 0.75k^(2/3)={lhs:.2f} ≥ wp(k+0.75k^(2/3))-1={rhs:.2f}: {lhs >= rhs};  k^(1/3)={k**(1/3):.3f} (≥11.10?)")
    B = 2.218*k**(-1/3); sB = (2*math.pi)**-0.5
    R12 = 3*0.25 - 2*B*0.5**1.5 - 2*sB*0.5**0.5 + sB*B
    dR = 6*0.5 - 3*B*0.5**0.5 - sB/0.5**0.5
    P(f"  lemma-M(나) 상수: 𝔅={B:.4f} (3√(1/2)=2.12>2𝔅: {2.1213>2*B}), 𝔑(1/2)={R12:.4f}>0: {R12>0}, 𝔑'(1/2)={dR:.3f}>0: {dR>0}")
    Nn = int(0.35*k); K = k+Nn+1
    P(f"  old-8-11 전제: (2k)^(2/3)={(2*k)**(2/3):.1f} ≤ 0.65k-1={0.65*k-1:.1f}: {(2*k)**(2/3) <= 0.65*k-1}; 생존 상계를 쓸 용량 K={K}, q=2k-K={2*k-K} ≤ K: {2*k-K<=K}; k-𝒩={k-Nn} > 477: {k-Nn>477}; 2k={2*k} ≤ 20000: {2*k<=20000}")

P("\n== 참고: 10.21 7단계 상수(A5 _3_analytic_out)에 따르면 1.15 꼴은 y≥2000 에서 1.1444<1.15 로 닫힘(계수 재확인 필요; K2 의 S3). 6.1 꼴 C=3.2 는 k≥2000 에서 (6.8) 성립(A5). ==")
with open(os.path.join(ROOT, r"scripts\구조압축\결정_K1_V확장_out.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out)+"\n")
print("\n".join(out))
