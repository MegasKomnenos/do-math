# 검토전체20 N7a: 7.4절 기호 검산 (2) — hermite-nu, 조각 지수 공식, Neumann 전개, Green 원자
# 실행: python -I 검토전체20_N7a_check2.py > 검토전체20_N7a_check2_out.txt
import sympy as sp
from itertools import permutations
from math import comb, factorial

print("== A. hermite-nu (가)(나): nm, H0,H1,H2 ==")
w, nu, th = sp.symbols('w nu theta')
Nk = 3+(nu+1-th)*w
xx = w*(1-th*w)/Nk**2
xn = (2+(nu-1)*w)*(1-th*w)/Nk**2
nm_claim = 1+(2*nu+10+2*th)*w+((nu+1)**2+2*(nu-3)*th+th**2)*w**2
print("nm identity:", sp.simplify((1-4*xn)*Nk**2-nm_claim) == 0)
gam = sp.sqrt(nm_claim)/Nk
ups0 = (1+gam)/2
C1 = (1-ups0)/gam**2
C2 = -(1-ups0)*(2+ups0)/gam**5
C3 = sp.Rational(5, 2)*(1-ups0)*(6+gam-gam**2)/gam**8
hat = ups0+xx*C1+xx**2*C2+xx**3*C3
H = (Nk*hat-2-nu*w)/w
ser = sp.series(H, w, 0, 3).removeO()
H0 = sp.expand(ser.coeff(w, 0)); H1 = sp.expand(ser.coeff(w, 1)); H2 = sp.expand(ser.coeff(w, 2))
print("H0 =", H0, "| claim 4")
print("H1 =", H1, "| claim", sp.expand(-(26+4*nu)-8*th))
print("H2 =", H2, "| claim", sp.expand(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2))
print("H1 ok:", sp.simplify(H1-(-(26+4*nu)-8*th)) == 0, " H2 ok:", sp.simplify(H2-(506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2)) == 0)

print("== B. hermite-nu (라)(마): U_i, V_i, 일반 y의 M2/M0 ==")
k, d, y, n = sp.symbols('k d y n')
def M_ratio(i, yv, nv):
    # He_{n-1}=1, He_n = n+d ; reverse recursion He_{j-1} = (N He_j - He_{j+1})/(y j), N=n+y+1
    N = nv+yv+1
    He = {nv: nv+d, nv-1: sp.Integer(1)}
    # compute symbolic He_{n-2..}: use j symbolic shift: He_{n-2} = (N*He_{n-1}-He_n)/(y*(n-1))
    He_m2 = (N*He[nv-1]-He[nv])/(yv*(nv-1))
    He_m3 = (N*He_m2-He[nv-1])/(yv*(nv-2))
    He_m4 = (N*He_m3-He_m2)/(yv*(nv-3))
    He_m5 = (N*He_m4-He_m3)/(yv*(nv-4))
    Hs = [He[nv], He[nv-1], He_m2, He_m3, He_m4, He_m5]
    def coef(i):
        # [Y^n](1-Y)^{i+1} E = sum_s C(i+1,s)(-1)^s He_{n-s}/(n-s)!  ; multiply by n! -> sum C(i+1,s)(-1)^s He_{n-s} * n!/(n-s)!
        tot = 0
        for s_ in range(0, i+2):
            ff = 1
            for t in range(s_): ff *= (nv-t)
            tot += sp.binomial(i+1, s_)*(-1)**s_*Hs[s_]*ff
        return tot
    return sp.simplify(coef(i)/coef(0))
