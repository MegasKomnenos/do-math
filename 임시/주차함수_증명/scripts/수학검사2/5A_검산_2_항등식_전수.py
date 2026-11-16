# -*- coding: utf-8 -*-
"""수학 검사 2(태그 5A) 검산 2: 항등식·재귀·부등식을 정확 산술과 전수 주차(n<=7)로 대조.
python -I scripts/수학검사2/5A_검산_2_항등식_전수.py
"""
import itertools, math
from fractions import Fraction as Fr
import sympy as sp
from mpmath import mp, mpf, binomial as mbinom, e as me, sqrt as msqrt, pi as mpi, factorial as mfac, log as mlog, exp as mexp, gamma as mgamma
mp.dps = 30
ok = True
def chk(name, cond, *vals):
    global ok
    ok &= bool(cond)
    print(('OK ' if cond else 'NG ') + name, *vals)
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def C(n, k): return math.comb(n, k) if 0 <= k <= n else 0

# ---------- 전수 주차 (n<=7) ----------
def enumerate_pf(n):
    """각 주차함수의 (M, M#, outcome sigma(자리->차), 변위 목록)"""
    out = []
    for a in itertools.product(range(1, n+1), repeat=n):
        spots = [0]*(n+1); disp = [0]*(n+1); okpf = True
        for car in range(1, n+1):
            s = a[car-1]
            while s <= n and spots[s]: s += 1
            if s > n: okpf = False; break
            spots[s] = car; disp[car] = s - a[car-1]
        if okpf: out.append((tuple(spots[1:]), tuple(disp[1:])))
    return out
def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        j = i-1
        while j >= 1 and sigma[j-1] < sigma[i-1]: j -= 1
        h.append(i - j)
    return h
NMAX = 7
data = {}
for n in range(1, NMAX+1):
    pf = enumerate_pf(n)
    assert len(pf) == p(n)
    rows = []
    for sigma, disp in pf:
        M = max(disp); Msh = sum(1 for d in disp if d == M); h = caps(sigma)
        blocked = all(h[i] == M+1 for i in range(n) if disp[sigma[i]-1] == M)
        rows.append((M, Msh, blocked, tuple(h), sigma))
    data[n] = rows
def b(n, l): return sum(1 for M, _, _, _, _ in data[n] if M == l)
def E(n, k): return sum(1 for M, Msh, _, _, _ in data[n] if M == k and Msh % 2 == 0 and Msh > 0)
def E2(n, k): return sum(1 for M, Msh, _, _, _ in data[n] if M == k and Msh == 2)
def B(n, m): return sum(1 for M, _, bl, _, _ in data[n] if M == m and bl)
def A(n, l): return sum(1 for M, _, _, _, _ in data[n] if M <= l) if n >= 1 else 1
# 정리 2.6 재귀로 A 독립 계산
def A_rec(n, l):
    memo = {0: 1}
    for m in range(1, n+1):
        memo[m] = sum(C(m-1, j)*min(j+1, l+1)*memo[j]*memo[m-1-j] for j in range(m))
    return memo[n]
chk('A_{n,l} 전수 = 정리 2.6 재귀 (n<=7)', all(A(n, l) == A_rec(n, l) for n in range(1, NMAX+1) for l in range(0, n)))
chk('정리 2.28 d_{n,k} = 2E - B (전수)', all(b(n,k)-b(n,k-1) == 2*E(n,k)-B(n,k-1) for n in range(1,NMAX+1) for k in range(1,n+1)))
chk('따름 2.29 2E2-B <= d (전수)', all(2*E2(n,k)-B(n,k-1) <= b(n,k)-b(n,k-1) for n in range(1,NMAX+1) for k in range(1,n+1)))
# 경계 응답 다항식
def Gamma(d, y, n):
    G = [sp.Integer(1)]
    for dd in range(1, d+1):
        G.append(sp.expand(C(n, dd)*p(dd) + y*sum(C(n-dd+j, j)*p(j)*G[dd-1-j] for j in range(dd))))
    return G[d]
y = sp.symbols('y')
# green-connection (다) 셋째 귀결, (라)
chk('green-connection (다): B_{n,l} = p_l Gamma_{n-l-1}(l;n), l+1<=n<=2l+1', all(B(n,l) == p(l)*Gamma(n-l-1, l, n) for n in range(1,NMAX+1) for l in range(1,n) if n <= 2*l+1))
chk('green-connection (라): b_{n,l} = sum_m A_{m,l}Gamma_{n-m-1}(l;n)', all(b(n,l) == sum(A(m,l)*Gamma(n-m-1, l, n) for m in range(l, n)) for n in range(1,NMAX+1) for l in range(1,n) if n <= 2*l+1))
chk('green-connection (다) 첫째: Gamma^- = p_{k-1}Gamma_{n-k}(k-1;n) = B_{n,k-1}, k<=n<=2k-1', all(p(k-1)*Gamma(n-k, k-1, n) == B(n,k-1) for n in range(1,NMAX+1) for k in range(1,n+1) if k <= n <= 2*k-1))
# 얼린 다항식 K_{n,k}(y) 전수
def K(n, k):
    tot = sp.Integer(0)
    seen = {}
    for M, Msh, bl, h, sg in data[n]:
        # 섬유 크기 prod h: 각 sigma는 prod h_i 번 나타나므로 sigma마다 한 번만 센다
        seen[sg] = h
    for sg, h in seen.items():
        tot += sp.Mul(*[hi for hi in h if hi <= k]) * y**sum(1 for hi in h if hi > k)
    return sp.expand(tot)
def Tk_series(k, N):
    # phi^{[k]}_m: exp(T_{<=k}) 계수 (정확 유리수)
    xs = sp.symbols('x')
    T = sum(sp.Rational(j**(j-1), math.factorial(j))*xs**j for j in range(1, k+1))
    ser = sp.series(sp.exp(T), xs, 0, N+1).removeO()
    return [int(ser.coeff(xs, m)*math.factorial(m)) for m in range(N+1)]
good = True
for n in range(1, NMAX+1):
    for k in range(1, n+1):
        if n > 2*k+1: continue
        phi = Tk_series(k, n)
        rhs = sp.expand(phi[n] + y*sum(phi[m]*Gamma(n-m-1, y, n) for m in range(k, n)))
        if sp.expand(K(n,k) - rhs) != 0: good = False; print('  source-rep (가) 불일치', n, k, K(n,k), rhs)
