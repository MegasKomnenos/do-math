# -*- coding: utf-8 -*-
"""검토전체19 M4: 장5B(5.5절) 검산.
(1) n<=7 주차함수 전수로 b_{n,l}을 세어 2-13 재귀(첫 층)와 보조정리 5-19·5-27, 명제 5-22의 Abel 항등식을 확인.
(2) 첫 층 생존 확률의 정확 유리수 재귀로 정리 5-28, 따름정리 cor-L, 보조정리 5-25·stop-lower, 정리 5-31(Lc)을 작은 범위에서 확인.
(3) 5.5.5·5.5.8의 상수 확인.
(4) Y=300에서 정리 5-33 꼴의 부등식을 부동소수점으로 확인(범위 조건 Y>=25000은 무시; 구조 확인용).
"""
import itertools, math, sys
from fractions import Fraction as Fr
from math import comb, exp, log, sqrt, pi, erfc, floor, ceil

out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s)

# ---------- (1) 전수 ----------
def park_disp(pref):
    n = len(pref); spots = [False]*n; M = 0
    for p in pref:
        q = p
        while q < n and spots[q]: q += 1
        if q >= n: return None
        spots[q] = True; M = max(M, q-p)
    return M

def brute_b(n):
    b = [0]*n
    for pref in itertools.product(range(n), repeat=n):
        M = park_disp(pref)
        if M is not None: b[M] += 1
    return b

pn = lambda n: 1 if n == 0 else (n+1)**(n-1)
Bor = lambda m: Fr(m**(m-1), math.factorial(m)) * Fr(1)  # e^{-m} 생략: 비에서만 쓴다 -> 아래는 pi_n 직접 정의
def pi_n(n, t):  # 가장 큰 나무 핵(대수적 정의)
    return Fr(comb(n, t) * t**(t-1) * pn(n-t), pn(n))

BR = {}
for n in range(1, 8):
    BR[n] = brute_b(n)
    assert sum(BR[n]) == pn(n)
P("[1] 전수 b_{n,l} n=1..7 합 = p_n 확인")

def s_brute(m, y):  # A_{m,y-1}/p_m
    if m == 0: return Fr(1)
    if y <= 0: return Fr(0)
    return Fr(sum(BR[m][:min(y, m)]), pn(m))
def c_brute(m, Y): return s_brute(m, Y+1) - s_brute(m, Y)

