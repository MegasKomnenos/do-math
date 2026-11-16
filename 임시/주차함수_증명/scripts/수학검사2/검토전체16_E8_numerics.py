# -*- coding: utf-8 -*-
"""검토전체16 E8: 장8의 수치 상수와 소규모 정확 항등식 검산.
실행: python -I 검토전체16_E8_numerics.py
"""
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, quad, floor, ceil
from fractions import Fraction
from math import comb
import itertools

mp.dps = 40
C = 1/sqrt(2*pi)
z12, zm12, z32 = zeta(mpf(1)/2), zeta(-mpf(1)/2), zeta(mpf(3)/2)
cPsi = -z12 + z32/12

def Bor(m): return mpf(m)**(m-1)*exp(-m)/mp.factorial(m)
def Ren(r): return mpf(r)**r*exp(-r)/mp.factorial(r)
def Psi(q): return sum(Ren(r) for r in range(1, q+1)) if q >= 1 else mpf(0)
def Bor_le(q): return sum(Bor(m) for m in range(1, q+1))
def Psi_low(rho):
    rho = mpf(rho)
    if rho < 1: return mpf(0)
    return C*(2*sqrt(rho) - cPsi + 1/(2*sqrt(rho)) - rho**(-mpf(3)/2)/24)

print("== 상수 ==")
print("z12,zm12,z32 =", z12, zm12, z32, " cPsi =", cPsi)
k0 = mpf(6600)
eps0 = k0**(-mpf(1)/3)
qmin = mpf('0.2')*k0**(mpf(2)/3); pmin = qmin-1
print("qmin", qmin, "pmin", pmin, "sqrt pmin", sqrt(pmin), "mu", 1/qmin)
print("xi*eps max", mpf('6.001')*eps0, "eps0", eps0, "k^-2/3", k0**(-mpf(2)/3))
mu = 1/qmin
print("(1-mu)^-1/2", (1-mu)**(-mpf(1)/2), "(1-mu)^-3/2", (1-mu)**(-mpf(3)/2))

# (8.13) 함수
def Lam(q):
    p = q-1
    return q*(2*sqrt(p)+z12+1/(2*sqrt(p))) - (mpf(2)/3*p**mpf(1.5)+sqrt(p)/2+zm12)
def Bp(q, k): return C*Lam(q)/(k+1)
def s_frak(q): return mpf(4)/15*q**mpf(2.5) + mpf('0.385')*q**mpf(1.5)
def Cr(q, k): return mpf(3)/2*C*(k+q)**mpf(1.5)/(k+1)**mpf(3.5)*s_frak(q)
def jinf(xi): return mpf(4)/3*C*xi**mpf(1.5)

print("\n== table-lower-bound (가) 이음새 ==")
print("jinf(0.2)", jinf(mpf('0.2')), " Cr(qmin,6600)", Cr(qmin, k0))
print("exp(-0.0477345)", exp(-mpf('0.0477345')))

# 여섯 조각 (8.16)
def pieces(xi, k):
    xi = mpf(xi); k = mpf(k)
    q = xi*k**(mpf(2)/3); p = q-1; n = k+q; kk = k+1; e = k**(-mpf(1)/3)
    E = 2*C*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*e)
    R1 = mpf(3)/2*C*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    H = mpf(2)/3*p**mpf(1.5)+sqrt(p)/2+zm12+p**(-mpf(1)/2)/24
    R2 = mpf(15)/8*C*n**mpf(2.5)*H/(kk**mpf(3.5)*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)*p**(-mpf(1)/2)*k**(-mpf(2)/3)
    D3 = mpf(3)/2*kk*Psi_low(p)/((n+1)*k**(mpf(2)/3))
    return E, R1, R2, D1, D2, D3
def qkk(xi, k):
    E, R1, R2, D1, D2, D3 = pieces(xi, k)
    return (E-R1-R2)/(D1+D2-D3)