chk('source-rep (가) K_{n,k}(y) = phi_n + y sum phi_m Gamma (전수, n<=7, n<=2k+1)', good)
chk('따름 2.4: K(k+1)=A_{n,k}, K(k)=A_{n,k-1}', all(K(n,k).subs(y,k+1) == A(n,k) and K(n,k).subs(y,k) == A(n,k-1) for n in range(1,NMAX+1) for k in range(1,n+1)))
chk('K(k-1) = A_{n,k-2} + B_{n,k-1} (모든 n)', all(K(n,k).subs(y,k-1) == A(n,k-2) + B(n,k-1) for n in range(1,NMAX+1) for k in range(1,n+1)))
chk('K(k+1)-2K(k)+K(k-1) = 2E_{n,k}', all(K(n,k).subs(y,k+1)-2*K(n,k).subs(y,k)+K(n,k).subs(y,k-1) == 2*E(n,k) for n in range(1,NMAX+1) for k in range(1,n+1)))
def sd(d, yy, n): hg = lambda t: t*Gamma(d, t, n); return hg(yy+1)-2*hg(yy)+hg(yy-1)
good = True
for n in range(1, NMAX+1):
    for k in range(1, n+1):
        if n > 2*k+1: continue
        phi = Tk_series(k, n)
        lhs1 = 2*E(n,k); rhs1 = sum(phi[m]*sd(n-m-1, k, n) for m in range(k, n))
        Kk = K(n,k); cfr = Kk.subs(y,k+2)-3*Kk.subs(y,k+1)+3*Kk.subs(y,k)-Kk.subs(y,k-1)
        rhs2 = sum(phi[m]*sd(n-m-1, k+1, n) for m in range(k, n))
        if lhs1 != rhs1 or lhs1 + cfr != rhs2 or cfr < 0: good = False; print('  source-rep (나) 불일치', n, k, lhs1, rhs1, cfr, rhs2)
chk('source-rep (나) 2E = sum phi sd(k), 2E+c = sum phi sd(k+1), c>=0 (전수)', good)
# (다) S_{n,k} 식과 Gamma^+
good = True
for n in range(1, NMAX+1):
    for k in range(1, n+1):
        if not (k+2 <= n <= 2*k-1): continue
        Gm = p(k-1)*Gamma(n-k, k-1, n); Gp = p(k)*Gamma(n-k-1, k+2, n)
        Kk = K(n,k)
        if Gp != Kk.subs(y,k+2) - A(n,k+1): good = False; print('  Gamma^+ 불일치', n, k)
        d1 = b(n,k)-b(n,k-1); d2 = b(n,k+1)-b(n,k)
        S = Gp*d1 - Gm*d2
        phi = Tk_series(k, n); r = n-k
        S2 = sum(phi[n-d-1]*(Gp*sd(d, k, n) - Gm*sd(d, k+1, n)) for d in range(1, r))
        if S != S2: good = False; print('  S_{n,k} 불일치', n, k, S, S2)
chk('source-rep (다) Gamma^+ = K(k+2)-A_{n,k+1}; S_{n,k} = sum_d phi[Gamma^+ sd_d(k) - Gamma^- sd_d(k+1)] (전수)', good)
# marked-riccati 회복식 (전수; 보조정리 2.17로 sigma 합)
def Jn(n, k, xx, xp, ww):
    if n == 0: return sp.Integer(1)
    seen = {}
    for M, Msh, bl, h, sg in data[n]: seen[sg] = h
    tot = sp.Integer(0)
    for sg, h in seen.items():
        w = sp.Integer(1)
        for hi in h:
            w *= hi*min(sp.Integer(1), sp.Rational(k, hi))
            if hi > k+1: w *= xx
            elif hi == k+1: w *= xp
            elif hi == k: w *= ww
        tot += w
    return sp.nsimplify(tot)
good = True
for n in range(1, NMAX+1):
    for k in range(1, n+1):
        q = sp.Rational(k-1, k); q1 = sp.Rational(k+1, k); q2 = sp.Rational(k+2, k)
        if not (Jn(n,k,q,q,q) == A(n,k-2) and Jn(n,k,1,1,1) == A(n,k-1) and Jn(n,k,q1,q1,1) == A(n,k) and Jn(n,k,q2,q1,1) == A(n,k+1)):
            good = False; print('  riccati 회복 불일치', n, k)
chk('marked-riccati 네 용량 회복 (전수 n<=7)', good)
# marked-riccati ODE: 계수 x^n/n! 급수, n<=6, 기호 x,x',w
xx, xp, ww, X = sp.symbols('xx xp ww X')
for k in (2, 3):
    N = 6
    J = sum(Jn(n, k, xx, xp, ww)*X**n/math.factorial(n) for n in range(0, N+1))
    R = sum((j+1-k*xx)*p(j)*X**j/math.factorial(j) for j in range(0, k-1)) + k*(ww-xx)*p(k-1)*X**(k-1)/math.factorial(k-1) + k*(xp-xx)*(p(k)+(ww-1)*k**(k-1))*X**k/math.factorial(k)
    lhs = sp.expand(sp.diff(J, X)); rhs = sp.expand(k*xx*J**2 + R*J)
    diff = sp.expand(lhs - rhs)
    good = all(sp.expand(diff.coeff(X, m)) == 0 for m in range(0, N))
    chk('marked-riccati ODE J\' = k xx J^2 + R J (k=%d, x^%d까지)' % (k, N-1), good)
# response-kernel: H_t 급수 전수 + ODE (가), 고정 크기 응답 (나)(다)
def Ht_coeff(n, k, t):
    if n == 0: return Fr(0)
    seen = {}
    for M, Msh, bl, h, sg in data[n]: seen[sg] = h
    tot = Fr(0)
    for sg, h in seen.items():
        w = Fr(1)
        for hi in h: w *= hi*min(1, Fr(k, hi))
        tot += w*sum(1 for hi in h if hi == t)
    return tot
for k, t in ((2, 2), (2, 3), (3, 3), (3, 4)):
    N = 7
    a = [Fr(A(m, k-1), math.factorial(m)) for m in range(N+1)]
    Ak = sum(a[m]*X**m for m in range(N+1))
    Qp = sum((k-1-j)*p(j)*X**j/math.factorial(j) for j in range(0, k-1))
    H = sum(Ht_coeff(n, k, t)*X**n/math.factorial(n) for n in range(0, N+1))
    diff = sp.expand(sp.diff(H, X) - ((2*k*Ak - Qp)*H + k*a[t-1]*X**(t-1)*Ak))
    good = all(diff.coeff(X, m) == 0 for m in range(0, N))
    chk('response-kernel (가) ODE (k=%d,t=%d, x^%d까지)' % (k, t, N-1), good)
    # (나) R_m(t) = [x^{t+m}]H_t/(k a_{t-1}) = int tau^{t-1} K_m
    tau = sp.symbols('tau')
    Eexp = sum(k*a[j-1]/j*(1-tau**j)*X**j for j in range(1, N+1))
    Kser = sp.expand(sp.series(Ak*sp.exp(Eexp), X, 0, N+1).removeO())
    good = True
    for m in range(0, N+1-t):
        Km = Kser.coeff(X, m)
        Rm = sp.integrate(tau**(t-1)*Km, (tau, 0, 1))
        lhs = Fr(Ht_coeff(t+m, k, t), math.factorial(t+m))/(k*a[t-1])
        if sp.Rational(lhs.numerator, lhs.denominator) != Rm: good = False
        if Km.subs(tau, 1) != a[m]: good = False
    chk('response-kernel (나) R_m(t)=int tau^{t-1}K_m, K_m(1)=a_m (k=%d,t=%d)' % (k, t), good)
    # fixed-size-response (나): sum wt H_t = n! k a_{t-1} fs_{n-t}/t, fs 재귀
    good = True
    for n in range(t, N+1):
        fs = [Fr(1)]
        for m in range(1, n-k+1):
            fs.append(a[m] + k*sum(a[m-1-i]*fs[i]/(n-i) for i in range(m)))
        if n-t <= n-k:
            if Ht_coeff(n, k, t) != math.factorial(n)*k*a[t-1]*fs[n-t]/t: good = False
    chk('fixed-size-response (나) 가중 합 = n! k a_{t-1} fs_{n-t}/t (k=%d,t=%d)' % (k, t), good)
