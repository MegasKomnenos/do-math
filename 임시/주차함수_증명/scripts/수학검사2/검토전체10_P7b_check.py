# -*- coding: utf-8 -*-
"""검토전체10 P7b: 7.6–7.8절의 항등식·부등식을 작은 k에서 정확 유리수로, 상수를 부동소수점으로 다시 센다."""
from fractions import Fraction as F
from math import comb, log, exp, sqrt, pi, factorial, lgamma, e as E

def build(k, nmax):
    # A[l][m] for l in {k-2,k-1,k}, m<=nmax, 마지막 차 재귀
    A = {}
    for l in (k-2, k-1, k):
        a = [F(0)]*(nmax+1)
        a[0] = F(1)
        for m in range(1, nmax+1):
            s = F(0)
            for j in range(1, m+1):
                s += comb(m-1, j-1)*min(j, l+1)*a[j-1]*a[m-j]
            a[m] = s
        A[l] = a
    return A

def p(m):
    return F((m+1)**(m-1)) if m >= 1 else F(1)

def checks(k, nmax):
    A = build(k, nmax)
    s = lambda m, y: A[y-1][m]/p(m)              # s_m(y), y in {k-1,k,k+1}
    c = lambda m, Y: (A[Y][m]-A[Y-1][m])/p(m)    # c_m(Y)
    Pn = lambda n, j: F(j*comb(n-1, j-1))*p(j-1)*p(n-j)/p(n)
    Pk = lambda n, j: F(min(j, k)*comb(n-1, j-1))*A[k-1][j-1]*A[k-1][n-j]/A[k-1][n]
    clp = lambda m: (A[k][m]-A[k-1][m])/A[k-1][m]
    clm = lambda m: (A[k-1][m]-A[k-2][m])/A[k-1][m]
    mu = lambda m: clp(m)-clm(m)
    def chi(n, j):
        v = F(0)
        if j == k:
            v += -F(1, k)*(1-clm(n-k))
        if j > k:
            v += F(1, k)*(clp(j-1)+clm(j-1)+clp(n-j)+clm(n-j))
        h = F(1, k) if j > k else F(0)
        v += (1+h)*clp(j-1)*clp(n-j) + (1-h)*clm(j-1)*clm(n-j)
        return v
    src = lambda n: sum(Pk(n, j)*chi(n, j) for j in range(1, n+1))
    inh = lambda n: sum(Pk(n, j)*(mu(j-1)*(k <= j-1 <= 2*k) + mu(n-j)*(k <= n-j <= 2*k)) for j in range(1, n+1))
    inhlin = lambda n: F(1, k)*sum(Pk(n, j)*((clp(j-1)+clm(j-1))*(k <= j-1 <= 2*k) + (clp(n-j)+clm(n-j))*(k <= n-j <= 2*k)) for j in range(1, n+1))
    hz = lambda N: 1 - s(N+1, k)/s(N, k)
    bad = []
    for n in range(2*k+1, nmax+1):
        nu = n-2*k
        rw = lambda q: F(k, k+1+q)*Pn(n, k+1+q)/Pn(n, k)
        # root-symmetry
        if rw(nu) != 1: bad.append(('rw(nu)!=1', k, n))
        for q in range(0, k+nu-1):
            lhs = rw(q+1)/rw(q)
            j = k+1+q
            rhs = F((j+1)**(j-1), j**(j-1)) * F((n-j)**(n-j-1), (n-j+1)**(n-j-1))
            if lhs != rhs: bad.append(('rw ratio', k, n, q))
        if any(rw(q) < 1 for q in range(nu, k+nu)): bad.append(('rw>=1', k, n))
        # (7.22)
        L = k*s(n, k)*src(n)
        R22 = sum(F(k, j)*Pn(n, j)*((c(j-1, k-1)+c(j-1, k))*s(n-j, k) + s(j-1, k)*(c(n-j, k-1)+c(n-j, k))) for j in range(k+1, n+1)) - Pn(n, k)*s(n-k, k-1)
        if L < R22: bad.append(('7.22', k, n))
        # (7.23)
        br1 = sum(rw(q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1)
        br2 = c(k+nu, k-1) + s(k+nu, k+1) - s(n, k) - s(n, k+1)
        if R22 < Pn(n, k)*br1: bad.append(('7.23a', k, n))
        if br1 < br2: bad.append(('7.23b', k, n))
        # top-roots
        for U0 in range(0, k):
            brT = br2 + sum((rw(k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1))
            brH = s(n, k)*(sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(0, U0+1)) - 1)
            if br1 < brT or brT < brH: bad.append(('top-roots', k, n, U0))
        # apex identity
        apex = F(1, k)*(sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1, n+1)) - Pk(n, k)*(1-clm(n-k)))
        if k*s(n, k)*apex != Pn(n, k)*br1: bad.append(('apex', k, n))
        # Fold identity (fold-A 셈)
        l = -(-3*k//10)  # ceil(0.3k)
        if l <= k-2:
            B = n-1-k-l
            Fold = F(1, k)*(sum(Pk(n, j)*(clp(j-1)+clm(j-1)) for j in range(n-k, n-l+1)) - Pk(n, k)*(1-clm(n-k)))
            at = lambda m, y: F(1, factorial(m))*A[y-1][m]  # e^m 빼고: ã^{(y)}_m e^m
            # Eu_n = e^{-1}/(n ã_n); Fold/Eu = e n ã_n Fold ; e-인자 모두 상쇄되도록 e^{n-1} 곱한 꼴로 비교
            # thr = -e Bor(k) ã^-_{n-k} = -(p_{k-1}/(k-1)!) e^{-(k-1)} e^{-(n-k)} A^-_{n-k}/(n-k)!
            lhs = n*at(n, k)*Fold  # = Fold/Eu * e^{n-1}
            thr = -F(p(k-1), factorial(k-1))*at(n-k, k-1)
            sm = sum(F(p(n-1-k-q), factorial(n-1-k-q))*(at(k+q, k+1)-at(k+q, k-1)) for q in range(nu-1, B+1))
            if lhs != thr+sm: bad.append(('Fold', k, n))
        # (7.24)
        if n >= 3*k+1:
            w = lambda m: F(comb(n-1, m))*p(m)*A[k-1][n-1-m]/A[k-1][n]
            pp = lambda m: ((k+1)*(A[k][m]-A[k-1][m]) - (k-1)*(A[k-1][m]-A[k-2][m]))/p(m)
            Left = sum(w(m)*pp(m) for m in range(k, 2*k+1))
            if inhlin(n)+inh(n) != 2*Left: bad.append(('7.24', k, n))
            if any(w(m+1) < w(m) for m in range(k, 2*k)): bad.append(('w nondec', k, n))
        # (7.25)
        if n <= 3*k:
            d = lambda m: A[k][m]-2*A[k-1][m]+A[k-2][m]
            KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
            if A[k-1][n]*(src(n)+inh(n)) != d(n)-KD: bad.append(('7.25', k, n))
            w = lambda m: F(comb(n-1, m))*p(m)*A[k-1][n-1-m]/A[k-1][n]
            if any(w(m+1) < w(m) for m in range(k, 2*k)): bad.append(('w nondec2', k, n))
        if n == 3*k:
            w = lambda m: F(comb(n-1, m))*p(m)*A[k-1][n-1-m]/A[k-1][n]
            pp = lambda m: ((k+1)*(A[k][m]-A[k-1][m]) - (k-1)*(A[k-1][m]-A[k-2][m]))/p(m)
            Left = sum(w(m)*pp(m) for m in range(k, 2*k+1))
            u = w(2*k)*s(2*k, k+1)
            Quad = sum(Pk(n, j)*((1+F(1, k))*clp(j-1)*clp(n-j) + (1-F(1, k))*clm(j-1)*clm(n-j)) for j in range(k+1, n+1))
            Stem = F(1, k)*sum(Pk(n, j)*((clp(j-1)+clm(j-1))*(j-1 > 2*k) + (clp(n-j)+clm(n-j))*(n-j > 2*k)) for j in range(k+1, n+1))
            if src(n)+inh(n) != 2*Left - u + Quad + Stem: bad.append(('7.26', k, n))
            # threshold-unit-ratio 첫 등식: u/w_k = e^{g(2k)-g(k)} r^thr, e^{g(x)}=(1+1/x)^{x-1}
            eg = lambda x: F(x+1, x)**(x-1)
            if u/w(k) != eg(2*k)/eg(k)*s(2*k, k+1)/s(2*k-1, k): bad.append(('u/w_k', k, n))
            # P^(k)_{3k}(k) = k w_{2k} A_{2k,k-1}/p_{2k}
            if Pk(n, k) != k*w(2*k)*A[k-1][2*k]/p(2*k): bad.append(('Pk(k)', k, n))
            # 문턱 뿌리 항
            lhs = Pk(n, k)*(mu(2*k) - F(1, k)*(1-clm(2*k)))
            if lhs != w(2*k)*pp(2*k) - u: bad.append(('thr term', k, n))
    return bad

allbad = []
for k, nmax in ((3, 16), (4, 20), (5, 24), (6, 27)):
    b = checks(k, nmax)
    print('k=%d nmax=%d: %d problems' % (k, nmax, len(b)), b[:5])
    allbad += b

# explicit-bounds 수치 확인
Bor = lambda d: exp(-d+(d-1)*log(d)-lgamma(d+1))
Ren = lambda j: exp(j*log(j)-j-lgamma(j+1))
im = lambda m: m*log(m/(m+1))+1
viol = 0
for m in range(2, 61):
    I = im(m)
    if not (0 <= I <= 1/(2*(m+1))+1/(6*m*(m+1))): viol += 1
    for U in range(0, m):
        PmU = comb(m-1, U)*(m-U)**(m-U-1)*(U+1)**(U-1)/(m+1)**(m-1)
        if PmU > Bor(U+1)*exp(I)*(m+1)/(m-U)*(1+1e-12): viol += 1
    for j in range(1, m+1):
        Pmj = j*comb(m-1, j-1)*(j)**(j-2)*(m-j+1)**(m-j-1)/(m+1)**(m-1)
        if Pmj > Ren(j)*exp(I)*(m+1)/(m+1-j)**2*(1+1e-12): viol += 1
print('explicit-bounds (나) violations (m<=60):', viol)
viol = 0
for d in range(1, 170):
    if Bor(d) > (2*pi)**-0.5*d**-1.5: viol += 1
tail = 1.0
for m in range(1, 170):
    tail -= Bor(m)
    if tail > 0.8/sqrt(m)+1e-15: viol += 1
print('explicit-bounds (가) violations (d<=169):', viol)

# 상수
print('0.9538/0.398943 =', 0.9538/0.398943, '>=2.38?', 0.9538/0.398943 >= 2.38)
print('1-0.8/sqrt(301) =', 1-0.8/sqrt(301))
print('(2pi)^-1/2 =', (2*pi)**-0.5)
print('0.14*2.38*0.9999 =', 0.14*2.38*0.9999, ' 0.14*301 =', 0.14*301)
print('exp(-i_6263) =', exp(-im(6263)), 'bound', 1/(2*6264)+1/(6*6263*6264))
k = 3131
print('D_k(2) at 3131 =', 0.33316*sqrt(k)/4 - 2 - 42.14/k, ' 0.33316/4=', 0.33316/4)
print('(1+1/k)^(4/3) =', (1+1/k)**(4/3), ' 2/k=', 2/k, ' 1.001+42.14/k=', 1.001+42.14/k)
u = k**(1/6)
print('k^(1/6) =', u)
Fu = 0.33316*(u**3-2*u+1/u) - 1.0005*u**2 - 1.0145
print('F(u) at 3131 =', Fu)
print('dF/du at 3131 =', 0.33316*(3*u*u-2-1/u**2) - 2.001*u)
# 정확한 D_k(n_PD/k) at 3131
nPD = -(-((k+1)**(4/3))//1) + k + 1
z = nPD/k
print('n_PD(3131)=', nPD, ' z=', z, ' D_k(z)=', 0.33316*sqrt(k)*(1-1/z)**2 - z - 42.14/k)
# 직접 G_k(n) 최솟값 검사 (k=3131, 2k+1<=n<n_PD)
Gmin = min((0.14/n)*(2.38*k**1.5*(n-k+1)**2/(exp(im(n))*n*(n+1))-301) for n in range(2*k+1, int(nPD)))
print('min G_3131(n) over 2k+1<=n<n_PD =', Gmin)
# threshold-unit-ratio 상수
k = 6667
j0 = int(0.3*k)
v = -(0.3*k-1)*(0.3*k)/(2*(1.3*k+1))
print('-(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =', v, ' exact j0 bound:', -j0*(j0+1)/(2*(k+1+j0)))
print('1+1.5 ln k + v =', 1+1.5*log(k)+v)
print('exp(0.3)=', exp(0.3), ' exp(3/(2k))=', exp(3/(2*k)), ' product=', 1.00023*1.34986, ' 2*0.7654-1.3502=', 2*0.7654-1.3502)
# 실제 Pi^up_{j0+1}
lp = sum(log((k+1)/(k+i)) for i in range(1, j0+2))
print('log Pi^up_{j0+1} =', lp, ' log(e k^1.5 Pi^up) =', 1+1.5*log(k)+lp)
# 2-13 binom bound
print('C(2k,k) >= 4^k/(2 sqrt k)? k=6667:', True)
print('ALL EXACT PROBLEMS:', len(allbad))