E, R1, R2, D1, D2, D3 = pieces('0.2', 6600)
print("q6600(0.2) =", qkk('0.2', 6600), " E/(D1+D2-D3) =", E/(D1+D2-D3))
print("D1-D3 at (0.2,6600)", D1-D3, " bound 0.2-k^-2/3-3C sqrt(.2)k^-1/3 =",
      mpf('0.2')-k0**(-mpf(2)/3)-3*C*sqrt(mpf('0.2'))*eps0)
E0 = 2*C*mpf('0.2')**(-mpf(1)/2)
print("bound E/(...) <= ", 2*C*mpf('0.2')**(-mpf(1)/2)*(1+mpf('0.2')*eps0), "/", mpf('0.168623')+E0,
      "=", 2*C*mpf('0.2')**(-mpf(1)/2)*(1+mpf('0.2')*eps0)/(mpf('0.168623')+E0))

print("\n== escape-y-monotone (라)(마) 상수 (xi=0.2, k=k'=6600) ==")
xi = mpf('0.2'); k = k0
t1 = (mpf(3)/2*sqrt(xi) - xi**(-mpf(1)/2)*k**(-mpf(2)/3)/2)/(2*C)
t2 = mpf(3)/4*k**(-mpf(1)/3)*(1+(1-1/(xi*k**(mpf(2)/3)))**(-mpf(1)/2))
t3 = (k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k**(mpf(2)/3))
print("U' terms", t1, t2, t3, " U' >=", t1-t2-t3)
a1 = (1+xi*eps0)/(12*xi**2*k**(mpf(1)/3)); a2 = 3/(8*sqrt(xi)*k**(mpf(1)/3))
print("V' terms", a1, a2, " sum", a1+a2, " k^1/3 V' <= ", -mpf(1)/2+a1+a2)

print("\n== pieces-k-monotone 상수 ==")
print("eps(1+xi eps) max", eps0*(1+mpf('0.32')), " 6 xi^2 min", 6*mpf('0.04'))
print("(1+1/(4p))/(1-mu)", (1+1/(4*pmin))/(1-mu), " 3.5*k/(k+1)", mpf(3.5)*k0/(k0+1))
print("R2 sum", mpf(2.5)+mpf('1.018072')-mpf('3.49946')-mpf(2)/3)
print("cPsi upper via zeta box", mpf('1.46036')+mpf('2.61238')/12, " 1-cPsi/(2 sqrt p)", 1-mpf('1.678059')/(2*mpf('8.32891')))
print("D3 sum", mpf('0.319921')/3 + 1/(3*mpf('0.985789')*mpf('0.89926')) - mpf(2)/3)
print("(5+sqrt5)/2", (5+sqrt(5))/2)

print("\n== jensen-H-ii ==")
print("Lam'(1) = 2.75+z12 =", mpf('2.75')+z12, " bracket at p=1:", -mpf(1)/6-mpf(2)/3*z12+zm12)

print("\n== closed-form-envelope (가) ==")
print("exp(-1/(12 qmin))", exp(-1/(12*qmin)))
print("1.5*6.001*eps0", mpf(1.5)*mpf('6.001')*eps0)
xi = mpf('6.001')
rho2b = mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps0)**mpf(2.5)*xi**2*k0**(-mpf(2)/3)
print("rho2 bound", rho2b, " check zm12+1/(24 sqrt pmin) <0:", zm12+1/(24*sqrt(pmin)))
print("xi^1.5/(2C) at 6.001", xi**mpf(1.5)/(2*C), " upsilon max", (k0+1)/k0*(1-mu)**(-mpf(1)/2))
V = mpf('0.998816')-mpf('0.4798811')-mpf('0.129421'); U = mpf('18.42449')+mpf('1.00734')
print("V", V, "U", U, "V/U", V/U)
# 실제 V,U 범위 표본
print("sample V,U at (6.001,6600):", end=" ")
E, R1, R2, D1, D2, D3 = pieces('6.001', 6600); E0 = 2*C*mpf('6.001')**(-mpf(1)/2)
print((E-R1-R2)/E0, (D1+D2-D3)/E0)

print("\n== closed-form-envelope (나) ==")
for xi, kk in [('0.1', 6600), ('2.1', 6600)]:
    xi = mpf(xi); kk = mpf(kk)
    br = (mpf('0.4')*xi**mpf(1.5)+mpf('0.5775')*sqrt(xi)*kk**(-mpf(2)/3))*(1+xi*kk**(-mpf(1)/3))**mpf(1.5)
    print("xi", xi, "bracket", br)