# fixed-size-response (다): (n)_m fs_m = Gamma_m(k;n) for k<=n<=2k
good = True
for k in range(1, 8):
    for n in range(k, 2*k+1):
        a = [Fr(A_rec(m, k-1), math.factorial(m)) for m in range(n+1)]
        fs = [Fr(1)]
        for m in range(1, n-k+1):
            fs.append(a[m] + k*sum(a[m-1-i]*fs[i]/(n-i) for i in range(m)))
        for m in range(0, n-k+1):
            if sp.Rational(fs[m].numerator, fs[m].denominator)*sp.ff(n, m) != Gamma(m, k, n): good = False
chk('fixed-size-response (다) (n)_m fs_m = Gamma_m(k;n), k<=n<=2k, k<=7', good)
# inverse-renewal 재귀와 타일 합
def tw(j): return Fr(1) if j == 1 else Fr((j-1)**(j-1), math.factorial(j))
good = True
for n in range(2, 12):
    for yy in (sp.Rational(3,2), 2, 5, -1):
        fs = [sp.Integer(1)]
        for d in range(1, n):
            fs.append((1 + sp.Rational(yy)/(n-d+1))*fs[d-1] + sum(sp.Rational(tw(j).numerator, tw(j).denominator)*fs[d-j] for j in range(2, d+1)))
            if sp.simplify(fs[d]*sp.ff(n, d) - Gamma(d, yy, n)) != 0: good = False
chk('inverse-renewal fs\'_d 재귀 = Gamma_d(y;n)/(n)_d (n<=11, y=3/2,2,5,-1)', good)
chk('tw_2/tw_1=1/2 < tw_3/tw_2=4/3, 비 비감소', tw(2)/tw(1) == Fr(1,2) and tw(3)/tw(2) == Fr(4,3) and all(tw(j+1)/tw(j) <= tw(j+2)/tw(j+1) for j in range(1, 30)))
# [x^j]e^{-T} = -tw_j
xs = sp.symbols('x')
Tser = sum(sp.Rational(j**(j-1), math.factorial(j))*xs**j for j in range(1, 9))
em = sp.series(sp.exp(-Tser), xs, 0, 9).removeO()
chk('[x^j]e^{-T} = -tw_j (j<=8)', all(em.coeff(xs, j) == -sp.Rational(tw(j).numerator, tw(j).denominator) for j in range(1, 9)))
# 생일 법칙
rho = sp.symbols('rho')
def hb(d):
    H = [sp.Integer(1)]
    for dd in range(1, d+1):
        H.append(sp.expand((1+rho)*H[dd-1] + sum(sp.Rational(tw(j).numerator, tw(j).denominator)*H[dd-j] for j in range(2, dd+1))))
    return H[d]
good = True
for d in range(1, 9):
    Hd = hb(d)
    for j in range(0, d+1):
        if Hd.coeff(rho, j) != sp.Rational((j+1)*(d+1)**(d-j-1), math.factorial(d-j)): good = False
    if Hd.subs(rho, 1) != sp.Rational((d+1)**d, math.factorial(d)): good = False
    bd = [sp.Rational((j+1)*sp.ff(d, j), (d+1)**(j+1)) for j in range(d+1)]
    if sum(bd) != 1: good = False
    if any(sum(bd[j:]) != sp.Rational(sp.ff(d, j), (d+1)**j) for j in range(d+1)): good = False
    tm = sp.simplify((rho*sp.diff(Hd, rho)/Hd).subs(rho, 1))
    if tm != sum(j*bd[j] for j in range(d+1)): good = False
chk('생일 법칙: [rho^j]hb_d, hb_d(1), bd_d 확률분포·꼬리, tm_d(1) (d<=8)', good)
# suff-cond (가) 계수비, 끝점비 (1+1/r)^r at rho=1
good = True
for r in range(2, 10):
    X1 = [hb(r).coeff(rho, j) for j in range(r+1)]; X2 = [hb(r-1).coeff(rho, j) for j in range(r)]
    for j in range(0, r-1):
        if X1[j]/X2[j] != sp.Rational((r+1)**(r-j-1), r**(r-j-2)*(r-j)): good = False
    if X1[r-1]/X2[r-1] != r or (r >= 2 and X1[r-2]/X2[r-2] != sp.Rational(r+1, 2)): good = False
    if hb(r).subs(rho,1)/hb(r-1).subs(rho,1) != sp.Rational(r+1, r)**r: good = False
    # 수치: V_r(k-1) <= (1+1/r)^r V_{r-1}(k), k=r+1..r+6 (특수 좌표 타일 합 = Gamma/(n)_d)
    for k in range(r+1, r+7):
        n = k+r
        Vr = Gamma(r, k-1, n)/sp.ff(n, r); Vr1 = Gamma(r-1, k, n)/sp.ff(n, r-1)
        if not Vr <= sp.Rational(r+1, r)**r*Vr1: good = False
chk('suff-cond (가) 계수비 R_j, R_{r-1}=r, R_{r-2}=(r+1)/2, rho=1 비; V_r(k-1)<=(1+1/r)^r V_{r-1}(k) 표본', good)
# suff-cond (다) hg\'\'\'/hg\'\' <= (1+sqrt(3 pi d/2))/y 표본, (라) 둘째 식 표본
good = True
for r in range(3, 9):
    for k in range(r+1, r+8):
        n = k+r
        for d in range(1, r):
            hg = y*Gamma(d, y, n)
            for yy in (k-1, k, k+1):
                h2 = sp.diff(hg, y, 2).subs(y, yy); h3 = sp.diff(hg, y, 3).subs(y, yy)
                if h2 <= 0: good = False
                if float(h3/h2) > (1+math.sqrt(3*math.pi*d/2))/yy + 1e-12: good = False
            if float(sd(d, k+1, n)/sd(d, k, n)) > math.exp((1+math.sqrt(3*math.pi*(r-1)/2))/(k-1)) + 1e-12: good = False
chk('suff-cond (다) 두 부등식 표본 (3<=r<=8)', good)
# (라) log Gamma^+/Gamma^- >= log cr_k - r log(1+1/r) + tm_{r-1}(k/n) log(1+2/k)
def tm_num(d, rh):
    bd = [Fr((j+1)*math.perm(d, j), (d+1)**(j+1)) for j in range(d+1)]
    w = [rh**j*bd[j] for j in range(d+1)]
    return sum(j*w[j] for j in range(d+1))/sum(w)
