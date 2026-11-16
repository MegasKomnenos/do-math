# -*- coding: utf-8 -*-
"""심사 A5 — 해석 부등식의 수치 재계산 (mpmath 30자리).
S3: 10.21 증명 7단계를 y>=4000 (q>=277) 에서 다시 셈; 1.15(2k+1)<3k.
S5: F3의 지수 손실 max over m>=2001, 14<=d<=m^{2/3}/2 (Psi 정확).
S4: 9.7 하계 >= Psi(d)/(2m) 가 성립하는 m 문턱.
S11: eps_N=g(2k)-g(k) 하계, hz>=1-e^{-eps} >= (1/k)(3/4-11/(6k)) >= 1/(2k).
S12: 6.1 증명의 (6.8) 을 C=3.2, k>=2000 에서; V_k(k) 하계 2001..3130; (6.50) at k=2001; critical-front 여유.
S1: max_d Bor(k+d)U_d 의 자리와 (2-1/k)sqrt(k/(k+1))<2.
E6/F4 나머지 공식 at k=3131.
실행: python -I 심사_A5_3_analytic.py > 심사_A5_3_analytic_out.txt
"""
from mpmath import mp, mpf, exp, log, sqrt, pi, floor, ceil, factorial, e as E, nsum, inf
mp.dps = 30

def Bor(n): n = mpf(n); return exp(-n)*n**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
_PSI = [mpf(0)]
def Psi(d):
    d = int(d)
    while len(_PSI) <= d:
        _PSI.append(_PSI[-1] + Ren(len(_PSI)))
    return _PSI[d]
def g(x): x = mpf(x); return (x-1)*log(1+1/x)

print("# S3: 10.21 증명, y>=4000")
y = 4000
a_ = floor((mpf('1.15')*y)**(mpf(2)/3)); print("  a'=floor((1.15y)^{2/3}) =", a_, " → q>=", a_+1)
c2 = 2/sqrt(2*pi)
def coef(up, q):  # 7단계 E 의 계수 2c[1/4(1-1/(2q))^{-3/2} + (1+u+u^2)(1-u)^{-1/2}(1+u)^{-3/2}]
    return c2*(mpf(1)/4*(1-mpf(1)/(2*q))**(-mpf(3)/2) + (1+up+up**2)*(1-up)**(-mpf(1)/2)*(1+up)**(-mpf(3)/2))
q = 277
for lo, hi, Fmax, Ecoef in ((0, '0.9', 2/sqrt(pi), '2.82'), ('0.9', '0.99', None, '9.3'), ('0.99', '0.9999', None, '85')):
    up = mpf(hi)
    cE = coef(up, q)
    if Fmax is None:
        Fmax = c2*(1+2*mpf(lo)**2)*sqrt(1-mpf(lo)**2)  # F 는 u>=1/sqrt2 에서 감소 → 구간 왼끝
    print("  u in (%s,%s]: E계수=%.5f (원고 %s) | F<=%.5f | F+E/277 = %.6f" % (lo, hi, cE, Ecoef, Fmax, Fmax+cE/q))
print("  u>0.9999 직접: 0.182+7.3*0.0003 =", mpf('0.182')+mpf('7.3')*mpf('0.0003'), "; q/50-1/2>=0.77q/50 needs q>=", mpf(25)/mpf('0.23'))
print("  1.15(2k+1)<3k iff k>", mpf('1.15')/(3-2.3))

print("\n# S5: 지수 손실 x(m,d)=(d/(m-d)) * d (1-d/m)^{-3/2} e^{1/(12(m+1))} / Psi(d); 2e^{-x}>=1 iff x<=log2=%.6f" % log(2))
def xloss(m, d):
    delta = mpf(d)/m
    return delta/(1-delta)*d*(1-delta)**(-mpf(3)/2)*exp(mpf(1)/(12*(m+1)))/Psi(d)
def xloss653(m, d):  # 6.53 의 꼴: (d-1)((m+1)/(m-d+1))^{3/2} e^{1/(12(m+1))} * (-log(1-d/m)) / Psi(d)  (log w >= -d/k 대신 정확 log)
    k = m-d
    return (d-1)*((mpf(m)+1)/(k+1))**(mpf(3)/2)*exp(mpf(1)/(12*(m+1)))*(-log(1-mpf(d)/m))/Psi(d)
best = (0, None); best2 = (0, None)
for m in list(range(2001, 2101)) + list(range(2101, 4001, 20)) + list(range(4001, 40001, 250)) + [10**5, 10**6]:
    dmax = int(floor(mpf(m)**(mpf(2)/3)/2))
    for d in range(14, dmax+1):
        x = xloss(m, d)
        if x > best[0]: best = (x, (m, d))
        x2 = xloss653(m, d)
        if x2 > best2[0]: best2 = (x2, (m, d))
