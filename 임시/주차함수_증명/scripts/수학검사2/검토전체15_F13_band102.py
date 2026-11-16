# F13: D.band102-integer (ㄱ)(ㄴ)(ㄷ) 수치 검산 (정확 분수 / mpmath)
from fractions import Fraction as Fr
from mpmath import mp, mpf, e as E, exp, factorial, sqrt
mp.dps = 40
# (ㄱ) k=10000, shells <= 50
k = 10000
def exbar(q):
    pi = Fr(q*(q-1), 2*(k+1)); return q + (k+q)*pi/(1-pi)
best = None
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51):
            if q+qp+j <= 50:
                v = 1 - Fr(j, k)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/Fr(2*k)
                if best is None or v < best[0]: best = (v, q, qp, j)
print('(ㄱ) min', float(best[0]), best[1:])
# (ㄴ) five triples
def Bor(m): return exp(-m)*mpf(m)**(m-1)/factorial(m)
for K1, M, tf in [(10**4,120,mpf('0.54')),(2*10**4,250,mpf('0.593')),(10**5,300,mpf('0.522')),(10**5,450,mpf('0.548')),(10**6,700,mpf('0.519'))]:
    ke = mpf(3*(M-1))/(2*(K1+1)) + mpf((M-1)*(3*M-4))/(12*(K1+1)**2) + mpf((M-1)**2)/(2*(K1+1)*(K1+2-M)) + mpf((M-1)**4)/(12*(K1+1)**2*(K1+2-M))
    minrel = None
    for q in range(2, M+1):
        F = tf*mpf(q)**1.5 - exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*mpf(q-1-s)**1.5) for s in range(0, q-1))
        rel = F/(tf*mpf(q)**1.5)
        if minrel is None or rel < minrel[0]: minrel = (rel, q)
        if F < 0: print('  NEG', K1, M, q)
    print('(ㄴ)', K1, M, float(tf), 'ke=%.4f' % ke, 'min rel', mp.nstr(minrel[0], 4), 'at q=', minrel[1])
# (ㄷ) K1=12000 with (120,0.54): shells 93 and 94
def lb(K1, M, tf, q, qp, j):
    def nh(q): return Fr(0) if q == 1 else tf*Fr(q)**1 * 0  # placeholder
    return None
import math
def lbk(K1, tf, q, qp, j):
    def exh(q):
        if q == 1: return mpf(q)
        n = tf*mpf(q)**1.5/K1
        return q + (K1+q)*n/(1-n)
    return 1 - mpf(j)/K1*(exh(q)+exh(qp)) - (exh(q)*(qp-1)+exh(qp)*(q-1))/(2*K1)
for K1, M, tf, nuP in [(12000,120,mpf('0.54'),93),(13000,120,mpf('0.54'),96),(10**6,700,mpf('0.519'),590)]:
    for nu in (nuP, nuP+1):
        worst = None
        for q in range(1, nu):
            for qp in range(q, nu-q+1):
                j = nu-q-qp
                if j < 0: continue
                v = lbk(K1, tf, q, qp, j)
                if worst is None or v < worst[0]: worst = (v, q, qp, j)
        print('(ㄷ)', K1, 'shell', nu, 'min lb', mp.nstr(worst[0], 4), worst[1:])
