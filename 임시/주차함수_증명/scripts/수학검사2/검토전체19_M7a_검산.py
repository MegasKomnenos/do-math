# M7a 검산: 7.4-7.5절의 항등식·수치를 작은 k에서 정확 유리수로, 큰 k에서 배정밀도로 다시 센다.
from fractions import Fraction as Fr
from math import comb, factorial, exp, log, sqrt, pi
from functools import lru_cache
import sys
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j-1)*min(j, l+1)*A(j-1, l)*A(n-j, l) for j in range(1, n+1))
def p(n): return (n+1)**(n-1) if n > 0 else 1

# 1: (7.10)
P("== (7.10) check")
bad = 0
for k in range(2, 8):
    def s(m): return Fr(A(m, k-1), p(m))
    for q in range(2, k+3):
        m = k+q-1
        lhs = 1-s(m)
        rhs = Fr(0)
        for j in range(k+1, k+q):
            pij = Fr(comb(m, j)*j**(j-1)*p(m-j), p(m))
            rhs += pij*(Fr(j-k, j)+Fr(k, j)*(1-s(j-1)))
        if lhs != rhs: bad += 1; P("  FAIL k,q", k, q, float(lhs), float(rhs))
P("  (7.10) failures:", bad)
bad = 0
for k in range(2, 12):
    def s(m): return Fr(A(m, k-1), p(m))
    for q in range(1, k+3):
        if 1-s(k+q-1) > Fr(q*(q-1), 2*(k+1)): bad += 1
P("  (la) pi^sharp failures:", bad)

# 2: (7.13), fold-A, fold-R, fold-L1, fold-T
P("== (7.13)/fold check")
bad = 0
for k in range(2, 6):
    def cl_p(m): return Fr(A(m, k)-A(m, k-1), A(m, k-1))
    def cl_m(m): return Fr(A(m, k-1)-A(m, k-2), A(m, k-1))
    def mu(m): return Fr(A(m, k)-2*A(m, k-1)+A(m, k-2), A(m, k-1))
    def Pk(m, j): return Fr(min(j, k)*comb(m-1, j-1)*A(j-1, k-1)*A(m-j, k-1), A(m, k-1))
    def chi(m, j):
        I = 1 if j > k else 0
        v = Fr(0)
        if j == k: v -= Fr(1, k)*(1-cl_m(m-k))
        if j > k: v += Fr(1, k)*(cl_p(j-1)+cl_m(j-1)+cl_p(m-j)+cl_m(m-j))
        v += (1+Fr(I, k))*cl_p(j-1)*cl_p(m-j)+(1-Fr(I, k))*cl_m(j-1)*cl_m(m-j)
        return v
    def src(m): return sum(Pk(m, j)*chi(m, j) for j in range(1, m+1))
    for m in range(1, 3*k+3):
        rhs = src(m)+sum(Pk(m, j)*(mu(j-1)+mu(m-j)) for j in range(1, m+1))
        if mu(m) != rhs: bad += 1; P("  FAIL (7.13)", k, m)
    def a(m): return Fr(A(m, k-1), factorial(m))
    def ap(m): return Fr(A(m, k), factorial(m))
    def am(m): return Fr(A(m, k-2), factorial(m))
    for n in range(k, 3*k+3):
        thr = -a(k-1)*am(n-k)
        heavy = sum(a(n-1-m)*(ap(m)-am(m))*(1+(1 if n-1-m >= k else 0)) for m in range(k, n))
        quad = sum(min(j, k+1)*(ap(j-1)-a(j-1))*(ap(n-j)-a(n-j))+min(j, k-1)*(a(j-1)-am(j-1))*(a(n-j)-am(n-j)) for j in range(1, n+1))
        lhs = n*a(n)*src(n)
        if lhs != thr+heavy+quad: bad += 1; P("  FAIL fold-A", k, n)
        if n >= 2*k+1:
            nu = n-2*k
            for l in range(0, k-1):
                B = n-1-k-l
                def sib(q): return a(n-1-k-q)
                lhsR = sum(sib(q)*(ap(k+q)-am(k+q)) for q in range(nu-1, B+1))
                ed1 = a(k)*ap(n-1-k); ed2 = a(k-1)*ap(n-k)
                up = a(l+1)*am(n-2-l)+a(l)*am(n-1-l)
                inn = [sib(q+1)*ap(k+q+1)-sib(q-1)*am(k+q-1) for q in range(nu, B)]
                if lhsR != ed1+ed2+sum(inn)-up: bad += 1; P("  FAIL fold-R", k, n, l)
                if k >= 3 and lhs < ed1+a(k-1)*(ap(n-k)-am(n-k))-up: bad += 1; P("  FAIL fold-L1", k, n, l)
                if any(v < 0 for v in inn): bad += 1; P("  FAIL fold-T", k, n, l)
