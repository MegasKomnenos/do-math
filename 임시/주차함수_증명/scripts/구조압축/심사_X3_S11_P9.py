# -*- coding: utf-8 -*-
"""심사 X3 — S11(위험률 1/(2k) 하계)과 P9(중앙 띠 쌍 검사의 일반 최대화 대체)의 수치 검산.
(1) S11: g(x)=(x−1)log(1+1/x). ε=g(2k)−g(k)의 상하계 3/(4k)−17/(24k²) ≤ ε ≤ 3/(2k), hz ≥ 1−e^{−ε} ≥ (1/k)(3/4−11/(6k)) ≥ 1/(2k) 를
    k=2000..3131, 10^4, 10^5, 10^6, 10^7에서 mpmath 50자리로 확인. 그리고 7:top-roots 괄호에 hz≥1/(2k)를 넣은
    (1/(2k))[2.38·0.9999·k^{3/2}(1−k/n)²−301]−1 이 n≥3k+1, k≥2001에서 양수인지, 최솟값(n=3k+1, k=2001)을 센다.
(2) P9: 꼬리 확률 1−𝔰_q(k) 를 (7.10) 재귀 (π_m(j)=C(m,j) j^{j−1} p_{m−j}/p_m, m=k+q−1)로 mpmath로 정확히 구해
    1−𝔰_q(k) ≤ q^{3/2}/(2k) (k∈{9950,10000,12000,15000}, 1≤q≤101)인지 보고, 비 (1−𝔰_q)k/q^{3/2}의 최댓값을 적는다.
    또 ê_q = q+(k+q)n̂_q/(1−n̂_q), n̂_q=C q^{3/2}/k (C=1/2)로 (7.11) 하계 lb_k(q,q',j)=1−(j/k)(ê_q+ê_q')−[ê_q(q'−1)+ê_q'(q−1)]/(2k)
    를 접합점 (K,L)=(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)의 껍질 q+q'+j≤L 전체에서 전수 평가해 최솟값을 적고,
    F4의 닫힌 상계 L²/3+(8C/25)√(2/5)L^{5/2} (e_q=q+Cq^{3/2}, C=21/40)와 전수 최댓값을 견준다.
"""
import os
from mpmath import mp, mpf, log, exp, sqrt, binomial, power
mp.dps = 50
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def g(x):
    x = mpf(x); return (x-1)*log(1+1/x)
out.append("== (1) S11 ==")
worst = None
for k in list(range(2000, 3132)) + [10**4, 10**5, 10**6, 10**7]:
    kk = mpf(k)
    eps = g(2*k) - g(k)
    lo = 3/(4*kk) - mpf(17)/(24*kk*kk); hi = 3/(2*kk)
    hz = 1 - exp(-eps)
    hz_lo = (mpf(3)/4 - mpf(11)/(6*kk))/kk
    okb = lo <= eps <= hi and hz >= hz_lo >= 1/(2*kk)
    if not okb:
        out.append(f"  k={k}: 실패 eps={eps} lo={lo} hi={hi} hz={hz} hz_lo={hz_lo}")
    r = hz*kk
    if worst is None or r < worst[1]:
        worst = (k, r)
out.append(f"  모든 k에서 상하계·1/(2k) 성립: {'예' if not any('실패' in s for s in out) else '아니오'}; k·hz_k(2k−1)의 최솟값 {float(worst[1]):.5f} (k={worst[0]}) — 참고: 극한값 k·(g(2k)−g(k))→3/4")
# g upper bound check: g(x) <= 1 - 3/(2x) + 5/(6x^2) for x>=2000?
mx = max(float(g(x) - (1 - mpf(3)/(2*x) + mpf(5)/(6*x*x))) for x in [2000, 2001, 3000, 4000, 10**4, 10**6])
out.append(f"  g(x) ≤ 1−3/(2x)+5/(6x²) 검사(차의 최댓값, 음수여야): {mx:.3e}")
mn = min(float(g(x) - (1 - mpf(3)/(2*x) + mpf(1)/(2*x*x))) for x in [2000, 2001, 3000, 4000, 10**4, 10**6])
out.append(f"  g(x) ≥ 1−3/(2x)+1/(2x²) 검사(차의 최솟값, 양수여야; 2.26(다)): {mn:.3e}")
# top-roots bracket with hz >= 1/(2k)
def bracket(k, n):
    k = mpf(k); n = mpf(n)
    return (1/(2*k))*(mpf('2.38')*mpf('0.9999')*power(k, mpf(3)/2)*((n+1-k)**2)/(n*(n+1)) - 301) - 1
vals = [(k, float(bracket(k, 3*k+1))) for k in [2000, 2001, 2500, 3130, 3131, 6667, 10**4, 10**5]]
out.append("  hz≥1/(2k)로 바꾼 7:top-roots 괄호 (n=3k+1): " + ", ".join(f"k={k}: {v:.3f}" for k, v in vals))
# monotone in n: (n+1-k)^2/(n(n+1)) increasing in n for n>=k? check numerically
k = 2001
seq = [float(bracket(k, n)) for n in [3*k+1, 4*k, 10*k, 100*k, 10**7]]
out.append(f"  k=2001에서 n=3k+1,4k,10k,100k,1e7의 괄호: {[round(v,3) for v in seq]} (n에 증가)")
# compare with F3's expression sqrt(k)/2 - 301/(2k) - 1
f3 = [(k, float(sqrt(mpf(k))/2 - mpf(301)/(2*k) - 1)) for k in [2001, 3130]]
out.append("  F3의 식 √k/2−301/(2k)−1: " + ", ".join(f"k={k}: {v:.3f}" for k, v in f3) + " (>20 주장)")
# current theorem-W(가) at hz=0.14/n for comparison at n=n_PD(k)
def Gk(k, n):
    k = mpf(k); n = mpf(n)
    return (mpf('0.14')/n)*(mpf('2.38')*power(k, mpf(3)/2)*((n-k+1)**2)/(n*(n+1)) - 301)