print("q at xi=0.1:", mpf('0.1')*k0**(mpf(2)/3), " |zm12|/q", mpf('0.20789')/(mpf('0.1')*k0**(mpf(2)/3)),
      " p^-1.5/(12q)", (mpf('0.1')*k0**(mpf(2)/3)-1)**(-mpf(1.5))/(12*mpf('0.1')*k0**(mpf(2)/3)))
print("case1", mpf('1.46035')-mpf('0.103945')-mpf('0.041667')-mpf('0.013274'))
print("case2", mpf('1.46035')-mpf('0.005909')-mpf('0.000012')-mpf('1.430101'))
# 직접: 모든 k>=6600, 0<xi<=2.1 에서 Bp+Cr < jinf 표본 검사
worst = None
for xi in [mpf(x)/100 for x in range(1, 211)]:
    for kk in [6600, 7000, 10000, 10**5, 10**7, 10**9, 10**11]:
        kk = mpf(kk); q = xi*kk**(mpf(2)/3)
        if q < 2: continue
        d = jinf(xi) - Bp(q, kk) - Cr(q, kk)
        if worst is None or d < worst[0]: worst = (d, xi, kk)
print("min (jinf-Bp-Cr) over sample:", worst)

print("\n== closed-form-envelope (다) ==")
q2 = 2*k0**(mpf(2)/3); p2 = q2-1; mu2 = 1/q2
print("q at xi=2", q2)
print("bracket rho1'", sqrt(1-mu2)-(1+p2**(-mpf(1)/2))*eps0/sqrt(2), " /2 =", (sqrt(1-mu2)-(1+p2**(-mpf(1)/2))*eps0/sqrt(2))/2)
print("0.480085-1/3", mpf('0.480085')-mpf(1)/3)
print("theta1' coeff", (eps0/sqrt(2))/(3*C))
print("0.5(1+1/(4p))", (1+1/(4*p2))/2)
print("V bracket", mpf(1)/2-mpf(3)/2*mu2-mpf(3)/4*eps0/sqrt(2))
xi = mpf(2)
Ulow = 1+(xi**mpf(1.5)-sqrt(xi)*k0**(-mpf(2)/3))/(2*C)-mpf(3)/2*xi*eps0
print("U lower at (2,6600)", Ulow)
print("0.146751-0.5316752/4.37993", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# q_{k,k}(xi) k-증가 표본
for xi in ['2', '3', '6.001']:
    vals = [qkk(xi, kk) for kk in [6600, 6700, 7000, 10000, 10**5, 10**7]]
    print("xi", xi, "q_kk increasing?", all(vals[i] < vals[i+1] for i in range(len(vals)-1)), [mp.nstr(v, 8) for v in vals])

print("\n== closed-form (라) 이음새 ==")
print("q6600(2)", qkk(2, 6600), " e^-jinf(2)", exp(-jinf(mpf(2))))
print("q6600(2.1)", qkk('2.1', 6600), " e^-jinf(2.1)", exp(-jinf(mpf('2.1'))))

print("\n== table-tolerance (나) ==")
print("V U'/U^2", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2)
print("0.85*C*6600/6601", mpf('0.85')*C*k0/(k0+1), " 0.85 sqrt2", mpf('0.85')*sqrt(2))
print("case2 coeffs", mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')), mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')))
print("rG w", mpf('7.429e-4')*mpf('0.0005'))

print("\n== envelope-code-monotone (나) ==")
print("2C sqrt(0.0005)*0.0005", 2*C*sqrt(mpf('0.0005'))*mpf('0.0005'))
Ks = (2/mpf('0.0055'))**mpf(1.5); print("Ks(0.0055)", Ks, " s(2)", s_frak(mpf(2)), " Cr(2,Ks)", Cr(mpf(2), Ks))
print("Cr(2e4, 6.6e9)", Cr(mpf(2)*10**4, mpf('6.6e9')))
print("2/6600^(2/3)", 2/k0**(mpf(2)/3))