good = True
for r in range(3, 9):
    for k in range(r+1, r+10):
        n = k+r
        Gp = p(k)*Gamma(r-1, k+2, n); Gm = p(k-1)*Gamma(r, k-1, n)
        cr = (1+1/k)**(k-2)
        lhs = math.log(float(Gp)/float(Gm)); rhs = math.log(cr) - r*math.log(1+1/r) + float(tm_num(r-1, Fr(k, n)))*math.log(1+2/k)
        if lhs < rhs - 1e-12: good = False
        if not (abs(p(k)/p(k-1) - (k+1)*cr) < 1e-9*p(k)/p(k-1)): good = False
chk('suff-cond (라) 경계 이득 표본; p_k/p_{k-1} = (k+1)cr_k', good)

# ---------- 5.2.3 핵 ----------
def Ren(m): return mpf(m)**m*mexp(-m)/mfac(m) if m >= 1 else mpf(1)
def cb(m): return mbinom(2*m, m)/mpf(4)**m
def rb(m): return mlog(mfac(m)) - (m+mpf(1)/2)*mlog(m) + m - mlog(2*mpi)/2
o = 1/msqrt(mpf(2))
chk('Robbins 1/(12m+1) < rb_m < 1/(12m) (m<=200)', all(1/(12*mpf(m)+1) < rb(m) < 1/(12*mpf(m)) for m in range(1, 201)))
chk('Ren(m)/(o cb_m) = e^{rb_m-rb_{2m}} in [1, 1+1/(12(2m-1))] (m<=200)', all(abs(Ren(m)/(o*cb(m)) - mexp(rb(m)-rb(2*m))) < mpf(10)**-25 and 1 <= Ren(m)/(o*cb(m)) <= 1+mpf(1)/(12*(2*m-1)) for m in range(1, 201)))
chk('(K1) Ren(m) >= o cb_m(1+1/(25(2m-1))) (m<=2000)', all(Ren(m) >= o*cb(m)*(1+mpf(1)/(25*(2*m-1))) for m in range(1, 2001)))
Wm = lambda m: (m+1)*mexp(-1)*(1+mpf(1)/m)**m - m
chk('W_m 정의 = (m+1)Ren(m+1)/Ren(m) - m', all(abs(Wm(m) - ((m+1)*Ren(m+1)/Ren(m) - m)) < mpf(10)**-25 for m in range(1, 50)))
chk('1/2-1/(2m) <= W_m <= 1/2-1/(24m)+11/(24m^2) <= 1/2+1/(2m)', all(mpf(1)/2-mpf(1)/(2*m) <= Wm(m) <= mpf(1)/2-mpf(1)/(24*m)+mpf(11)/(24*m*m) <= mpf(1)/2+mpf(1)/(2*m) for m in range(1, 2001)))
chk('(K) 1/2-1/(24m) <= W_m <= 1/2-1/(44m) (m<=5000)', all(mpf(1)/2-mpf(1)/(24*m) <= Wm(m) <= mpf(1)/2-mpf(1)/(44*m) for m in range(1, 5001)))
chk('[z^m]E = Ren(m)W_m in [o cb(1/2-1/(2m)), o cb(1/2+1/m)]; (K2) [o cb(1/2-1/(12(2m-1))), o cb/2]', all(o*cb(m)*(mpf(1)/2-mpf(1)/(2*m)) <= Ren(m)*Wm(m) <= o*cb(m)*(mpf(1)/2+mpf(1)/m) and o*cb(m)*(mpf(1)/2-mpf(1)/(12*(2*m-1))) <= Ren(m)*Wm(m) <= o*cb(m)/2 for m in range(1, 2001)))
chk('rb_{2m}-2rb_m in (-1/(6m), 0); cb_m in [(1-1/(6m))/sqrt(pi m), 1/sqrt(pi m)]', all(-1/(6*mpf(m)) < rb(2*m)-2*rb(m) < 0 and (1-1/(6*mpf(m)))/msqrt(mpi*m) <= cb(m) <= 1/msqrt(mpi*m) for m in range(1, 300)))
chk('cb_N sqrt N 증가, cb_N sqrt(N+1/2) 감소 (N<=300)', all(cb(N+1)*msqrt(N+1) > cb(N)*msqrt(N) and cb(N+1)*msqrt(N+mpf(3)/2) < cb(N)*msqrt(N+mpf(1)/2) for N in range(1, 300)))
chk('(1-2/S^2)/sqrt pi <= cb_{r+3} sqrt r <= 1/sqrt pi (r=S^2, S=13..40)', all((1-mpf(2)/S**2)/msqrt(mpi) <= cb(S*S+3)*S <= 1/msqrt(mpi) for S in range(13, 41)))
chk('1/(sqrt pi(1+5/(4r))) <= sqrt r cb_{r+2} <= 1/sqrt pi (r<=300)', all(1/(msqrt(mpi)*(1+mpf(5)/(4*r))) <= msqrt(r)*cb(r+2) <= 1/msqrt(mpi) for r in range(1, 301)))
chk('Ren(m)/cb_m 감소, 첫 값 2/e', all(Ren(m+1)/cb(m+1) < Ren(m)/cb(m) for m in range(1, 300)) and abs(Ren(1)/cb(1) - 2/me) < mpf(10)**-25)
chk('third-group (나): gamma/(gamma+1) <= Ren(g+1)/Ren(g) <= 1', all(mpf(g)/(g+1) <= Ren(g+1)/Ren(g) <= 1 for g in range(1, 300)))
# Laurent 계수 [z^U]w^i 네 경우 (sympy 급수와 대조)
z = sp.symbols('z')
def coef_formula(U, i):
    if i % 2 == 0:
        Up = -i//2
        if Up >= 1: return sp.binomial(U+Up-1, Up-1)
        return sp.binomial(-Up, U) if U <= -Up else 0  # (1-z)^{-Up} 다항식: 본문은 U > i/2에서 0만 주장
    half = sp.Rational(-i, 2)
    cbU = sp.binomial(2*U, U)/sp.Integer(4)**U
    if half > 0:
        Up = int(half - sp.Rational(1,2))
        num = sp.Mul(*[U+sp.Rational(1,2)+t for t in range(Up)]); den = sp.Mul(*[sp.Rational(1,2)+t for t in range(Up)])
        return cbU*num/den
    Up = int(sp.Rational(1,2) - half)
    num = sp.Mul(*[-sp.Rational(1,2)-t for t in range(Up)]); den = sp.Mul(*[U-sp.Rational(1,2)-t for t in range(Up)])
    return cbU*num/den
good = True
for i in range(-9, 8):
    ser = sp.series((1-z)**sp.Rational(i, 2), z, 0, 9).removeO()
    for U in range(1, 9):
        if i % 2 == 0 and -i//2 <= 0 and U <= i//2: continue
        if sp.simplify(ser.coeff(z, U) - coef_formula(U, i)) != 0: good = False; print('  Laurent 계수 불일치', U, i, ser.coeff(z, U), coef_formula(U, i))
