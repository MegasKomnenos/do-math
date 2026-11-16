# -*- coding: utf-8 -*-
"""수학 검사 2(태그 5A) 검산 3: 5.4.2절 적분 표현(cut-rep (가)(다)(라), hat-normalization, unit-circle)을
작은 k에서 수치 적분과 전수 주차로 대조한다.
python -I scripts/수학검사2/5A_검산_3_적분표현.py
"""
import itertools, math
from mpmath import mp, mpf, mpc, pi, e, exp, log, sqrt, sin, cos, cot, quad, factorial, re, im, fabs, inf
mp.dps = 20
import sys
def _flush(): sys.stdout.flush()
ok = True
def chk(name, cond, *vals):
    global ok
    ok &= bool(cond)
    print(('OK ' if cond else 'NG ') + name, *vals); sys.stdout.flush()
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def Bor(j): return exp(-j)*mpf(j)**(j-1)/factorial(j)
def rb(k): return log(factorial(k)) - (k+mpf(1)/2)*log(k) + k - log(2*pi)/2
def Borz(j, z): return exp(-j*z)*(j*z)**(j-1)/factorial(j)
def Btail(k, z): return 1 - sum(Borz(j, z) for j in range(1, k+1))

# ---- cut-rep (가): k^{k-1}/k! = (1/pi) int Im T_+ ct^{-k-1} dct, ct = phi e^{-phi cot phi}/sin phi
ct = lambda ph: ph*exp(-ph*cot(ph))/sin(ph)
dlogct = lambda ph: 1/ph - 2*cot(ph) + ph/sin(ph)**2  # (log ct)' 닫힌 꼴
good = True
for k in range(1, 6):
    val = quad(lambda ph: ph*ct(ph)**(-k)*dlogct(ph), [0, pi/2, pi])/pi
    if fabs(val - mpf(k)**(k-1)/factorial(k)) > mpf(10)**-15: good = False; print('  (가) 불일치', k, val, mpf(k)**(k-1)/factorial(k))
chk('cut-rep (가) k^{k-1}/k! 적분 표현 (k<=5)', good)
# T_+(ct) = phi cot phi + i phi satisfies pt e^{-pt} = ct
chk('cut-rep (가) (phi cot phi + i phi)e^{-(...)} = ct(phi)', all(fabs((ph*cot(ph)+1j*ph)*exp(-(ph*cot(ph)+1j*ph)) - ct(ph)) < mpf(10)**-16 for ph in (mpf('0.3'), mpf('1.1'), mpf('2.5'))))
# ---- cut-rep (다): Bor^tail_k(pt') = xi^{k+1}/(pi pt') int_1^inf Im T_+(et/e) et^{-k-1}/(et - xi) d et, et = e*ct(phi)
et = lambda ph: e*ct(ph)
good = True
for k in (3, 4, 6):
    for ag in (mpf('0.5'), mpf('0.9'), mpf('2.0')):
        ptp = exp(1j*ag); xi = ptp*exp(1-ptp)
        f = lambda ph: ph*et(ph)**(-k)*dlogct(ph)/(et(ph)-xi)
        val = xi**(k+1)/(pi*ptp)*quad(f, mp.linspace(0, pi, 13))
        direct = Btail(k, ptp)
        if fabs(val - direct) > mpf(10)**-12*(1+fabs(direct)): good = False; print('  (다) 불일치', k, ag, val, direct)
