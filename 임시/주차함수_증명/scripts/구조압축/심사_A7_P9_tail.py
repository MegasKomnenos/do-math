# -*- coding: utf-8 -*-
"""심사 A7 — P9 검산: F4 §5의 두 주장
 (a) 1 - s_{k+q-1}(k) <= q^{3/2}/(2k)  (k>=9950, 1<=q<=101)
 (b) j(e_q+e_p) + (e_q(p-1)+e_p(q-1))/2 <= L^2/3 + (8C/25) sqrt(2/5) L^{5/2}  (p,q>=1, j>=0, p+q+j<=L, e_q=q+Cq^{3/2})
를 다시 센다.
 (a)는 원고의 정확한 재귀 (7.10)  1-s_q = sum_{j=k+1}^{k+q-1} pi_m(j)[(j-k)/j + (k/j)(1-s_{j-k})], m=k+q-1,
     pi_m(j) = C(m,j) j^{j-1} p_{m-j}/p_m 를 로그 스케일로 k=9950, 10000, 15000, 10^5 에서 직접 계산해
     k(1-s_q)/q^{3/2} 의 최댓값을 보고, k->inf 극한 T(q) = sum_{s=0}^{q-2} Bor(s+1)[(q-1-s)+T(q-1-s)] 도 센다.
     또 원고 보조정리 7:tail-bound 의 (7.12)를 tf=1/2, K_1=9950, M=101 로 평가한다.
 (b)는 정수 전수(L<=102)로 확인한다.
"""
import os
from mpmath import mp, mpf, log, exp, sqrt, loggamma, e as E

mp.dps = 30
ROOT = r"C:\math\임시\주차함수_증명"
out = []

def logp(m):  # log p_m = (m-1) log(m+1)
    return (m - 1) * log(mpf(m + 1)) if m >= 1 else mpf(0)
def logC(m, j):
    return loggamma(m + 1) - loggamma(j + 1) - loggamma(m - j + 1)
def log_pi(m, j):  # pi_m(j) = C(m,j) j^{j-1} p_{m-j} / p_m
    return logC(m, j) + (j - 1) * log(mpf(j)) + logp(m - j) - logp(m)

def tail_probs(k, Q):
    """1 - s_{k+q-1}(k) for q=1..Q via (7.10)."""
    t = {1: mpf(0)}
    for q in range(2, Q + 1):
        m = k + q - 1
        s = mpf(0)
        for j in range(k + 1, k + q):
            pj = exp(log_pi(m, j))
            s += pj * (mpf(j - k) / j + mpf(k) / j * t[j - k])
        t[q] = s
    return t

Q = 101
out.append("(a) k(1-s_{k+q-1}(k))/q^{3/2} via exact recursion (7.10):")
for k in [9950, 10000, 15000, 100000]:
    t = tail_probs(k, Q)
    ratios = [(k * t[q] / mpf(q) ** mpf(1.5), q) for q in range(2, Q + 1)]
    mx = max(ratios)
    viol = [q for r, q in ratios if r > mpf(1) / 2]
    out.append(f"  k={k}: max ratio = {mp.nstr(mx[0],6)} at q={mx[1]}; ratio at q=101: {mp.nstr(ratios[-1][0],6)}; #q in [2,101] with ratio>1/2: {len(viol)} (first few {viol[:6]})")
# limit T(q)
def Bor(w):
    w = mpf(w)
    return exp(-w + (w - 1) * log(w) - loggamma(w + 1))
T = {1: mpf(0)}
for q in range(2, 701):
    T[q] = sum(Bor(s + 1) * ((q - 1 - s) + T[q - 1 - s]) for s in range(0, q - 1))
rl = [(T[q] / mpf(q) ** mpf(1.5), q) for q in range(2, 701)]
out.append(f"  k->inf limit T(q)/q^{{3/2}}: max over q<=101: {mp.nstr(max(rl[:100])[0],6)} at q={max(rl[:100])[1]}; at q=101: {mp.nstr(rl[99][0],6)}; at q=120: {mp.nstr(rl[118][0],6)}; at q=250: {mp.nstr(rl[248][0],6)}; at q=700: {mp.nstr(rl[698][0],6)}")
out.append(f"  (원고 꼬리 삼중의 tf: 0.54 (M=120), 0.593 (M=250), 0.522 (M=300), 0.548 (M=450), 0.519 (M=700))")

# (7.12) with tf = 1/2, K1 = 9950, M = 101
def kebar(K1, M):
    K1 = mpf(K1); M = mpf(M)
    return 3 * (M - 1) / (2 * (K1 + 1)) + (M - 1) * (3 * M - 4) / (12 * (K1 + 1) ** 2) + (M - 1) ** 2 / (2 * (K1 + 1) * (K1 + 2 - M)) + (M - 1) ** 4 / (12 * (K1 + 1) ** 2 * (K1 + 2 - M))
def F712(tf, K1, M):
    kb = kebar(K1, M)
    worst = None
    for q in range(2, M + 1):
        v = tf * mpf(q) ** mpf(1.5) - exp(kb) * sum(Bor(s + 1) * ((q - 1 - s) + tf * mpf(q - 1 - s) ** mpf(1.5)) for s in range(0, q - 1))
        if worst is None or v < worst[0]:
            worst = (v, q)
    return worst
for tf in ["0.5", "0.52", "0.54"]:
    w = F712(mpf(tf), 9950, 101)
    out.append(f"  (7.12) with tf={tf}, K1=9950, M=101: min_q F = {mp.nstr(w[0],6)} at q={w[1]}  -> lemma 7:tail-bound {'gives' if w[0]>=0 else 'does NOT give'} 1-s <= {tf} q^1.5/k")

# (b) pair bound
out.append("(b) brute force: max over p,q>=1, j>=0, p+q+j<=L of LHS vs RHS, C=21/40:")
C = mpf(21) / 40
def e_(q):
    return q + C * mpf(q) ** mpf(1.5)
for L in [50, 58, 79, 99, 102]:
    best = (mpf(-1), None)
    for p in range(1, L):
        for q in range(1, L - p + 1):
            j = L - p - q
            v = j * (e_(q) + e_(p)) + (e_(q) * (p - 1) + e_(p) * (q - 1)) / 2
            if v > best[0]:
                best = (v, (p, q, j))
    rhs = mpf(L) ** 2 / 3 + (8 * C / 25) * sqrt(mpf(2) / 5) * mpf(L) ** mpf(2.5)
    out.append(f"  L={L}: max LHS = {mp.nstr(best[0],6)} at (p,q,j)={best[1]}; RHS = {mp.nstr(rhs,6)}; holds: {best[0]<=rhs}")
out.append("  F4의 접합점 (15000,102): 손실 분자 상계 14767 < 15000 라고 적음; 위 RHS(L=102)와 견준다.")
# what C is implied by the manuscript's tf at K1=15000 M=120 tf=0.54 for q=102: ex_hat = q + (k+q) n/(1-n), n = tf q^1.5/k
for tf in ["0.5", "0.54"]:
    k = mpf(15000); q = mpf(102); n = mpf(tf) * q ** mpf(1.5) / k
    exh = q + (k + q) * n / (1 - n)
    out.append(f"  implied C at k=15000,q=102 with tf={tf}: (ex_hat-q)/q^1.5 = {mp.nstr((exh-q)/q**mpf(1.5),5)}  (F4 needs C < 21/40 = 0.525)")

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_A7_P9_tail_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