chk('sign-sandwich (다) [z^U]w^i 네 경우 (i=-9..7, U<=8)', good)
# kernel-bounds P_Theta, Q_Theta 항등식과 Bernstein 양성
Psi, vt = sp.symbols('Psi vartheta')
uP = 1 + vt/2 - vt**2/44; uM = 1 + vt/2 - vt**2/24
LT = 2*sum(Psi**(2*i+1)/(2*i+1) for i in range(4)); UT = LT + 2*Psi**9/(9*(1-Psi**2))
vt_of = 2*Psi/(1-Psi)
numP = sp.simplify((vt**2*sp.diff(uP, vt) - (vt - LT)*uP).subs(vt, vt_of))
numM = sp.simplify((vt**2*sp.diff(uM, vt) - (vt - UT)*uM).subs(vt, vt_of))
PT = 175-665*Psi+581*Psi**2-427*Psi**3+375*Psi**4-309*Psi**5+150*Psi**6+15*Psi**7
QT = 945+42*Psi-252*Psi**2+66*Psi**3-108*Psi**4+42*Psi**5-60*Psi**6-10*Psi**7
chk('kernel-bounds P_Theta 항등식', sp.simplify(numP - 2*Psi**3*PT/(1155*(1-Psi)**3)) == 0)
chk('kernel-bounds Q_Theta 항등식', sp.simplify(numM + Psi**4*QT/(945*(1-Psi)**3*(1+Psi))) == 0)
def bern(poly, a, b):
    t = sp.symbols('t'); q = sp.Poly(sp.expand(poly.subs(Psi, a + (b-a)*t)), t); n = q.degree(); c = [q.coeff_monomial(t**i) for i in range(n+1)]
    return [sum(c[i]*sp.binomial(kk, i)/sp.binomial(n, i) for i in range(kk+1)) for kk in range(n+1)]
chk('P_Theta, Q_Theta Bernstein 계수 [0,1/3] 모두 양', all(cf > 0 for cf in bern(PT, 0, sp.Rational(1,3))) and all(cf > 0 for cf in bern(QT, 0, sp.Rational(1,3))))
chk('Theta\'(t) = (t - log(1+t))/t^2', sp.simplify(sp.diff((1+1/vt)*sp.log(1+vt)-1, vt) - (vt - sp.log(1+vt))/vt**2) == 0)
# ---------- 사슬 합·생성함수 ----------
def Ch_direct(j, d):
    if d < 0: return mpf(0)
    if j == 0: return mpf(1)
    tot = mpf(0)
    for gam in itertools.product(range(1, d+1), repeat=j):
        if sum(gam) > d: continue
        pr = mpf(1); s = 0
        for g in gam:
            s += g; pr *= Ren(g)*max(d-s, 0)
        tot += pr
    return tot
def ser_mul(a, b, N): return [sum(a[i]*b[n-i] for i in range(n+1)) for n in range(N+1)]
def ser_C(N): return [mpf(0)] + [Ren(m) for m in range(1, N+1)]
def ser_deriv(a): return [ (i+1)*a[i+1] for i in range(len(a)-1)] + [mpf(0)]
def ser_inv1mz(a, N):  # a/(1-z)
    out = []; s = mpf(0)
    for i in range(N+1): s += a[i]; out.append(s)
    return out
def ser_shift(a, N): return [mpf(0)] + a[:N]
def Z_series(iota, j, N):
    Cs = ser_C(N)
    # Z_1 = z C (1-z)^{iota-2}
    Z = ser_shift(Cs, N)
    for _ in range(2 - iota): Z = ser_inv1mz(Z, N)
    for _ in range(max(0, iota-2)):
        Z = [Z[i] - (Z[i-1] if i else 0) for i in range(N+1)]
    for jj in range(2, j+1):
        inner = [ser_deriv(Z)[i] + iota*ser_inv1mz(Z, N)[i] for i in range(N+1)]
        Z = ser_mul(Cs, ser_shift(inner, N), N)
    return Z
good = True
for j in range(1, 4):
    for r in range(1, 7):
        for iota in (2, 3):
            vals = [Ch_direct(j, r+iota-t) for t in range(iota+1)]
            delta = sum((-1)**t*math.comb(iota, t)*vals[t] for t in range(iota+1))
            Zc = Z_series(iota, j, r+iota+1)[r+iota]
            if abs(delta - Zc) > mpf(10)**-20*(1+abs(delta)): good = False; print('  Z 불일치', iota, j, r, delta, Zc)
chk('marked-recursion (가): Delta^iota Ch_j(r) = [z^{r+iota}]Z^{(iota)}_j (j<=3, r<=6, iota=2,3)', good)
# Z^{(3)}_2 = z(1+z)C^2 + z^2 C E
N = 12; Cs = ser_C(N); Es = [(1-0)*0]*(N+1)
Cp = ser_deriv(Cs); Es = [Cp[i] - (Cp[i-1] if i else 0) for i in range(N+1)]
C2 = ser_mul(Cs, Cs, N); t1 = ser_shift(C2, N); t1 = [t1[i] + (t1[i-1] if i else 0) for i in range(N+1)]
t2 = ser_shift(ser_shift(ser_mul(Cs, Es, N), N), N)
Z32 = Z_series(3, 2, N)
chk('Z^{(3)}_2 = z(1+z)C^2 + z^2 C E', all(abs(Z32[i] - t1[i] - t2[i]) < mpf(10)**-22 for i in range(N+1)))
chk('[z^0]E = 1/e, [z^m]E = (m+1)Ren(m+1) - m Ren(m)', abs(Es[0]-1/me) < mpf(10)**-25 and all(abs(Es[m] - ((m+1)*Ren(m+1)-m*Ren(m))) < mpf(10)**-25 for m in range(1, N)))
# 일차·이차 가중치 생성함수 Y_j, O_j 대 직접 합
def U_N_direct(j, d, which):
    tot = mpf(0)
    for gam in itertools.product(range(1, d+1), repeat=j):
        if sum(gam) > d: continue
        ds = list(itertools.accumulate(gam))
        Lg = mpf(5)/2*(ds[-1]-1) + sum(ds[i]-1 for i in range(j-1))
        Ng = Lg**2/2 + mpf(5)/4*(ds[-1]-1)**2 - mpf(ds[-1]-1)/12 + sum(mpf(ds[i]-1)**2 for i in range(j-1))/2
        pr = mpf(1)
        for i in range(j): pr *= Ren(gam[i])*max(d-ds[i], 0)
        tot += (Lg if which == 'L' else Ng)*pr
    return tot
def ops(F, N):  # F' + 2F/(1-z)
    d = ser_deriv(F); s = ser_inv1mz(F, N); return [d[i] + 2*s[i] for i in range(N+1)]
