# -*- coding: utf-8 -*-
"""심사 A7 — S11 검산: 위험률 하계 hz_k(N) >= 1-e^{-eps_N}, eps_N = g(N+1)-g(k) (보조정리 6:old-7-24 (6.18)의
kappa 몫을 버린 쪽)에서 N+1>=2k일 때 hz >= (1/k)(3/4 - 11/(6k)) >= 1/(2k) 가 서는지,
그리고 그것을 정리 7:theorem-W (가)의 증명(U_0=300)에 넣었을 때 src - inh^lin 의 하계가
(P_n(k)/k)(c sqrt k - 301/(2k) - 1) 꼴로 k>=2001, n>=3k+1 전체에서 20 P_n(k)/k 를 넘는지를
정확한 g 값으로 다시 센다. 현행 (가)의 G_k(n) (0.14/n 하계)와도 견준다.
"""
import os
from mpmath import mp, mpf, log, exp, sqrt, pi

mp.dps = 30
ROOT = r"C:\math\임시\주차함수_증명"
out = []

def g(x):
    x = mpf(x)
    return (x - 1) * log(1 + 1 / x)

# 1. eps lower bound for N+1 >= 2k:  g(2k)-g(k) vs 3/(4k) - 17/(24k^2)
out.append("1. eps_N = g(N+1)-g(k) >= g(2k)-g(k) (g increasing) vs claimed 3/(4k)-17/(24k^2):")
for k in [301, 2001, 3131, 10**4, 10**6]:
    e = g(2 * k) - g(k)
    lb = mpf(3) / (4 * k) - mpf(17) / (24 * k * k)
    hz = 1 - exp(-e)
    hz_lb = (mpf(3) / 4 - mpf(11) / (6 * k)) / k
    out.append(f"  k={k}: g(2k)-g(k)={mp.nstr(e,10)}  claimed lb={mp.nstr(lb,10)}  ok={e>=lb};  1-e^-eps={mp.nstr(hz,10)}  claimed hz lb={mp.nstr(hz_lb,10)} ok={hz>=hz_lb}; >=1/(2k): {hz_lb >= mpf(1)/(2*k)}")

# 2. Is the 1-e^{-eps} part really dropped in the current proof?  current: hz >= kappa/(N+1) >= 0.307/(n-U) >= 0.14/n
out.append("2. current proof uses hz >= kappa_N/(N+1) >= 0.14/n; the new bound 1/(2k) vs 0.14/n at n=3k+1 and n=n_PD:")
for k in [2001, 3131, 10**4, 10**5]:
    nPD = int(mp.ceil(mpf(k + 1) ** (mpf(4) / 3))) + k + 1
    out.append(f"  k={k}: 1/(2k)={mp.nstr(mpf(1)/(2*k),6)}; 0.14/n at n=3k+1: {mp.nstr(mpf('0.14')/(3*k+1),6)}, at n=n_PD={nPD}: {mp.nstr(mpf('0.14')/nPD,6)}  (ratio new/old at n_PD: {mp.nstr(nPD/(2*k*mpf('0.14')),4)})")

# 3. Put into theorem-W(가) chain with U_0 = 300, n >= 3k+1:
#   sum_{U<=300} (rw-1) >= 2.38 k^{3/2} (n+1-k)^2/(e^{sg_n} n(n+1)) - 301   (current, unchanged)
#   bracket := sum (rw-1) hz - 1 >= (1/(2k)) * [above] - 1
out.append("3. bracket = sum_{U<=300}(rw-1) hz_k(n-1-U) - 1 with hz >= 1/(2k):  min over n>=3k+1 is at n=3k+1 (factor (1-k/n)^2 increasing in n):")
def bracket_new(k, n):
    k = mpf(k); n = mpf(n)
    sg = n * log(n / (n + 1)) + 1
    S = mpf('2.38') * k ** mpf('1.5') * (n + 1 - k) ** 2 / (exp(sg) * n * (n + 1)) - 301
    return S / (2 * k) - 1
def bracket_old(k, n):  # current G_k(n) - 1
    k = mpf(k); n = mpf(n)
    sg = n * log(n / (n + 1)) + 1
    return mpf('0.14') / n * (mpf('2.38') * k ** mpf('1.5') * (n + 1 - k) ** 2 / (exp(sg) * n * (n + 1)) - 301) - 1
for k in [301, 841, 2001, 3131, 6667, 10**4]:
    n = 3 * k + 1
    bn = bracket_new(k, n)
    F3 = sqrt(mpf(k)) / 2 - mpf(301) / (2 * k) - 1
    out.append(f"  k={k}: new bracket at n=3k+1: {mp.nstr(bn,6)}  (F3's sqrt(k)/2-301/(2k)-1 = {mp.nstr(F3,6)});  >20: {bn>20};  current G_k(3k+1)-1 = {mp.nstr(bracket_old(k,n),6)}")
# check validity conditions: N = n-1-U >= k and N+1 = n-U >= 2k for U<=300 when n>=3k+1
out.append("  conditions: n-1-U >= k and n-U >= 2k for all U<=300, n>=3k+1  <=>  k >= 300 (3k+1-300 >= 2k).  U_0=300 <= k-1 needs k>=301.")
# 4. current (나) threshold: G_k(n)>1 for k>=3131 and 2k+1<=n<=n_PD-1 ; check min over that range at k=3131 (sanity, record says 1.044)
k = 3131
nPD = int(mp.ceil(mpf(k + 1) ** (mpf(4) / 3))) + k + 1
vals = [bracket_old(k, n) + 1 for n in range(2 * k + 1, nPD)]
out.append(f"4. sanity: min_n G_3131(n) over [2k+1, n_PD-1] = {mp.nstr(min(vals),5)} (결정 128 기록의 1.044와 견줌); n_PD(3131)={nPD}")
# with the new hazard, how far down in k does the bracket stay positive at n=3k+1?
kk = 301
while bracket_new(kk, 3 * kk + 1) <= 0:
    kk += 1
out.append(f"5. smallest k>=301 with new bracket>0 at n=3k+1: {kk}")

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_A7_S11_hazard_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