P("  (7.13)/fold failures:", bad)

# 3: Hermite
P("== Hermite check")
def He_list(N, y, n):
    Nn = n+y+1; H = [Fr(1), Fr(Nn)]
    for j in range(1, N): H.append(Nn*H[j]-j*y*H[j-1])
    return H
def Mratio(i, y, n):
    H = He_list(n+1, y, n)
    def c(i): return sum(comb(i+1, r)*(-1)**r*H[n-r]/factorial(n-r) for r in range(0, i+2) if n-r >= 0)
    return c(i)/c(0), H
bad = 0
for k in [7, 9, 12]:
    for nu in [1, 2, 5]:
        for y in [Fr(k), Fr(k)-Fr(1, 2), Fr(k-1)]:
            n = 2*k+nu
            r2, H = Mratio(2, y, n); r4, _ = Mratio(4, y, n)
            d = H[n]/H[n-1]-n
            if y == k:
                U2 = 1+Fr(2*nu+2, k)+Fr(nu*(nu+1), k*k); V2 = 4+Fr(4*nu+2, k)+Fr(nu*(nu+1), k*k)
                U4 = 1+Fr(4*nu+16, k)+Fr(6*nu*nu+30*nu+18, k**2)+Fr(4*nu**3+17*nu**2+15*nu+2, k**3)+Fr(nu*(nu+1)**3, k**4)
                V4 = 4+Fr(12*nu+38, k)+Fr(13*nu**2+49*nu+22, k**2)+Fr(6*nu**3+21*nu**2+17*nu+2, k**3)+Fr(nu*(nu+1)**3, k**4)
                if r2 != U2-V2/d or r4 != U4-V4/d: bad += 1; P("  FAIL U/V", k, nu)
            gen = 1-Fr(2*n)/y+Fr(n*(n+1))/y**2-Fr(n*(n+1))/(y**2*d)
            if r2 != gen: bad += 1; P("  FAIL (ma) formula", k, nu, y)
P("  U/V and (ma) failures:", bad)
k = 10000; nu = 1; n = 2*k+nu
H = He_list(n+1, Fr(k), n); d = H[n]/H[n-1]-n
approx = Fr(4)-Fr(26+4*nu, k)+Fr(506+97*nu+5*nu**2, k*k)
P("  d(k=1e4,nu=1)=", float(d), " 4-(26+4nu)/k+H2/k^2=", float(approx), " (d-approx)*k^3=", float((d-approx)*k**3))
P("  4-(26+4nu)/k <= d < 4 :", Fr(4)-Fr(30, k) <= d < 4)
import mpmath as mp
mp.mp.dps = 40
def mpf(fr): return mp.mpf(fr.numerator)/mp.mpf(fr.denominator)
lnHe = mp.log(mpf(H[n]))
M0 = mp.exp(-mp.mpf(k)/2+lnHe-(n-1)*mp.log(n+1))*mpf(d)/(n+mpf(d))
P("  M0=", mp.nstr(M0, 10), " lower bound=", mp.nstr(4*mp.sqrt(2)*(1-(23.75+2.5*nu)/k), 10))
r2f = mpf(Mratio(2, Fr(k), n)[0]); r4f = mpf(Mratio(4, Fr(k), n)[0])
P("  k*M2/M0=", mp.nstr(k*r2f, 8), " g_k=2-kM2/M0=", mp.nstr(2-k*r2f, 8), " M4/M0*k^2=", mp.nstr(r4f*k*k, 8))