nv = 2*k+nu
U2 = 1+(2*nu+2)/k+nu*(nu+1)/k**2; V2 = 4+(4*nu+2)/k+nu*(nu+1)/k**2
U4 = 1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4 = 4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
r2 = M_ratio(2, k, nv); r4 = M_ratio(4, k, nv)
print("M2/M0 = U2 - V2/d :", sp.simplify(r2-(U2-V2/d)) == 0)
print("M4/M0 = U4 - V4/d :", sp.simplify(r4-(U4-V4/d)) == 0)
r2y = M_ratio(2, y, n)
print("general y: M2/M0 = 1-2n/y+n(n+1)/y^2-n(n+1)/(y^2 d):", sp.simplify(r2y-(1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))) == 0)
# (마) k-coefficient 20
dy = 4-(26+4*nu+8*th)/k
expr = sp.expand((nv*(nv+1)-dy*((nv-(k-th))**2+nv)))
print("n(n+1)-d[(n-y)^2+n] with d=4-(26+4nu+8th)/k: k^2 coef =", sp.expand(expr).coeff(k, 2), ", k coef =", sp.expand(expr).coeff(k, 1))
# (다) off quadratic checks
off = sp.symbols('off')
print("off=2:", sp.expand((2)**2+(k+nu-1)*2-(2*k+nu)), "; off=2-(3+nu)/k:", sp.simplify(sp.expand((2-(3+nu)/k)**2+(k+nu-1)*(2-(3+nu)/k)-(2*k+nu))))
print("1-4q numerator:", sp.simplify(sp.expand((3*k+nu+1)**2-4*(2*k+nu)*k-((k+nu+3)**2-4*(nu+2)))) == 0)

print("== C. 조각 지수 공식 (7.6), X의 최저 차수, (7.7), Neumann 전개, bd 값, Green 원자 (k=2,3) ==")
x, z = sp.symbols('x z')
def caps(sig):
    h = []
    for i in range(len(sig)):
        j = i-1
        while j >= 0 and sig[j] < sig[i]: j -= 1
        h.append(i-j)
    return h
def ser_trunc(e, D):
    return sp.series(sp.expand(e), x, 0, D+1).removeO()
def integ(e):
    return sp.integrate(sp.expand(e), x)
