# -*- coding: utf-8 -*-
"""T7a 검산: 7.4절의 수치 몇 가지를 다시 센다."""
from fractions import Fraction as Fr
import math

# (a) 명제 pair-check-10000: k=10000, q+q'+j<=50, (7.11) 우변
def pish(q, k): return Fr(q*(q-1), 2*(k+1))
def exbar(q, k):
    p = pish(q, k); return q + (k+q)*p/(1-p)
def rhs711(q, qp, j, k):
    eq, eqp = exbar(q, k), exbar(qp, k)
    return 1 - Fr(j, k)*(eq+eqp) - (eq*(qp-1)+eqp*(q-1))/Fr(2*k)
k = 10000
cnt = 0; cnt_ord = 0; mn = None; arg = None
for q in range(1, 51):
    for qp in range(q, 51):
        for j in range(0, 51-q-qp):
            cnt += 1
            cnt_ord += 1 if q == qp else 2
            v = rhs711(q, qp, j, k)
            if mn is None or v < mn: mn, arg = v, (q, qp, j)
print("(a) unordered count", cnt, "ordered", cnt_ord, "min", float(mn), "at", arg)

# (b) 명제 pair-reach-table: nu_P(K1) (배정밀도)
def lb(q, qp, j, k, tf):
    def ex(q):
        if q == 1: return 1.0
        nh = tf*q**1.5/k
        return q + (k+q)*nh/(1-nh)
    eq, eqp = ex(q), ex(qp)
    return 1 - j/k*(eq+eqp) - (eq*(qp-1)+eqp*(q-1))/(2*k)
table = [(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),
         (30000,250,0.593),(50000,250,0.593),(100000,300,0.522),(200000,450,0.548),(500000,450,0.548),(10**6,700,0.519)]
for K1, M, tf in table:
    nu = 2
    while True:
        ok = True
        for q in range(1, nu):
            qp = nu - q  # j=0 shell element; lb decreasing in j so check j = nu-q-qp for each (q,qp)
        # check all (q,qp) with q+qp<=nu, j=nu-q-qp
        for q in range(1, nu):
            for qp in range(q, nu-q+1):
                if q > M or qp > M: ok = False; break
                j = nu - q - qp
                if lb(q, qp, j, K1, tf) <= 0: ok = False; break
            if not ok: break
        if not ok: break
        nu += 1
    print("(b) K1", K1, "nu_P =", nu-1)

# (c) (7.12) for the five triples (float, Bor via lgamma)
def Bor(m): return math.exp(-m + (m-1)*math.log(m) - math.lgamma(m+1))
def kebar(K1, M):
    return 3*(M-1)/(2*(K1+1)) + (M-1)*(3*M-4)/(12*(K1+1)**2) + (M-1)**2/(2*(K1+1)*(K1+2-M)) + (M-1)**4/(12*(K1+1)**2*(K1+2-M))
for K1, M, tf in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    E = math.exp(kebar(K1, M)); worst = None
    for q in range(2, M+1):
        F = tf*q**1.5 - E*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0, q-1))
        rel = F/(tf*q**1.5)
        if worst is None or rel < worst[0]: worst = (rel, q)
    print("(c) triple", (K1, M, tf), "kebar", round(kebar(K1,M),4), "min rel margin", worst)

# (d) n_X(2002)
import decimal
decimal.getcontext().prec = 50
v = decimal.Decimal(2002) ** (decimal.Decimal(4)/decimal.Decimal(3))
print("(d) 2002^(4/3) =", v, "ceil =", math.ceil(v))
# tf*M^1.5 values
for M, tf in [(120,0.54),(250,0.593),(300,0.522),(450,0.548),(700,0.519)]:
    print("   tf*M^1.5", M, tf, round(tf*M**1.5, 1))
# n_M ratios
print("(d) nM ratios", 20507/841**1.5, 73032/2000**1.5)
# 1160 columns, 1130 columns
print("(d) 2000-841+1 =", 2000-841+1, "; 3130-2001+1 =", 3130-2001+1)