out.append("  현행 𝔊_k(n) (hz=0.14/n) 참고: " + ", ".join(f"k={k},n={n}: {float(Gk(k,n)):.3f}" for k, n in [(3131, 3*3131+1), (3131, 41800+3132), (2001, 3*2001+1), (2001, 26800)]))

out.append("== (2) P9 ==")
def tail_probs(k, Q):
    """1−𝔰_q(k) for q=1..Q via (7.10): 1−𝔰_q = Σ_{j=k+1}^{k+q−1} π_m(j)[(j−k)/j + (k/j)(1−𝔰_{j−k})], m=k+q−1."""
    k = int(k)
    logp = lambda t: (t-1)*log(t+1) if t >= 1 else mpf(0)  # log p_t, p_t=(t+1)^{t-1}, p_0=1
    res = {1: mpf(0)}
    for q in range(2, Q+1):
        m = k+q-1
        s = mpf(0)
        for j in range(k+1, k+q):
            # π_m(j) = C(m,j) j^{j-1} p_{m-j}/p_m
            lpi = log(binomial(m, j)) + (j-1)*log(j) + logp(m-j) - logp(m)
            pij = exp(lpi)
            s += pij*((mpf(j-k)/j) + (mpf(k)/j)*res[j-k])
        res[q] = s
    return res
for K in [9950, 10000, 12000, 15000]:
    tp = tail_probs(K, 101)
    ratio = max((float(tp[q]*K/power(mpf(q), mpf(3)/2)), q) for q in range(2, 102))
    okall = all(tp[q] <= power(mpf(q), mpf(3)/2)/(2*K) for q in range(1, 102))
    out.append(f"  k={K}: max_q (1−𝔰_q)k/q^(3/2) = {ratio[0]:.4f} (q={ratio[1]}); 1−𝔰_q ≤ q^(3/2)/(2k) 전부 성립: {okall}; 1−𝔰_101 = {float(tp[101]):.5f}, 101/k = {101/K:.5f}")
# pairwise bound with C=1/2 tail constant and junctions
def lb_min(K, L, C):
    K = mpf(K); C = mpf(C)
    def ex(q):
        if q == 1: return mpf(1)
        nh = C*power(mpf(q), mpf(3)/2)/K
        return q + (K+q)*nh/(1-nh)
    E = {q: ex(q) for q in range(1, L)}
    best = None; worst_num = None
    for q in range(1, L):
        for qq in range(q, L-q+1):
            j = L - q - qq  # lb decreasing in j, so j max suffices for shell L
            if j < 0: continue
            num = j*(E[q]+E[qq]) + (E[q]*(qq-1)+E[qq]*(q-1))/2
            lb = 1 - num/K
            if best is None or lb < best[0]:
                best = (float(lb), q, qq, j)
            if worst_num is None or num > worst_num[0]:
                worst_num = (float(num), q, qq, j)
    return best, worst_num
for (K, L) in [(10000, 50), (12000, 58), (13000, 79), (14000, 99), (15000, 102)]:
    best, wn = lb_min(K, L, mpf(1)/2)
    closed = float(mpf(L)**2/3 + (8*mpf('0.525')/25)*sqrt(mpf(2)/5)*power(mpf(L), mpf(5)/2))
    out.append(f"  접합 (K,L)=({K},{L}): 껍질 L의 전수 최소 lb = {best[0]:.4f} at (q,q',j)={best[1:]}; 손실 분자 최댓값 {wn[0]:.1f} (< K={K}: {wn[0] < K}); F4 닫힌 상계(C=21/40) {closed:.1f}")
    # also with the manuscript's tf for comparison
    best2, _ = lb_min(K, L, mpf('0.54'))
    out.append(f"      (현행 tf=0.54로 같은 껍질: 최소 lb = {best2[0]:.4f})")
# effective C: does ê_q ≤ q + C' q^{3/2} with C' = 21/40 hold for q ≤ 101, k ≥ 10000 when tail constant is 1/2?
def Ceff(K, q):
    K = mpf(K); nh = power(mpf(q), mpf(3)/2)/(2*K)
    return float((K+q)*nh/(1-nh)/power(mpf(q), mpf(3)/2))
out.append("  ê_q=q+(k+q)n̂/(1−n̂) (n̂=q^{3/2}/(2k))의 유효 C=(k+q)/(k(1−n̂))/2: " + ", ".join(f"(k={K},q={q}): {Ceff(K,q):.4f}" for K, q in [(10000, 49), (12000, 57), (13000, 78), (14000, 98), (15000, 101), (10000, 101)]) + "  (21/40=0.525)")
txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_X3_S11_P9_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
