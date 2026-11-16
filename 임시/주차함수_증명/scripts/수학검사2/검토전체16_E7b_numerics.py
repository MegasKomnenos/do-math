# E7b: 7.6-7.7절 수치 재계산 (정리 theorem-W, 보조정리 threshold-unit-ratio, 정리 old-6-21, old-6-22)
from mpmath import mp, mpf, sqrt, log, exp, pi, cbrt
mp.dps = 30
k = mpf(3131)
print("sqrt(2pi)^-1 =", 1/sqrt(2*pi))
print("0.9538/0.398943 =", mpf('0.9538')/mpf('0.398943'))
print("1-0.8/sqrt(301) =", 1-mpf('0.8')/sqrt(301))
print("2/sqrt(2pi) =", 2/sqrt(2*pi))
print("0.14*2.38*0.9999 =", mpf('0.14')*mpf('2.38')*mpf('0.9999'), " 0.14*301 =", mpf('0.14')*301)
# sg_n bound at n=6263
n = mpf(6263)
sg_ub = 1/(2*(n+1)) + 1/(6*n*(n+1))
print("sg_6263 ub =", sg_ub, " exp(-ub) =", exp(-sg_ub), " exact sg =", n*log(n/(n+1))+1)
# D_k(2)
D2 = mpf('0.08329')*sqrt(k) - 2 - mpf('42.14')/k
print("0.33316/4 =", mpf('0.33316')/4, " D_3131(2) =", D2)
# right end
t = k**(mpf(1)/6)
print("k^(1/6) =", t)
R = mpf('0.33316')*(sqrt(k) - 2*t + 1/t) - mpf('1.0005')*k**(mpf(1)/3) - mpf('1.0145')
print("right-end bound at 3131 =", R)
dR = mpf('0.33316')*(3*k**(mpf(1)/3) - 2 - k**(-mpf(1)/3)) - mpf('2.001')*t
print("derivative wrt t at 3131 =", dR)
print("(1+1/k)^(4/3) =", (1+1/k)**(mpf(4)/3), " 1+2/k =", 1+2/k, " 42.14/k+1.001 =", mpf('42.14')/k + mpf('1.001'))
# n_PD vs 3k+2
nPD = mp.ceil((k+1)**(mpf(4)/3)) + k + 1
print("n_PD(3131) =", nPD, " 3k+2 =", 3*k+2)
# D_k concave check: actual G_k(n) > 1 on grid for k=3131
def G(k, n):
    sg = n*log(n/(n+1))+1
    return mpf('0.14')/n*(mpf('2.38')*k**mpf(1.5)*(n-k+1)**2/(exp(sg)*n*(n+1)) - 301)
k0 = mpf(3131)
nPD0 = int(mp.ceil((k0+1)**(mpf(4)/3)) + k0 + 1)
mn = min(G(k0, mpf(nn)) for nn in range(2*3131+1, nPD0))
print("min G_3131(n) over [2k+1, nPD-1] =", mn)
# threshold-unit-ratio
k = mpf(6667)
j0 = mp.floor(mpf('0.3')*k)
val = -((mpf('0.3')*k-1)*(mpf('0.3')*k))/(2*(mpf('1.3')*k+1))
print("j0 =", j0, " -(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =", val)
print("1+1.5 log k + val =", 1+mpf(1.5)*log(k)+val)
print("exact -j0(j0+1)/(2(k+1+j0)) =", -j0*(j0+1)/(2*(k+1+j0)))
print("e^0.3 =", exp(mpf('0.3')), " e^(3/(2k)) =", exp(3/(2*k)))
print("1.00023*1.34986 =", mpf('1.00023')*mpf('1.34986'))
print("2*0.7654-1.3502 =", 2*mpf('0.7654')-mpf('1.3502'))
print("x_k*n at k=501,n=1003 >= n/e =", mpf(1003)/exp(1), " x_501*1003 =", (mpf(501)/502)**500*1003)
# ratio (n-k+1)^2/(n(n+1)) >= (1-k/n)^2 check for a few
for (kk,nn) in [(3131,6263),(3131,20000),(2000,4001)]:
    kk,nn = mpf(kk),mpf(nn)
    print("ratio check", (nn-kk+1)**2/(nn*(nn+1)) >= (1-kk/nn)**2)
# D_k second derivative sign: f=(1-1/x)^2, f''=2(3-2x)/x^4
# W_L^flat / LRP_2 residual boundaries
print("3*3333-1 =", 3*3333-1, " 3*3334-1 =", 3*3334-1, " 3*6667-1 =", 3*6667-1, " 3*6668-1=", 3*6668-1, " 2*6668+103 =", 2*6668+103)
# Bor tail numeric check: sum_{d>301} Bor(d)
from mpmath import factorial
Bor = lambda d: exp(-d)*d**(d-1)/factorial(d)
s = sum(Bor(mpf(d)) for d in range(1,302))
print("sum_{d<=301} Bor(d) =", s)
# kappa floor use: 0.307/(n-U) >= 0.14/n trivially
