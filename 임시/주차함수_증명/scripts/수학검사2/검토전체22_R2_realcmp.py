# R2 검산: 정리 4:old-4-7 (실수 비교) 하계의 수치 대조 — k=2000, omega=7 과 698/100
from mpmath import mp, mpf, quad, exp, log, loggamma, pi
mp.dps = 110
def run(k, oms):
    lb = [(-j + (j-1)*log(mpf(j)) - loggamma(j+1)) for j in range(1, k+1)]   # log Bor(j)
    Bork = exp(lb[k-1])
    def tail(Z):   # Bor^tail_k(Z) = 1 - sum_{j<=k} Bor(j) Z^{-1} (Z e^{1-Z})^j
        lq = log(Z) + 1 - Z
        s = mpf(0)
        for j in range(1, k+1):
            s += exp(lb[j-1] + j*lq)
        return 1 - s/Z
    cache = {}
    def w(v):
        if v not in cache: cache[v] = exp(k*v*v/2)*tail(1-v)
        return cache[v]
    pts = [mpf(0), mpf('0.02'), mpf('0.05'), mpf('0.08'), mpf('0.12'), mpf('0.18'), mpf('0.26'), mpf('0.36')]
    mp.dps = 110
    Wi = [quad(lambda v: w(v)*v*v*(v*v/2)**j, pts, maxdegree=5) for j in range(3)]
    eta = lambda v: -log(1-v) - v - v*v/2
    Ik = quad(lambda v: v/(1-v)*exp(-v*v/2)*exp(-k*eta(v)), pts + [mpf('0.6'), mpf('0.9'), mpf(1)], maxdegree=6)
    a0 = quad(lambda t: exp(-t**3/3), [0, 1, 4, mp.inf]); a1 = quad(lambda t: t*exp(-t**3/3), [0, 1, 4, mp.inf])
    for om in oms:
        R = k*Wi[2] + om*Wi[1] - Bork*Ik
        val = k*R/Bork
        bound = om - mpf(7)/2 - (4*om + mpf(1)/2)*a0*mpf(k)**(-mpf(1)/3) - mpf(13)*om/2*a1*mpf(k)**(-mpf(2)/3) - 12*om/mpf(k)
        print('k=%d omega=%s  k R/Bor(k) = %s   theorem lower bound = %s   ok=%s' % (k, mp.nstr(om, 4), mp.nstr(val, 10), mp.nstr(bound, 10), val >= bound))
    print('   Wi0,Wi1,Wi2 =', [mp.nstr(x, 8) for x in Wi], ' Bor(k) I_k =', mp.nstr(Bork*Ik, 8), ' k Wi2 =', mp.nstr(k*Wi[2], 8))
run(300, [mpf(7)])
run(2000, [mpf(7), mpf('6.98')])