print("  max x (F3꼴) = %.6f at (m,d)=%s  (F3: .663774)" % best)
print("  max x (6.53꼴, 정확 log) = %.6f at %s" % best2)
# d<14 도 포함하면?
best3 = (0, None)
for m in list(range(2001, 2101)) + list(range(2101, 4001, 20)) + list(range(4001, 40001, 250)):
    for d in range(1, 14):
        x = xloss(m, d)
        if x > best3[0]: best3 = (x, (m, d))
print("  1<=d<=13: max x = %.6f at %s" % best3)
# 소비 범위 m>=3145 (k>=3131, d>=14)
best4 = (0, None)
for m in list(range(3145, 3300)) + list(range(3300, 6000, 25)) + list(range(6000, 60000, 500)):
    dmax = int(floor(mpf(m)**(mpf(2)/3)/2))
    for d in range(14, dmax+1):
        x = xloss(m, d)
        if x > best4[0]: best4 = (x, (m, d))
print("  소비 범위 m>=3145: max x = %.6f at %s → 하계/(Psi/2m) 최소 = %.4f" % (best4[0], best4[1], 2*exp(-best4[0])))

print("\n# S4: 9.7 하계 Lo9(m,d) vs Psi(d)/(2m), d<=m^{2/3}/2")
def lo97(m, d):
    w = m-d; gg = ((mpf(m)+1)/(m-d+1))**(mpf(3)/2)*exp(mpf(1)/(12*(m-d+1)))
    P = Psi(d)
    return P/w*exp(-(gg*(2*pi)**(-mpf(1)/2)*(mpf(4)/3*mpf(d)**(mpf(3)/2)+2*sqrt(d)) + gg**2*(mpf(5)/8*d**2+d))/(w*P))
first_ok = None; fails = []
for m in range(4, 1201):
    dmax = int(floor(mpf(m)**(mpf(2)/3)/2))
    ok = all(lo97(m, d) >= Psi(d)/(2*m) for d in range(1, dmax+1))
    if not ok: fails.append(m)
print("  Lo9 < Psi/(2m) 가 어느 d 에서든 일어나는 m (m<=1200):", fails[:10], "...", fails[-5:], "| 개수", len(fails), "| 최대 실패 m =", max(fails) if fails else None)
ratios = []
for m in (3145, 5000, 10000, 10**5):
    dmax = int(floor(mpf(m)**(mpf(2)/3)/2))
    r = min(lo97(m, d)/(Psi(d)/(2*m)) for d in range(1, dmax+1))
    ratios.append((m, float(r)))
print("  min_d Lo9/(Psi/2m) at m =", ratios)

print("\n# S11: eps=g(2k)-g(k) 하계와 위험률")
for k in (2, 10, 100, 2001, 3131, 10**4, 10**6):
    k = mpf(k); eps = g(2*k)-g(k)
    lb = mpf(3)/(4*k)-mpf(17)/(24*k**2)
    hz = 1-exp(-eps); hzb = (mpf(1)/k)*(mpf(3)/4-mpf(11)/(6*k))
    print("  k=%-8d eps=%.3e  3/(4k)-17/(24k^2)=%.3e  eps>=하계:%s | 1-e^-eps=%.3e  (3/4-11/6k)/k=%.3e  ok:%s | >=1/(2k):%s" % (
        int(k), eps, lb, eps >= lb, hz, hzb, hz >= hzb, hz >= 1/(2*k)))
# 6.9 (6.18) 와 결합: hz >= 1-e^{-eps}(1-kappa/(N+1)), kappa>=0.307: N+1=2k, k=3131
k = mpf(3131); eps = g(2*k)-g(k)
print("  k=3131, N+1=2k: (6.18) 전체 하계 = %.4e ; 1-e^-eps 만 = %.4e ; kappa/(N+1) 만 = %.4e ; 7B의 0.14/n (n=3k+1) = %.4e" % (
    1-exp(-eps)*(1-mpf('0.307')/(2*k)), 1-exp(-eps), mpf('0.307')/(2*k), mpf('0.14')/(3*k+1)))

print("\n# S12: 6.1 증명 (6.8) 을 C=3.2 에서")
def cond68(C, k):
    C = mpf(C); k = mpf(k)
    qs = ceil((C*k)**(mpf(2)/3))
    lhs = 1-mpf('1.6')/sqrt(qs)+mpf('0.8')/qs
    rhs = 2*(mpf('0.8')*sqrt(2)/C*(1+1/(2*(qs-1))) + mpf('3.923')*C**(-mpf(4)/3)*k**(-mpf(1)/3) + mpf('1.5')/(C*sqrt(qs)))
    return qs, lhs, rhs
