# -*- coding: utf-8 -*-
"""수학검사2 태그 10: 10.4-10.6절과 부록 D(M-natural-integrals, four-families)의 상수·식을 mpmath로 다시 계산한다.
python -I scripts/수학검사2/10_검산_상수.py"""
from mpmath import mp, mpf, sqrt, log, exp, quad, pi, e, floor, ceil, findroot
import numpy as np
mp.dps = 30
def P(*a): print(*a)

P("== 10.3절 표")
P("20001-2k>0.48k <=> k<", 20001/2.48)
for k, phi, lab in ((9705, 1.3, '1a'), (9551, 2.0, '1b')):
    P(lab, "k0=%d: 20001-2k=%d  phi k^(2/3)=%s ; k0-1: %d vs %s" % (k, 20001-2*k, mp.nstr(phi*mpf(k)**(mpf(2)/3), 7), 20001-2*(k-1), mp.nstr(phi*mpf(k-1)**(mpf(2)/3), 7)))
P("2: k0=8065: 20001-2k=%d  0.48k=%s ; k=8064: %d vs %s" % (20001-16130, mp.nstr(0.48*8065, 7), 20001-16128, mp.nstr(0.48*8064, 7)))
P("row-3k: 2*0.7654 =", 2*0.7654, "> 1.3502")

P("\n== 10.4절")
P("e^0.48 =", mp.nstr(exp(0.48), 6), "<2")
k = mpf(6667)
P("0.48k =", 0.48*k, " 1.5(2k+3)^(2/3) =", mp.nstr(1.5*(2*k+3)**(mpf(2)/3), 7))
P("(3(k+1))^(2/3) at 6667 =", mp.nstr((3*(k+1))**(mpf(2)/3), 7))
y = mpf(6666)
P("0.6y-1 =", 0.6*y-1, " 1.5(2y+3)^(2/3) =", mp.nstr(1.5*(2*y+3)**(mpf(2)/3), 7))
P("g(6667) =", mp.nstr((k-1)*log(1+1/k), 12), " 1-3/(2k) =", mp.nstr(1-3/(2*k), 12))

