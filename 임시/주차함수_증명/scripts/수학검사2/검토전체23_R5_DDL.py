# 검토전체23 R5: (6.37)의 H_d와 DDL_2(k)를 정의대로 세어 명제 6:old-8-23의 항별 상계·닫힌 꼴과 대조
import math, sys
from math import lgamma, exp, log, sqrt, pi
def g(x): return (x-1)*math.log1p(1/x)
def lbor(m): return -m + (m-1)*log(m) - lgamma(m+1)
def run(k, check_terms=True):
    y0 = k
    G = [0.0]+[g(x) for x in range(1, 2*k+5)]
    LB = [0.0]+[lbor(m) for m in range(1, 2*k+5)]
    coef = 21/(5*sqrt(pi)*k)
    tot = 0.0; worst = 0.0; worstAc = 0.0
    for d in range(2, k+2):
        Hd = 0.0
        for q in range(1, d):
            j = d-q
            incm = G[y0-1+d]-G[y0-1+q]
            incp = G[y0+d]-G[y0+q]
            kk = math.expm1(incm) + math.expm1(-incp)
            Ac = (y0-1)*kk/(2*(-math.expm1(-incp)))
            stp = Ac*(y0+1+q)/q
            tilt = exp(LB[y0+q]-LB[y0+d])
            r = (k-1)/(k-1+q)
            s = 0.0; rp = 1.0
            jj = 1
            while jj < stp:
                rp *= r
                s += jj*(1-jj/stp)*rp
                jj += 1
            term = q*kk*tilt*exp(LB[j])*min(j, s)
            Hd += term
            if check_terms:
                bd = coef*min(q*sqrt(j)/k**2, 1/(3*q*sqrt(j)))
                worst = max(worst, term/bd)
                worstAc = max(worstAc, Ac)
        tot += Hd
    DDL2 = 2*tot
    DDLn = 14*(log(3*k)-1)/(5*sqrt(pi*k)) + 37.6/(5*sqrt(pi)*k)
    print("k", k, "DDL_2", DDL2, "DDL^nat", DDLn, "ratio", DDLn/DDL2, "max term/bound", worst, "max Acrit", worstAc)
for k in (300, 2001):
    run(k)