# 2-13 둘째 식 확인: s_n(y)=pi0_n(y)+sum_{t>y} pi_n(t) (y/t) s_{t-1}(y), n<=2y+1, pi0 = 1 - sum_{t>y} pi_n(t)
ok = True
for n in range(2, 8):
    for y in range((n-1+1)//2, n+1):
        if n > 2*y+1: continue
        pi0 = 1 - sum(pi_n(n, t) for t in range(y+1, n+1))
        rhs = pi0 + sum(pi_n(n, t)*Fr(y, t)*s_brute(t-1, y) for t in range(y+1, n+1))
        if rhs != s_brute(n, y): ok = False; P("  2-13 불일치", n, y, rhs, s_brute(n, y))
P("[1] 2-13 둘째 식(첫 층) 전수 대조:", "OK" if ok else "FAIL")

def sT(t, Y):  # 나무 생존 확률 (전수 기반 s)
    return Fr(1) if t <= Y else Fr(Y, t)*s_brute(t-1, Y)
def x_t(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)

ok = True
for n in range(3, 8):
    for y in range((n+1+1)//2, n):
        if 2*y < n+1: continue
        lhs = c_brute(n, y) - c_brute(n, y-1)
        rhs = sum(pi_n(n, t)*x_t(t, y) for t in range(y, n+1))
        if lhs != rhs: ok = False; P("  5-19 불일치", n, y)
        # 5-27
        Pn = sum(x_t(t, y) for t in range(y, n+1))
        rhs27 = -Fr(1, y) + sum(((y+1)*c_brute(m, y) - (y-1)*c_brute(m, y-1))/Fr(m+1) for m in range(y, n))
        if Pn != rhs27: ok = False; P("  5-27 불일치", n, y)
        # x_y(y) = -1/y
        if x_t(y, y) != Fr(-1, y): ok = False; P("  x_y(y) 불일치", n, y)
        # Abel 재배열 항등식
        tail = lambda s: sum(x_t(t, y) for t in range(s+1, n+1))
        rhsA = pi_n(n, y)*Pn + sum((pi_n(n, s+1)-pi_n(n, s))*tail(s) for s in range(y, n))
        if lhs != rhsA: ok = False; P("  Abel 불일치", n, y)
P("[1] 5-19, 5-27, x_y(y)=-1/y, Abel 재배열 항등식 전수 대조:", "OK" if ok else "FAIL")

# ---------- (2) 첫 층 정확 재귀 ----------
NMAX = 90
S = {}  # S[(n,y)] for y >= (n-1)/2
def s_rec(n, y):
    if y >= n: return Fr(1)
    if y <= 0: return Fr(0)
    key = (n, y)
    if key in S: return S[key]
    assert 2*y >= n-1, (n, y)
    pi0 = 1 - sum(pi_n(n, t) for t in range(y+1, n+1))
    v = pi0 + sum(pi_n(n, t)*Fr(y, t)*s_rec(t-1, y) for t in range(y+1, n+1))
    S[key] = v; return v
def c_rec(m, Y): return s_rec(m, Y+1) - s_rec(m, Y)
def pi0_rec(n, y):
    if y >= n: return Fr(1)
    return 1 - sum(pi_n(n, t) for t in range(y+1, n+1))

# 전수와 재귀 대조
ok = all(s_rec(n, y) == s_brute(n, y) for n in range(1, 8) for y in range((n+1)//2, n+1))
P("[2] 재귀 vs 전수 (n<=7):", "OK" if ok else "FAIL")

# 정리 5-28
bad = 0; worst = None
for m in range(2, 61):
    for d in range(1, m//2+1):
        w = m-d
        lhs = c_rec(m+1, w+1); rhs = c_rec(m, w)
        z = exp((d-1)/w)/(w+1) + 3*d/(2*(w+1)*(m+1))
        if float(lhs) < (1-z)*float(rhs) - 1e-15: bad += 1
        if rhs > 0:
            loss = 1 - float(lhs/rhs)
            if worst is None or loss - z > worst[0]: worst = (loss-z, m, d, loss, z)
P("[2] 5-28 (m<=60, 1<=d<=m/2): 위반", bad, "; 최대(실손실-z):", worst)

# cor-L: P_n(y) >= -(1+top)/y ; diag-first-layer (6.31)
def xt_rec(t, y):
    sT_ = lambda t, Y: Fr(1) if t <= Y else Fr(Y, t)*s_rec(t-1, Y)
    return sT_(t, y+1) - 2*sT_(t, y) + sT_(t, y-1)
bad = 0; bad31 = 0
for y in range(2, 40):
    for n in range(y+1, 2*y+1):  # n=2y+1은 c_{2y}(y-1)이 첫 층 밖이라 뺀다
        Pn = sum(xt_rec(t, y) for t in range(y, n+1))
        top = Fr(y*(y-1), n)*c_rec(n-1, y-1)
        if Pn < -(1+top)/y: bad += 1
for m in range(2, 50):
    for d in range(1, (m+1)//2+1):
        if m < max(2, 2*d-1): continue
        w = m-d
        if not ((w+2)*(m+1)*c_rec(m+1, w+1) > w*(m+2)*c_rec(m, w)): bad31 += 1
P("[2] cor-L (y<40) 위반:", bad, "; (6.31) (m<50) 위반:", bad31)

# 5-25 항별 상계: (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)), Bor(m)=e^{-m}m^{m-1}/m!
def Borf(m): return exp(-m + (m-1)*log(m) - math.lgamma(m+1))
bad = 0
for y in range(3, 40):
    for t in range(y+1, 2*y):
        xm = max(0.0, -float(xt_rec(t, y)))
        bound = (t-y)*Borf(t-y)*Borf(y)/(y*Borf(t))
        if xm > bound*(1+1e-12): bad += 1
P("[2] 5-25 항별 상계 (y<40, y<t<2y) 위반:", bad)

# stop-lower: pi0_{Y+j}(Y) <= Pr(beta>j)
bad = 0
for Y in range(1, 40):
    for j in range(0, Y+1):
        lhs = float(pi0_rec(Y+j, Y)); rhs = 1 - sum(Borf(i) for i in range(1, j+1))
        if lhs > rhs + 1e-12: bad += 1
P("[2] stop-lower 상계 (Y<40, j<=Y) 위반:", bad)

# 정리 5-31: c_{Y+q}(Y) >= Lc(Y,q)
def BT(z, D):  # Borel–Tanner
    if D < z: return 0.0
    return exp(log(z) - log(D) - D + (D-z)*log(D) - math.lgamma(D-z+1))
def Lc(Y, q):
    tot = 0.0
    for z in range(1, q+1):
        for D in range(z, q+1):
            tot += z*BT(z, D)*Borf(Y+q+1-D)/Borf(Y+q+1)*float(pi0_rec(Y+q-D, Y))*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
bad = 0; minratio = 9
for Y in range(1, 36):
    for q in range(1, Y+2):
        cv = float(c_rec(Y+q, Y)); lc = Lc(Y, q)
        if cv < lc*(1-1e-12): bad += 1
        if lc > 0: minratio = min(minratio, cv/lc)
P("[2] 5-31 Lc 하계 (Y<36, q<=Y+1) 위반:", bad, "; 최소 c/Lc:", round(minratio, 4))

# ---------- (3) 상수 ----------
n0 = 50001
P("[3] 5-30: 0.0133 case:", (2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n0)**1.5*n0**-0.5*exp(1/(12*(n0+1))))
P("[3] 5-30: (0.15)^{1.5}=", 0.15**1.5, "; 0.0232 case:", (2*pi)**-0.5*0.15**1.5*(1+1/n0)**1.5*exp(1/(12*(n0+1))))
P("[3] 5-30: pi_n(n-1) bound:", exp(-2)*((n0+1)/(n0-1))**1.5*exp(1/(12*(n0+1))), "; e^-1-0.1354-0.0232=", exp(-1)-0.1354-0.0232)
h0 = 0.0342; P("[3] h0^3=", h0**3, ">=1/25000:", h0**3 >= 1/25000, "; 25000^{-1/3}=", 25000**(-1/3))
um = sqrt(6*h0); c2 = 1/(2*(1-um)); c3 = 1/sqrt(2)-um/3
P("[3] upsilon_max=", um, " c2=", c2, " c3=", c3)
f12 = c3*12**1.5 - 12 - log(sqrt(2)*(1+6*h0)*12/c3)
P("[3] f(12)=", f12, "; sqrt2(1+6h0)12/c3=", sqrt(2)*(1+6*h0)*12/c3, "; f'(12)=", 1.5*c3*sqrt(12)-1-1/12)
O = lambda Y: Y**-2*sqrt(12/pi)*Y**(1/3)*sqrt(2/Y)*(Y+1)
P("[3] O(25000)=", O(25000))
# right-part
y0 = 33335; nmin = 50001
P("[3] right-part: 2n/3 at n=50001 =", 2*nmin/3, "; 10*33334^{2/3}-1=", 10*33334**(2/3)-1)
hv = lambda chi: chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
P("[3] hv coefficient at chi=2064:", hv(2064)*sqrt(2064), "; 0.2*10357-7.3=", 0.2*10357-7.3)
eps_hov = lambda y: 1.6932*(y**(1/3)/10+1)*(2*y**(2/3)-7.5)**-0.5
P("[3] eps_hov(33334)=", eps_hov(33334), " eps_hov(33335)=", eps_hov(33335))
P("[3] sqrt(2/pi)/sqrt(2064)=", sqrt(2/pi)/sqrt(2064), "; 0.75*1.1^{2/3}=", 0.75*1.1**(2/3))
P("[3] (2pi)^-1/2 (1.50003/0.9199)^1.5=", (2*pi)**-0.5*(1.50003/0.9199)**1.5, "; *e^{1/(12*50002)}=", (2*pi)**-0.5*(1.50003/0.9199)**1.5*exp(1/(12*50002)))
r1 = 10358
P("[3] 0.24924/sqrt(10358)=", 0.24924/sqrt(r1), "; 1-0.01757-0.00245=", 1-0.01757-0.00245)
P("[3] (r+1)/(r-wid) at r+1=10358:", r1/(0.92007*r1-2), "; (0.7993y^{2/3}+2)^{1.5}/y at y=33334:", (0.7993*33334**(2/3)+2)**1.5/33334)
P("[3] eps0 bound:", 1.5*(0.07993*r1+1)/(0.92007*r1-1), "; (1+wid/y)^1.5:", (1+(0.7993*33334**(2/3)+1)/33334)**1.5)
W = (2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008)
P("[3] (r+1)/y * W bound:", W)
c4 = 1/156+1/(12*33334)+1/(12*50002)
P("[3] e^-c4=", exp(-c4), "; 0.8427*0.71216*0.9936*1.9366-0.3678=", 0.8427*0.71216*0.9936*1.9366-0.3678)
P("[3] Psi_R at 2/3:", 0.7869*2/3-(1/3)-2.5e-5)
# band: condition 0.4(n-y)>=6y^{2/3}+1 at y=2n/3,n=50001 ; wid<=0.7(n-y)
P("[3] band: 0.4n/3=", 0.4*n0/3, " 6(2n/3)^{2/3}+1=", 6*(2*n0/3)**(2/3)+1, "; n/3 vs 10(2n/3)^{2/3}:", n0/3, 10*(2*n0/3)**(2/3))
P("[3] band: c4 denominator derivative at lb=2/3:", 0.4/3-4*(2/3)**(2/3)*n0**(-1/3))
# wid bound check: wid <= 0.75(1.1y)^{2/3}+1 for y in [25000, 60000] via definition of t0
def t0(y):
    t = y+2
    while not (y <= (t-1) - floor(0.75*(t-1)**(2/3))): t += 1
    return t
bad = 0
for y in list(range(25000, 25100)) + list(range(25000, 400000, 3571)):
    wid = t0(y)-1-y
    if wid > 0.75*(1.1*y)**(2/3)+1: bad += 1
P("[3] wid<=0.75(1.1y)^{2/3}+1 표본 위반:", bad, "; wid(25000)=", t0(25000)-1-25000, " 0.75(1.1*25000)^{2/3}+1=", 0.75*(1.1*25000)**(2/3)+1)

# ---------- (4) 5-33 구조 확인 (Y=300, float) ----------
import functools
Yt = 300; qmax = floor(6*Yt**(2/3)); chi = 10
mlo = Yt+qmax+chi+1; mhi = 2*Yt+1
sys.setrecursionlimit(10000)
sf = {}
def pif(n, t):
    return exp(math.lgamma(n+1)-math.lgamma(t+1)-math.lgamma(n-t+1) + (t-1)*log(t) + (n-t-1)*log(n-t+1) - (n-1)*log(n+1))
def sF(n, y):
    if y >= n: return 1.0
    if y <= 0: return 0.0
    k = (n, y)
    if k in sf: return sf[k]
    v = 1 - sum(pif(n, t) for t in range(y+1, n+1)) + sum(pif(n, t)*y/t*sF(t-1, y) for t in range(y+1, n+1))
    sf[k] = v; return v
def pi0F(n, y): return 1.0 if y >= n else 1 - sum(pif(n, t) for t in range(y+1, n+1))
def LcF(Y, q):
    tot = 0.0
    for z in range(1, q+1):
        for D in range(z, q+1):
            tot += z*BT(z, D)*Borf(Y+q+1-D)/Borf(Y+q+1)*pi0F(Y+q-D, Y)*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
Lam = sum(Yt/(Yt+q+1)*LcF(Yt, q) for q in range(1, qmax+1))
# hov: Pr(R_z <= chi-1) exact-ish via convolution of Borel pmf truncated at chi-1
pmf = [0.0]+[Borf(i) for i in range(1, chi)]
def hov(rho, chi):
    dist = [1.0]+[0.0]*(chi-1); tot = 0.0; z = 0
    while True:
        pz = sum(dist); term = rho**z*pz
        tot += term
        if term < 1e-16: break
        new = [0.0]*chi
        for a, pa in enumerate(dist):
            if pa == 0: continue
            for b in range(1, chi-a): new[a+b] += pa*pmf[b]
        dist = new; z += 1
    return tot
def Vf(m, Y, chi, q): return (2*pi)**-0.5*((m+1)/((Y+1)*(m-Y)))**1.5*exp(-1/(12*(m-chi-Y-q+1))-1/(12*(Y+1)))
bad = 0; mr = 9
for m in range(mlo, mhi+1):
    cm = sF(m, Yt+1) - sF(m, Yt)
    lb = hov(Yt/(m+1), chi)*Vf(m, Yt, chi, qmax)*Lam
    if cm < lb: bad += 1
    mr = min(mr, cm/lb)
P("[4] 5-33 Y=300, chi=10, m in [%d,%d]: 위반 %d, 최소 c/하계 %.4f, Lambda_w(300)=%.4f" % (mlo, mhi, bad, mr, Lam))

open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체19_M4_검산_out.txt", "w", encoding="utf-8").write("\n".join(out)+"\n")
print("\n".join(out))