P("\n== 명제 old-8-23 (M-natural) 증명 상수")
q = lambda r: 1+mpf('0.7501')*r/(1+r)
P("1단계: (1+1/k)(1+2/k)/(1-3/(4k)) at 6667 =", mp.nstr((1+1/k)*(1+2/k)/(1-mpf(3)/(4*k)), 10), "<= 1.00057")
P("  9/8*(1+e^{3/(2k)}) =", mp.nstr(mpf(9)/8*(1+exp(3/(2*k))), 10), " vs 3*0.7501 =", 3*0.7501)
P("  c_d coefficient 1.00057^2 (1+2/k)^2 /6 =", mp.nstr(mpf('1.00057')**2*(1+2/k)**2/6, 10), "<= 0.16696")
P("2단계: 2*0.8*(2/7) =", mp.nstr(2*mpf('0.8')*2/7, 10), "<= 0.457143")
P("3단계: sqrt(sqrt2*0.16696) =", mp.nstr(sqrt(sqrt(2)*mpf('0.16696')), 10), " (text 0.4859188..., rounded down 0.485917)")
P("  2.5-log2-log0.485917 =", mp.nstr(mpf('2.5')-log(2)-log(mpf('0.485917')), 12), "<= 2.528571")
P("  3*sqrt2*0.16696 =", mp.nstr(3*sqrt(2)*mpf('0.16696'), 12), "<= 0.70836")
P("  3*0.485917/2 =", mp.nstr(3*mpf('0.485917')/2, 10), "<= 0.72888")
P("  2*0.485917*q_max(=1.37505) =", mp.nstr(2*mpf('0.485917')*(1+mpf('0.7501')/2), 8), " < 2^{3/2} =", mp.nstr(mpf(2)**1.5, 8))
qk1 = 1+mpf('0.7501')*k/(2*k)
P("  3.9 check: 2*0.72888*q_{k+1}^2*sqrt(2) =", mp.nstr(2*mpf('0.72888')*qk1**2*sqrt(2), 8), "<= 3.9  (q_{k+1}=", mp.nstr(qk1,8), ")")
P("4단계: bracket lower bound 2.528571+log(2^{3/2})-log q(1+1/k) =", mp.nstr(mpf('2.528571')+1.5*log(2)-log(q(1+1/k)), 8), ">= 3.246")
P("  gamma coeff sqrt2*0.70836*q(1+1/6667)^3 =", mp.nstr(sqrt(2)*mpf('0.70836')*q(1+1/k)**3, 10), "<= 2.6047")
dn = 2*k**(mpf(2)/3)
P("  eps' check: (1+0.7501/k)^3*(1+1.5/(3.246*(dnat-1))) - 1 - 2.26/k - 0.47/(dnat-1) =", mp.nstr((1+mpf('0.7501')/k)**3*(1+1.5/(mpf('3.246')*(dn-1)))-1-mpf('2.26')/k-mpf('0.47')/(dn-1), 6), "(<=0 needed)")
P("5단계: dnat(6667) =", mp.nstr(dn, 8), " floor/k =", mp.nstr(mpf(708)/k, 8), " 2k^{-1/3} =", mp.nstr(2*k**(-mpf(1)/3), 8), " <= 0.10635")
P("  q(0.10635) =", mp.nstr(q(mpf('0.10635')), 8), " q(708/6667) =", mp.nstr(q(mpf(708)/k), 8))
lb = 1.5*log(2)+1.5*log(1-1/dn)
P("  log(2^{3/2}(1-1/dnat)^{3/2}) =", mp.nstr(lb, 8), " log(708^{1.5}/6667) =", mp.nstr(log(mpf(708)**1.5/k), 8))
i0a = mpf('2.528571')+lb-log(mpf('1.0722'))
i0b = mpf('2.528571')+lb-log(q(mpf(708)/k))
P("  iota_0 from stated bounds (q<=1.0722):", mp.nstr(i0a, 8), " ; with q(708/6667):", mp.nstr(i0b, 8), " ; text 3.4966")
for i0 in (i0a, mpf('3.4966'), mpf('3.4964')):
    s0 = exp(-i0/1.5)
    P("   iota0=%s: sigma0=%s  bracket 2i0-6-0.0288*6*sqrt(s0) = %s" % (mp.nstr(i0,7), mp.nstr(s0,6), mp.nstr(2*i0-6-mpf('0.0288')*6*sqrt(s0), 6)))
rr = mpf('0.10635')*mpf('0.0972')
P("  d(rho)q^3*sqrt(rho) at rho=rho0*sigma0 =", mp.nstr(sqrt(1+rr)*q(rr)**3, 8), "<= 1.0288")
P("6단계: 2^{3.5} =", mp.nstr(mpf(2)**3.5, 8), " j1+j2(log(6667)/2-1) =", mp.nstr(mpf('0.7998716895841891')+mpf('2.717199867930190')*(log(6667)/2-1), 12))

P("\n== 부록 D M-natural: 적분 직접 재계산(tanh-sinh, 30자리)")
C = mpf('0.70836'); K = mpf('2.528571')
j2 = quad(lambda r: sqrt((1+r)/r)*C*q(r)**3, [0, mpf('1e-6'), mpf('0.01'), 1])
j1 = quad(lambda r: sqrt((1+r)/r)*C*q(r)**3*(K-log(q(r))+mpf('1.5')*log(r)), [0, mpf('1e-6'), mpf('0.01'), 1])
P("j2 =", mp.nstr(j2, 20), " j1 =", mp.nstr(j1, 20))
def DDL(kk, j1=j1, j2=j2):
    kk = mpf(kk); d = 2*kk**(mpf(2)/3)
    eps = -log(1-sqrt(kk+1)/(mpf('0.485917')*kk)); epsp = mpf('2.26')/kk+mpf('0.47')/(d-1)
    gam = mpf('2.6047')*(mpf('2.53')+log(kk)/2+eps+mpf('1.5')/kk)/kk
    b = 1/sqrt(2*pi)
    return mpf('0.457143')*b*q(d/kk)*sqrt(1+d/kk)*(d+1)**mpf('3.5')/kk**3 + 2*b/sqrt(kk)*(1+epsp)*(j1+(log(kk)/2+eps)*j2+gam) + mpf('3.9')*b/kk
