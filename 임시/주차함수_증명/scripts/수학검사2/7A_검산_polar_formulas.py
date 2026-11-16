"""7A 부록 D.polar-blocks-488 식 (1)-(11)의 손 유도·닫힌 꼴·상수를 mpmath로 확인한다 (코드는 읽지 않고 식만 재구현)."""
import mpmath as mp
from mpmath import mpf, exp, log, sqrt, pi, e, quad, inf, gamma, zeta, cos, sin, binomial, factorial, mpf as F
mp.mp.dps = 40

def Bor(m): m = mpf(m); return exp(-m)*m**(m-1)/factorial(m)
def pr0(j): j = mpf(j); return (j-1)**(j-1)*exp(-j)/factorial(j) if j > 1 else exp(-1)
pc = exp(-1)/sqrt(2*pi); C2PI = 1/sqrt(2*pi)
print('=== (1) exact series check at small k ===')
k = 6; N = 260
p = lambda n: mpf(n+1)**(n-1) if n >= 1 else mpf(1)
# Q_{k-1}(x) = sum_{j=0}^{k-2} (k-1-j) p_j x^{j+1}/(j+1)!  as coefficient list
Qc = [mpf(0)]*(N+1)
for j in range(0, k-1): Qc[j+1] = (k-1-j)*p(j)/factorial(j+1)
def ser_mul(a, b):
    c = [mpf(0)]*(N+1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(0, N+1-i): c[i+j] += ai*b[j]
    return c
def ser_exp(a):      # exp of series with a[0]=0:  f' = a' f
    f = [mpf(0)]*(N+1); f[0] = mpf(1)
    da = [(i+1)*a[i+1] for i in range(N)] + [mpf(0)]
    for n in range(1, N+1):
        s = mpf(0)
        for i in range(0, n): s += da[i]*f[n-1-i]
        f[n] = s/n
    return f
eQ = ser_exp(Qc); emQ = ser_exp([-c for c in Qc])
integ = [mpf(0)] + [emQ[i]/(i+1) for i in range(N)]          # int_0^x e^{-Q}
inner = [mpf(1) - k*integ[0]] + [-k*integ[i] for i in range(1, N+1)]
Ck = ser_mul(eQ, inner); Ck = [mpf(1) - Ck[0]] + [-c for c in Ck[1:]]   # C_k = 1 - e^Q (1 - k int e^{-Q})
Cnk = [Ck[n]*factorial(n) for n in range(N+1)]                           # C_{n,k}
print('C_{n,k} = (n-1)^{n-1} for n<=k:', all(abs(Cnk[n] - ((mpf(n-1))**(n-1) if n > 1 else 1)) < mpf(10)**-25 for n in range(1, k+1)), ' C_{k+1,k}=', mp.nstr(Cnk[k+1], 12), ' vs (k)^k=', k**k)
Ck_eval = lambda x: sum(Ck[n]*x**n for n in range(N+1))
rho_k = mp.findroot(lambda x: Ck_eval(x) - 1, mpf('0.5'))
sig_k = k*log(e*rho_k)
print('rho_k = %s  varsigma_k = %s  C_k(rho_k)-1 = %s  tail term size %s' % (mp.nstr(rho_k, 15), mp.nstr(sig_k, 15), mp.nstr(Ck_eval(rho_k)-1, 3), mp.nstr(Ck[N]*rho_k**N, 3)))
def J_direct(s):
    r = exp(-1 + s/k); return sum(Ck[n]*r**n for n in range(k+1, N+1))
def T_i(s, i):          # second expression
    return exp(s*(1 + mpf(i)/k))*sum((k-m)*Bor(m)*pr0(k-m+i) for m in range(i, k))
def T_i_coef(s, i):     # first expression: rho^{k+i} [x^{k+i-1}] (Q' * sum_{j<=k} C_{j,j} x^j/j!)
    r = exp(-1 + s/k)
    Qp = [(j+1)*Qc[j+1] for j in range(N)] + [mpf(0)]
    Cle = [mpf(0)] + [((mpf(j-1))**(j-1) if j > 1 else mpf(1))/factorial(j) for j in range(1, k+1)] + [mpf(0)]*(N-k)
    prod = ser_mul(Qp, Cle)
    return r**(k+i)*prod[k+i-1]
theta_k = sum(Bor(m) for m in range(k, 4000)) + sum(m*Bor(m) for m in range(1, k))/k
theta_k_alt = 1 - sum(Bor(m) for m in range(1, k)) + sum(m*Bor(m) for m in range(1, k))/k
print('theta_k (tail to 4000) vs 1-sum_{m<k}:', mp.nstr(theta_k, 12), mp.nstr(theta_k_alt, 12))
theta_k = theta_k_alt
Xi = lambda s: sum(mpf(k-m)/m*Bor(m)*(exp(s*m/k) - 1 - s*m/k) for m in range(1, k))
Om = lambda s: s*(1 - theta_k) + Xi(s)
Qeval = lambda x: sum(Qc[n]*x**n for n in range(0, k))
r0 = exp(-1 + sig_k/k)
print('Omega(s)-Omega(s-f) == Q(rho)-Q(rho e^{-f/k}) at f=1.3:', mp.nstr(Om(sig_k) - Om(sig_k - mpf('1.3')) - (Qeval(r0) - Qeval(r0*exp(-mpf('1.3')/k))), 3))
def J_i(s, i): return quad(lambda f: exp(Om(s) - Om(s-f) - f*(1 + mpf(i)/k)), [0, 5, 20, 80, inf])
for s in (sig_k, mpf('1.0')):
    lhs = J_direct(s); rhs = sum(T_i(s, i)*J_i(s, i) for i in range(1, k))/k
    print('s=%s: J direct %s  formula %s  rel diff %s' % (mp.nstr(s, 8), mp.nstr(lhs, 15), mp.nstr(rhs, 15), mp.nstr(lhs/rhs - 1, 3)))
    print('   T_i coef-form vs Bor-form rel diff:', [mp.nstr(T_i_coef(s, i)/T_i(s, i) - 1, 2) for i in range(1, k)])
# K(x) = e^Q int_0^x f^k e^{-Q} = (x^{k+1}/k) J_1(varsigma(x))
for x in (rho_k, mpf('0.5')):
    sx = k*log(e*x)
    Kd = exp(Qeval(x))*quad(lambda f: f**k*exp(-Qeval(f)), [0, x])
    Kf = x**(k+1)/k*J_i(sx, 1)
    print('K(x) direct %s  (x^{k+1}/k)J_1 %s  rel %s' % (mp.nstr(Kd, 15), mp.nstr(Kf, 15), mp.nstr(Kd/Kf-1, 3)))
a_km1 = p(k-1)/factorial(k-1)
Pinf = k*a_km1*exp(Qeval(rho_k))*quad(lambda f: f**k*exp(-Qeval(f)), [0, rho_k])/rho_k
Pinf2 = Bor(k)*exp(sig_k)*J_i(sig_k, 1)
print('P_k(inf): k a_{k-1} K(rho)/rho = %s ; Bor(k) e^{s} J_1 = %s ; a_{k-1} rho^k vs Bor(k)e^s: %s' % (mp.nstr(Pinf, 15), mp.nstr(Pinf2, 15), mp.nstr(a_km1*rho_k**k/(Bor(k)*exp(sig_k)) - 1, 3)))
# bracket: sum_{n<=k} pr0_n e^{s n/k} + J(s) = 1 at s = sigma_k
print('sum_{n<=k} pr0 e^{sn/k} + J(s_k) - 1 =', mp.nstr(sum(pr0(n)*exp(sig_k*n/k) for n in range(1, k+1)) + J_direct(sig_k) - 1, 3))
# moments via Leibniz/Stirling
def ffall(x, v):
    out = mpf(1)
    for i in range(v): out *= (x - i)
    return out
S2 = {1: {1: 1}, 2: {1: 1, 2: 1}, 3: {1: 1, 2: 3, 3: 1}, 4: {1: 1, 2: 7, 3: 6, 4: 1}}
s = sig_k; r = exp(-1 + s/k)
q = [None] + [sum((k-m)*ffall(mpf(m), c)/m*Bor(m)*exp(s*m/k) for m in range(1, k)) for c in range(1, 5)]
qd = [None] + [r**c*sum(Qc[n]*ffall(mpf(n), c)*r**(n-c) for n in range(c, k)) for c in range(1, 5)]
print('q_c Bor-form vs rho^c Q^{(c)}(rho):', [mp.nstr(q[c]/qd[c]-1, 2) for c in range(1, 5)])
t = [sum(T_i(s, i)*ffall(mpf(k+i-1), v) for i in range(1, k)) for v in range(0, 4)]
y = [J_direct(s)]
for v in range(0, 4): y.append(sum(binomial(v, i)*q[i+1]*y[v-i] for i in range(0, v+1)) + t[v])
for j in range(1, 5):
    direct = sum(mpf(n)**j*Ck[n]*r**n for n in range(k+1, N+1))
    rec = sum(S2[j][v]*y[v] for v in S2[j])
    print('moment j=%d: direct %s  Leibniz/Stirling %s  rel %s' % (j, mp.nstr(direct, 15), mp.nstr(rec, 15), mp.nstr(direct/rec-1, 3)))

print('\n=== theta_j bounds (pr0_j = pc j^{-3/2} theta_j) ===')
def theta(j):
    j = mpf(j)
    return exp((j-1)*log(j-1) - j - mp.loggamma(j+1) + 1 + mpf(3)/2*log(j) + log(sqrt(2*pi))) if j > 1 else sqrt(2*pi)
js = list(range(1, 3001)) + [10**4, 10**5, 10**6, 10**7, 2*10**7]
bad_lo = [j for j in js if theta(j) < exp(mpf(5)/(12*j))]
bad_hi = [j for j in js if theta(j) > 1 + mpf('0.7')/j]
print('theta_1 = %s (>1.7: upper bound fails at j=1); fails lower:' % mp.nstr(theta(1), 8), bad_lo[:5], ' fails upper (j>=2 expected none):', [j for j in bad_hi if j >= 2][:5])
print('theta_2..5 =', [mp.nstr(theta(j), 10) for j in range(2, 6)], ' 1+0.7/j =', [mp.nstr(1 + mpf('0.7')/j, 6) for j in range(2, 6)], ' e^{5/12j}=', [mp.nstr(exp(mpf(5)/(12*j)), 6) for j in range(2, 6)])
mono = all(theta(j) > theta(j+1) for j in range(1, 3000)) and all(theta(a) > theta(b) for a, b in zip(js[-5:-1], js[-4:]))
print('theta_j strictly decreasing on tested j:', mono, '  theta_j - 1 - 5/(12j) at j=10^4: %s' % mp.nstr(theta(10**4) - 1 - mpf(5)/(12*10**4), 3))
print('Bor(m) <= (2pi)^{-1/2} m^{-3/2}, ratio e^{-eps} in [e^{-1/(12m)}, e^{-1/(12m+1)}]:', all(exp(-mpf(1)/(12*m)) <= Bor(m)*sqrt(2*pi)*mpf(m)**1.5 <= exp(-mpf(1)/(12*m+1)) for m in range(1, 500)))

print('\n=== (3) rho(x) increasing: q(w) = w^2 - 2(1-w)(-log(1-w)-w) >= 0 ===')
qw = lambda w: w*w - 2*(1-w)*(-log(1-w) - w)
print('min over w in (0,1):', mp.nstr(min(qw(mpf(i)/1000) for i in range(1, 1000)), 5), ' series: q = w^3/3 + ... :', mp.nstr(qw(mpf('0.01'))/(mpf('0.01')**3/3), 8))
# w(1): rho(1)
w1 = mp.findroot(lambda w: -log(1-w) - w - 1, mpf('0.8'))
print('w(x=1) = %s, rho(1) = 1 - w^2/2 = %s (>=1/2 for B>=v/2 on v>=k)' % (mp.nstr(w1, 10), mp.nstr(1 - w1**2/2, 8)))
# psi_1 at k=1e7
kk = mpf(10)**7
psi1 = 1 - mpf(2)/3*sqrt(2)*kk**(-mpf(1)/6) - kk**(-mpf(1)/3)/(1 - sqrt(2)*kk**(-mpf(1)/6))
print('psi_1(k=1e7) = %s (>=0.93?)' % mp.nstr(psi1, 8), ' psi_dagger = psi(k/8) =', mp.nstr(1 - mpf(2)/3*mpf('0.5') - mpf('0.125')/mpf('0.5'), 8), '= 5/12 =', mp.nstr(mpf(5)/12, 8))
print('2*3^{-3/2}*0.73^{-3/2} = %s (<=0.62?)   2*3^{-3/2}*(3/4)^{-3/2} = %s' % (mp.nstr(2*mpf(3)**-1.5*mpf('0.73')**-1.5, 6), mp.nstr(2*mpf(3)**-1.5*mpf('0.75')**-1.5, 6)))
# psi_i(u) = u (u+i)^{-3/2}: max at u=2i
i = mpf(7); print('psi_i max at 2i:', mp.nstr(2*i*(3*i)**-1.5, 10), ' 2*3^{-3/2} i^{-1/2} =', mp.nstr(2*mpf(3)**-1.5/sqrt(i), 10))
# w lower bound: w >= sqrt(2x) psi^{1/2}
for x in (mpf('1e-6'), mpf('0.01'), mpf('0.1')):
    w = mp.findroot(lambda w: -log(1-w) - w - x, sqrt(2*x)*0.9)
    y = sqrt(2*x); ps = 1 - mpf(2)/3*y - x/(1-y)
    print('x=%s: w=%s  lower sqrt(2x)psi^{1/2}=%s  upper sqrt(2x)=%s  B=kS3+w vs k w^3/3+w <= B <= k w^3/(3(1-w))+w:' % (mp.nstr(x, 3), mp.nstr(w, 10), mp.nstr(y*sqrt(ps), 10), mp.nstr(y, 10)),
          mp.nstr((-log(1-w) - w - w*w/2) - w**3/3, 3), mp.nstr(w**3/(3*(1-w)) - (-log(1-w) - w - w*w/2), 3))

print('\n=== (6) antiderivative A_N(u,m) = 2 sqrt(u)/(N sqrt m) - 2 i (u-m)/(N^2 sqrt(u m)) ===')
k1 = mpf(2001); i = mpf(5); N_ = k1 + i
A = lambda u, m: 2*sqrt(u)/(N_*sqrt(m)) - 2*i*(u-m)/(N_**2*sqrt(u*m))
g = lambda m: (k1 - m)*m**-1.5*(N_ - m)**-1.5
dA = mp.diff(lambda u: A(u, N_ - u), mpf(700))
print('dA/du at u=700: %s  vs (u-i)u^{-3/2}(N-u)^{-3/2}: %s' % (mp.nstr(dA, 12), mp.nstr((700-i)*mpf(700)**-1.5*(N_-700)**-1.5, 12)))
n1, n2 = mpf(60), mpf(1500)
print('int_{n1}^{n2} g dm quad %s  vs A(N-n1,n1)-A(N-n2,n2) %s' % (mp.nstr(quad(g, [n1, n2]), 15), mp.nstr(A(N_-n1, n1) - A(N_-n2, n2), 15)))
print('int_s^k g (A3 Ghat first term) = 2(k-s)^2/((k+s)^2 sqrt(ks)):', mp.nstr(A(N_-i, i) - A(N_-k1, k1), 12), mp.nstr(2*(k1-i)**2/((k1+i)**2*sqrt(k1*i)), 12))
D = mpf(40); xh = 2*sqrt(D+i) + 2*i/sqrt(D+i) - 4*sqrt(i) + 2*mpf(3)**-1.5/sqrt(i)
print('xh: sum_{j=1}^{D} j(j+i)^{-3/2} = %s <= int_0^D + max = %s' % (mp.nstr(sum(j*(j+i)**-1.5 for j in range(1, int(D)+1)), 10), mp.nstr(xh, 10)))

print('\n=== (10) closed form B_{[n1,n2]}(theta) ===')
r = exp(mpf('5.3')/2050); th = mpf('0.0137'); a, b = 40, 61
direct = sum(r**m*(1 - cos(m*th)) for m in range(a, b+1))
cf = (r**(b+1) - r**a)/(r-1) - (r**(b+2)*cos(b*th) - r**(b+1)*cos((b+1)*th) - r**(a+1)*cos((a-1)*th) + r**a*cos(a*th))/(r*r - 2*r*cos(th) + 1)
print('direct %s  closed %s  diff %s' % (mp.nstr(direct, 15), mp.nstr(cf, 15), mp.nstr(direct-cf, 3)))
print('Lipschitz: |dB/dtheta| <= sum m r^m <= n2 sum r^m :', mp.nstr(abs(sum(m*r**m*sin(m*th) for m in range(a, b+1))), 8), '<=', mp.nstr(b*(r**(b+1)-r**a)/(r-1), 8))
# L_far: sum_{m=m1}^{k1} f(m) >= int_{m1-1}^{k1} x^{-3/2} e^{sL x/k2}, f increasing for m >= 3k/(2 sL)
k1 = 2001; k2 = 2011; sL = mpf('5.29'); m1 = int(mp.ceil(max(k1/mpf(3), 3*k1/(2*sL)))) + 1
f = lambda m: mpf(m)**-1.5*exp(sL*m/k2)
print('L_far: m1=%d  sum f(m) = %s  >= int = %s ; series form = %s' % (m1, mp.nstr(sum(f(m) for m in range(m1, k1+1)), 10), mp.nstr(quad(lambda x: x**-1.5*exp(sL*x/k2), [m1-1, k1]), 10),
      mp.nstr(mpf(k1)**-0.5*sum((sL*k1/k2)**j/factorial(j)*(1 - (mpf(m1-1)/k1)**(j-mpf(1)/2))/(j-mpf(1)/2) for j in range(0, 71)), 10)))
print('   f increasing from m1-1? (log f)\' = -1.5/m + sL/k2 >= 0 at m1-1:', mp.nstr(-1.5/(m1-1) + sL/k2, 3))

print('\n=== (4) constants ===')
Ch = sqrt(pi)*mpf(2)/3*gamma(mpf(1)/3)
print('C_h = sqrt(pi)(2/3)Gamma(1/3) = %s ; quad int e^{-u^{3/2}} sqrt(pi/u) du = %s ; (asymptotic3.md says 3.1663)' % (mp.nstr(Ch, 10), mp.nstr(quad(lambda u: exp(-u**1.5)*sqrt(pi/u), [0, 1, inf]), 10)))
print('zeta(3/2) = %s <= 2.6124 ; Gamma(5/3) = %s ; 6*0.95^2/e = %s' % (mp.nstr(zeta(1.5), 12), mp.nstr(gamma(mpf(5)/3), 12), mp.nstr(6*mpf('0.95')**2/e, 6)))
tc = [mpf(n+1)/2**(n+2) for n in range(5)] + [mpf(12)/64]
worst = max(sum(tc[n]*(1-y)**n for n in range(6)) - (1+y)**-2 for y in [mpf(i)/500 for i in range(0, 501)])
print('(1+y)^{-2} <= sum tc_n (1-y)^n on [0,1]: min slack = %s ; tail at y=0: 1-sum_{n<5}tc_n = %s <= tc_5 = %s' % (mp.nstr(min(sum(tc[n]*(1-y)**n for n in range(6)) - (1+y)**-2 for y in [mpf(i)/500 for i in range(0, 501)]), 4), mp.nstr(1 - sum(tc[:5]), 6), mp.nstr(tc[5], 6)))
# Dlb_0 closed form
for s_, ph in ((mpf('10.9'), mpf('1.0')), (mpf('10.9'), mpf('4.5')), (mpf(30), mpf(20))):
    D0 = quad(lambda u: exp(-s_*u)*(1 - cos(ph*(1-u))), [0, inf])
    cf = (s_*s_*(1 - cos(ph)) - s_*ph*sin(ph) + ph*ph)/(s_*(s_*s_ + ph*ph))
    lb = max(s_*s_*(1 - cos(ph)), ph*ph)/(2*s_*(s_*s_ + ph*ph))
    print('Dlb_0(s=%s,phi=%s): quad %s closed %s  lower %s ok=%s' % (mp.nstr(s_, 4), mp.nstr(ph, 3), mp.nstr(D0, 12), mp.nstr(cf, 12), mp.nstr(lb, 8), lb <= D0))
s_ = mpf('10.9')
b1 = s_*(1 - cos(1))/(2*(s_*s_ + pi*pi)); b2 = 4*pi*pi*s_/((pi + sqrt(2)*s_)**2*(s_*s_ + 4*pi*pi)); b3 = 2*pi*pi/(s_*(s_*s_ + 4*pi*pi))
print('three regime values at s=10.9: %s %s %s ; min = %s (achain_iv Dlb at [10.9,10.92] = 0.0078492)' % (mp.nstr(b1, 8), mp.nstr(b2, 8), mp.nstr(b3, 8), mp.nstr(min(b1, b2, b3), 8)))
# check regime bounds against the max(...) bound over a grid of phi
def Bphi(ph): return max(s_*s_*(1 - cos(ph)), ph*ph)/(2*s_*(s_*s_ + ph*ph))
print('regime [1,pi]: min B - b1 = %s ; [pi,2pi]: %s ; [2pi,14s]: %s' % (
    mp.nstr(min(Bphi(1 + (pi-1)*mpf(i)/400) for i in range(401)) - b1, 3), mp.nstr(min(Bphi(pi + pi*mpf(i)/400) for i in range(401)) - b2, 3), mp.nstr(min(Bphi(2*pi + (14*s_-2*pi)*mpf(i)/2000) for i in range(2001)) - b3, 3)))
print('far: 2pi/(14 s) = %s/s (code 0.449); (1-e^{-s/2}-0.449)/s at 10.9 = %s >= 0.5/s = %s' % (mp.nstr(2*pi/14, 5), mp.nstr((1 - exp(-s_/2) - mpf('0.449'))/s_, 6), mp.nstr(mpf('0.5')/s_, 6)))

print('\n=== (5) TV constants ===')
for s_ in (mpf('10.9'), mpf(20), mpf(60)):
    for ph in (2*s_, 14*s_):
        half1 = 4*sqrt(2) + (12*sqrt(2) + 2*sqrt(2)*ph)/s_
        half0 = exp(-s_/2)*ph*ph*(s_ + 21)/(6*sqrt(2))
        # direct bound integral of the stated majorant
        maj = lambda x: exp(s_*x)*((s_*x**-1.5 + 1.5*x**-2.5)*min(2, ph*ph*x*x/2) + ph*x**-1.5*min(1, ph*x))
        direct = exp(-s_)*quad(maj, [0, mpf(1)/ph, 2/ph, mpf('0.5'), 1])
        closed = (11.32 + 17/s_ + (0.472*s_**3 + 9.9*s_**2)*exp(-s_/2)) if ph == 2*s_ else (45.3 + 17/s_ + (23.1*s_**3 + 486*s_**2)*exp(-s_/2))
        print('s=%s phi=%s: e^{-s} int majorant = %s ; pieces %s + %s = %s ; text closed form %s ; 150 s^2 = %s' % (mp.nstr(s_, 4), mp.nstr(ph/s_, 2) + 's', mp.nstr(direct, 6), mp.nstr(half1, 6), mp.nstr(half0, 6), mp.nstr(half1 + half0, 6), mp.nstr(closed, 6), mp.nstr(150*s_*s_, 6)))
print('4sqrt2=%s 12sqrt2=%s 4sqrt2+4sqrt2=%s 12sqrt2+... /s: 2sqrt2*2=%s -> 11.32+17/s ; 2sqrt2*14+4sqrt2=%s ; 4/(6sqrt2)=%s 21*that=%s ; 196/(6sqrt2)=%s 21*that=%s' % (
    mp.nstr(4*sqrt(2), 6), mp.nstr(12*sqrt(2), 6), mp.nstr(8*sqrt(2), 6), mp.nstr(4*sqrt(2), 6), mp.nstr(32*sqrt(2), 6), mp.nstr(4/(6*sqrt(2)), 6), mp.nstr(21*4/(6*sqrt(2)), 6), mp.nstr(196/(6*sqrt(2)), 6), mp.nstr(21*196/(6*sqrt(2)), 6)))
CGslack = min(2.2*s_*s_ + 7.4*s_ + 14 - (11.32 + 17/s_ + (0.472*s_**3 + 9.9*s_**2)*exp(-s_/2)) for s_ in [mpf('10.9') + mpf(i)/10 for i in range(0, 3000)])
print('2.2s^2+7.4s+14 - (11.32+17/s+(0.472s^3+9.9s^2)e^{-s/2}) min over s in [10.9,310.9]:', mp.nstr(CGslack, 6))
print('150 s^2 - (45.3+17/s+(23.1s^3+486s^2)e^{-s/2}) at s=10.9:', mp.nstr(150*mpf('10.9')**2 - (45.3 + 17/mpf('10.9') + (23.1*mpf('10.9')**3 + 486*mpf('10.9')**2)*exp(-mpf('10.9')/2)), 6))
# (log phi)' <= s - 1/(2y) numerically for the three functions
s_ = mpf('10.9')
f1 = lambda y: y**-1.5*(exp(s_*y)-1)*(1-y)**2*(1+y)**-2
fxe = lambda x: (1-x)*x**-2.5*(exp(s_*x)-1-s_*x)
f0 = lambda y: y**-0.5*exp(s_*y)*(1-y)**2*(1+y)**-2
for name, fn in (('phi_1', f1), ('phi_xe', fxe), ('phi_0', f0)):
    worst = max(mp.diff(lambda t: log(fn(t)), y) - (s_ - 1/(2*y)) for y in [mpf(i)/200 for i in range(1, 200)])
    print('%s: max[(log phi)\' - (s - 1/(2y))] = %s (<=0?)' % (name, mp.nstr(worst, 4)))
phc = lambda x, ph: x**-1.5*exp(s_*x)*(1 - cos(ph*x))
print('phi_c (log)\' at phi=pi, x=1/2: %s vs s+pi-3 = %s' % (mp.nstr(mp.diff(lambda t: log(phc(t, pi)), mpf('0.5')), 8), mp.nstr(s_ + pi - 3, 8)))

print('\n=== (8) P, Xi, theta_k bound formulas vs truth at k=2001, 2011 ===')
JJ = 70
def pwL(j, k):
    k = mpf(k)
    if j == 2: return mpf(4)/3 - 2/sqrt(k) + mpf(2)/3*k**-1.5
    d = j - mpf(5)/2; return 1/((d+1)*(d+2)) - d**d/((d+1)**(d+1)*k)
def pwU(j, k):
    k = mpf(k)
    if j == 2: return 1/sqrt(k) - k**-1.5 + 2*sqrt(1-1/k) - mpf(2)/3*(1-1/k)**1.5 - 2/sqrt(k) + mpf(2)/3*k**-1.5
    d = j - mpf(5)/2; return 1/((d+1)*(d+2)) + d**d/((d+1)**(d+1)*k)
def pwpU(j, k):
    k = mpf(k)
    if j == 2: return zeta(1.5)/sqrt(k)
    if j == 3: return pwU(2, k)/k
    d = j - mpf(7)/2; return (1/((d+1)*(d+2)) + 1/k)/k
for k in (2001, 2011, 150000):
    km = mpf(k)
    Cj = lambda j: sum((km-m)*mpf(m)**(j-mpf(5)/2) for m in range(1, k))
    Cpj = lambda j: sum((km-m)*mpf(m)**(j-mpf(7)/2) for m in range(1, k))
    oks = []
    for j in range(2, 8):
        v = Cj(j)/km**(j-mpf(1)/2); vp = Cpj(j)/km**(j-mpf(1)/2)
        oks.append((j, pwL(j, k) <= v <= pwU(j, k), vp <= pwpU(j, k), mp.nstr((pwU(j,k)-v)/v, 2), mp.nstr((v-pwL(j,k))/v, 2), mp.nstr((pwpU(j,k)-vp)/vp, 2)))
    print('k=%d: (j, pw ok, pw\' ok, relslack U, L, U\'):' % k, oks)
    # theta_k
    tk = 1 - sum(Bor(m) for m in range(1, k)) + sum(m*Bor(m) for m in range(1, k))/km
    tlo = C2PI*(2/sqrt(km)*(1 - 1/(12*km)) + (2*sqrt(km) - 2 - zeta(1.5)/12)/km); thi = C2PI*(2/sqrt(km-1) + (2*sqrt(km-1) - 1)/km)
    print('   theta_k = %s in [%s, %s]: %s ; tt = 2(2pi)^{-1/2}(k-1)^{-1/2} = %s >= sum_{m>=k} Bor = %s' % (mp.nstr(tk, 10), mp.nstr(tlo, 10), mp.nstr(thi, 10), tlo <= tk <= thi, mp.nstr(2*C2PI/sqrt(km-1), 8), mp.nstr(1 - sum(Bor(m) for m in range(1, k)), 8)))
    if k > 3000: continue
    # Xi bounds
    for u in (mpf('5.3'), mpf('0.02')):
        Xi_true = sum(mpf(k-m)/m*Bor(m)*(exp(u*m/km) - 1 - u*m/km) for m in range(1, k))
        RJ = u**(JJ+1)/factorial(JJ+1)*exp(u)*(1/((JJ+mpf(1)/2)*(JJ+mpf(3)/2)) + 1/km)
        Xlo = C2PI/sqrt(km)*sum(u**j/factorial(j)*(pwL(j, k) - pwpU(j, k)/12) for j in range(2, JJ+1))
        Xhi = C2PI/sqrt(km)*(sum(u**j/factorial(j)*pwU(j, k) for j in range(2, JJ+1)) + RJ)
        true_tail = C2PI/sqrt(km)*sum(u**j/factorial(j)*Cj(j)/km**(j-mpf(1)/2) for j in range(JJ+1, JJ+6))
        print('   Xi(u=%s) = %s in [%s, %s]: %s ; true tail j>J = %s vs R_J term %s (ratio R_J/tail = %s)' % (mp.nstr(u, 3), mp.nstr(Xi_true, 10), mp.nstr(Xlo, 10), mp.nstr(Xhi, 10), Xlo <= Xi_true <= Xhi, mp.nstr(true_tail, 3), mp.nstr(C2PI/sqrt(km)*RJ, 3), mp.nstr(RJ/(true_tail*sqrt(km)/C2PI), 4)))
    # P bounds
    for u in (mpf('5.3'), mpf('5.5')):
        P_true = sum(pr0(n)*exp(u*n/km) for n in range(1, k+1))
        x = u*(1 + 1/km)
        aL = lambda j: (2*sqrt(km+1) - 2*sqrt(2))/sqrt(km) if j == 1 else (1 - km**-(j-mpf(1)/2))/(j-mpf(1)/2)
        aU = lambda j: (2*sqrt(km) - 2)/sqrt(km) if j == 1 else ((1+1/km)**(j-mpf(1)/2) - (2/km)**(j-mpf(1)/2))/(j-mpf(1)/2)
        ap = lambda j: 2/sqrt(km) if j == 1 else ((2*sqrt(km)-2)*km**-1.5 if j == 2 else ((1+1/km)**(j-mpf(3)/2) - (2/km)**(j-mpf(3)/2))/((j-mpf(3)/2)*km))
        dPL = exp(-1)*(exp(u/km)-1) + pc/sqrt(km)*sum(u**j/factorial(j)*aL(j) for j in range(1, JJ+1))
        dPU = exp(-1)*(exp(u/km)-1) + pc/sqrt(km)*sum(u**j/factorial(j)*(aU(j) + mpf('0.7')*ap(j)) for j in range(1, JJ+1)) + pc/sqrt(km+1)*x**(JJ+1)/factorial(JJ+1)*exp(x)*(1/(JJ+mpf(1)/2) + mpf('0.7')/((km+1)*(JJ-mpf(1)/2)))
        PL = 1 - exp(-1) - 2*pc/sqrt(km)*(1 + mpf('0.7')/(km+1)) + dPL; PU = 1 - exp(-1) - 2*pc/sqrt(km+1) + dPU
        print('   P(%s) = %s in [%s, %s]: %s' % (mp.nstr(u, 3), mp.nstr(P_true, 12), mp.nstr(PL, 12), mp.nstr(PU, 12), PL <= P_true <= PU))
    tail_true = sum(pr0(n) for n in range(k+1, 200000)) + 2*pc/sqrt(mpf(200000))   # approx tail beyond 2e5 by integral
    print('   sum_{n>k} pr0 ~ %s in [2pc(k+1)^{-1/2}=%s, 2pc k^{-1/2}(1+0.7/(k+1))=%s]' % (mp.nstr(tail_true, 8), mp.nstr(2*pc/sqrt(km+1), 8), mp.nstr(2*pc/sqrt(km)*(1+mpf('0.7')/(km+1)), 8)))
    # (9) body moments and q_c at k with sp = 5.5, block [2001,2011]
    k1, k2 = 2001, 2011; sp = mpf('5.5')
    for j in (2, 3, 4):
        true = sum(mpf(n)**j*pr0(n)*exp(sp*n/km) for n in range(1, k+1))
        tot = exp(sp/k1 - 1); x = sp*(1 + mpf(1)/k1)
        for l in range(0, JJ+1):
            d = l + j - mpf(3)/2
            A_ = (k2+1)**(j-mpf(1)/2)*(1+mpf(1)/k1)**l*(1 - (mpf(2)/(k2+1))**(d+1))/(d+1)
            Ap = (k2+1)**(j-mpf(1)/2)*(1+mpf(1)/k1)**l*(1 - (mpf(2)/(k2+1))**d)/((k1+1)*d) if d >= 1 else 2*sqrt(k2) - 2
            tot += pc*sp**l/factorial(l)*(A_ + mpf('0.7')*Ap)
        tot += pc*(k2+1)**(j-mpf(1)/2)*x**(JJ+1)/factorial(JJ+1)*exp(x)*mpf('1.1')/(JJ + j - mpf(1)/2)
        print('   body moment j=%d at k=%d: true %s <= bound %s : %s (slack %s)' % (j, k, mp.nstr(true, 10), mp.nstr(tot, 10), true <= tot, mp.nstr(tot/true-1, 3)))
    true2 = sum(mpf(n)**2*pr0(n)*exp(mpf('5.29')*n/km) for n in range(1, k+1))
    lo2 = pc*mpf(k1)**1.5*sum(mpf('5.29')**l/factorial(l)*(1 - mpf(k1)**-(l+mpf(3)/2))/(l+mpf(3)/2) for l in range(0, JJ+1))
    print('   body moment2 lower at sL=5.29: true %s >= %s : %s' % (mp.nstr(true2, 10), mp.nstr(lo2, 10), lo2 <= true2))
    for c in (1, 2, 3, 4):
        qt = sum((km-m)*ffall(mpf(m), c)/m*Bor(m)*exp(sp*m/km) for m in range(1, k))
        tot = mpf(0)
        for l in range(0, JJ+1):
            jj = c + l
            Cn = zeta(1.5)*sqrt(km) if jj == 1 else pwU(jj, k)
            tot += sp**l/factorial(l)*Cn
        tot = C2PI*km**(c-mpf(1)/2)*(tot + sp**(JJ+1)/factorial(JJ+1)*exp(sp)*mpf('1.1')/((JJ+c-mpf(1)/2)*(JJ+c+mpf(1)/2)))
        print('   q_%d at k=%d: true %s <= Q_up %s : %s (slack %s)' % (c, k, mp.nstr(qt, 10), mp.nstr(tot, 10), qt <= tot, mp.nstr(tot/qt-1, 3)))
    sLq = mpf('5.29'); qt1 = sum((km-m)*Bor(m)*exp(sLq*m/km) for m in range(1, k))
    W = mpf(0)
    for l in range(0, JJ+1):
        jj = l+1
        if jj == 1: Cn = (km*(2 - 2/sqrt(km)) - (2*sqrt(km-1) - 1))/sqrt(km); Cp = mpf('1.3415')*sqrt(km)
        else: Cn = pwL(jj, k); Cp = pwpU(jj, k)
        W += sLq**l/factorial(l)*max(Cn - Cp/12, 0)
    W = C2PI*sqrt(km)*W
    print('   q_1 lower at sL: true %s >= W_lo %s : %s ; zeta(5/2)=%s <= 1.3415' % (mp.nstr(qt1, 10), mp.nstr(W, 10), W <= qt1, mp.nstr(zeta(2.5), 8)))

print('\n=== [A10] constants at sigma = 300 and 1000 (Poisson expectations) ===')
def pois_E(sig, f, J=None):
    if J is None: J = int(4*sig + 200)
    return sum(exp(-sig)*sig**j/factorial(j)*f(j) for j in range(0, J+1))
for sig in (mpf(300), mpf(1000)):
    pe = pois_E(sig, lambda j: 1/(j - mpf(1)/2) if j >= 1 else 0)
    xe = pois_E(sig, lambda j: 1/((j - mpf(3)/2)*(j - mpf(1)/2)) if j >= 2 else 0)
    q1 = pois_E(sig, lambda j: 1/((j - mpf(1)/2)*(j + mpf(1)/2)) if j >= 1 else 0)
    xit = pois_E(sig, lambda j: 1/(j - mpf(3)/2) if j >= 2 else 0)
    m05 = pois_E(sig, lambda j: 1/(j + mpf(1)/2))
    tc_ = [mpf(n+1)/2**(n+2) for n in range(5)] + [mpf(12)/64]
    def bp(j, start, n):
        out = factorial(n)
        for i in range(n+1): out /= (j + start + i)
        return out
    tr1 = sum(tc_[n]*pois_E(sig, lambda j, n=n: bp(mpf(j), -mpf(1)/2, n+2) if j >= 1 else 0) for n in range(6))
    s0 = sum(tc_[n]*pois_E(sig, lambda j, n=n: bp(mpf(j), mpf(1)/2, n+2)) for n in range(6))
    print('sigma=%s: pe*s=%s in [0.99,2.01]; xe*s^2=%s q1*s^2=%s (<=4.1); xit*s=%s m_{1/2}*s=%s (<=2.1); tr1*s^3=%s s0*s^3=%s (<=8.5); Chernoff P(J<=s/2)=%s vs e^{-0.153s}=%s; Lam_hi<= (sqrt(2pi)+1e-3)/pe /s = %s (<=2.54)' % (
        mp.nstr(sig, 4), mp.nstr(pe*sig, 5), mp.nstr(xe*sig**2, 5), mp.nstr(q1*sig**2, 5), mp.nstr(xit*sig, 5), mp.nstr(m05*sig, 5), mp.nstr(tr1*sig**3, 5), mp.nstr(s0*sig**3, 5),
        mp.nstr(sum(exp(-sig)*sig**j/factorial(j) for j in range(0, int(sig/2)+1)), 3), mp.nstr(exp(-mpf('0.153')*sig), 3), mp.nstr((sqrt(2*pi) + mpf('0.001'))/pe/sig, 5)))
print('D_lb(300) = 4pi^2 s/((pi+sqrt2 s)^2(s^2+4pi^2)) vs 1.9pi^2/s^3:', mp.nstr(4*pi*pi*300/((pi+sqrt(2)*300)**2*(300**2+4*pi*pi)), 6), mp.nstr(1.9*pi*pi/300**3, 6), ' c0*1.17*1.9pi^2 =', mp.nstr(pc*1.17*1.9*pi*pi, 4), '>= 2.7')
print('6 gamma^2 e^{-1} with gamma=0.95:', mp.nstr(6*mpf('0.95')**2/e, 5))

print('\n=== [A8] 1/(1-e^{-1/k}) <= k+1 ; polar-W numbers ===')
for kk in (2, 10, 2001):
    print('k=%d: 1/(1-e^{-1/k}) = %s <= k+1' % (kk, mp.nstr(1/(1-exp(-mpf(1)/kk)), 10)))
print('2^{3/2}/3 =', mp.nstr(2**1.5/3, 8), ' psi_1^{3/2} at 0.93:', mp.nstr(mpf('0.93')**1.5, 6), ' k w_*^3/3 with w_*=sqrt(5/12)/2: coefficient', mp.nstr((sqrt(mpf(5)/12)/2)**3/3, 6))