def Y_O_series(j, N):
    Cs = ser_C(N); zCp = ser_shift(ser_deriv(Cs), N); zzCpp = ser_shift(ser_deriv(zCp), N)
    Z = Z_series(2, 1, N)
    Y = [mpf(5)/2*v for v in ser_shift([zCp[i]-Cs[i] for i in range(N+1)], N)]
    O = ser_shift([mpf(35)/8*(zzCpp[i]-2*zCp[i]+Cs[i]) - mpf(1)/12*(zCp[i]-Cs[i]) for i in range(N+1)], N)
    for jj in range(2, j+1):
        oZ = ops(Z, N); oY = ops(Y, N); oO = ops(O, N)
        coefY = [(jj+mpf(3)/2)*zCp[i] - Cs[i] for i in range(N+1)]
        coefO2 = [(jj+mpf(5)/2)*zCp[i] - Cs[i] for i in range(N+1)]
        coefO3 = [mpf((2*jj+3)*(2*jj+5))/8*zzCpp[i] - (jj+mpf(31)/12)*zCp[i] + Cs[i] for i in range(N+1)]
        Onew = [ser_mul(Cs, ser_shift(oO, N), N)[i] + ser_mul(coefO2, ser_shift(oY, N), N)[i] + ser_mul(coefO3, ser_shift(oZ, N), N)[i] for i in range(N+1)]
        Ynew = [ser_mul(Cs, ser_shift(oY, N), N)[i] + ser_mul(coefY, ser_shift(oZ, N), N)[i] for i in range(N+1)]
        Znew = ser_mul(Cs, ser_shift(oZ, N), N)
        Z, Y, O = Znew, Ynew, Onew
    return Z, Y, O
good = True
for j in range(1, 4):
    for r in range(1, 6):
        Z, Y, O = Y_O_series(j, r+3)
        dU = sum((-1)**t*math.comb(2, t)*U_N_direct(j, r+2-t, 'L') for t in range(3))
        dN = sum((-1)**t*math.comb(2, t)*U_N_direct(j, r+2-t, 'N') for t in range(3))
        if abs(dU - Y[r+2]) > mpf(10)**-18*(1+abs(dU)) or abs(dN - O[r+2]) > mpf(10)**-18*(1+abs(dN)): good = False; print('  Y/O 불일치', j, r, dU, Y[r+2], dN, O[r+2])
chk('marked-recursion (나) Y_j, marked-chain-rec (나) O_j = 직접 합의 둘째 차분 (j<=3, r<=5)', good)
# marked-chain-rec (가) 분해 항등식 (기호)
gam, Lp_, Np_, jj = sp.symbols('gamma Lp Np j')
dsym = sp.symbols('d1:6')
# j=3: ds = (g, g+d1', g+d2') with d' partial sums of remaining
g1, g2 = sp.symbols('g1 g2')
ds = [gam, gam+g1, gam+g1+g2]; j3 = 3
Lfull = sp.Rational(5,2)*(ds[-1]-1) + sum(d_-1 for d_ in ds[:-1])
Nfull = Lfull**2/2 + sp.Rational(5,4)*(ds[-1]-1)**2 - (ds[-1]-1)/12 + sum((d_-1)**2 for d_ in ds[:-1])/2
dsp = [g1, g1+g2]
Lp = sp.Rational(5,2)*(dsp[-1]-1) + sum(d_-1 for d_ in dsp[:-1])
Np = Lp**2/2 + sp.Rational(5,4)*(dsp[-1]-1)**2 - (dsp[-1]-1)/12 + sum((d_-1)**2 for d_ in dsp[:-1])/2
rhs = Np + ((j3+sp.Rational(5,2))*gam-1)*Lp + sp.Rational(1,2)*(j3+sp.Rational(3,2))*(j3+sp.Rational(5,2))*gam**2 - (j3+sp.Rational(31,12))*gam + 1
chk('marked-chain-rec (가) N 분해 (j=3 기호)', sp.simplify(sp.expand(Nfull - rhs)) == 0)
chk('marked-recursion (나) L 분해 (j=3 기호)', sp.simplify(Lfull - (Lp + (j3+sp.Rational(3,2))*gam - 1)) == 0)
chk('marked-chain-rec (가) j=1: N = 35/8(g-1)^2-(g-1)/12', sp.simplify((sp.Rational(5,2)*(gam-1))**2/2 + sp.Rational(5,4)*(gam-1)**2 - (gam-1)/12 - (sp.Rational(35,8)*(gam-1)**2 - (gam-1)/12)) == 0)
# weight-envelope (가) lc_i
dd, n_ = sp.symbols('d n', positive=True)
def lc(i, d):
    return sp.Rational(1, i)*(sp.Integer(d)**(i+1)/(i+1) + 2*sp.Integer(d)**i - sum(sp.Integer(rr)**i for rr in range(d)))
good = True
for d in range(0, 8):
    for n in (20, 37):
        lognf = d + sum(sp.log(1-sp.Rational(rr, n)) for rr in range(d)) + (n-d-2)*sp.log(1-sp.Rational(d, n))
        # 급수 비교: 수치
        approx = sum(lc(i, d)/sp.Integer(n)**i for i in range(1, 60))
        if abs(float(lognf) - float(approx)) > 1e-12: good = False
    if lc(1, d) != sp.Rational(5, 2)*d or lc(2, d) != sp.Rational(5,4)*d*d - sp.Rational(d, 12): good = False
    if any(not (0 <= lc(i, d) <= sp.Rational(5,2)*sp.Integer(d)**i/i) for i in range(1, 8)): good = False
chk('weight-envelope (가) lc_i(d): 급수 합 = log nf, lc_1, lc_2, 0<=lc_i<=5d^i/(2i)', good)
# weight-envelope (나)(다), third-group (마), last-gap, parity-tail (가)(나), omitted-tail (다): 직접 Q 계산으로 대조
def nf(n, d): return mpf(me)**d*mfac(n)/mfac(n-d)*mpf(n-d)**(n-d-2)/mpf(n)**(n-2)
def Q_direct(n, r, j, iota):
    tot = mpf(0)
    for gam in itertools.product(range(1, r+iota), repeat=j):
        if sum(gam) > r+iota-1: continue
        ds = list(itertools.accumulate(gam))
        W = nf(n, ds[-1]-1)
        for i in range(j-1): W *= mpf(n)/(n+1-ds[i])
        pr = W
        for g in gam: pr *= Ren(g)
        delta = sum((-1)**t*math.comb(iota, t)*math.prod(max(r+iota-t-ds[i], 0) for i in range(j)) for t in range(iota+1))
        tot += pr*delta
    return me*mpf(n)**(1-j)*tot