for kk in (6667, 6668, 8065, 9551, 9705, 9949):
    P("DDL(%d) = %s" % (kk, mp.nstr(DDL(kk), 12)))
C2 = mpf('0.708345'); K2 = mpf('2.528570')
j2r = j2*C2/C; j1r = C2/C*(j1-(K-K2)*j2)
P("record constants: j2' =", mp.nstr(j2r, 10), " j1' =", mp.nstr(j1r, 10))
for kk in (6667, 6668, 9705):
    P("  shift DDL-DDL' at %d = %s" % (kk, mp.nstr(DDL(kk)-DDL(kk, j1r, j2r), 6)), " (text: <= 2.7e-6)")

P("\n== 정리 old-8-25 상수")
th1 = findroot(lambda t: (1-t)**2.5-1+2*t, 0.28)
P("theta_1 =", mp.nstr(th1, 8), " 2/sqrt(pi) =", mp.nstr(2/sqrt(pi), 8))
b2 = 2/sqrt(2*pi)
coef = lambda u, qq: b2*(mpf(1)/4*(1-1/(2*qq))**(-1.5)+(1+u+u*u)*(1-u)**(-0.5)*(1+u)**(-1.5))
P("E coeff at u=0.9,q=113:", mp.nstr(coef(mpf('0.9'),113), 6), "<=2.82 ; u=0.99:", mp.nstr(coef(mpf('0.99'),113), 6), "<=9.3 ; u=0.9999:", mp.nstr(coef(mpf('0.9999'),113), 6), "<=85")
P("F bounds: 2(2pi)^{-1/2}*3*sqrt(1-0.81) =", mp.nstr(b2*3*sqrt(1-0.81), 8), "<=1.044 ; *sqrt(1-0.99^2) =", mp.nstr(b2*3*sqrt(1-mpf('0.99')**2), 6), "<=0.34")
P("1.6*0.8/sqrt(50) =", mp.nstr(1.6*0.8/sqrt(50), 6), "<=0.182 ; v(0.02)/0.02 =", mp.nstr(((1-mpf('0.02'))**(-1.5)-1)/mpf('0.02'), 6), "<=1.6")
P("2(2pi)^{-1/2} sqrt(50/0.77) =", mp.nstr(b2*sqrt(50/mpf('0.77')), 6), "<=6.5 ; q/50-1/2>=0.77q/50 iff q>=", mp.nstr(0.5/(0.23/50), 6))
P("0.182+7.3*0.0003 =", 0.182+7.3*0.0003, "<0.19 ; 1-0.9999^3 =", mp.nstr(1-mpf('0.9999')**3, 6))
P("a'(6666; m_S=1.15) = floor((1.15*6666)^{2/3}) =", int(floor((mpf('1.15')*6666)**(mpf(2)/3))), " ; a'(1000; m_S=1.2) = floor((1.2*1000)^{2/3}) =", int(floor((mpf('1.2')*1000)**(mpf(2)/3))))
P("1.1284+2.82/389 =", mp.nstr(mpf('1.1284')+mpf('2.82')/389, 6), " 1.1284+2.82/113 =", mp.nstr(mpf('1.1284')+mpf('2.82')/113, 6), " 1.044+9.3/389=", mp.nstr(1.044+9.3/389,5), " 0.34+85/389=", mp.nstr(0.34+85/389,5), " 1.044+9.3/113=", mp.nstr(1.044+9.3/113,5), " 0.34+85/113=", mp.nstr(0.34+85/113,5))
for a_, b_, lim in ((0,0.9,2.82),(0.9,0.99,9.3),(0.99,0.9999,85)):
    mx = max(float(coef(mpf(u),113)) for u in np.linspace(a_, b_, 2001))
    P("  max E coeff on [%g,%g] (q=113) = %.4f <= %g" % (a_, b_, mx, lim))