chk('cut-rep (다) Borel 꼬리 절단 표현 (k=3,4,6; ag=0.5,0.9,2.0)', good)
# ---- cut-rep (라): 𝔍 꼴과 Bt
def lm(m): return (2+mpf(1)/m)*mp.zeta(2*m)/pi**(2*m)
good = True
for k in (4, 7):
    ku = mpf(k)**(-mpf(1)/3)
    for ag in (mpf('0.4'), mpf('1.3')):
        ptp = exp(1j*ag); xi = ptp*exp(1-ptp); agh = ag/ku
        Zh = (xi-1)/ku**2
        def integrand(phh):
            ph = ku**mpf(1.5)*phh
            Lh = k*log(et(ph)); lg = dlogct(ph)/ph; nu = phh**2*lg*exp(-Lh)
            qy = k*(et(ph)-1)
            return nu/(ku*qy - Zh)
        I = quad(integrand, [0, 1, 5, pi*ku**(-mpf(1.5))])
        tail_formula = xi**(k+1)/(pi*ptp)*ku**mpf(2.5)*I
        direct = Btail(k, ptp)
        if fabs(tail_formula - direct) > mpf(10)**-13*(1+fabs(direct)): good = False; print('  (라) Bor^tail 불일치', k, ag, tail_formula, direct)
        A = (1-exp(1j*ku*agh))/ku
        ph_ = k*(1j*ag + (1-ptp) + (1-ptp)**2/2)
        Bt_direct = ku**2*direct*exp(k*(1-ptp)**2/2)/Bor(k)
        Bt_formula = sqrt(2/pi)*exp(rb(k))*exp(ku*A)*exp(ph_)*I
        if fabs(Bt_direct - Bt_formula) > mpf(10)**-13*(1+fabs(Bt_direct)): good = False; print('  (라) Bt 불일치', k, ag, Bt_direct, Bt_formula)
        # ph 급수, 1-pt' = ku A, et - xi = ku^2(ku qy - Zh), xi^{k+1}e^{k(1-pt')^2/2}/pt' = e^{ph + ku A}
        ph_ser = sum((2**(m-1)-2)*ku**(m-3)*(1j*agh)**m/factorial(m) for m in range(3, 80))
        if fabs(ph_ser - ph_) > mpf(10)**-18: good = False; print('  ph 급수 불일치', k, ag)
        if fabs(xi**(k+1)*exp(k*(1-ptp)**2/2)/ptp - exp(ph_ + ku*A)) > mpf(10)**-18: good = False; print('  xi^{k+1} 식 불일치')
        phh0 = mpf('0.7'); ph0 = ku**mpf(1.5)*phh0
        Lh = k*log(et(ph0)); Lh_ser = sum(lm(m)*ku**(3*(m-1))*phh0**(2*m) for m in range(1, 60))
        lg_ser = sum(2*m*lm(m)*ku**(3*(m-1))*phh0**(2*m-2) for m in range(1, 60))
        if fabs(Lh - Lh_ser) > mpf(10)**-18 or fabs(dlogct(ph0)/ph0 - lg_ser) > mpf(10)**-15: good = False; print('  L̂/lg 급수 불일치')
        if fabs((et(ph0)-xi) - ku**2*(ku*k*(et(ph0)-1) - Zh)) > mpf(10)**-18: good = False
chk('cut-rep (라) 𝔍 표현, Bt 식, ph·L̂·lg 급수, et-xi 분해 (k=4,7)', good)
chk('Bor(k) = e^{-rb_k}/(sqrt(2pi) k^{3/2})', all(fabs(Bor(k) - exp(-rb(k))/(sqrt(2*pi)*mpf(k)**mpf(1.5))) < mpf(10)**-20 for k in (1, 4, 10)))

# ---- unit-circle (가)(나) 수치 표본
good = True
for k, n in ((10, 15), (30, 50)):
    r = n-k
    for ag in (mpf('0.3'), mpf('1.2'), mpf('2.8')):
        for agp in (ag/3, ag):
            pt = exp(1j*ag); ptp = exp(1j*agp)
            lhs1 = fabs(exp(n*(pt-1))*exp((k-1)*((pt-pt**2/2)-mpf(1)/2)))*fabs(ptp**(k-1)*exp(-(k-1)*(2*ptp-ptp**2/2)+3*(k-1)/mpf(2)))
            if lhs1 > exp(-(r+1)*(1-cos(ag)))*(1+mpf(10)**-18): good = False; print('  unit-circle (가) 위반', k, n, ag, agp)
            V = lambda z: (1-z)**2/2
            lhs2 = fabs(exp(n*(pt-1))*exp(-k*V(pt)))*fabs(exp(k*V(ptp))*Btail(k, ptp))
            if lhs2 > 2*exp(-r*(1-cos(ag)))*(1+mpf(10)**-18): good = False; print('  unit-circle (나) 위반', k, n, ag, agp)
