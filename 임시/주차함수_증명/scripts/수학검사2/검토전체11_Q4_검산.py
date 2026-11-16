# -*- coding: utf-8 -*-
"""검토전체11 Q4: 장5B.md(5.5절)의 수치·항등식·부등식 검산.
정확 분수로 A_{n,l}, b_{n,l}, c_m(Y), s^T_t(Y), x_t(y), pi_n(m), pi^0_n(y)를 계산해
보조정리 5.19(열 재귀), 5.25(창 항 항별 상계), 정리 5.28(크기 방향 하계), 5.31(Lc 하계),
stop-lower, cor-L을 작은 범위에서 확인하고, 5.5.5·5.5.8의 상수들을 다시 센다."""
from fractions import Fraction as Fr
from math import comb, factorial, exp, sqrt, pi, log, floor, ceil
import sys

NMAX = 44
# p_n = (n+1)^(n-1)
def p(n): return (n+1)**(n-1) if n >= 1 else 1
# A_{n,l}: 지수 공식 V_l = exp(T_l), T_l' = sum min(j+1,l+1) V_j x^j/j!
def A_table(l, nmax):
    V = [Fr(0)]*(nmax+1); V[0] = Fr(1)
    for n in range(nmax):
        V[n+1] = sum(comb(n, j)*min(j+1, l+1)*V[j]*V[n-j] for j in range(n+1))
    return V
Atab = {}
def A(n, l):
    if l < 0: return Fr(0)
    if n == 0: return Fr(1)
    if l not in Atab: Atab[l] = A_table(l, NMAX)
    return Atab[l][n]
def b(n, l): return A(n, l) - A(n, l-1)
def c(m, Y): return b(m, Y)/p(m)
def s(m, y): return A(m, y-1)/p(m) if y >= 1 else Fr(0)
def sT(t, Y):  # 크기 t 균등 뿌리 나무가 용량 Y 아래 살아남을 확률
    if t <= Y: return Fr(1)
    return Fr(Y*A(t-1, Y-1), t**(t-1))
def x(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)
def pi_n(n, m): return Fr(comb(n, m)*m**(m-1)*p(n-m), p(n))
def Bor(m): return exp(-m)*m**(m-1)/factorial(m)
def Ren(j): return 1.0 if j == 0 else j*Bor(j)
# pi^0_n(y): 모든 나무 크기 <= y 인 숲의 수 / p_n (EGF exp(sum_{t<=y} t^{t-1}x^t/t!))
def pi0(n, y):
    F = [Fr(0)]*(n+1); F[0] = Fr(1)
    for k in range(n):
        F[k+1] = sum(comb(k, j)*(j+1)**j*F[k-j] for j in range(0, min(k, y-1)+1))
    return F[n]/p(n)

# 검증: 자명한 일치 (A_{n,n-1} = p_n)
for n in range(1, 12):
    assert A(n, n-1) == p(n), n
print("A_{n,n-1}=p_n OK")

# (1) 5.5.1 x_t(y) 식: t>=y+1 에서 x_t(y)=(1/t)[(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)], x_y(y)=-1/y
bad = 0
for y in range(2, 16):
    assert x(y, y) == Fr(-1, y)
    for t in range(y+1, min(2*y, 30)+1):
        if x(t, y) != Fr(1, t)*((y+1)*c(t-1, y) - (y-1)*c(t-1, y-1)): bad += 1
print("x_t(y) 식 불일치:", bad)