for C, k in ((3, 4000), (3.2, 2000), (3.2, 2700), (3.2, 1500), (3.5, 1000)):
    qs, lhs, rhs = cond68(C, k)
    print("  C=%.1f k=%d: q*=%d  좌변=%.4f  우변=%.4f  성립:%s" % (C, k, qs, lhs, rhs, lhs >= rhs))
# 작은 항 1.212, 1.203, 1.508 은 q*>=525 가정; q*=346 에서 재평가
qs = 346
print("  q*=346: 1.2(1-2/q)^{-5/2}=%.4f (<=1.212?), 1.2(1+2/q)^{1/2}=%.4f (<=1.203?), 1.5(1-1/q)^{-5/2}=%.4f (<=1.508?)" % (
    mpf('1.2')*(1-mpf(2)/qs)**(-mpf(5)/2), mpf('1.2')*(1+mpf(2)/qs)**(mpf(1)/2), mpf('1.5')*(1-mpf(1)/qs)**(-mpf(5)/2)))
def u_of(k, C): k = mpf(k); return (mpf(C)/mpf('0.35'))*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
worst = (10, None)
for k in range(2001, 3131):
    R = (3*(k-1))//2; qR = R-(k-1)
    sR = min(mpf(1), mpf('3.2')*(k-1)*mpf(qR)**(-mpf(3)/2))
    low = mpf(k-1)/(R+1)*(1-sR) - u_of(k, 3.2)
    if low < worst[0]: worst = (low, k)
print("  V_k(k) 하계 (C=3.2, u_3.2) 최소 over 2001..3130 = %.5f at k=%d  (F3: .0041)" % worst)
print("  u_3.2(2001)=%.4f, u_3(3131)=%.4f, 0.0648 e 2^{3/2}=%.4f (critical-front 가 요구하는 k c_2k(k-1) 상계)" % (u_of(2001, 3.2), u_of(3131, 3), mpf('0.0648')*E*2**(mpf(3)/2)))
# (6.50) at k=2001
def L50(k, d): return (k-1)*(E*Ren(d+1)-mpf(60)*(d+1)/(k+d))
def R50(k, d): return 2*(1+sum(E*Ren(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1, d)))
bad = [d for d in range(1, 14) if L50(2001, d) <= R50(2001, d)]
print("  (6.50) at k=2001: 깨지는 d =", bad, "| d=13: L=%.2f R=%.2f ; d=12: L=%.2f R=%.2f" % (L50(2001, 13), R50(2001, 13), L50(2001, 12), R50(2001, 12)))
bad3131 = [d for d in range(1, 15) if L50(3131, d) <= R50(3131, d)]
print("  (6.50) at k=3131: 깨지는 d(1..14) =", bad3131)

print("\n# S1: 해석 상계")
for k in (2, 3, 10, 3131):
    k = mpf(k)
    vals = [(Bor(k+d)*(k+d)*(2*k-1-d)*(2*k-d)/(2*k**2*(k-1)), int(d)) for d in range(1, int(k)+1)]
    mx = max(vals)
    print("  k=%d: argmax_d Bor(k+d)U_d = %d, 값=%.4e, (2/sqrt(2pi))k^{-3/2}=%.4e, 비=%.5f, (2-1/k)sqrt(k/(k+1))=%.5f" % (
        int(k), mx[1], mx[0], 2/sqrt(2*pi)*k**(-mpf(3)/2), mx[0]/(2/sqrt(2*pi)*k**(-mpf(3)/2)), (2-1/k)*sqrt(k/(k+1))))
# 1-U_{d+1}/U_d = (3d+2)/((2k-d)(k+d)) 확인
from fractions import Fraction as Fr
k = 37; ok = True
for d in range(1, k):
    U = lambda dd: Fr((k+dd)*(2*k-1-dd)*(2*k-dd), 2*k*k*(k-1))
    ok &= (1-U(d+1)/U(d) == Fr(3*d+2, (2*k-d)*(k+d)))
print("  1-U_{d+1}/U_d=(3d+2)/((2k-d)(k+d)) at k=37 all d:", ok)

print("\n# E6/F4: 10장 대각선 손실 해석 상계 14(1+log3k)/(5 sqrt(pi k)) + 42/(5 sqrt(3pi) k)")
for k in (3131, 4000, 6667):
    k = mpf(k)
    print("  k=%d: %.4f  (V-핵심의 경계항 하계 0.987, 현 theorem-U 상계 50.62/sqrt(k-1)=%.4f)" % (int(k), 14*(1+log(3*k))/(5*sqrt(pi*k))+42/(5*sqrt(3*pi)*k), mpf('50.62')/sqrt(k-1)))