chk('unit-circle (가)(나) 수치 표본', good)

# ---- hat-normalization: 전수 주차로 e_n=2E2, B_{n,k-1} 계산 (n=6,7; k=4)
def enumerate_counts(n):
    E2 = {}; Bc = {}
    for a in itertools.product(range(1, n+1), repeat=n):
        spots = [0]*(n+1); disp = [0]*(n+1); okpf = True
        for car in range(1, n+1):
            s = a[car-1]
            while s <= n and spots[s]: s += 1
            if s > n: okpf = False; break
            spots[s] = car; disp[car] = s - a[car-1]
        if not okpf: continue
        sigma = spots[1:]; M = max(disp[1:]); Msh = sum(1 for d in disp[1:] if d == M)
        h = []
        for i in range(1, n+1):
            j = i-1
            while j >= 1 and sigma[j-1] < sigma[i-1]: j -= 1
            h.append(i-j)
        if Msh == 2: E2[M] = E2.get(M, 0) + 1
        if all(h[i] == M+1 for i in range(n) if disp[sigma[i]] == M): Bc[M] = Bc.get(M, 0) + 1
    return E2, Bc
def Upsilons(n, k):
    ku = mpf(k)**(-mpf(1)/3); r = n-k; xh = (r+1)*mpf(k)**(-mpf(2)/3)
    A = lambda agh: (1-exp(1j*ku*agh))/ku
    V = lambda z: (1-z)**2/2
    def Om_e(agh):
        ag = ku*agh; pt = exp(1j*ag)
        return (n+1)*(pt-1) - 1j*n*ag - k*V(pt)
    def Om_e_series(agh):
        return 1j*ku*agh - xh*agh**2/2 + sum((xh*ku**(m-2) - (2**(m-1)-2)*ku**(m-3))*(1j*agh)**m/factorial(m) for m in range(3, 120))
    Om_B = lambda agh: Om_e(agh) + ku**2*A(agh)**2/2
    ph_ = lambda agp: k*(1j*agp + (1-exp(1j*agp)) + (1-exp(1j*agp))**2/2)
    Bt = lambda aghp: ku**2*Btail(k, exp(1j*ku*aghp))*exp(k*(1-exp(1j*ku*aghp))**2/2)/Bor(k)
    Wr = [quad(lambda v: v**2*Btail(k, 1-v)*exp(k*v**2/2)*(v**2/2)**j, [0, 1])/Bor(k) for j in range(3)]
    Wh = [Wr[j]/ku**(1+2*j) for j in range(3)]
    Jk = quad(lambda v: v*exp(v-(k-1)*(-log(1-v)-v-v**2/2)), [0, 1]); Jh = Jk/ku**2
    def Ce(m, agh): return quad(lambda t: A(t)**(2+2*m)*Bt(t)*1j*exp(1j*ku*t), [0, agh], maxdegree=6)
    def Cb(agh): return quad(lambda t: exp((1-ku**3)*ph_(ku*t))*A(t)*exp(ku*A(t))*1j*exp(1j*ku*t), [0, agh], maxdegree=6)
    def fe(agh):
        c0 = Wh[2] + 2*ku*Wh[1] + Ce(2, agh)/4 + ku*Ce(1, agh)
        c1 = Wh[1] + ku*Wh[0] + Ce(1, agh)/2 + ku*Ce(0, agh)
        c2 = (Wh[0] + Ce(0, agh))/4
        Aa = A(agh)
        return Aa*exp(Om_e(agh))*(c0 - Aa**2*c1 + Aa**4*c2)
    def fB(agh):
        return A(agh)*exp(Om_B(agh))*(Jh + Cb(agh))
    top = pi/ku
    Ue = re(quad(fe, mp.linspace(0, top, 7), maxdegree=6)); UB = re(quad(fB, mp.linspace(0, top, 7), maxdegree=6))
    # Ω_e 급수 = 닫힌 꼴, Ω_e' = i(ku - xh A - A^2), |e^{Ω_e}| 식
    agh0 = mpf('0.8')
    c1 = fabs(Om_e(agh0) - Om_e_series(agh0)) < mpf(10)**-15
    c2 = fabs(mp.diff(Om_e, agh0) - 1j*(ku - xh*A(agh0) - A(agh0)**2)) < mpf(10)**-12
    c3 = fabs(fabs(exp(Om_e(agh0))) - exp(-(r+1)*(1-cos(ku*agh0)) - k*(1-cos(ku*agh0))**2)) < mpf(10)**-15
    return Ue, UB, c1 and c2 and c3