P("\n== 보조정리 old-8-30/31/32 상수")
P("f1 = 4/(3 sqrt(2pi)) =", mp.nstr(4/(3*sqrt(2*pi)), 8), " c_R = sqrt(2pi)/2 e^{1/12} =", mp.nstr(sqrt(2*pi)/2*exp(mpf(1)/12), 8))
cR = sqrt(2*pi)/2*exp(mpf(1)/12)
ge = lambda t: exp(-t)*(1+1.5*t)
P("beta0 min = c_R 1.04^{1.5}/sqrt2 =", mp.nstr(cR*mpf('1.04')**1.5/sqrt(2), 6), " g^e(1.0216) =", mp.nstr(ge(mpf('1.0216')), 6), "<=0.912")
P("iota q0 max = c_R 2^{2/3} 6669^{-1/3} =", mp.nstr(cR*mpf(2)**(mpf(2)/3)/mpf(6669)**(mpf(1)/3), 6), "<=0.115 ; 1-0.115^2/2 =", 1-0.115**2/2)
P("beta2 range: c_R*1.04^{1.5}=", mp.nstr(cR*mpf('1.04')**1.5, 6), " c_R*2 =", mp.nstr(cR*2, 6), " sqrt(1/2+1/562) =", mp.nstr(sqrt(mpf(1)/2+mpf(1)/562), 6), "<=0.7084")
P("min |g^e'| on [1.02,2.73]: at 1.02:", mp.nstr(exp(-1.02)*(1.5*1.02-0.5), 6), " at 2.73:", mp.nstr(exp(-2.73)*(1.5*2.73-0.5), 6), " ; 0.234*0.2916*1.444 =", mp.nstr(0.234*0.2916*1.444, 6), " ; e^{-1}/564 =", mp.nstr(exp(-1)/564, 6))

P("\n== 명제 old-8-33 (ii) 상수")
cAb = lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
P("2 cAb(0.6) - 4/sqrt(0.6) =", mp.nstr(2*cAb(mpf('0.6'))-4/sqrt(mpf('0.6')), 8), " (text 10.836)")
P("int_0^0.6 (1+r) r^{-1/2} (1-r)^{-2} dr =", mp.nstr(quad(lambda r: (1+r)/sqrt(r)/(1-r)**2, [0, mpf('0.6')]), 8), " (text 3.873)")
yv = mpf(6666); ms = mpf('1.15')
ab = (ms*(yv+2*yv**(mpf(2)/3)))**(mpf(2)/3); dab = mpf(2)/3*ab*(1+mpf(4)/3*yv**(-mpf(1)/3))/(yv+2*yv**(mpf(2)/3))
P("Flat decreasing check at y=6666: a'(y+1) =", mp.nstr(dab*(yv+1), 6), " < a-1 =", mp.nstr(ab-1, 6))
xi = mpf('0.1234'); u = mpf('0.37')
P("partial fraction check (should be 0):", mp.nstr((u-xi)*(1+u)/(u*(1-u)**2) - (-xi/u-(1+xi)/(1-u)+2*(1-xi)/(1-u)**2), 5))
kk = mpf(9705); nub = mpf('1.3')*kk**(mpf(2)/3); xi = (nub+4)/(kk-1)
G = lambda s: xi/s+(1-xi)*s/(1-s*s)-xi*log((1+s)/(1-s))
SubC = (kk-1)/kk*2*(G(sqrt(mpf('0.6')))-G(sqrt(xi)))
SubQ = (kk-1)/kk*quad(lambda r: (r-xi)*(1+r)*r**(-1.5)*(1-r)**(-2), [xi, mpf('0.6')])
P("Sub closed vs quad (1a, 9705):", mp.nstr(SubC, 12), mp.nstr(SubQ, 12))
ee = (nub+1)/kk; rlo = mpf('0.6')-mpf('2.6')/kk
TopQ = quad(lambda r: min(2, 2+ee-r)*(1+r/3)*r**(-1.5), [rlo, 1])
a0 = 2+ee; a1 = a0/3-1; Fp = lambda r: -2*a0/sqrt(r)+2*a1*sqrt(r)-mpf(2)/9*r**1.5
P("Top closed vs quad (1a, 9705):", mp.nstr(Fp(1)-Fp(rlo), 12), mp.nstr(TopQ, 12), " e<=rlo:", ee <= rlo)
P("family 2: 0.48+1/k <= 0.6-2.6/k iff k >= 3.6/0.12 =", 3.6/0.12)