# 4: pair check
P("== pair check")
def Bor(m): return exp(-m+(m-1)*log(m)-sum(log(i) for i in range(1, m+1)))
k = 10000
def exbar(q):
    ps = q*(q-1)/(2*(k+1)); return q+(k+q)*ps/(1-ps)
cnt = 0; mn = (9, None)
for q in range(1, 50):
    for qp in range(q, 50):
        for j in range(0, 51-q-qp):
            cnt += 1
            v = 1-j/k*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if v < mn[0]: mn = (v, (q, qp, j))
P("  count", cnt, "min", mn)
def nuP(K1, M, tf):
    def exh(q):
        if q == 1: return 1.0
        nh = tf*q**1.5/K1; return q+(K1+q)*nh/(1-nh)
    nu = 1
    while True:
        ok = True
        for q in range(1, nu):
            for qp in range(q, nu-q+1):
                j = nu-q-qp
                if q > M or qp > M: ok = False; break
                lb = 1-j/K1*(exh(q)+exh(qp))-(exh(q)*(qp-1)+exh(qp)*(q-1))/(2*K1)
                if lb <= 0: ok = False; break
            if not ok: break
        if not ok: return nu-1
        nu += 1
for K1, M, tf, exp_ in [(12000, 120, 0.54, 93), (15000, 120, 0.54, 102), (20000, 120, 0.54, 115), (10**5, 300, 0.522, 228), (10**6, 700, 0.519, 590)]:
    P("  nu_P", K1, "=", nuP(K1, M, tf), "expected", exp_)
def F712(K1, M, tf):
    ke = 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    mnv = 1e9
    for q in range(2, M+1):
        v = tf*q**1.5-exp(ke)*sum(Bor(s+1)*((q-1-s)+tf*(q-1-s)**1.5) for s in range(0, q-1))
        mnv = min(mnv, v/(tf*q**1.5))
    return mnv, ke
for t in [(10**4, 120, 0.54), (2*10**4, 250, 0.593), (10**5, 300, 0.522), (10**5, 450, 0.548), (10**6, 700, 0.519)]:
    P("  (7.12) min rel margin", t, F712(*t))
P("  tf M^1.5:", [round(tf*M**1.5) for M, tf in [(700, 0.519), (450, 0.548), (120, 0.54), (250, 0.593), (300, 0.522)]])

# 5: misc
P("== misc")
P("  20507/841^1.5=", 20507/841**1.5, " 73032/2000^1.5=", 73032/2000**1.5)
P("  (ga) count", sum(2*k-19960 for k in range(9981, 10000))+1100*40, " (na)+(da) count", sum(2*k-19898 for k in range(9950, 9980))+2020*62+74000)
P("  polar-PD: 2e^{-5.3146*0.6996}=", 2*exp(-5.3146*0.6996), " 0.3^1.5/2=", 0.3**1.5/2, " 0.0821e^{-3/25233}=", 0.0821*exp(-3/25233), " lp needed=", log(2/0.0820)/0.6996, " 2002^{4/3}=", 2002**(4/3), " 0.7*2001/2002=", 0.7*2001/2002)
P("  vertical-nu: 1.50005^1.5 e^{1/240000}=", 1.50005**1.5*exp(1/240000), " 1.84*2/sqrt(pi)=", 1.84*2/sqrt(pi), " 2.08/sqrt(2pi)=", 2.08/sqrt(2*pi))
P("  hermite: 2e7*3.07/9^4=", 2e7*3.07/9**4, " 3+601/1e4=", 3+601/1e4)
P("  (1,33,16) rhs=", 1-16/10000*(exbar(1)+exbar(33))-(exbar(1)*32)/(20000))
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