for n, k in ((6, 4), (7, 4)):
    E2, Bc = enumerate_counts(n)
    en = 2*E2.get(k, 0); Bn = Bc.get(k-1, 0)
    ku = mpf(k)**(-mpf(1)/3); nn = factorial(n)*exp(n+1)/p(n)
    Ue, UB, aux = Upsilons(n, k)
    pred_e = nn*Bor(k)/pi*ku**4*Ue; pred_B = nn*Bor(k)/pi*ku**4*UB
    print(' n=%d k=%d: e_n/p_n=%s vs %s;  B/p_n=%s vs %s' % (n, k, mp.nstr(mpf(en)/p(n), 12), mp.nstr(pred_e, 12), mp.nstr(mpf(Bn)/p(n), 12), mp.nstr(pred_B, 12)))
    chk('hat-normalization e_n 식 (n=%d,k=%d)' % (n, k), fabs(pred_e - mpf(en)/p(n)) < mpf(10)**-9)
    chk('hat-normalization B_{n,k-1} 식 (n=%d,k=%d)' % (n, k), fabs(pred_B - mpf(Bn)/p(n)) < mpf(10)**-9)
    chk('Omega_e 급수=닫힌 꼴, Omega_e\' 식, |e^{Omega_e}| 식 (n=%d,k=%d)' % (n, k), aux)
    chk('e_n > B_{n,k-1} <=> Upsilon_e > Upsilon_B (n=%d,k=%d)' % (n, k), (en > Bn) == (Ue > UB), en, Bn)
# Ŵr_j: v = ku s 치환 (부록 D (d))
k = 5; ku = mpf(k)**(-mpf(1)/3)
for j in range(3):
    Wr = quad(lambda v: v**2*Btail(k, 1-v)*exp(k*v**2/2)*(v**2/2)**j, [0, 1])/Bor(k)
    Wh = Wr/ku**(1+2*j)
    Wh2 = ku**2*2**(-j)*quad(lambda s: s**(2+2*j)*Btail(k, 1-ku*s)*exp(s**2/(2*ku)), [0, 1/ku])/Bor(k)
    chk('Ŵr_%d = ku^2 2^{-j} int_0^{1/ku} s^{2+2j} Bor^tail(1-ku s) e^{s^2/(2ku)}/Bor(k) ds' % j, fabs(Wh - Wh2) < mpf(10)**-15*(1+fabs(Wh)), mp.nstr(Wh, 10))
    # 코드 꼴의 피적분함수와 점별 일치: ku^2 Bor^tail(1-v)e^{kv^2/2}/Bor(k) = (1-v)^{-1} e^{-kappa_rho} Shat, Shat = ku^2 S_k/Bor(k)
    good = True
    for v in (mpf('0.2'), mpf('0.5'), mpf('0.8')):
        xi = (1-v)*exp(v); kr = k*(-log(1-v)-v-v**2/2)
        S = mpf(0); jj = 1
        while True:
            t = Bor(k+jj)*xi**jj; S += t; jj += 1
            if t < mpf(10)**-28: break
        lhs = ku**2*Btail(k, 1-v)*exp(k*v**2/2)/Bor(k); rhs = (1-v)**-1*exp(-kr)*ku**2*S/Bor(k)
        if fabs(lhs-rhs) > mpf(10)**-15*(1+fabs(lhs)): good = False; print('  코드 꼴 불일치', v, lhs, rhs)
    if j == 0: chk('  코드 꼴 (1-ku s)^{-1}e^{-kappa_rho}Shat 와 점별 일치 (Shat = ku^2 S_k/Bor(k))', good)