P("\n== 보조정리 old-8-34 / 명제 old-8-35 / bulk-majorants 상수")
P("nu Pr(Bor>=nu) coeff at nu=103: 2(2pi)^{-1/2}(1-1/206)^{-1/2} =", mp.nstr(b2*(1-mpf(1)/206)**(-0.5), 6), "<=0.7999")
P("theta_0 = (2e^{-0.48}-1)e^{-0.48} =", mp.nstr((2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')), 8))
P("(2pi)^{-1/2}/e * 2^{3/2} =", mp.nstr(1/sqrt(2*pi)/e*mpf(2)**1.5, 8), " *e^{-1/(12*6667)-1/(12*3200)} =", mp.nstr(1/sqrt(2*pi)/e*mpf(2)**1.5*exp(-mpf(1)/(12*6667)-mpf(1)/(12*3200)), 8), ">=0.41508 ; 1/0.41508 =", mp.nstr(1/mpf('0.41508'), 8))
k = mpf(6667)
P("m_hit(6667) = ceil(sqrt(5k log k)) =", int(ceil(sqrt(5*k*log(k)))), " /k =", mp.nstr(ceil(sqrt(5*k*log(k)))/k, 5), "<=0.09 ; 0.48k-1 =", 0.48*k-1)
P("s^up log-deriv sign 1.5 sqrt(th)-0.5 phi^2 th-2phi at th=354.3, phi=1.3:", mp.nstr(1.5*sqrt(354.3)-0.5*1.69*354.3-2.6, 5))
br = mpf('0.48')**(-0.5)-1+(1-sqrt(mpf('0.48')))/3
P("bulk bracket at nu/k=0.48:", mp.nstr(br, 8), "<=0.5458 ; 132.32*bracket =", mp.nstr(mpf('132.32')*br, 8), " <= 72.217 ; 132.32*0.5458 =", mp.nstr(mpf('132.32')*mpf('0.5458'), 8))
P("4*16.54*2 =", 4*16.54*2)

P("\n== check-na/check-ga 표")
P("2: 4-1.3392+0.1470-0.7615-0.1223 =", mp.nstr(4-1.3392+0.1470-0.7615-0.1223, 6), " ; 1b: 4-2.4644+0.7463-0.5254-0.1140 =", mp.nstr(4-2.4644+0.7463-0.5254-0.1140,6), " ; 1a: 2-0.0250-0.5062-0.1133 =", mp.nstr(2-0.0250-0.5062-0.1133,6), " ; bulk 0.1880+1.1190+0.1324+0.8844 =", mp.nstr(0.1880+1.1190+0.1324+0.8844,6))
for k0 in (6668, 8065, 9551, 9705):
    P("eps0(%d) = floor(2^{2/3}(k0+1)^{2/3}) = %d ; 2^{2/3}-(k0+1)^{-2/3} = %s" % (k0, int(floor((2*mpf(k0+1))**(mpf(2)/3))), mp.nstr(mpf(2)**(mpf(2)/3)-mpf(k0+1)**(-mpf(2)/3), 6)))
P("0.8*1.3 =", 0.8*1.3, " 0.8*2^{2/3} =", mp.nstr(0.8*mpf(2)**(mpf(2)/3), 6), " 1.3*6669^{2/3} =", mp.nstr(1.3*mpf(6669)**(mpf(2)/3), 7))