for kk in (2, 3):
    D = 3*kk+2
    BF = D if kk == 2 else 9   # brute-force limit (k=3: 9! permutations)
    T = sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1, D+1))
    eT = ser_trunc(sp.exp(T), D)
    Kpoly = {0: sp.Integer(1)}; Jpoly = {0: sp.Integer(0)}; Bnum = {}; Anum = {}
    # K via last-car decomposition recursion (independent of the exponential formula under test)
    Krec = {0: sp.Integer(1)}
    for m in range(1, D+1):
        Krec[m] = sp.expand(sum(sp.binomial(m-1, j)*(sp.Integer(j+1) if j+1 <= kk else z)*Krec[j]*Krec[m-1-j] for j in range(0, m)))
    for m in range(1, D+1):
        if m > BF:
            Kpoly[m] = Krec[m]; Anum[m] = Kpoly[m].subs(z, kk); continue
        K = 0; J = 0; B = 0; Acnt = 0
        for sig in permutations(range(1, m+1)):
            h = caps(sig)
            wk = 1; Hc = 0; Zc = 0; wlt = 1
            for hi in h:
                if hi <= kk: wk *= hi
                if hi < kk: wlt *= hi
                if hi == kk: Hc += 1
                if hi > kk: Zc += 1
            K += wk*z**Zc
            J += wlt*Hc*kk**(Hc-1)*z**Zc if Hc > 0 else 0
            B += wlt*(kk-1)**Zc*(kk**Hc-(kk-1)**Hc)
            Acnt += wk*kk**Zc
        Kpoly[m] = sp.expand(K); Jpoly[m] = sp.expand(J); Bnum[m] = B; Anum[m] = Acnt
        assert sp.expand(Kpoly[m]-Krec[m]) == 0
    print(f"k={kk}: brute-force K_n (n<={BF}) agrees with last-car recursion")
    Dser = sum(Kpoly[m]*x**m/sp.factorial(m) for m in range(0, D+1))
    Elt = sum(sp.Integer(m+1)**(m-1)*x**m/sp.factorial(m) for m in range(0, kk))
    Dge = sp.expand(Dser-Elt)
    Tle = sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1, kk+1))
    Tgt = sp.expand(T-Tle)
    rhs76 = ser_trunc(sp.exp(Tle+z*integ(Dge)), D)
    print(f"k={kk}: (7.6) holds mod x^{D+1}:", sp.expand(rhs76-Dser) == 0)
    Qk = ser_trunc((1-T)*(eT-Elt), D)
    # S^G series: S' = Qk + z e^T S, S(0)=0 ; solve coefficientwise
    S = 0
    for it in range(D+2):
        S = ser_trunc(integ(Qk+z*eT*S), D)
    Gstar = ser_trunc(Elt+Qk+z*eT*S, D)
    Xs = sp.expand(Dser-Gstar)
    lowdeg = min([sp.Poly(Xs, x).monoms()[i][0] for i in range(len(sp.Poly(Xs, x).monoms()))])
    print(f"   X lowest degree = {lowdeg} (claim {2*kk+2})")
    bd = sp.expand(z*integ(Dge)-Tgt)
    eTle = ser_trunc(sp.exp(Tle), D)
    rhs77 = ser_trunc(eTle*(z*integ(Xs)+bd**2/2), D)
    print("   (7.7) holds mod x^{3k+3}:", sp.expand(rhs77-Xs) == 0)
    # Gstar functional eq.
    print("   G* = e^T(1-T_{>k}+z int(G*-E)):", sp.expand(ser_trunc(eT*(1-Tgt+z*integ(Gstar-Elt)), D)-Gstar) == 0)
    # Neumann expansion of X''(k)
    def Neu(f): return ser_trunc(eTle*integ(f), D)
    bdz = bd; bd1 = sp.diff(bd, z); bd2 = sp.diff(bd, z, 2)
    tot = 0
    for j in range(0, D+1):
        Qj = sp.Rational(j*(j-1), 2)/kk**2*bdz**2+sp.Rational(2*j, kk)*bdz*bd1+bd1**2+bdz*bd2
        f = ser_trunc(eTle*Qj, D)
        for _ in range(j): f = Neu(f)
        tot += kk**j*f
    tot = ser_trunc(tot.subs(z, kk), D)
    X2 = ser_trunc(sp.diff(Xs, z, 2).subs(z, kk), D)
    print("   X''(k) = sum k^j Neu^j[e^{T<=k} Q_j]:", sp.expand(tot-X2) == 0)
    # bd_t values at z=k
    okbd = True
    for t in range(kk+1, D+1):
        A_t1 = Anum[t-1]
        bdt = sp.expand(bd.coeff(x, t)*sp.factorial(t))
        # moments of size t-1 under Pr^sigma
        Zf = sp.Rational(sp.diff(Kpoly[t-1], z).subs(z, kk)*kk, A_t1)
        ZZ = sp.Rational(sp.diff(Kpoly[t-1], z, 2).subs(z, kk)*kk**2, A_t1)
        ex = sp.Rational(t*(t)**(t-2), A_t1)-kk
        okbd &= (bdt.subs(z, kk) == -A_t1*ex)
        okbd &= (sp.diff(bdt, z).subs(z, kk) == A_t1*(1+Zf))
        okbd &= (sp.diff(bdt, z, 2).subs(z, kk) == sp.Rational(A_t1, kk)*(2*Zf+ZZ))
    print("   bd_t(k), bd'_t, bd''_t formulas:", okbd)
    # Green atom
    ac = sp.Rational(kk**(kk-2), sp.factorial(kk-1))  # a°_{k-1} = p_{k-1}/(k-1)!
    gr = 0
    for it in range(D+2):
        gr = ser_trunc(integ(ac*x**(kk-1)+z*eT*gr), D)
    JG = {m: sp.expand(sp.factorial(m)*ser_trunc(eT*gr, D).coeff(x, m)) for m in range(0, D+1)}
    okeq = all(sp.expand(JG[m]-Jpoly[m]) == 0 for m in range(0, 2*kk+1))
    okineq = True
    for m in range(2*kk+1, BF+1):
        for zv in [0, sp.Rational(1, 2), 1, kk-1, kk, kk+1]:
            okineq &= (JG[m].subs(z, zv) >= Jpoly[m].subs(z, zv))
    print(f"   Green atom: equality n<=2k {okeq}; J_n(z)<=J^G_n(z) for 2k<n<={BF}, z in [0,k+1] samples {okineq}")
    # (7.5): d >= K'' - B >= K'' - J(k-1)
    ok75 = True
    for m in range(1, BF+1):
        Ak = Anum[m]; Akm1 = Kpoly[m].subs(z, kk-1)  # not A_{m,k-2}
        # A_{m,k} = K(k+1), A_{m,k-2} = K(k-1) - B
        Akp = Kpoly[m].subs(z, kk+1); Akm2 = Kpoly[m].subs(z, kk-1)-Bnum[m]
        dmk = Akp-2*Ak+Akm2
        K2 = sp.diff(Kpoly[m], z, 2).subs(z, kk)
        ok75 &= (dmk >= K2-Bnum[m] >= K2-Jpoly[m].subs(z, kk-1))
    print("   (7.5) chain:", ok75)