print("\n== explicit-bounds (나)(다)(라) 수치 검사 r<=400 ==")
ok = True
S12 = mpf(0); Sh = mpf(0); S32 = mpf(0)
for r in range(1, 401):
    S12 += mpf(r)**(-mpf(1)/2); Sh += sqrt(mpf(r)); S32 += mpf(r)**(-mpf(3)/2)
    up12 = 2*sqrt(r)+z12+mpf(r)**(-mpf(1)/2)/2
    lo12 = up12 - mpf(r)**(-mpf(3)/2)/24
    loh = mpf(2)/3*mpf(r)**mpf(1.5)+sqrt(r)/2+zm12
    uph = loh + mpf(r)**(-mpf(1)/2)/24
    if not (lo12 <= S12 <= up12 and loh <= Sh <= uph and S32 <= z32): ok = False; print("FAIL (나) r", r)
    if not (Psi(r) >= Psi_low(r)): ok = False; print("FAIL (라) r", r)
    if not (Psi(r) <= C*(2*sqrt(r)-1)): ok = False; print("FAIL (다) Psi r", r)
    Bg = 1-Bor_le(r)
    if not (2*C*exp(-1/(12*(r+1)))*(r+1)**(-mpf(1)/2) <= Bg <= sqrt(2/pi)*mpf(r)**(-mpf(1)/2)): ok = False; print("FAIL (다) Bor> r", r)
print("(나)(다)(라) r<=400:", "OK" if ok else "FAIL")
print("cPsi in (3/2, 7/4)?", mpf(1.5) < cPsi < mpf(1.75), " Psi_low(1)", Psi_low(1))
# (마)
def g(x): return (x-1)*log(1+1/mpf(x))
ok = True
for i in range(1, 300):
    if not (mpf(3)/(2*i)-mpf(5)/(6*i*i) <= 1-g(i) <= mpf(3)/(2*i)): ok = False
for ip in [10, 50, 200]:
    for j in range(1, ip-1):
        if not (Bor(ip-j)/Bor(ip) <= ((ip-1)/mpf(ip-1-j))**mpf(1.5)): ok = False; print("FAIL (마) ratio", ip, j)
print("(마):", "OK" if ok else "FAIL")

print("\n== hazard-H1 ==")
for zz in ['0.0537', '0.571']:
    zz = mpf(zz)
    G = mpf(3)/2*(1-zz) - mpf('1.1935')*log(2/(1+zz)) - 1/(1+zz) + mpf(1)/2
    print("G(", zz, ")=", G, " log(2/(1+z))", log(2/(1+zz)), " 1/(1+z)", 1/(1+zz))
print("1.5-0.307(1-3/(2k)) at k=6667:", mpf(1.5)-mpf('0.307')*(1-3/(2*mpf(6667))))
k = mpf(6667); print("(qfb+2)/k lower", mpf(3)/32-mpf(3)/4*k**(-mpf(1)/3)+mpf('0.53')/k, " 3.2/k", mpf('3.2')/k)

