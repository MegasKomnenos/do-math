# R2 검산(수치, mpmath): a_0,a_1; 정리 4:old-4-7; (4.9); int F_1; Borel 둘째 조각; M_0 하계; g_k
import mpmath as mp
mp.mp.dps = 40
a0 = mp.quad(lambda w: mp.e**(-w**3/3), [0, 2, 6, mp.inf]); a1 = mp.quad(lambda w: w*mp.e**(-w**3/3), [0, 2, 6, mp.inf])
print("a0", a0, "closed", 3**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3)); print("a1", a1, "closed", 3**(-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3))

def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def Bor2(j, Z): return mp.e**(-j*Z)*(j*Z)**(j-1)/mp.factorial(j)
def Btail(k, Z): return 1 - mp.fsum(Bor2(j, Z) for j in range(1, k+1))

# 정리 4.7: k R_{k,w}/Bor(k) >= ...
def Rk(k, om):
    Wi = lambda j: mp.quad(lambda v: mp.e**(k*v*v/2)*v*v*Btail(k, 1-v)*(v*v/2)**j, [0, 0.2, 0.5, 0.8, 1])
    eta = lambda v: -mp.log(1-v) - v - v*v/2
    Ik = mp.quad(lambda v: v/(1-v)*mp.e**(-v*v/2)*mp.e**(-k*eta(v)), [0, 0.2, 0.5, 0.8, 1])
    return k*Wi(2) + om*Wi(1) - Bor(k)*Ik
mp.mp.dps = 25
for k in (5, 20, 60):
    for om in (0, 3.5, 6.98):
        lhs = k*Rk(k, om)/Bor(k)
        rhs = om - 3.5 - (4*om+0.5)*a0*k**(-mp.mpf(1)/3) - 6.5*om*a1*k**(-mp.mpf(2)/3) - 12*om/mp.mpf(k)
        print("thm4.7 k=%d om=%s lhs=%s rhs=%s ok=%s" % (k, om, mp.nstr(lhs, 8), mp.nstr(rhs, 8), lhs >= rhs))

# 둘째 조각: sum_{j<=k} j Bor(j) - (2(2pi)^{-1/2} sqrt k - 2/3) in [0, (2/3)(2pi)^{-1/2} k^{-1/2}]
mp.mp.dps = 30
c = 1/mp.sqrt(2*mp.pi)
s = mp.mpf(0); okk = True; worst = None
for k in range(1, 3001):
    s += k*Bor(k)
    diff = s - (2*c*mp.sqrt(k) - mp.mpf(2)/3)
    up = mp.mpf(2)/3*c/mp.sqrt(k)
    if not (0 <= diff <= up): okk = False; worst = k; break
print("second piece interval ok k<=3000:", okk, worst, "ratio at 3000:", mp.nstr(diff/up, 6))
# 첫 조각: 0 <= 2c eps - Btail_k(1) <= (5/9) c eps^3
okk = True
tot = mp.mpf(0)
for k in range(1, 3001):
    tot += Bor(k)
    t1 = 1 - tot
    diff = 2*c/mp.sqrt(k) - t1
    if not (0 <= diff <= mp.mpf(5)/9*c*k**(-1.5)): okk = False; print("first piece fail", k); break
print("first piece ok:", okk)

# (4.9)
def Bsum(k, phi): return mp.fsum(Bor(j)*mp.e**(-phi*j/k) for j in range(1, k+1))
def Bld(phi): return 2 + mp.quad(lambda w: w**(-1.5)*(1 - mp.e**(-phi*w)), [0, 0.01, 0.1, 0.5, 1])
allok = True
for k in (10, 100, 1000):
    for phi in (mp.mpc(-0.5, 0.1), mp.mpc(-2, 1.5), mp.mpc(-8, 6), mp.mpc(-0.01, 0.0), mp.mpc(-30, -20), mp.mpc(0, 0)):
        lhs = abs(Bsum(k, phi) - 1 + c*k**-0.5*Bld(phi) - mp.mpf(2)/3*phi/k)
        rhs = c*k**-1.5*mp.e**(-phi.real)*(mp.mpf(5)/9 + mp.mpf(2)/3*abs(phi) + mp.mpf(13)/12*abs(phi)**2)
        if lhs > rhs: allok = False; print("(4.9) FAIL", k, phi, lhs, rhs)
print("(4.9) samples ok:", allok)

# int_R F_1 = 46 sqrt2 - 12
ninf = 2/mp.sqrt(mp.pi)
def F1int():
    def inner(rho):
        mu = 1 - rho*rho; a = (1 + rho*rho)/2
        gm = lambda m: mp.gamma(m + mp.mpf(1)/2)/a**(m + mp.mpf(1)/2)   # int_R z^{2m} e^{-a z^2}
        # z^4 * Pq * [4/3 rho^2 z^2 - 2/3 rho z^4],  Pq = mu z^2 + mu^2 z^4/4
        val = rho**2*(mu*(mp.mpf(4)/3*rho**2*gm(4) - mp.mpf(2)/3*rho*gm(5)) + mu**2/4*(mp.mpf(4)/3*rho**2*gm(5) - mp.mpf(2)/3*rho*gm(6)))
        return val
    return -ninf*mp.quad(inner, [0, 0.5, 1])
print("int F1 =", F1int(), " 46sqrt2-12 =", 46*mp.sqrt(2) - 12)

# M_0 하계, g_k (k=10^4, nu in {-1,0}; 또 nu=19, k=10^4; nu=102,k=15000)
mp.mp.dps = 60
def gauss(k, nu, yv=None):
    n = 2*k + nu; yv = mp.mpf(k) if yv is None else mp.mpf(yv); N = n + yv + 1
    # 비 upsilon_j 로 계산
    ups = mp.mpf(1); x = yv/N**2
    logHe = mp.log(N)   # He_1 = N
    u_prev = ups
    us = [None, mp.mpf(1)]
    for j in range(2, n+1):
        u = 1 - (j-1)*x/u_prev
        us.append(u); u_prev = u
    logHe_n = n*mp.log(N) + mp.fsum(mp.log(u) for u in us[1:])
    theta = N*us[n] - n
    logpn = (n-1)*mp.log(n+1)
    M0 = mp.e**(-yv/2 + logHe_n - logpn)*theta/(n + theta)
    kk = mp.mpf(k); v = mp.mpf(nu)
    U2 = 1 + (2*v+2)/kk + v*(v+1)/kk**2; V2 = 4 + (4*v+2)/kk + v*(v+1)/kk**2
    g = 2 - kk*(U2 - V2/theta)
    return M0, theta, g
for (k, nu) in [(10000, -1), (10000, 0), (10000, 19), (15000, 102), (1000000, 590)]:
    M0, th, g = gauss(k, nu)
    lb = 4*mp.sqrt(2)*(1 - (23.75 + 2.5*nu)/k)
    H = 4 - (26 + 4*nu)/mp.mpf(k) + (506 + 97*nu + 5*nu*nu)/mp.mpf(k)**2
    print("k=%d nu=%d M0=%s lb=%s ok=%s theta=%s (in [4-(26+4nu)/k,4): %s) k^2(theta-H0-H1/k-H2/k^2)=%s g_k=%s" % (
        k, nu, mp.nstr(M0, 10), mp.nstr(lb, 10), M0 >= lb, mp.nstr(th, 12), (4 - (26+4*nu)/mp.mpf(k) <= th < 4), mp.nstr((th - H)*mp.mpf(k)**2, 6), mp.nstr(g, 8)))