# (2) 보조정리 5.19 열 재귀
bad = 0
for n in range(3, 30):
    for y in range((n+2)//2, n):
        lhs = c(n, y) - c(n, y-1)
        rhs = sum(pi_n(n, t)*x(t, y) for t in range(y, n+1))
        if lhs != rhs: bad += 1
print("열 재귀 불일치:", bad)

# (3) 보조정리 5.25: (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)),  t/2<y<t
bad = 0; worst = 0
for y in range(2, 20):
    for t in range(y+1, 2*y):
        neg = max(-float(x(t, y)), 0.0)
        bd = Ren(t-y)*Bor(y)/(y*Bor(t))
        if neg > bd*(1+1e-12): bad += 1
        worst = max(worst, neg/bd)
print("5.25 위반:", bad, " 최대 비:", round(worst, 4))

# (4) 정리 5.28: c_{m+1}(w+1) >= (1-z_m(d)) c_m(w), m>=2, 1<=d<=m/2
def zloss(m, d):
    w = m-d
    return exp((d-1)/w)/(w+1) + 3*d/(2*(w+1)*(m+1))
bad = 0; worst = -1
for m in range(2, 36):
    for d in range(1, m//2+1):
        w = m-d
        lhs = float(c(m+1, w+1)); rhs = (1-zloss(m, d))*float(c(m, w))
        if lhs < rhs - 1e-15: bad += 1
        if float(c(m, w)) > 0:
            worst = max(worst, 1 - lhs/float(c(m, w)))  # 실제 손실률
print("5.28 위반:", bad, " 최대 실제 손실률:", round(worst, 4))

# (4b) 6.4 정리의 손실률 (m+d+2)/((w+2)(m+1)) <= z_m(d)
bad = 0
for m in range(2, 400):
    for d in range(1, m//2+1):
        w = m-d
        if (m+d+2)/((w+2)*(m+1)) > zloss(m, d) + 1e-15: bad += 1
print("손실률 비교 위반:", bad)

# (4c) cor-L: P_n(y) >= -(1+top)/y,  y>=2, y+1<=n<=2y+1
bad = 0
for y in range(2, 18):
    for n in range(y+1, 2*y+2):
        P = sum(x(t, y) for t in range(y, n+1))
        top = Fr(y*(y-1), n)*c(n-1, y-1)
        if P < -(1+top)/y: bad += 1
print("cor-L 위반:", bad)

# (5) 정리 5.31: c_{Y+q}(Y) >= Lc(Y,q), 1<=q<=Y+1
def BorT(z, D):  # Bor^{*z}(D)
    if D < z: return 0.0
    return z/D*exp(-D)*D**(D-z)/factorial(D-z)
def Lc(Y, q):
    tot = 0.0
    for z in range(1, q+1):
        for D in range(z, q+1):
            tot += z*BorT(z, D)*Bor(Y+q+1-D)/Bor(Y+q+1)*float(pi0(Y+q-D, Y))*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
bad = 0; worst = 0
for Y in range(1, 14):
    for q in range(1, Y+2):
        cv = float(c(Y+q, Y)); lc = Lc(Y, q)
        if cv < lc*(1-1e-12): bad += 1
        worst = max(worst, lc/cv)
print("5.31 위반:", bad, " Lc/c 최대:", round(worst, 4))

# (6) stop-lower 상계: pi^0_{Y+j}(Y) <= Pr(beta>j)
def Prbeta_gt(j): return 1 - sum(Bor(i) for i in range(1, j+1))
bad = 0
for Y in range(1, 16):
    for j in range(0, Y+1):
        if float(pi0(Y+j, Y)) > Prbeta_gt(j) + 1e-12: bad += 1
print("stop-lower 상계 위반:", bad)
# 하계의 핵심 식: Pr_m(G_1 = U-i) = Bor(i) (U-i)Bor(U-i)/((U-1)Bor(U)) 와 pi_m(t)=(m/t)Pr(G_1=t)
bad = 0
for m in range(2, 20):
    U = m+1
    for i in range(1, m):
        t = U-i
        PG1 = Fr(comb(m-1, t-1)*t**(t-1)*p(m-t), p(m))
        if abs(float(PG1) - Bor(i)*(U-i)*Bor(U-i)/((U-1)*Bor(U))) > 1e-12: bad += 1
        if PG1 != Fr(t, m)*pi_n(m, t): bad += 1
print("G_1 식 위반:", bad)

# (7) 보조정리 5.20 비 식: pi_n(t+1)/pi_n(t) = e^{g(t)-g(n-t)}
def g(xv): return (xv-1)*log(1+1/xv)
bad = 0
for n in range(3, 30):
    for t in range((n+2)//2, n):
        r = float(pi_n(n, t+1)/pi_n(n, t))
        if abs(r - exp(g(t)-g(n-t))) > 1e-12: bad += 1
print("5.20 비 식 위반:", bad)

# (8) 보조정리 5.24 방문 확률 vs 직접 계산 (사슬이 크기 s 를 밟을 확률, t/2<s<t): 전이 확률 곱의 합성 합
def visit(t, s):
    # 사슬 S_0=t -> ... ; 각 전이 S' -> S'' 확률 pi_{S'-1}(S'') (S''>s>t/2 보장)
    from functools import lru_cache
    @lru_cache(None)
    def f(cur):
        if cur == s: return 1.0
        if cur < s: return 0.0
        return sum(float(pi_n(cur-1, nxt))*f(nxt) for nxt in range(s, cur))
    return f(t)
bad = 0
for t in range(3, 22):
    for s in range(t//2+1, t):
        if abs(visit(t, s) - Ren(t-s)*Bor(s)/Bor(t)) > 1e-10: bad += 1
print("5.24 방문 확률 위반:", bad)

# ---------- 5.5.5 보조정리 5.30 상수 ----------
n = 50001
v1 = (2*pi)**-0.5*sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*exp(1/(12*(n+1)))
v2 = (1.5/10)**1.5
v3 = (2*pi)**-0.5*0.0581*(1+1/n)**1.5*exp(1/(12*(n+1)))
v4 = exp(-2)*((n+1)/(n-1))**1.5*exp(1/(12*(n+1)))
print("5.30:", round(v1, 6), "<=0.0133;", round(v2, 6), "<=0.0581;", round(v3, 6), "<=0.0232;", round(v4, 6), "<0.1354;", round(exp(-1)-0.1354-0.0232, 5), ">0.2")

# ---------- 5.5.2 t_0<=n, 폭 ----------
print("5.5.2:", 10*((n+1)/2)**(2/3), ">", 6*n**(2/3)+2, ";", 6*n**(2/3)+1, ">", 1+floor(0.75*(n-1)**(2/3)))
y = 25000; tt = y+1+ceil(0.75*(1.1*y)**(2/3)); print("y=25000: t-1=", tt-1, "<=1.1y", 1.1*y, "; 0.75(t-1)^{2/3}=", 0.75*(tt-1)**(2/3), "<= t-1-y=", tt-1-y)

# ---------- stop-lower 상수 ----------
print("stop-lower:", 1.5*0.95**-2.5, "<=1.706;", (0.8**-1.5-1)/0.2, "<=1.988;", 4/sqrt(2*pi), "<1.596;", "e^{1/(12U)}<=1+1/(11U) at U=25000:", exp(1/(12*25000)) <= 1+1/(11*25000))

# ---------- hover-tail: z^{3/2}(2z-3)^{-1/2} >= 2sqrt2 (z>=2) ----------
print("hover:", min(z**1.5*(2*z-3)**-0.5 for z in range(2, 2000)), ">=", 2*sqrt(2), ";", 2/sqrt(pi)*2*sqrt(2), ">1")

# ---------- scaled-integrand 상수 ----------
h0 = 0.0342; umax = sqrt(6*h0); c2 = 1/(2*(1-umax)); c3 = 1/sqrt(2)-umax/3
print("h0^3=", h0**3, ">=", 1/25000, "; umax=", umax, "; c2=", c2, "; c3=", c3, ">=0.556")
f12 = c3*12**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3); print("f(12)=", f12, ">7 ;  f'(12)=", 1.5*c3*sqrt(12)-1-1/12)
O25 = 1/25000**2*sqrt(12/pi)*25000**(1/3)*sqrt(2/25000)*25001; print("O(25000)=", O25)
# 6Y^{2/3}<=Y/4 at Y=13824 ; q_max<=Y+1
print("6*13824^{2/3}=", 6*13824**(2/3), "<= 3456 =", 13824/4)

# ---------- band-inequality 조건 ----------
print("band: 0.4n/3=", 0.4*n/3, ">= 6(2n/3)^{2/3}+1=", 6*(2*n/3)**(2/3)+1, "; 0.75(1.1*2n/3)^{2/3}+1=", 0.75*(1.1*2*n/3)**(2/3)+1, "<=0.7n/3=", 0.7*n/3)
lb = 2/3; print("c4 분모 도함수 at lam_b=2/3:", 0.4*(1-lb)-4*lb**(2/3)*n**(-1/3))

# ---------- right-part 상수 ----------
y0 = 33334
print("right: 10*y0^{2/3}-1=", 10*y0**(2/3)-1, "; 0.2*10357-7.3=", 0.2*10357-7.3)
hv = lambda ch: ch**-0.5*(2/sqrt(pi)*(1+1/ch)+1/sqrt(pi))
print("hv(2064)*sqrt(2064)=", hv(2064)*sqrt(2064), "<=1.6932")
t = y0**(1/3); eh = 1.6932*(t/10+1)/sqrt(2*t*t-7.5); print("eps_hov=", eh, "<=0.1573")
print("sqrt(2/pi)/sqrt(2064)=", sqrt(2/pi)/sqrt(2064), "<=0.01757")
print("0.75*1.1^{2/3}=", 0.75*1.1**(2/3), "<=0.7993 ; (n+1)/y<=", 1.5+1/y0)
k1 = (2*pi)**-0.5*(1.50003/0.9199)**1.5; print("pi_n(t0-1) 상수=", k1, "*e^{1/(12*50002)}=", k1*exp(1/(12*50002)), "<=0.8308")
print("0.3*0.8308=", 0.3*0.8308, "<=0.24924 ; /sqrt(10358)=", 0.24924/sqrt(10358), "<=0.00245 ;", 1-0.01757-0.00245, ">=0.9799")
r = 10357; rho0 = 0.07993*(r+1)+1
print("(r+1)/(r-rho0)=", (r+1)/(r-rho0), "<=1.0872 ; (0.7993y^{2/3}+2)^{1.5}/y=", (0.7993*y0**(2/3)+2)**1.5/y0, "<=0.7172")
print("eps0<=", 1.5*rho0/(r+1-rho0), "<=0.1305 ; (1+rho/y)^{1.5}=", (1+(0.7993*y0**(2/3)+1)/y0)**1.5, "<=1.0376")
W = (2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008); print("(r+1)W/y<=", W, "<=0.3678")
print("c4<=", 1/156+1/(12*y0)+1/(12*50002), "; e^{-c4}=", exp(-(1/156+1/(12*y0)+1/(12*50002))), ">=0.9936")
K = 0.8427*0.71216*0.9936*1.9366-0.3678; print("0.7869 상수:", K, ">=0.7869 ;", 0.7869*2/3-1/3-2.5e-5, ">0.191")
# 2/3 경계: y>2n/3 -> y>=33335 ; 3-case: 9199 조건
print("0.00017*(r+1)>=1:", 0.00017*10358)