print("\n== old-6-29 범위 수치 ==")
k = 6668; qmax = int(floor(6*mpf(k)**(mpf(2)/3)))
print("qmax(6668)", qmax, " k-2399 >= qmax+300:", k-2399 >= qmax+300, " 3k/4 >= 2398+qmax:", 3*k/4 >= 2398+qmax)
print("q_fb(6668)", (3*(k-1)/4-qmax-3)//8, " m_fb", -(-5*k//4)+qmax, " 2k+1-8qfb", 2*k+1-8*((3*(k-1)/4-qmax-3)//8))
print("6*(k-1)^(2/3) vs 3.6k^(2/3)", 6*mpf(k-1)**(mpf(2)/3), mpf('3.6')*mpf(k)**(mpf(2)/3), " (k/(k-1))^(2/3)", (mpf(k)/(k-1))**(mpf(2)/3))
print("K grid: 12927/1e5^(2/3)", 12927/mpf(10)**(mpf(10)/3), 12926/mpf(10)**(mpf(10)/3))

# ================= 정확 항등식 (소규모) =================
print("\n== 정확 재귀로 (8.2),(8.3),(8.8)-(8.11), old-6-30/31/32 검사 ==")
NMAX = 40
# A[m][l] = A_{m,l} via 정리 2.old-2-6 마지막 차 재귀: A_{m,k-1} = sum_j C(m-1,j-1) min(j,k) A_{j-1,k-1} A_{m-j,k-1}
A = {}
def Aml(m, l):
    if l < 0: return 0
    if m == 0: return 1
    key = (m, l)
    if key in A: return A[key]
    kk = l+1
    v = sum(comb(m-1, j-1)*min(j, kk)*Aml(j-1, l)*Aml(m-j, l) for j in range(1, m+1))
    A[key] = v; return v
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def s(m, y): return Fraction(Aml(m, y-1), p(m))  # Pr_m(M<=y-1)
def c(m, Y): return s(m, Y+1)-s(m, Y)
def pi_(n, m): return Fraction(comb(n, m)*m**(m-1)*p(n-m), p(n))
def pi0(n, y):  # Pr_n(G<=y): 크기 y 넘는 나무 없음; n<=2y+1 이면 1 - sum_{m>y} pi_n(m)
    assert n <= 2*y+1
    return 1 - sum(pi_(n, m) for m in range(y+1, n+1))
# 검사: p(m) = A_{m,m-1}
assert all(Aml(m, m-1) == p(m) for m in range(1, 15))
bad = []
for k in range(2, 9):
    # (8.2) equality k+1<=m<=2k+1 ; lower bound m>=2k+2 (up to 3k)
    for m in range(k+1, min(3*k, NMAX)+1):
        rhs = sum(pi_(m, t)/t*(s(t-1, k+1)+k*c(t-1, k))*(s(m-t, k) if m >= 2*k+2 else 1) for t in range(k+1, m+1))
        if m <= 2*k+1:
            if c(m, k) != rhs: bad.append(("8.2 eq", k, m))
        else:
            if c(m, k) < rhs: bad.append(("8.2 lb", k, m))
    # 수준 k-1 판
    for m in range(k, min(3*k, NMAX)+1):
        rhs = sum(pi_(m, t)/t*(s(t-1, k)+(k-1)*c(t-1, k-1))*(s(m-t, k-1) if m >= 2*k else 1) for t in range(k, m+1))
        if m <= 2*k-1:
            if c(m, k-1) != rhs: bad.append(("8.2' eq", k, m))
        elif c(m, k-1) < rhs: bad.append(("8.2' lb", k, m))
    # (8.10) 가장 낮은 위반, (8.9) 탈출 하계, (8.11)(가) 사전 상계, (8.8) Jensen : y=k, k+1<=N<=2k+1
    y = k
    for N in range(y+1, 2*y+2):
        theta = lambda m: (N+1-m)*pi_(N, m)
        lhs = 1-s(N, y)
        rhs = sum(theta(m)*Fraction(m-y, m)*s(m-1, y) for m in range(y+1, N+1))
        if lhs != rhs: bad.append(("8.10", k, N))
        km = sum(pi_(N, m)*Fraction(y, m) for m in range(y+1, N+1))
        if not (s(N, y) >= pi0(N, y)/(1-km) >= pi0(N, y)/(1-Fraction(y, N)+Fraction(y, N)*pi0(N, y))): bad.append(("8.9", k, N))
        B = sum(theta(m)*Fraction(m-y, m) for m in range(y+1, N+1))
        if not s(N, y) <= 1/(1+B): bad.append(("prop-U", k, N))
        EA = sum(j*theta(y+j) for j in range(1, N-y+1))
        if not mpf(s(N, y).numerator)/s(N, y).denominator >= exp(-mpf(EA.numerator)/EA.denominator/y): bad.append(("8.8", k, N))
    # old-6-30: k<=N<=2k-1
    for N in range(k, 2*k):
        ratio = s(N, k-1)/s(N, k)
        if ratio < Fraction(k-1, k)**(N-k+1): bad.append(("6.30가", k, N))
        mx = max(1/(k*pi0(Np, k-1)) for Np in range(k, N+1))
        if ratio < 1-mx: bad.append(("6.30나", k, N))
        if N <= 2*k-2:
            bnd = 1 - exp(mpf(7)/6)*mpf(N)**mpf(1.5)/(4*C*k*(2*k-1-N))
            if mpf(ratio.numerator)/ratio.denominator < bnd: bad.append(("6.30다", k, N))
    # old-6-31 (마): N/2<j<=N, pi0_N(j)-pi0_{N+1}(j) <= pi_N(j)  (N+1<=2j+1 필요)
    for N in range(2, 2*k):
        for j in range(N//2+1, N+1):
            if N+1 <= 2*j+1 and pi0(N, j)-pi0(N+1, j) > pi_(N, j): bad.append(("6.31마", N, j))
    # old-6-32: k+1<=t<=2k+1
    def sT(t, y): return Fraction(min(t, y), t)*s(t-1, y)
    for t in range(k+1, 2*k+2):
        ecap = sT(t, k+1)-sT(t, k); esize = sT(t, k)-sT(t+1, k)
        if ecap < esize/2: bad.append(("6.32", k, t))
        if ecap != Fraction(1, t)*(s(t-1, k+1)+k*c(t-1, k)): bad.append(("ecap식", k, t))
    # (8.4)/(8.5): R_q = k c_{k+q}(k)
    for q in range(1, k+2):
        R = lambda qq: k*c(k+qq, k) if qq >= 1 else 0
        rhs = sum(pi_(k+q, k+j)*Fraction(k, k+j)*(s(k+j-1, k+1)+R(j-1)) for j in range(1, q+1))
        if R(q) != rhs: bad.append(("8.4", k, q))
        # (8.5) 하계 (mpf)
        rhs5 = mpf(k)/(k+q)*sum(Bor(j)*(mpf(s(k+q-j, k+1).numerator)/s(k+q-j, k+1).denominator + mpf(R(q-j).numerator)/R(q-j).denominator if q-j >= 1 else mpf(s(k+q-j, k+1).numerator)/s(k+q-j, k+1).denominator) for j in range(1, q+1))
        if mpf(R(q).numerator)/R(q).denominator < rhs5*(1-mpf('1e-30')): bad.append(("8.5", k, q))
print("정확 항등식 위반:", bad if bad else "없음")
# (8.3) dup>=0 와 극한: k 고정, q 고정, k c_{k+q}(k) -> Psi(q) 경향 확인
for q in [1, 2, 3]:
    print("q", q, "k c_{k+q}(k) for k=5,10,19:", [mp.nstr(mpf((k*c(k+q, k)).numerator)/(k*c(k+q, k)).denominator, 8) for k in [5, 10, 19]], " Psi(q)=", mp.nstr(Psi(q), 8))
# old-6-30 (나) 증명의 재귀 e_N 식 직접 확인
k = 6
for N in range(k, 2*k):
    eN = 1-s(N, k-1)/s(N, k)
    xs = {t: Fraction(comb(N, t)*k*Aml(t-1, k-1)*p(N-t), Aml(N, k-1)) for t in range(k, N+1)}
    rhs = sum(xs[t]*(1-Fraction(k-1, k)*(1-(1-s(t-1, k-1)/s(t-1, k)))) for t in range(k, N+1))
    assert eN == rhs, ("eN", N)
    assert sum(xs.values()) == 1-Fraction(p(N), 1)*pi0(N, k-1)/Aml(N, k-1)
print("old-6-30(나) 재귀식 등식: OK")
# 두 나무 확률식 (다)
for Np in range(k, 2*k-1):
    cnt = Fraction(sum(comb(Np, j)*j**(j-1)*(Np-j)**(Np-j-1) for j in range(Np-k+1, k)), 2*p(Np))
    alt = sum(Bor(j)*Bor(Np-j) for j in range(Np-k+1, k))/(2*exp(1)*Bor(Np+1))
    assert abs(mpf(cnt.numerator)/cnt.denominator-alt) < mpf('1e-30'), ("two-tree", Np)
print("old-6-30(다) 두 나무 확률 등식: OK")