good = True; good2 = True; good3 = True; good4 = True; good5 = True
for n, r in ((60, 5), (90, 7), (200, 9)):
    rq_r = mpf(r+3)/n; rq = mpf(r)/n
    for j in range(1, 4):
        Z3 = Z_series(3, j, r+4)[r+3]; Q3 = Q_direct(n, r, j, 3)
        lo = me*mpf(n)**(1-j)*Z3; hi = lo*(1-rq_r)**(-j-2)*(1+6*rq_r/(1-rq_r)); hi5 = lo*(1-rq_r)**(-j-2)*(1+6*rq_r/(5*(1-rq_r)))
        if j >= 2 and not (0 <= lo <= Q3 + mpf(10)**-20 and Q3 <= hi + mpf(10)**-20): good = False; print('  third-group (마) 위반', n, r, j, lo, Q3, hi)
        if j >= 2 and not (lo <= Q3 + mpf(10)**-20 and Q3 <= hi5 + mpf(10)**-20): good2 = False; print('  last-gap 위반', n, r, j)
        Z2, Y2, O2 = Y_O_series(j, r+3)
        Q2 = Q_direct(n, r, j, 2)
        dCh = Z2[r+2]; dU = Y2[r+2]; dN = O2[r+2]
        erj = rq_r**2/2*((j+mpf(3)/2)**2/(1-rq_r)**2*mexp((j+mpf(3)/2)*rq_r/(1-rq_r)) + (j+4)/(1-rq_r))
        lo2 = me*mpf(n)**(1-j)*(dCh + dU/n); hi2 = me*mpf(n)**(1-j)*(dCh*(1+erj) + dU/n)
        if not (lo2 <= Q2 + mpf(10)**-20 <= hi2 + 2*mpf(10)**-20): good3 = False; print('  parity-tail (가) 위반', n, r, j, lo2, Q2, hi2)
        Rm = (1-rq)**(-j-mpf(3)/2) - 1 - (j+mpf(3)/2)*rq; Rm2 = Rm - (j+mpf(3)/2)*(j+mpf(5)/2)*rq**2/2
        hiA = me*mpf(n)**(1-j)*(dCh*(1+Rm) + dU/n); loA2 = me*mpf(n)**(1-j)*(dCh + dU/n + dN/n**2); hiA2 = me*mpf(n)**(1-j)*(dCh*(1+Rm2) + dU/n + dN/n**2)
        if not (lo2 <= Q2 + mpf(10)**-20 <= hiA + 2*mpf(10)**-20 and loA2 <= Q2 + mpf(10)**-20 <= hiA2 + 2*mpf(10)**-20): good4 = False; print('  weight-envelope (다) 적용 위반', n, r, j)
        if j >= 2:
            thp = mpf(3)*j/2 - 1; dcp = mpf(2)
            for jj in range(2, j): dcp *= mpf(3)/4*(mpf(3)*jj/2-1+2)
            Tl = me*mpf(n)**(1-j)*(1-rq)**(-j-mpf(3)/2)*dcp*mgamma(r+2+thp)/(mgamma(thp)*mfac(r+2))
            if not (0 <= Q2 <= Tl): good5 = False; print('  omitted-tail (다) 위반', n, r, j, Q2, Tl)
            if not dCh <= dcp*mgamma(r+2+thp)/(mgamma(thp)*mfac(r+2)): good5 = False
            th3 = mpf(3)*j/2 - 2; dc3 = mpf(11)/8
            for jj in range(2, j): dc3 *= mpf(3)/4*(mpf(3)*jj/2-2+3)
            if not Z3 <= dc3*mgamma(r+3+th3)/(mgamma(th3)*mfac(r+3)): good5 = False; print('  sign-sandwich (마) 위반', n, r, j)
    # j=1 식
    Q31 = Q_direct(n, r, 1, 3); Q21 = Q_direct(n, r, 1, 2)
    if abs(Q31 - me*(Ren(r+2)*nf(n, r+1) - Ren(r+1)*nf(n, r))) > mpf(10)**-20: good = False; print('  sign-sandwich (라) j=1 식 불일치')
    if abs(Q21 - me*nf(n, r)*Ren(r+1)) > mpf(10)**-20: good3 = False; print('  parity-tail j=1 식 불일치')
chk('third-group (마) 양쪽 부등식 (n,r)=(60,5),(90,7),(200,9), j<=3; (라) j=1 식', good)
chk('last-gap 상계 (1+6rq/(5(1-rq)))', good2)
chk('parity-tail (가) 양쪽 부등식; j=1 식', good3)
chk('weight-envelope (다) 첫째·둘째 보정 적용 부등식', good4)
chk('omitted-tail (다) Tl_j, sign-sandwich (마) dc_j 꼬리 상계', good5)
# weight-envelope (나) 계수별: [n^{-i}]W_n(gamma) in [0, binom(j+1/2+i,i) r^i]; [n^-1]=L, [n^-2]=N (기호, 작은 보기)
nn = sp.symbols('n', positive=True)
good = True
for gam in ((1,), (2,), (1,2), (3,1), (2,2,1)):
    j = len(gam); ds = list(itertools.accumulate(gam)); r = ds[-1]-1
    d = ds[-1]-1
    lognf = d + sum(sp.log(1-sp.Rational(rr)/nn) for rr in range(d)) + (nn-d-2)*sp.log(1-sp.Rational(d)/nn)
    W = sp.exp(lognf)*sp.Mul(*[nn/(nn+1-ds[i]) for i in range(j-1)])
    h = sp.symbols('h'); Wh = W.subs(nn, 1/h)
    ser = sp.series(Wh, h, 0, 5).removeO()
    Lg = sp.Rational(5,2)*(ds[-1]-1) + sum(ds[i]-1 for i in range(j-1))
    Ng = sp.Rational(1,2)*Lg**2 + sp.Rational(5,4)*(ds[-1]-1)**2 - sp.Rational(ds[-1]-1, 12) + sum((ds[i]-1)**2 for i in range(j-1))/sp.Integer(2)
    if sp.simplify(ser.coeff(h, 0) - 1) != 0 or sp.simplify(ser.coeff(h, 1) - Lg) != 0 or sp.simplify(ser.coeff(h, 2) - Ng) != 0: good = False; print('  W 전개 불일치', gam, ser)
    for i in range(1, 5):
        c = ser.coeff(h, i)
        if not (0 <= c <= sp.binomial(j+sp.Rational(1,2)+i, i)*sp.Integer(r)**i): good = False; print('  W 계수 범위 위반', gam, i, c)
chk('weight-envelope (나): [n^0]=1, [n^-1]=L, [n^-2]=N, 0<=[n^-i]W<=binom(j+1/2+i,i)r^i (기호 보기)', good)
# third-group (가),(다) 기호·수치
v = sp.symbols('v', integer=True)
good = True
ws = {g: sp.symbols('w%d' % g) for g in range(1, 12)}
def iota_ws(vv): return vv*sum(ws[g]*max(vv-g, 0) for g in range(1, 12))
for vv in range(3, 9):
    d3 = iota_ws(vv) - 3*iota_ws(vv-1) + 3*iota_ws(vv-2) - iota_ws(vv-3)
    if sp.expand(d3 - (vv*ws[vv-1] - (vv-3)*ws[vv-2])) != 0: good = False
    d2 = iota_ws(vv) - 2*iota_ws(vv-1) + iota_ws(vv-2)
    if sp.expand(d2 - (vv*ws[vv-1] + 2*sum(ws[g] for g in range(1, vv-1)))) != 0: good = False
