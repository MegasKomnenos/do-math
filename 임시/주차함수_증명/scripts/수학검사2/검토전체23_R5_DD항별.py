# 검토전체23 R5: 정리 6:old-8-22의 항별 부등식 DD(k+d-2,k-1) >= -H_d 표본 확인 (k=60, 300)
import math
from math import lgamma, exp, log
def g(x): return (x-1)*math.log1p(1/x)
def lbor(m): return -m + (m-1)*log(m) - lgamma(m+1)
def surv(y, dmax, LB):
    s = [None, 1.0]
    for d in range(2, dmax+1):
        tot = 0.0; acc = 0.0; base = LB[y+d]
        for q in range(1, d):
            p = exp(LB[d-q] + LB[y+q] - base); tot += p; acc += p*(y/(y+q))*s[q]
        val = (1.0-tot)+acc
        if d == y+3: val += exp(-1+2*LB[y+1]-LB[2*y+3])/2/(y+1)**2
        s.append(val)
    return s
def run(k):
    LB = [0.0]+[lbor(m) for m in range(1, 2*k+8)]
    G = [0.0]+[g(x) for x in range(1, 2*k+8)]
    Sm = surv(k-1, k+2, LB); S0 = surv(k, k+2, LB); Sp = surv(k+1, k+1, LB)
    sof = lambda tab, y, m: 1.0 if m <= y else tab[m-y+1]
    worst = None; cnt = 0
    for d in range(2, k+2):
        m = k+d-2
        DD = (k+1)*sof(Sp, k+1, m+2) - 2*k*sof(S0, k, m+1) + (k-1)*sof(Sm, k-1, m)
        Hd = 0.0
        for q in range(1, d):
            j = d-q
            incm = G[k-1+d]-G[k-1+q]; incp = G[k+d]-G[k+q]
            kk = math.expm1(incm)+math.expm1(-incp)
            Ac = (k-1)*kk/(2*(-math.expm1(-incp)))
            stp = Ac*(k+1+q)/q
            tilt = exp(LB[k+q]-LB[k+d]); r = (k-1)/(k-1+q)
            s = 0.0; rp = 1.0; jj = 1
            while jj < stp:
                rp *= r; s += jj*(1-jj/stp)*rp; jj += 1
            Hd += q*kk*tilt*exp(LB[j])*min(j, s)
        if DD < -Hd: cnt += 1
        v = DD + Hd
        if worst is None or v < worst[0]: worst = (v, d, DD, Hd)
    print("k", k, "violations of DD >= -H_d:", cnt, "min(DD+H_d), d, DD, H_d:", worst)
for k in (60, 300):
    run(k)