Jk = quad(lambda v: v*exp(v-(k-1)*(-log(1-v)-v-v**2/2)), [0, 1])
Jh2 = quad(lambda s: s*exp(ku*s)*exp(-(1-ku**3)*k*(-log(1-ku*s)-ku*s-(ku*s)**2/2)), [0, 1/ku])
chk('𝔍̂ = 𝔍_k/ku^2 = int_0^{1/ku} s e^{ku s} e^{-(1-ku^3) kappa_rho(s)} ds', fabs(Jk/ku**2 - Jh2) < mpf(10)**-15*(1+fabs(Jh2)))
# S_k/Bor(k) 둘러싸기와 e^{rb_k} 둘러싸기
Phi = lambda z: quad(lambda y: (1+y)**(-mpf(3)/2)*exp(-z*y), [0, inf])
good = True
for k in (5, 20, 100):
    for v in (mpf('0.05'), mpf('0.3'), mpf('0.7')):
        xi = (1-v)*exp(v); alpha = -log(xi)
        S = mpf(0); jj = 1
        while True:
            t = Bor(k+jj)*xi**jj; S += t; jj += 1
            if t < mpf(10)**-25 and jj > 50: break
        S = S/Bor(k)
        lo = exp(-mpf(1)/(12*k))*(k*Phi(k*alpha)-1); hi = exp(mpf(1)/(12*k))*k*Phi(k*alpha)
        if not (lo <= S <= hi): good = False; print('  S_k/Bor(k) 둘러싸기 위반', k, v, lo, S, hi)
    if not (1 <= exp(rb(k)) <= exp(mpf(k)**-1/12)): good = False
    for jj in (1, 5, 50):
        ratio = Bor(k+jj)/Bor(k); base = (1+mpf(jj)/k)**(-mpf(3)/2)
        if not (exp(-mpf(1)/(12*k))*base <= ratio <= exp(mpf(1)/(12*k))*base): good = False; print('  Bor 비 둘러싸기 위반', k, jj)
chk('S_k/Bor(k), e^{rb_k}, Bor(k+j)/Bor(k) 둘러싸기 (k=5,20,100)', good)
# 불완전 감마 상계 (d)
good = True
for a in (mpf('0.5'), mpf('0.8'), mpf('1')):
    for x in (mpf(2), mpf(5), mpf(20)):
        if mp.gammainc(a, x) > x**(a-1)*exp(-x): good = False
for a in (mpf('1.3'), mpf('1.7'), mpf('2')):
    for x in (mpf(2), mpf(5), mpf(20)):
        if mp.gammainc(a, x) > x**(a-1)*exp(-x)*(1+(a-1)/x): good = False
chk('Gamma(a,x) <= x^{a-1}e^{-x} (a<=1); <= x^{a-1}e^{-x}(1+(a-1)/x) (1<a<=2)', good)
# -log(1-v)-v-v^2/2 >= v^3/3; e^q <= (1-q/16)^{-16}
chk('-log(1-v)-v-v^2/2 >= v^3/3; e^q <= (1-q/16)^{-16} (0<=q<16)', all(-log(1-v)-v-v**2/2 >= v**3/3 for v in (mpf('0.1'), mpf('0.5'), mpf('0.9'))) and all(exp(q) <= (1-q/16)**-16 for q in (mpf(0), mpf(1), mpf(8), mpf('15.9'))))
print('ALL OK' if ok else 'SOME NG')