chk('third-group (가) nabla^3, nabla^2 식 (v=3..8)', good and sp.expand(iota_ws(2)-3*iota_ws(1)+3*iota_ws(0)-iota_ws(-1) - 2*ws[1]) == 0)
chk('third-group (다) nf 비 = e(1-1/r)^{r-3}, 1<= 비 <=1+6/r', all(abs(nf(n,d+1)/nf(n,d) - me*(1-mpf(1)/(n-d))**(n-d-3)) < mpf(10)**-20 and 1 <= nf(n,d+1)/nf(n,d) <= 1+mpf(6)/(n-d) for n in (30, 80) for d in range(0, n-3)))
chk('last-gap: v Ren(v-1)/nabla^3 iota° <= v(2v-5)/(5v-12) <= 2v/5', all(mpf(vv)*Ren(vv-1)/(vv*Ren(vv-1)-(vv-3)*Ren(vv-2)) <= mpf(vv)*(2*vv-5)/(5*vv-12) <= mpf(2)*vv/5 for vv in range(3, 200)))
chk('third-group (나): Ren(v-2) <= nabla^3 iota° <= 3Ren(v-2)', all(Ren(vv-2) <= vv*Ren(vv-1)-(vv-3)*Ren(vv-2) <= 3*Ren(vv-2) for vv in range(3, 200)))
# sign-sandwich (나) Lp^± 감싸기 (j=2,3,4) 대 정확 Z^{(3)}_j
wv = sp.symbols('w')
qm = 1/wv - sp.Rational(24,25) - wv/25; qp = 1/wv - sp.Rational(11,12) - wv/12
em_ = sp.Rational(1,2)/wv - sp.Rational(1,12) + wv/12; ep_ = sp.Rational(1,2)/wv + sp.Rational(1,40)
def lp_next(L):
    L = sp.expand(L); terms = sp.Poly(sp.expand(L*wv**40), wv)
    out = 0
    for (deg,), c in terms.terms():
        i = deg - 40
        out += (3 - sp.Rational(i, 2))*c*wv**(i-2)
    return out
Lm = sp.expand((1-wv**2)*(2-wv**2)*qm**2 + (1-wv**2)**2*qm*em_); Lp = sp.expand((1-wv**2)*(2-wv**2)*qp**2 + (1-wv**2)**2*qp*ep_)
def laurent_z_coeffs(L, N):
    out = [mpf(0)]*(N+1)
    for (deg,), c in sp.Poly(sp.expand(L*wv**40), wv).terms():
        i = deg - 40
        ser = sp.series((1-z)**sp.Rational(i,2), z, 0, N+1).removeO()
        for U in range(N+1): out[U] += mpf(c)*mpf(ser.coeff(z, U))
    return out
good = True
for j in range(2, 5):
    N = 14
    Zc = Z_series(3, j, N)
    lo = laurent_z_coeffs(Lm, N); hi = laurent_z_coeffs(Lp, N)
    for U in range(0, N+1):
        if not (o**j*lo[U] - mpf(10)**-18 <= Zc[U] <= o**j*hi[U] + mpf(10)**-18): good = False; print('  Lp 감싸기 위반', j, U, o**j*lo[U], Zc[U], o**j*hi[U])
        if lo[U] < -mpf(10)**-18: good = False; print('  Lp^- z계수 음수', j, U)
    Lm = sp.expand(qm*(1-wv**2)*lp_next(Lm)); Lp = sp.expand(qp*(1-wv**2)*lp_next(Lp))
chk('sign-sandwich (나) o^j Lp^-_j <= Z^{(3)}_j <= o^j Lp^+_j (j=2,3,4, z^14까지), Lp^-의 z계수 비음', good)
# kernel-C-bound Laurent 계수식
chk('[z^m]o(1/2 w^-1 - 3/4 + w - w^2/4): m=1 -> 0, m>=2 -> o cb(1/2-1/(2m-1)); [z^m]o(1/2w^-1+5/2-2w) = o cb(1/2+2/(2m-1))', all(abs(laurent_z_coeffs(sp.Rational(1,2)/wv - sp.Rational(3,4) + wv - wv**2/4, 8)[m] - (0 if m == 1 else cb(m)*(mpf(1)/2 - mpf(1)/(2*m-1)))) < mpf(10)**-20 and abs(laurent_z_coeffs(sp.Rational(1,2)/wv + sp.Rational(5,2) - 2*wv, 8)[m] - cb(m)*(mpf(1)/2+mpf(2)/(2*m-1))) < mpf(10)**-20 for m in range(1, 9)))
# D.exact-n20000 (ㄹ) 미달 수 재귀
good = True
for k in range(2, 9):
    for n in range(k+1, 2*k+2):
        Ac = lambda nn, l: p(nn) - A_rec(nn, l)
        rhs = sum(C(n-1, i)*(n-k-i)*p(i)*p(n-1-i) for i in range(0, n-k)) + sum(C(n-1, i)*(k+i+1)*p(i)*Ac(n-1-i, k-1) for i in range(0, n-k-1))
        if Ac(n, k-1) != rhs: good = False; print('  A^c 재귀 불일치', n, k, Ac(n,k-1), rhs)
chk('D.exact-n20000 (ㄹ) 미달 수 재귀 A^c_{n,k-1} (k<=8, k+1<=n<=2k+1)', good)
# D.c50 hB 정규화 재귀 수치 (정확 b와 대조)
def Bor(j): return mexp(-j)*mpf(j)**(j-1)/mfac(j)
def hB(x): return me*Bor(x)
good = True
for k in range(2, 7):
    Y = {}; Yk1 = {}
    def Yrec(kk, M):
        Yv = [hB(m+1) for m in range(0, kk+1)]
        for m in range(kk+1, M+1):
            Yv.append(hB(m+1) - sum(Bor(m+1-s)*hB(s) for s in range(kk+1, m+1)) + kk*sum(Bor(m+1-s)*Yv[s-1]/s for s in range(kk+1, m+1)))
        return Yv
    M = 2*k+1
    Yk = Yrec(k, M); Yk1 = Yrec(k+1, M)
    Zv = [mpf(0)]*(k+1)
    for n in range(k+1, M+1):
        Zv.append(sum(Bor(n+1-s)*(Yk1[s-1] + k*Zv[s-1])/s for s in range(k+1, n+1)))
    for n in range(k+1, M+1):
        bnk = A_rec(n, k) - A_rec(n, k-1)
        if abs(Zv[n] - bnk*mexp(-n)/mfac(n)) > mpf(10)**-20*abs(Zv[n]): good = False; print('  Z 불일치', n, k, Zv[n], bnk*mexp(-n)/mfac(n))
        snk = A_rec(n, k-1)/mpf(p(n))  # s_n(k) = A_{n,k-1}/p_n
        if abs(Yk[n] - hB(n+1)*snk) > mpf(10)**-20*abs(Yk[n]): good = False; print('  Y 불일치', n, k)
chk('D.c50 Y^{(k)}, Z^{(k)} 재귀: Z = b e^{-n}/n!, Y = hB(n+1)s_n (k<=6, n<=2k+1)', good)
chk('pi_n(s) = C(n,s)s^{s-1}p_{n-s}/p_n = Bor(n+1-s)hB(s)/hB(n+1)', all(abs(mpf(C(n,s))*mpf(s)**(s-1)*p(n-s)/p(n) - Bor(n+1-s)*hB(s)/hB(n+1)) < mpf(10)**-22 for n in range(1, 15) for s in range(1, n+1)))
print('ALL OK' if ok else 'SOME NG')
