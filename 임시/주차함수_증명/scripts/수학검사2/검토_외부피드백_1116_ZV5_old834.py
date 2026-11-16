# -*- coding: utf-8 -*-
"""ZV5 (외부 피드백 1116 묶음 B, 9.1) 보조정리 old-8-34 증명의 † 단계 검산.
a = 2(1+1/k)^{1-nu} - 1,  b = (1+1/(k-1))^{-(nu-1)},  theta = (nu-1)/(k-1),  q = 2e^{-theta} - 1.
현행 문장: 2e^{-theta}<1 이면 b in (0,1] 이고, a<0 이면 ab>=a, a>=0 이면 ab>=0 이므로 ab >= min(a,0) >= q.
(1) 피드백의 반례 k=6667, nu=4622 에서 a>0, ab<a 임을 확인한다(옛 문장 「곱은 첫째 인자 이상」이 거짓).
(2) 보조정리의 범위 k>=3, 103<=nu<=k-1 의 격자에서 a>=q, 0<b<=1, ab>=min(a,0)>=q, 그리고 두 경우 모두 >= 1-3theta-theta^2/2 를 확인한다.
(3) g(theta)=2e^{-theta}-2+3theta+theta^2/2 > 0 (theta>log 2) 와 h(theta)=(2e^{-theta}-1)e^{-theta}-(1-3theta-theta^2/2) >= 0 (theta in [0,log2]).
python -I 로 실행."""
from mpmath import mp, mpf, exp, log, sqrt
mp.dps = 30

k, nu = 6667, 4622
theta = mpf(nu - 1) / (k - 1); a = 2 * (1 + mpf(1) / k) ** (1 - nu) - 1; b = (1 + mpf(1) / (k - 1)) ** (-(nu - 1)); q = 2 * exp(-theta) - 1
print("(1) k=6667, nu=4622: theta =", mp.nstr(theta, 12), "> log2 =", mp.nstr(log(2), 12), "; 2e^-theta<1:", 2 * exp(-theta) < 1)
print("    a =", mp.nstr(a, 12), " ab =", mp.nstr(a * b, 12), " ab<a:", a * b < a, " q =", mp.nstr(q, 12), " min(a,0)>=q:", min(a, 0) >= q)

bad = 0; n = 0; worst = None
for kk in list(range(104, 400)) + list(range(400, 20001, 97)) + [6667, 100000, 10 ** 6]:
    nus = range(103, kk) if kk < 400 else sorted(set([103, 104, 200] + list(range(103, kk, max(1, (kk - 103) // 60))) + [kk - 2, kk - 1]))
    for nn in nus:
        if not (103 <= nn <= kk - 1):
            continue
        th = mpf(nn - 1) / (kk - 1); aa = 2 * (1 + mpf(1) / kk) ** (1 - nn) - 1; bb = (1 + mpf(1) / (kk - 1)) ** (-(nn - 1)); qq = 2 * exp(-th) - 1
        low = 1 - 3 * th - th * th / 2
        ok = (aa >= qq) and (0 < bb <= 1) and (aa * bb >= min(aa, 0)) and (min(aa, 0) >= qq if 2 * exp(-th) < 1 else aa * bb >= (2 * exp(-th) - 1) * exp(-th)) and (aa * bb >= low)
        n += 1
        if not ok:
            bad += 1; worst = (kk, nn)
print(f"(2) 격자 {n}개 점: 어긋남 {bad}개", worst if worst else "")

gmin = min(2 * exp(-t) - 2 + 3 * t + t * t / 2 for t in [log(2) + mpf(i) / 1000 for i in range(0, 1001)])
hmin = min((2 * exp(-t) - 1) * exp(-t) - (1 - 3 * t - t * t / 2) for t in [log(2) * mpf(i) / 1000 for i in range(0, 1001)])
print("(3) min_{theta in [log2, log2+1]} g =", mp.nstr(gmin, 8), "(g(log2) =", mp.nstr(2 * exp(-log(2)) - 2 + 3 * log(2) + log(2) ** 2 / 2, 8), "; g' = -2e^-t+3+t > 0)",
      "; min_{theta in [0,log2]} h =", mp.nstr(hmin, 8), "(h(0)=h'(0)=0, h''>0)")
