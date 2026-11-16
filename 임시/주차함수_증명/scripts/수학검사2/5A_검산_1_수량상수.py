# -*- coding: utf-8 -*-
"""수학 검사 2(태그 5A) 검산 1: 수량(비교 수·위치 수·격자 수)과 본문의 소수 상수.
python -I scripts/수학검사2/5A_검산_1_수량상수.py
"""
import math
from mpmath import mp, mpf, sqrt, pi, e, log, exp, zeta, cos, sin, cot, quad, inf, im, re, fabs, arg, degrees
import sympy as sp
mp.dps = 40
ok = True
def chk(name, cond, *vals):
    global ok
    ok &= bool(cond)
    print(('OK ' if cond else 'NG ') + name, *vals)

# ---- 5.1 / D.exact-n20000 / D.c50 수량 ----
def kn(n): return -(-n//2)
cnt2 = sum(kn(n)-1 for n in range(10001, 20001))
chk('둘째 조각 비교 수 74,995,000', cnt2 == 74995000, cnt2)
def pos(n): lo = -(-(n-1)//2); return max(0, n-3-lo+1)
cnt4 = sum(pos(n) for n in range(5, 20001))
chk('넷째 조각 위치 수 99,970,002', cnt4 == 99970002, cnt4)
cnt50 = sum(pos(n) for n in range(20001, 50001))
chk('C50 위치 수 524,955,000', cnt50 == 524955000, cnt50)
def pairs(n): lo = -(-(n-1)//2); return max(0, n-2-lo+1)
chk('C50 인접 쌍 524,985,000', sum(pairs(n) for n in range(20001, 50001)) == 524985000)
chk('C20 인접 쌍 99,989,998', sum(pairs(n) for n in range(5, 20001)) == 99989998)
chk('(ㅂ) 행 수 19,951', 20000-50+1 == 19951)
chk('C20 행 수 19,996', 20000-5+1 == 19996)
chk('94,192,042+5,777,960=99,970,002', 94192042+5777960 == 99970002)
chk('504,674,626+20,280,374=524,955,000', 504674626+20280374 == 524955000)
chk('504,674,626+20,310,374=524,985,000', 504674626+20310374 == 524985000)
chk('C20 쌍 감소 5,797,956 = 5,777,960 + 19,996', 5777960+19996 == 5797956)
chk('C50 쌍 감소 20,310,374 = 20,280,374 + 30,000', 20280374+30000 == 20310374)
def mfrak(n):
    best = 170; m = 171
    while m**1.5 + 9*m <= n:
        best = m; m += 1
    return best
chk('m(20001)=597', mfrak(20001) == 597, mfrak(20001))
chk('m(50001)=1160', mfrak(50001) == 1160, mfrak(50001))
chk('597^{3/2}+9*597<20001', 597**1.5+9*597 < 20001, 597**1.5+9*597)
chk('m^3<=(n-9m)^2 정수 판정과 일치(표본)', all((mfrak(n)**3 <= (n-9*mfrak(n))**2) and ((mfrak(n)+1)**3 > (n-9*(mfrak(n)+1))**2) for n in [20001, 25000, 33333, 50001, 100000]))
chk('14,365 = sum_{r=2}^{170}(r-1)', sum(r-1 for r in range(2,171)) == 14365)
chk('780 = sum_{r=2}^{40}(r-1)', sum(r-1 for r in range(2,41)) == 780)
chk('9,829 = 9999-171+1', 9999-171+1 == 9829)
chk('4935 = 21x235', 21*235 == 4935 and math.ceil(0.041/0.002) == 21 and round(0.47/0.002) == 235)
chk('19,270 = 82x235', 82*235 == 19270 and round(0.041/0.0005) == 82)
chk('10,500 = 70x150 (1/sqrt833=%.5f -> 70칸)' % (1/math.sqrt(833)), 70*150 == 10500 and math.ceil((1/math.sqrt(833))/0.0005) == 70)
chk('12,900 = 86x150 (1/sqrt2164=%.5f -> 86칸)' % (1/math.sqrt(2164)), 86*150 == 12900 and math.ceil((1/math.sqrt(2164))/0.00025) == 86)
chk('6,000 = 40x150', 40*150 == 6000 and math.ceil(0.01/0.00025) == 40)
chk('둘째 조각 r>=966: 30001.5^{2/3}', math.ceil(30001.5**(2/3)) == 966, 30001.5**(2/3))
chk('(A+) 첫 조각 r>=833: (6/5*20001)^{2/3}', math.floor((1.2*20001)**(2/3))+1 == 833, (1.2*20001)**(2/3))
chk('1/sqrt598 < 0.0409', 1/math.sqrt(598) < 0.0409, 1/math.sqrt(598))
chk('44 = 30+12+1+1, 43 = (10-1.4)/0.2, 1892 = 44x43', 44 == 30+12+2 and abs(8.6/0.2-43) < 1e-9 and 44*43 == 1892)
chk('10001^{-1/3} = 0.04641', abs(10001**(-1/3) - 0.046414) < 1e-6, 10001**(-1/3))
chk('0.0015/1.25^12 = 1.0308e-4', abs(0.0015/1.25**12 - 1.0308e-4) < 1e-8, 0.0015/1.25**12)
chk('G13: (1.0307e-4)^{-3} = 9.13e11', abs((1.0307e-4)**-3/9.13e11 - 1) < 2e-3, (1.0307e-4)**-3)

# ---- 5.2.1 Cayley 비 ----
vals = [mpf(1+mpf(1)/k)**(k-2) * (1 + mpf(5)/(2*k) + mpf(2)/k**2) for k in range(1,10)]
print('cr_k(1+5/(2k)+2/k^2), k=1..9:', [mp.nstr(v, 7) for v in vals])
txt = [2.75, 2.75, 2.7407, 2.7343, 2.7302, 2.7274, 2.7255, 2.7241, 2.7231]
chk('아홉 값 소수 넷째 자리 내림과 일치', all(math.floor(float(v)*10000)/10000 == t for v, t in zip(vals, txt)))
chk('아홉 값 > 87/32', all(v > mpf(87)/32 for v in vals))
chk('e < 65/24+1/100 < 87/32', e < mpf(65)/24 + mpf(1)/100 < mpf(87)/32, mp.nstr(mpf(65)/24+mpf(1)/100, 8))
th = sp.symbols('theta')
w = sp.Rational(5,2)*th + 2*th**2
expr = sp.expand((2+w)*(-sp.Rational(5,2)*th + sp.Rational(4,3)*th**2 - sp.Rational(11,12)*th**3 + sp.Rational(1,2)*th**4) + 5*th + 4*th**2)
target = sp.expand(th**2*(sp.Rational(5,12) - sp.Rational(7,2)*th + sp.Rational(11,8)*th**2 - sp.Rational(7,12)*th**3 + th**4))
chk('cayley-ratio 전개 식', sp.simplify(expr - target) == 0, expr)
chk('(1/t-2)(t-t^2/2+t^3/3-t^4/4) 전개', sp.expand((1/th-2)*(th-th**2/2+th**3/3-th**4/4)) == sp.expand(1-sp.Rational(5,2)*th+sp.Rational(4,3)*th**2-sp.Rational(11,12)*th**3+sp.Rational(1,2)*th**4))
g = lambda t: sp.Rational(5,12)-sp.Rational(7,2)*t+sp.Rational(11,8)*t**2-sp.Rational(7,12)*t**3+t**4
chk('t<=1/10에서 괄호 >= 1/15', min(float(g(sp.Rational(i,1000))) for i in range(0,101)) >= 1/15 - 1e-12, float(g(sp.Rational(1,10))))
e15 = sum(sp.Rational(1, sp.factorial(j)) for j in range(16))
chk('e_15 < e, 15!e_15 정수', e15 < sp.E and (sp.factorial(15)*e15).is_integer)

# ---- 5.2.2 lemma-L / T1 상수 ----
f = lambda y, q: y**q*exp(-y-y**2/2)
M = [quad(lambda y: f(y,q), [0, 6, inf]) for q in range(6)]
M26 = quad(lambda y: f(y,2), [0, 6])
Ms = {q: f((-1+sqrt(1+4*q))/2, q) for q in range(2,6)}
C1 = 2*Ms[2] + M[3]/2 + M[5]/3
C2 = Ms[3]/2 + Ms[5]/3 + M[4]/2
C3 = Ms[4]/2 + M[3]/6
C4 = Ms[3]/6
print('M_0..5 =', [mp.nstr(m, 7) for m in M]); print('M*_2..5 =', [mp.nstr(Ms[q], 7) for q in range(2,6)]); print('C_1..4 =', [mp.nstr(c, 7) for c in (C1,C2,C3,C4)])
chk('M_0+M_1=1, M_{q+1}=qM_{q-1}-M_q', fabs(M[0]+M[1]-1) < 1e-25 and all(fabs(M[q+1]-(q*M[q-1]-M[q])) < 1e-25 for q in range(1,5)))
chk('M 소수 다섯 자리 = 0.65568,0.34432,0.31136,0.37728,0.55680,0.95233', [round(float(m),5) for m in M] == [0.65568,0.34432,0.31136,0.37728,0.5568,0.95233])
chk('C = 0.95235,0.61306,0.24718,0.04287', [round(float(c),5) for c in (C1,C2,C3,C4)] == [0.95235, 0.61306, 0.24718, 0.04287])
chk('M_2-M_2^{(6)} <= e^{-6}(6+1/6)e^{-18}', M[2]-M26 <= exp(-6)*(6+mpf(1)/6)*exp(-18), mp.nstr(M[2]-M26, 5), mp.nstr(exp(-6)*(6+mpf(1)/6)*exp(-18), 5))
chk('M_0 교대급수', fabs(sum((-1)**i*mpf(2)**((i-1)/mpf(2))*mp.gamma((i+1)/mpf(2))/mp.factorial(i) for i in range(0, 200)) - M[0]) < 1e-20)
def L(r):
    s = sqrt(mpf(r)); st = 1/s
    return (M26 - st*C1 - st**2*C2 - st**3*C3 - st**4*C4)/(M[1] + st*(M[0]+exp(-mpf(1)/2)) + st**2)
print('L(10^4)=', mp.nstr(L(10**4), 10), ' L(2e4)=', mp.nstr(L(2*10**4), 6), ' L(1e5)=', mp.nstr(L(10**5), 6))
chk('L(10^4) >= 0.845204', L(10**4) >= mpf('0.845204'))
chk('L(10^4),L(2e4),L(1e5) = 0.8452,0.8622,0.8852', [round(float(L(x)),4) for x in (10**4, 2*10**4, 10**5)] == [0.8452,0.8622,0.8852])
def tm(d, rho):
    Nu = mpf(0); De = mpf(0); X = mpf(1); j = 0
    while True:
        term = (j+1)*rho**j*X
        Nu += j*term; De += term
        if j >= d: break
        X *= (1 - mpf(j+1)/(d+1)); j += 1
        if term < mpf(10)**-30 and j > 10: break
    return Nu/De
act = [tm(r-1, exp(-1/sqrt(mpf(r))))/sqrt(mpf(r)) for r in (10**4, 2*10**4, 10**5)]
print(' tm_{r-1}(e^{-1/sqrt r})/sqrt r at 1e4,2e4,1e5:', [mp.nstr(v,6) for v in act])
chk('실제 값 0.8935,0.8967,0.9009', [round(float(v),4) for v in act] == [0.8935,0.8967,0.9009])
chk('sqrt(pi/2) <= 1.2534, 2*1.2534 <= 2.507', sqrt(pi/2) <= mpf('1.2534') and 2*mpf('1.2534') <= mpf('2.507'), mp.nstr(sqrt(pi/2), 8))
chk('sqrt(3pi/2) <= 2.1709; 2.170804 반올림', sqrt(3*pi/2) <= mpf('2.1709') and sqrt(3*pi/2) <= mpf('2.170804'), mp.nstr(sqrt(3*pi/2), 10))
lead = mpf(1)/2 + 2*mpf('0.845204') - sqrt(3*pi/2)
chk('1/2+1.690408-sqrt(3pi/2) >= 0.019604', lead >= mpf('0.019604'), mp.nstr(lead, 8))
br = lambda s: 1/(3*s) + 8/(3*s**2) + mpf('2.507')/s**2 + (1+mpf('2.1709')*s)/s**3
chk('대괄호 s>=100에서 < 0.0041 (s=100: %s)' % mp.nstr(br(mpf(100)), 6), br(mpf(100)) < mpf('0.0041'))
chk('s>=25: 0.019604s-0.0041 >= 0.0196s-0.004', mpf('0.019604')*25 - mpf('0.0041') >= mpf('0.0196')*25 - mpf('0.004'))
chk('k_r/(k_r-1) <= 1+1/s^3 (r=10^4)', (mpf(10**6+8*10**4))/(10**6+8*10**4-1) <= 1 + mpf(1)/10**6)
chk('tm_d(1) <= sqrt(pi d/2) (d=100,1000)', all(tm(d, mpf(1)) <= sqrt(pi*d/2) for d in (100, 1000)), mp.nstr(tm(1000, mpf(1)),6), mp.nstr(sqrt(pi*1000/2),6))
kr = lambda r: math.ceil(r**1.5 + 8*r)
chk('k_171 = 3605, k_9999 = 1079843 (기록 k0와 일치)', kr(171) == 3605 and kr(9999) == 1079843, kr(171), kr(9999))
def Pc(k, r, eb): return k*(mpf(1)/(2*r) - mpf(1)/(3*r**2)) - mpf(5)/2 + 2*eb*(1-mpf(1)/k) - mpf(k)/(k-1)*(1+sqrt(3*pi*(r-1)/2))
for r in (171, 1000, 9999):
    k = kr(r); eb = tm(r-1, mpf(k)/(k+r)); P = Pc(k, r, eb)
    print(' r=%d k=%d tm=%s Pc=%s Pc/sqrt r=%s' % (r, k, mp.nstr(eb, 8), mp.nstr(P, 6), mp.nstr(P/sqrt(r), 6)))
chk('Pc(k_9999)/sqrt9999 = 0.1654 (기록 0.165385)', round(float(Pc(kr(9999), 9999, tm(9998, mpf(kr(9999))/(kr(9999)+9999)))/sqrt(9999)), 4) == 0.1654)

# ---- 5.2.3 핵 상수 ----
o = 1/sqrt(mpf(2))
chk('e^{1/23} < 1.045; o e^{1/23} < 3/4', exp(mpf(1)/23) < mpf('1.045') and o*exp(mpf(1)/23) < mpf(3)/4, mp.nstr(exp(mpf(1)/23), 8), mp.nstr(o*exp(mpf(1)/23), 8))
chk('e^{2/23}+21/80 e^{1/23} < 11/8 (<1.0921+0.2744)', exp(mpf(2)/23) + mpf(21)/80*exp(mpf(1)/23) < mpf(11)/8 and exp(mpf(2)/23) < mpf('1.0921') and mpf(21)/80*exp(mpf(1)/23) < mpf('0.2744'))
chk('o/2 < 4/11 < 1/e < 1/2 < o', o/2 < mpf(4)/11 < 1/e < mpf(1)/2 < o)
chk('o/2 < 1/e < 21o/40; 1957/720 < e; sqrt2 < 99/70; 147/396 > 720/1957', o/2 < 1/e < 21*o/40 and mpf(1957)/720 < e and sqrt(2) < mpf(99)/70 and mpf(147)/396 > mpf(720)/1957)
chk('2sqrt2/e > 26/25; sqrt2 > 181/128; e < 87/32; 181/174 > 26/25', 2*sqrt(2)/e > mpf(26)/25 and sqrt(2) > mpf(181)/128 and e < mpf(87)/32 and mpf(181)/174 > mpf(26)/25, mp.nstr(2*sqrt(2)/e, 6))
chk('312m^2-374m+25 >= 0 for m>=2, <0 at m=1', 312*4-374*2+25 > 0 and 312-374+25 < 0)
chk('2/e < 3/4, e > 8/3', 2/e < mpf(3)/4 and e > mpf(8)/3)
chk('(1+3/169)/25 < 1/12', (1+mpf(3)/169)/25 < mpf(1)/12, mp.nstr((1+mpf(3)/169)/25, 6))
rq_star = mpf(13)/20*(1+mpf(3)/529)/23
chk('rq_* = 13/20*(1+3/529)/23 < 1/12', rq_star < mpf(1)/12, mp.nstr(rq_star, 6))
chk('63/32 < 2; 9/16+9/32+9/8 = 63/32', sp.Rational(9,16)+sp.Rational(9,32)+sp.Rational(9,8) == sp.Rational(63,32))

# ---- 5.2.4 EI / 5.3 ----
chk('-0.02965 < -1/40', -0.02965 < -1/40)
chk('(20/13)r^{3/2} >= 2r+1 at r=529', 20/13*529**1.5 >= 2*529+1)
chk('27.14^3 < 20001; 27.14^2 > 736.6', 27.14**3 < 20001 and 27.14**2 > 736.6, 27.14**3, 27.14**2)
chk('r_0(20001) >= 552', math.floor(0.75*20001**(2/3)) >= 552, math.floor(0.75*20001**(2/3)))
chk('3/4-736.6^{-1} > 149/200', 0.75-1/736.6 > 149/200)
chk('(149/200)^3 > (16/25)^2; (3/4)^3 < (13/20)^2', (149/200)**3 > (16/25)**2 and (3/4)**3 < (13/20)**2)
chk('(3/4)^{3/2} < 0.65; 27/(4*27.14) < 0.25', 0.75**1.5 < 0.65 and 27/(4*27.14) < 0.25)
chk('(9/5)^{2/3} > 1.4; 10*2^{-2/3} > 6.29', (9/5)**(2/3) > 1.4 and 10*2**(-2/3) > 6.29, (9/5)**(2/3), 10*2**(-2/3))
chk('1/(1+9/sqrt598) > 73/100', 1/(1+9/math.sqrt(598)) > 0.73, 1/(1+9/math.sqrt(598)))
chk('100r^3<=324n^2 <=> x^{3/2}<=9/5', abs(math.sqrt(3.24)-1.8) < 1e-12)
# ---- 5.4 omitted-tail / 정리 5.12 ----
chk('(12/5)(1+1/598)/sqrt598 < 1/10', 2.4*(1+1/598)/math.sqrt(598) < 0.1, 2.4*(1+1/598)/math.sqrt(598))
chk('12/(110e) < 1/24; (12/11)^{3/2}(1+1/598) <= 1.15', 12/(110*math.e) < 1/24 and (12/11)**1.5*(1+1/598) <= 1.15, 12/(110*math.e), (12/11)**1.5*(1+1/598))
chk('log10(1.15*598^3) < 8.4; 598 log10 24 > 825', math.log10(1.15*598**3) < 8.4 and 598*math.log10(24) > 825, math.log10(1.15*598**3), 598*math.log10(24))
chk('(5/12)sqrt598 > 10; 12/(5 sqrt598) < 1/10', 5/12*math.sqrt(598) > 10 and 12/(5*math.sqrt(598)) < 0.1)
chk('tail_ratio_upper 3842619993/9025000000 < 1/2', 3842619993/9025000000 < 0.5, 3842619993/9025000000)
chk('(A) 첫 인증 최악 -2076.../2^120 = -0.01562', abs(-20763942788699649828208058950993518/2**120 - (-0.01562)) < 5e-6, -20763942788699649828208058950993518/2**120)
u = sp.symbols('u', positive=True)
chk('(1-u)^{-(j+1)}(1+u/(2(1-u))) >= (1-u)^{-j-3/2} <=> (2-u)^2 >= 4(1-u)', sp.simplify(sp.expand((2-u)**2 - 4*(1-u))) == u**2)

# ---- 5.4.2 임계 창 상수 ----
et = lambda ph: e*ph*exp(-ph*cot(ph))/sin(ph)
chk('log et(1/2) = 0.126775..., 0.1267 하계, 0.1268 아님', mpf('0.126775') < log(et(mpf(1)/2)) < mpf('0.126776') and mpf('0.1267') < log(et(mpf(1)/2)) < mpf('0.1268'), mp.nstr(log(et(mpf(1)/2)), 9))
lm = lambda m: (2+mpf(1)/m)*zeta(2*m)/pi**(2*m)
chk('l_1=1/2, l_2=1/36, l_3=1/405', fabs(lm(1)-mpf(1)/2) < 1e-30 and fabs(lm(2)-mpf(1)/36) < 1e-30 and fabs(lm(3)-mpf(1)/405) < 1e-30)
chk('log et(phi) = sum l_m phi^{2m} (phi=0.3)', fabs(log(et(mpf('0.3'))) - sum(lm(m)*mpf('0.3')**(2*m) for m in range(1,60))) < 1e-30)
chk('1-cos(1) = 0.4597 >= 0.458', 1-cos(mpf(1)) >= mpf('0.458'), mp.nstr(1-cos(mpf(1)), 6))
xi = lambda a: exp(1j*a)*exp(1-exp(1j*a))
grid = [mpf(i)/2000 for i in range(1, 2001)]
r1 = [fabs(xi(a)-1)/a**2 for a in grid]; r2 = [im(xi(a)-1)/a**3 for a in grid]
print(' |xi-1|/ag^2 in [%s, %s];  Im(xi-1)/ag^3 in [%s, %s]' % (mp.nstr(min(r1),6), mp.nstr(max(r1),6), mp.nstr(min(r2),6), mp.nstr(max(r2),6)))
chk('0.4999 <= |xi-1|/ag^2 <= 0.617 (0<ag<=1); 상계 1.3 안전', min(r1) >= mpf('0.4999') and max(r1) <= mpf('0.617') and max(r1) <= mpf('1.3'))
chk('주 영역 ag<=0.28에서 |xi-1|/ag^2 >= 0.49', min(fabs(xi(a)-1)/a**2 for a in grid if a <= mpf('0.28')) >= mpf('0.49'))
chk('Im(xi-1)/ag^3 >= 0.1666 >= 0.15; ->1/6', min(r2) >= mpf('0.1666') and min(r2) < mpf(1)/6 + 1e-3)
mm = min(max(im(xi(a)), et(mpf(1)/2) - fabs(xi(a))) for a in grid)
chk('min_ag max(Im xi, et(1/2)-|xi|) >= 0.019', mm >= mpf('0.019'), mp.nstr(mm, 6))
chk('pi/0.019 <= 166', pi/mpf('0.019') <= 166, mp.nstr(pi/mpf('0.019'), 6))
val = log(166) - log(mpf(10001))/6 - mpf('0.1267')*10001
chk('log(166*10001^{-1/6}e^{-0.1267*10001}) <= -1263; -1263+800 <= -460', val <= -1263 and -1263 + 800 <= -460, mp.nstr(val, 7))
rot = exp(-1j*pi/8)
cs = [mpf(i)/800*rot for i in range(1, 401)]
lgc = [sum(2*m*lm(m)*p**(2*m-2) for m in range(1, 80)) for p in cs]
Lc = [log(et(p))/fabs(p)**2 for p in cs]
qyc = [(et(p)-1)/fabs(p)**2 for p in cs]
print(' ray -pi/8 (ku->0): max|lg| = %s (code 1.03; 본문 1.0199), min Re Lhat/|phihat|^2 = %s (0.34; 0.3534), max |Lhat|/|phihat|^2 = %s (0.507; 0.505)' % (mp.nstr(max(fabs(v) for v in lgc),6), mp.nstr(min(re(v) for v in Lc),6), mp.nstr(max(fabs(v) for v in Lc),6)))
print(' ray -pi/8 (ku->0): arg(qy) deg in [%s, %s] (본문 [-48.21,-45.00]), max|qy|/|phihat|^2 = %s (0.545; 0.528)' % (mp.nstr(min(degrees(arg(v)) for v in qyc),6), mp.nstr(max(degrees(arg(v)) for v in qyc),6), mp.nstr(max(fabs(v) for v in qyc),6)))
chk('반직선 상수(ku->0 판): max|lg|<=1.03, min Re Lhat/|phihat|^2>=0.34, |Lhat|/|phihat|^2<=0.507, |qy|/|phihat|^2<=0.545, arg qy in [-48.5,-45]', max(fabs(v) for v in lgc) <= mpf('1.03') and min(re(v) for v in Lc) >= mpf('0.34') and max(fabs(v) for v in Lc) <= mpf('0.507') and max(fabs(v) for v in qyc) <= mpf('0.545') and min(degrees(arg(v)) for v in qyc) >= -48.5 and max(degrees(arg(v)) for v in qyc) <= -45)
chk('sin45 > 0.69', sin(pi/4) > mpf('0.69'))
chk('꼬리: exp(-(1-cos1)*1.4*10001^{2/3}) < 1e-100', exp(-(1-cos(mpf(1)))*mpf('1.4')*mpf(10001)**(mpf(2)/3)) < mpf(10)**-100, mp.nstr(exp(-(1-cos(mpf(1)))*mpf('1.4')*mpf(10001)**(mpf(2)/3)), 5))
chk('0.069/0.01~7, 0.253/0.01~25', round(0.069/0.01) == 7 and round(0.253/0.01) == 25)
chk('(n+1)/2 = 25001 at n=50001', (50001+1)//2 == 25001)
print('ALL OK' if ok else 'SOME NG')
