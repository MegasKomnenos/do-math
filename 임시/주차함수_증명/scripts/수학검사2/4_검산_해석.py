# -*- coding: utf-8 -*-
"""4장 4.3절 중앙 틈 사슬의 해석적 상수·식 검산 (수학검사2, 태그 4).
python -I scripts/수학검사2/4_검산_해석.py
"""
import mpmath as mp
import sympy as sp
from fractions import Fraction as Fr

mp.mp.dps = 30
out = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); out.append(s)

# ---------- 1. 보조정리 gauss-contraction: C_i, 도함수, 잔차 ----------
P("== 1. gauss-contraction 계수 ==")
g = sp.symbols('gamma', positive=True)
ups = (1+g)/2
C1 = (1-ups)/g**2
C2 = -(1-ups)*(2+ups)/g**5
C3 = 5*(1-ups)*(6+g-g**2)/(2*g**8)
P("C1==(1-g)/(2g^2):", sp.simplify(C1-(1-g)/(2*g**2))==0,
  " C2==-(1-g)(5+g)/(4g^5):", sp.simplify(C2+(1-g)*(5+g)/(4*g**5))==0,
  " C3==5(1-g)(6+g-g^2)/(4g^8):", sp.simplify(C3-5*(1-g)*(6+g-g**2)/(4*g**8))==0)
P("C1,C2,C3 at gamma=1/3:", [sp.nsimplify(c.subs(g, sp.Rational(1,3))) for c in (C1,C2,C3)])
# 로그 도함수(gamma에 관해)
P("dlogC1:", sp.simplify(sp.diff(sp.log(C1),g) - (-1/(1-g)-2/g))==0,
  " dlogC2:", sp.simplify(sp.diff(sp.log(-C2),g) - (-1/(1-g)+1/(5+g)-5/g))==0,
  " dlogC3:", sp.simplify(sp.diff(sp.log(C3),g) - (-1/(1-g)+(1-2*g)/(6+g-g**2)-8/g))==0)
D = lambda f: sp.diff(f, g)*(-2/g)   # d/d iota
u4 = D(D(D(D(ups))))
P("ups'''' == -120 g^-7:", sp.simplify(u4+120*g**-7)==0)
P("C1''' == 192g^-8-60g^-7:", sp.simplify(D(D(D(C1)))-(192*g**-8-60*g**-7))==0)
P("C2'' == -(175g^-9-96g^-8-15g^-7):", sp.simplify(D(D(C2))+(175*g**-9-96*g**-8-15*g**-7))==0)
P("C3' == 5/2(48g^-10-35g^-9-12g^-8+5g^-7):", sp.simplify(D(C3)-sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7))==0)
t3 = sp.Rational(1,3)
def termabs(expr):
    tot=0
    for e in range(-12,1):
        c=expr.coeff(g,e)
        if c!=0: tot+=abs(c)*t3**e
    return tot
s1 = 120*sp.Integer(3)**7/24; s2 = termabs(sp.expand(192*g**-8-60*g**-7))/6
s3 = termabs(sp.expand(175*g**-9-96*g**-8-15*g**-7))/2; s4 = termabs(sp.expand(sp.Rational(5,2)*(48*g**-10-35*g**-9-12*g**-8+5*g**-7)))
P("네 항:", s1, s2, s3, s4, " 합:", s1+s2+s3+s4, "(글 11328660)")
m1 = -D(ups)+C1; m2 = D(D(ups))/2 - D(C1) + C2; m3 = -D(D(D(ups)))/6 + D(D(C1))/2 - D(C2) + C3
P("m1==ups/g^2:", sp.simplify(m1-ups/g**2)==0, " m2==C2-2/g^4:", sp.simplify(m2-(C2-2/g**4))==0,
  " m3==C3+5(5-g^2)/(2g^7):", sp.simplify(m3-(C3+5*(5-g**2)/(2*g**7)))==0)
P("|m1|,|m2|,|m3| at 1/3:", [abs(m.subs(g,t3)) for m in (m1,m2,m3)], "(글 6,378,60750)")
x4 = 3*60750 + 216*378 + 34020*6
P("x^4 계수 상계 182250+81648+204120 =", x4, "(글 468018)")
xm = mp.mpf('1.12e-5')
P("x^5 항/x^4:", (216*60750+34020*378)*xm, "(글 291 이하)  x^6 항/x^4:", 34020*60750*xm**2, "(글 1 이하)")
uh1 = mp.mpf(1)/3+3*xm+216*xm**2+34020*xm**3
P("|uhat-1| 상계:", uh1, "< 1/3+4e-5:", uh1 < mp.mpf(1)/3+mp.mpf('4e-5'))
lit = (mp.mpf(1)/3+mp.mpf('4e-5'))*11328660 + 468018 + 291 + 1
P("글의 항 그대로 합 (1/3+4e-5)*11328660+468018+291+1 =", lit, " (글 4244983) -> 내림 여부:", lit > 4244983)
act = uh1*11328660 + 468018 + (216*60750+34020*378)*xm + 34020*60750*xm**2
P("실제 입력으로의 합:", act)
# 잔차 R 전개 (sympy, gamma Laurent)
h = sp.symbols('h')  # = x
gam = sp.symbols('gam', positive=True)
iota = (1-gam**2)/4
def upso(i): return (1+sp.sqrt(1-4*i))/2
def Cs(gg):
    u=(1+gg)/2
    return (1-u)/gg**2, -(1-u)*(2+u)/gg**5, 5*(1-u)*(6+gg-gg**2)/(2*gg**8)
def uhat(i, hh):
    gg = sp.sqrt(1-4*i); c1,c2,c3 = Cs(gg)
    return upso(i)+hh*c1+hh**2*c2+hh**3*c3
R = (uhat(iota,h)-1)*uhat(iota-h,h)+iota
ser = sp.series(R, h, 0, 5).removeO()
coeffs = [sp.simplify(ser.coeff(h,i)) for i in range(5)]
P("R의 x^0..x^3 계수 (0이어야):", [sp.simplify(c) for c in coeffs[:4]])
P("R의 x^4 계수 at gamma=1/3:", sp.nsimplify(sp.simplify(coeffs[4].subs(gam, sp.Rational(1,3)))), "(부록 2729376)")

# ---------- 2. (다) 두 적분 항등식, (라) 항등식 ----------
P("== 2. 적분 항등식 ==")
def upsf(i): return (1+mp.sqrt(1-4*i))/2
def gamf(i): return mp.sqrt(1-4*i)
for q in [mp.mpf('0.1'), mp.mpf('0.2'), mp.mpf(2)/9-mp.mpf('1e-6')]:
    lhs = mp.quad(lambda i: mp.log(upsf(i)), [0,q]); rhs = q*mp.log(upsf(q))+(1-upsf(q))**2/2
    lhs2 = mp.quad(lambda i: (1-upsf(i))/gamf(i)**2/upsf(i), [0,q]); rhs2 = mp.log(upsf(q))-mp.log(gamf(q))/2
    P(f"q={mp.nstr(q,6)}: int log ups diff {mp.nstr(lhs-rhs,3)}; int C1/ups diff {mp.nstr(lhs2-rhs2,3)}")
k,nu,th = sp.symbols('k nu theta')
N = 3*k+nu+1-th
P("(라) 2N^2-9(2k+nu)(k-th) == (3nu+12+6th)k+2(nu+1-th)^2+9 nu th:",
  sp.expand(2*N**2-9*(2*k+nu)*(k-th) - ((3*nu+12+6*th)*k+2*(nu+1-th)**2+9*nu*th))==0)
P("x<=k/(3k-1)^2 at k=10000:", mp.mpf(10000)/29999**2, " 11/(2*9)=", mp.mpf(11)/18, " 350*2/81=", mp.mpf(700)/81,
  " 합:", mp.mpf(11)/18+mp.mpf(700)/81, " nu=-1: 9.26*(1-1/30000)^-4=", mp.mpf('9.26')*(1-mp.mpf(1)/30000)**-4)

# ---------- 3. 보조정리 gauss-coeff: g(kappa) 전개 ----------
P("== 3. g(kappa) 전개 ==")
ka = sp.symbols('kappa')
for nuv in (0,-1):
    Nt = 3+(nuv+1-th)*ka
    xx = (1-th*ka)*ka/Nt**2
    xn = (2+(nuv-1)*ka)*(1-th*ka)/Nt**2
    nn = sp.expand(Nt**2-4*(2+(nuv-1)*ka)*(1-th*ka))
    P(f"nu={nuv}: n(kappa) =", sp.collect(nn, ka), " 글:", sp.expand(1+(2*nuv+10+2*th)*ka+((nuv+1)**2+2*(nuv-3)*th+th**2)*ka**2))
    gg = sp.sqrt(nn)/Nt
    c1,c2,c3 = Cs(gg)
    uh = (1+gg)/2 + xx*c1 + xx**2*c2 + xx**3*c3
    gk = (Nt*uh-2-nuv*ka)/ka
    s = sp.series(gk, ka, 0, 5).removeO()
    cs = [sp.expand(sp.simplify(s.coeff(ka,i))) for i in range(5)]
    P(f"  g 계수 kappa^0..4:", cs)
    P("   글의 kappa^1:", sp.expand(-(26+4*nuv+8*th)), " kappa^2:", sp.expand(506+97*nuv+5*nuv**2+(168+16*nuv)*th+12*th**2))
    g3 = sp.lambdify(th, cs[3]); g4 = sp.lambdify(th, cs[4])
    P("   max|g3|,|g4| on theta in [0,1]:", max(abs(g3(t/100)) for t in range(101)), max(abs(g4(t/100)) for t in range(101)))
    # 손 전개 확인
    P("   Nt*ups0 series:", sp.series(Nt*(1+gg)/2, ka, 0, 3).removeO().expand(), " 글: 2+(nu+3)k-(2nu+6+4th)k^2 =", sp.expand(2+(nuv+3)*ka-(2*nuv+6+4*th)*ka**2))
    P("   gamma series:", sp.series(gg, ka, 0, 2).removeO().expand(), " 글: 1/3+(2nu+14+4th)/9 k =", sp.expand(sp.Rational(1,3)+(2*nuv+14+4*th)*ka/9))
    P("   C1 series:", sp.series(c1, ka, 0, 2).removeO().expand(), " 글: 3-(5nu+35+10th)k =", sp.expand(3-(5*nuv+35+10*th)*ka))
    P("   x series:", sp.series(xx, ka, 0, 3).removeO().expand(), " 글:", sp.expand(ka/9*(1-(th+sp.Rational(2,3)*(nuv+1-th))*ka)))
    P("   Nt x C1:", sp.series(Nt*xx*c1, ka, 0, 3).removeO().expand(), " 글: k-(2nu+4th+12)k^2 =", sp.expand(ka-(2*nuv+4*th+12)*ka**2))
    P("   Nt x^2 C2:", sp.series(Nt*xx**2*c2, ka, 0, 3).removeO().expand(), " 글: -8k^2")
# Cauchy 경계 수치
P("|n-1| 최대 at |kappa|=1/100:", 12*0.01+7*0.0001, " gamma 범위:", mp.sqrt(1-0.1208)/3.01, mp.sqrt(1+0.1208)/2.99,
  " |g| 상계 (3.01*0.7+2+0.01)*100 =", (3.01*0.7+2+0.01)*100)
P("9300 확인: 3.01*2e7/9^4*(1-1/30000)^-8 =", 3.01*2e7/6561*(1-1/30000)**-8)
kk = mp.mpf(1)/30000
P("(4.8) 네 항:", 16988*kk, 404903*kk**2, 1000*100**5*kk**3/(1-100*kk), 9300*kk, " 합:", 16988*kk+404903*kk**2+1000*100**5*kk**3/(1-100*kk)+9300*kk)

# ---------- 4. (4.9)와 M4/M0 ----------
P("== 4. (4.9), M4/M0 ==")
n,y,vt = sp.symbols('n y vartheta')
Nn = n+y+1
H1 = sp.symbols('H1')  # He_{n-1}
H0 = (n+vt)*H1
He = {0:H0, 1:H1}
# He_{j} = N He_{j-1} - (j-1) y He_{j-2}  ->  He_{j-2} = (N He_{j-1} - He_j)/((j-1) y)
for i in range(2,6):
    # He_{n-i} = (N He_{n-i+1} - He_{n-i+2}) / ((n-i+1) y)
    He[i] = sp.simplify((Nn*He[i-1]-He[i-2])/((n-i+1)*y))
def numer(r):
    return sum(sp.binomial(r+1,i)*(-1)**i*sp.ff(n,i)*He[i] for i in range(r+2))
ratio2 = sp.simplify(numer(2)/numer(0))
P("(4.9) M2/M0 == 1-2n/y+n(n+1)/y^2-n(n+1)/(y^2 vt):", sp.simplify(ratio2-(1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*vt)))==0)
P("     == (vt[(n-y)^2+n]-n(n+1))/(y^2 vt):", sp.simplify(ratio2-(vt*((n-y)**2+n)-n*(n+1))/(y**2*vt))==0)
ratio4 = sp.simplify(numer(4)/numer(0))
for nuv,txt in ((0, 1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/vt), (-1, 1+12/k-6/k**2-(4+26/k-14/k**2)/vt)):
    r4 = ratio4.subs({n:2*k+nuv, y:k})
    P(f"M4/M0 nu={nuv} 글의 식과 일치:", sp.simplify(r4-txt)==0)
    center = 4-(26+4*nuv)/k+(506+97*nuv+5*nuv**2)/k**2
    expr = sp.series(txt.subs(vt,center), k, sp.oo, 4)
    P(f"   중심값 대입 전개 (k->oo):", expr)
# P 다항식 계수
for nuv in (0,-1):
    center = 4-(26+4*nuv+8*th)/k+(506+97*nuv+5*nuv**2+(168+16*nuv)*th+12*th**2)/k**2
    nn_=2*k+nuv; yy=k-th
    Pp = sp.expand(center*((nn_-yy)**2+nn_)-nn_*(nn_+1))
    P(f"nu={nuv}: (n-y)^2+n =", sp.expand((nn_-yy)**2+nn_), "; P k^2:", Pp.coeff(k,2), " k^1:", Pp.coeff(k,1), " k^0:", sp.expand(Pp.coeff(k,0)))
    den = sp.expand(yy**2*center)
    P("   y^2 vt: k^2", den.coeff(k,2), " k^1", sp.expand(den.coeff(k,1)))
    e1 = sp.expand(k*Pp+5*den); e2 = sp.expand(100*k*Pp+499*den)
    P("   kP+5y^2vt: k^3", e1.coeff(k,3), " k^2", e1.coeff(k,2), " k^1", sp.expand(e1.coeff(k,1)), "; 100kP+499y^2vt: k^3", e2.coeff(k,3), " k^2", sp.expand(e2.coeff(k,2)))

# ---------- 5. 넷째 단계: l, M0 하계 ----------
P("== 5. M0 하계 사슬 ==")
for K in (10000, 30000, 10**6):
    for nuv in (0,-1):
        nn_ = 2*K+nuv
        l = (-(nn_-K-1)+mp.sqrt((nn_-K-1)**2+4*nn_))/2
        U = nn_+l; NN = nn_+K+1; W = nn_-K-1+2*l
        a = (NN-U)**2/(2*K)-mp.mpf(K)/2
        b = nn_*mp.log(U/(nn_+1))
        c = mp.sqrt(U/W)
        P(f"k={K} nu={nuv}: l={mp.nstr(l,12)} in [2-2/k,2]: {2-2/mp.mpf(K)<=l<=2}; (N-U)^2/2k-k/2={mp.nstr(a,8)}>=-1; n log(U/(n+1))={mp.nstr(b,10)} >= 1-11/(4k)={mp.nstr(1-11/(4*mp.mpf(K)),10)}: {b>=1-11/(4*mp.mpf(K))}; sqrt(U/W)={mp.nstr(c,10)} >= sqrt2(1-3/k)={mp.nstr(mp.sqrt(2)*(1-3/mp.mpf(K)),10)}: {c>=mp.sqrt(2)*(1-3/mp.mpf(K))}")
    Kf = mp.mpf(K)
    lhs = mp.sqrt(2)*(1-3/Kf)**2*mp.e**(-mp.mpf(11)/(4*Kf)-10/Kf)*(4-26/Kf); rhs = 4*mp.sqrt(2)*(1-26/Kf)
    P(f"   M0 하계식 좌 {mp.nstr(lhs,10)} >= 우 {mp.nstr(rhs,10)}: {lhs>=rhs}")
P("4sqrt2(1-26/10000)=", 4*mp.sqrt(2)*(1-mp.mpf(26)/10000), " 4sqrt2(1-26/30000)=", 4*mp.sqrt(2)*(1-mp.mpf(26)/30000))
P("vt 상계 4-22/k+512/k^2 <4 ok; (4.8) 중심 최대: nu=-1,theta=0: 4-22/k+414/k^2; 허용폭 3 -> 417 <= 512")

# ---------- 6. 정리 4.7 / 따름정리 ----------
P("== 6. 실수 비교 상수 ==")
a0 = mp.quad(lambda w: mp.e**(-w**3/3), [0, mp.inf]); a1 = mp.quad(lambda w: w*mp.e**(-w**3/3), [0, mp.inf])
a3 = mp.quad(lambda w: w**3*mp.e**(-w**3/3), [0, mp.inf])
P("a0=", a0, " =3^(-2/3)Gamma(1/3):", mp.power(3,-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3), " a1=", a1, " =3^(-1/3)Gamma(2/3):", mp.power(3,-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3), " a3=", a3)
P("1.287899<a0<1.2879:", mp.mpf('1.287899')<a0<mp.mpf('1.2879'), " 0.938892<a1<0.939:", mp.mpf('0.938892')<a1<mp.mpf('0.939'))
P("꼬리: int_4^inf e^{-w^3/3} =", mp.quad(lambda w: mp.e**(-w**3/3),[4,mp.inf]), " <= e^{-64/3}/16 =", mp.e**(-mp.mpf(64)/3)/16,
  "; int_4^inf w e^{-w^3/3} =", mp.quad(lambda w: w*mp.e**(-w**3/3),[4,mp.inf]), " <= e^{-64/3}/4 =", mp.e**(-mp.mpf(64)/3)/4)
om = Fr(699,100)
val = om - Fr(7,2) - (6*om+Fr(3,4))/31 - (13*om/2)/961 - 12*om/30000
P("(나) 정확 유리수:", val, " == 495594511/240250000:", val==Fr(495594511,240250000), " >2:", val>2, float(val))
P("   (4w+1/2)*3/2 = 6w+3/4:", 4*om+Fr(1,2), (4*om+Fr(1,2))*Fr(3,2), 6*om+Fr(3,4), "; 31^3=", 31**3)
om2 = mp.mpf(698)/100; k13 = mp.mpf(10000)**(-mp.mpf(1)/3)
val2 = om2 - mp.mpf(7)/2 - (4*om2+mp.mpf(1)/2)*mp.mpf('1.2879')*k13 - (13*om2/2)*mp.mpf('0.939')*k13**2 - 12*om2/10000
P("(다) k^{-1/3}=", k13, " 값(상계 a 사용)=", val2, " >=1.6809:", val2>=mp.mpf('1.6809'))
val2b = om2 - mp.mpf(7)/2 - (4*om2+mp.mpf(1)/2)*mp.mpf('1.2879')*mp.mpf('0.0464159') - (13*om2/2)*mp.mpf('0.939')*mp.mpf('0.0464159')**2 - 12*om2/10000
P("   k^{-1/3}<=0.0464159 사용:", val2b, " 기록 Theorem1_LB_at_K1=1.680919551923166")
# 정리 4.7 단계 확인: 부등식들
P("log(1+x)>2x/(2+x) 도함수 x^2/((1+x)(2+x)^2):", sp.simplify(sp.diff(sp.log(1+h)-2*h/(2+h),h)-h**2/((1+h)*(2+h)**2))==0)
P("Bor(j+1)/Bor(j)=e^-1(1+1/j)^(j-1):", all(abs(mp.e**(-1)*(1+mp.mpf(1)/j)**(j-1) - (mp.e**(-(j+1))*(j+1)**j/mp.factorial(j+1))/(mp.e**(-j)*j**(j-1)/mp.factorial(j)))<1e-25 for j in (1,2,5,10)))
v=sp.symbols('v',positive=True)
F = -sp.log(1-v)-v; rho_ = F - v**2/2
P("rho'=v^2/(1-v):", sp.simplify(sp.diff(rho_,v)-v**2/(1-v))==0, " F'=v/(1-v):", sp.simplify(sp.diff(F,v)-v/(1-v))==0,
  " (v^4/(4F))'=v^3/F-v^5/(4(1-v)F^2):", sp.simplify(sp.diff(v**4/(4*F),v)-(v**3/F-v**5/(4*(1-v)*F**2)))==0)
# p(v) 조립 확인 (chi 기호)
chi, om_s, ks = sp.symbols('chi omega k_s', positive=True)
# F = v^2/(2 chi)
Fc = v**2/(2*chi)
orig = (ks/4*v**6+om_s/2*v**4)*(1/Fc-sp.Rational(1,2)-3/(2*ks*Fc**2)) - v*sp.exp(-v**2/2)
# IBP: replace (k/4) v^6/F  (times f/(1-v)) by  (1-v) v^3/F - v^5/(4F^2)
ibp = orig - ks/4*v**6/Fc + ((1-v)*v**3/Fc - v**5/(4*Fc**2))
ptext = v*(2*(1-v)*chi-chi**2-sp.exp(-v**2/2)) + om_s*v**2*chi - sp.Rational(3,2)*v**2*chi**2 - 3*om_s/ks*chi**2 - ks/8*v**6 - om_s/4*v**4
P("p(v) 조립식 일치:", sp.simplify(ibp-ptext)==0)
P("2(1-v)chi-chi^2 == (1-v)^2-(chi-1+v)^2:", sp.simplify(2*(1-v)*chi-chi**2-((1-v)**2-(chi-1+v)**2))==0)
P("int w^3 e^{-w^3/3} == int e^{-w^3/3}:", abs(a3-a0)<1e-20)
P("계수 모음: k^{-1/3}: (w+1/2+3w)a0 ; k^{-2/3}: (w/2+6w)a1 ; 1/k: 12w  -- 확인됨 (손)")

# ---------- 7. Borel 꼬리 전개 상수 ----------
P("== 7. Borel 꼬리 전개 ==")
def Bor(j):
    j = mp.mpf(j); return mp.e**(-j)*j**(j-1)/mp.factorial(j)
for K in (1000, 10000):
    s1 = mp.fsum(j*Bor(j) for j in range(1,K+1))
    approx = 2*mp.sqrt(K/(2*mp.pi)) - mp.mpf(2)/3
    P(f"k={K}: sum j Bor(j) - (2 sqrt(k/2pi) - 2/3) = {mp.nstr(s1-approx,6)}  허용 [0, (2/3)(2pi)^-1/2 eps]=[0,{mp.nstr(mp.mpf(2)/3/mp.sqrt(2*mp.pi)/mp.sqrt(K),6)}]")
    tail = 1 - mp.fsum(Bor(j) for j in range(1,K+1))
    diff = 2/mp.sqrt(2*mp.pi*K) - tail
    P(f"   2(2pi)^-1/2 eps - Bor^tail_k(1) = {mp.nstr(diff,6)} in [0, 5/9 (2pi)^-1/2 eps^3 = {mp.nstr(mp.mpf(5)/9/mp.sqrt(2*mp.pi)/mp.mpf(K)**1.5,6)}]")
    # Robbins
    P("   Robbins: max over j<=k of (2pi)^-1/2 j^-3/2 - Bor(j) in [0, (1/12)(2pi)^-1/2 j^-5/2]:",
      all(0 <= (1/mp.sqrt(2*mp.pi)*mp.mpf(j)**-1.5 - Bor(j)) <= (1/mp.sqrt(2*mp.pi)*mp.mpf(j)**-2.5)/12 for j in list(range(1,50))+[100,1000,K]))
# T(e^{-1-U}) 전개
def Tfun(x):  # tree function via Lambert
    return -mp.lambertw(-x)
for U in (mp.mpf('1e-4'), mp.mpf('1e-6')):
    T = Tfun(mp.e**(-1-U)); P(f"U={U}: T(e^-1-U) - (1 - sqrt(2U) + 2U/3) = {mp.nstr(T-(1-mp.sqrt(2*U)+2*U/3),4)} (U^1.5={mp.nstr(U**1.5,3)}); T/(1-T) - ((2U)^-1/2 - 2/3) = {mp.nstr(T/(1-T)-((2*U)**-0.5-mp.mpf(2)/3),4)}")
P("(4.11) 주항 모임: 2+2phi-int iota^-3/2(e^-phi iota -1+phi iota) = Bor^ld(phi): 2phi = int_0^1 iota^-3/2 phi iota diota =", mp.quad(lambda i: i**-1.5*i, [0,1]), "* phi")
P("e^{2.079}=", mp.e**mp.mpf('2.079'), "<8")

# ---------- 8. 수직선: Dawson, F0, F1, J 선도 ----------
P("== 8. 수직선 적분 ==")
mp.mp.dps = 20
def Daw(b): return mp.sqrt(mp.pi/2)*mp.e**(-b**2/2)*mp.erfi(b/mp.sqrt(2))
def BldR_int(b): return 2 + mp.quad(lambda i: i**-1.5*(1-mp.e**(b**2*i/2)), [0,1])
for b in (mp.mpf('0.3'), mp.mpf(1), mp.mpf(2)):
    P(f"beta={b}: Bor^ld_R(int)={mp.nstr(BldR_int(b),12)}  e^{{b^2/2}}(2-2bD)={mp.nstr(mp.e**(b**2/2)*(2-2*b*Daw(b)),12)}; betaD={mp.nstr(b*Daw(b),6)}")
P("max beta*D(beta) ~", max(b/10*Daw(mp.mpf(b)/10) for b in range(0,100)), " <=2")
def BldR(b): return mp.e**(b**2/2)*(2-2*b*Daw(b))
ninf = 2/mp.sqrt(mp.pi)
def Pq(z,r): mu=1-r**2; return mu*z**2+mu**2*z**4/4
def F0(z):
    return -ninf*z**4*mp.e**(-z**2)*mp.quad(lambda r: r**2*mp.e**((1-r**2)*z**2/2)*Pq(z,r)*BldR(r*z)/mp.sqrt(2*mp.pi), [0,1])
def F1(z):
    return -ninf*z**4*mp.e**(-z**2)*mp.quad(lambda r: r**2*mp.e**((1-r**2)*z**2/2)*Pq(z,r)*(mp.mpf(4)/3*r**2*z**2-mp.mpf(2)/3*r*z**4), [0,1])
I0 = 2*mp.quad(F0, [0,2,4,8]); I1 = 2*mp.quad(F1, [0,2,4,8])
P("int F0 =", I0, "(0이어야)   int F1 =", I1, " 46sqrt2-12 =", 46*mp.sqrt(2)-12, " (-23+3sqrt2)(-2sqrt2)=", (-23+3*mp.sqrt(2))*(-2*mp.sqrt(2)))
def crho(z,r): return (2-r**3)/3*z**3 - r*z
IJ = mp.quad(lambda z: z**3*mp.e**(-z**2/2)*mp.quad(lambda r: r*crho(z,r),[0,1]), [-mp.inf,0,mp.inf])
P("J 선도 적분 =", IJ, " 3sqrt(2pi)=", 3*mp.sqrt(2*mp.pi), "; z^3 int rho c_rho = z^4/15 (4z^2-5):", sp.simplify(sp.integrate(sp.symbols('r')*((2-sp.symbols('r')**3)/3*v**3-sp.symbols('r')*v),(sp.symbols('r'),0,1))*v**3 - v**4/15*(4*v**2-5))==0)
# (4.14) 계수 모임
e173 = mp.mpf(1)/173
P("T_R 계수(G=1/16): 5/9=", mp.mpf(5)/9, " 2+(2/3)(25/48)=", 2+mp.mpf(2)/3*mp.mpf(25)/48, " 7/6+(13/12)(25/48)^2+(31/18)sqrt(2pi)eps=", mp.mpf(7)/6+mp.mpf(13)/12*(mp.mpf(25)/48)**2+mp.mpf(31)/18*mp.sqrt(2*mp.pi)*e173, " 1/27=", mp.mpf(1)/27)
e100 = mp.mpf(1)/100
P("T_R 계수(G=1/8): 2+(2/3)(13/24)=", 2+mp.mpf(2)/3*mp.mpf(13)/24, " beta^4:", mp.mpf(7)/6+mp.mpf(13)/12*(mp.mpf(13)/24)**2+mp.mpf(31)/18*mp.sqrt(2*mp.pi)*e100)
P("|phi|<=beta^2(1/2+ G/3): G=1/16 ->", mp.mpf(1)/2+mp.mpf(1)/48, "=25/48; G=1/8 ->", mp.mpf(1)/2+mp.mpf(1)/24, "=13/24; 2(-Re phi)>=beta^2(1-G^2/2):", 1-mp.mpf(1)/512, 1-mp.mpf(1)/128)
# 호 경계 수치
for K in (30000,):
    Kf = mp.mpf(K)
    P(f"k={K}: k^5 e^(-k/520)=", Kf**5*mp.e**(-Kf/520), " 130(k/256)^6 e^(-k/512)=", 130*(Kf/256)**6*mp.e**(-Kf/512),
      " y_k >= 255k/131072-511/262144 =", 255*Kf/131072-mp.mpf(511)/262144, " k/520=", Kf/520)
    P("   log sqrt(1+1/256) >= 1/512-1/262144:", mp.log(mp.sqrt(1+mp.mpf(1)/256)) >= mp.mpf(1)/512-mp.mpf(1)/262144, mp.log(mp.sqrt(1+mp.mpf(1)/256)), mp.mpf(1)/512-mp.mpf(1)/262144)
    P("   |kappa|^3 on arc <= (G^2+2(1+sqrt(1+G^2)))^1.5 =", (mp.mpf(1)/256+2*(1+mp.sqrt(1+mp.mpf(1)/256)))**1.5, "<12")
Kf = mp.mpf(10000)
P("G=1/8: y_k >= 63k/8192-127/16384 at k=1e4:", 63*Kf/8192-mp.mpf(127)/16384, "; log sqrt(1+1/64)>=1/128-1/32768:", mp.log(mp.sqrt(1+mp.mpf(1)/64)) >= mp.mpf(1)/128-mp.mpf(1)/32768,
  " (2k-1)(1/128-1/32768)-k/128 =", sp.expand((2*k-1)*(sp.Rational(1,128)-sp.Rational(1,32768))-k/128))
P("   1-G^2/2-1/2 = 63/128 =", mp.mpf(63)/128, ">=0.49")
# 정규화 상수
for K in (10000, 30000):
    Kf = mp.mpf(K)
    for nuv in (0,-1):
        nn_ = 2*K+nuv
        nk = mp.factorial(nn_)/mp.mpf(nn_+1)**(nn_-1)*mp.e**(nn_+1)/(2*mp.pi*Kf**1.5)
        Bn = Bor(K)*Kf**1.5*nk
        P(f"k={K} nu={nuv}: n_k={mp.nstr(nk,12)} in [n_inf={mp.nstr(ninf,12)}, n_inf e^(1/k)={mp.nstr(ninf*mp.e**(1/Kf),12)}]: {ninf<=nk<=ninf*mp.e**(1/Kf)}; Bn_k={mp.nstr(Bn,10)} <= sqrt2/pi e^(1/k)={mp.nstr(mp.sqrt(2)/mp.pi*mp.e**(1/Kf),10)}")
    P(f"   Bor(k) k^1.5={mp.nstr(Bor(K)*Kf**1.5,10)}; (2pi)^-1/2 e^(-1/12k)={mp.nstr(mp.e**(-1/(12*Kf))/mp.sqrt(2*mp.pi),10)}; (2pi)^-1/2(1-1/12k)={mp.nstr((1-1/(12*Kf))/mp.sqrt(2*mp.pi),10)}")
P("sqrt2/pi =", mp.sqrt(2)/mp.pi, " 3sqrt(2pi)=", 3*mp.sqrt(2*mp.pi), " 46sqrt2-12=", 46*mp.sqrt(2)-12)

# ---------- 9. 조립 ----------
P("== 9. 조립 ==")
P("(가) 11/2*39/100*2-7/2 =", Fr(11,2)*Fr(39,100)*2-Fr(7,2))
P("(가) k^{5/2} b_J < 0.451*3*2.51+0.056+0.01 =", 0.451*3*2.51+0.056+0.01, " 1678/30000=", 1678/30000)
P("(나) 5.642*1.6809*0.39893-0.0163-3.554 =", mp.mpf('5.642')*mp.mpf('1.6809')*mp.mpf('0.39893')-mp.mpf('0.0163')-mp.mpf('3.554'))
P("(나) J: 0.4503*3*2.50663+1675.2/10000 =", mp.mpf('0.4503')*3*mp.mpf('2.50663')+mp.mpf('1675.2')/10000)
P("(나) D: 46sqrt2-12-5468.28/100 =", 46*mp.sqrt(2)-12-mp.mpf('5468.28')/100, " *10000/9999 =", (46*mp.sqrt(2)-12-mp.mpf('5468.28')/100)*mp.mpf(10000)/9999)
P("(가) D: 1/2(53-5000/173-1/100)-1/100 =", (53-mp.mpf(5000)/173-mp.mpf(1)/100)/2-mp.mpf(1)/100)
P("D 일곱 상계 합(G=1/16):", 176+2304+118+935+533+455+243, " (G=1/8):", Fr('183.51')+Fr('2303.07')+Fr('203.57')+Fr('983.74')+Fr('920.70')+Fr('454.86')+Fr('418.83'))
kap = mp.mpf(1)/10000
P("부록 (ㄷ) Cauchy k>=10000: 1000(100 kappa)^9/(1-100kappa) /kappa^2 at k=1e4:", 1000*(100*kap)**9/(1-100*kap)/kap**2)
P("S/2^30 =", mp.mpf(2918732888)/2**30, " e=", mp.e)
open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_4_검산_해석_출력.txt","w",encoding="utf-8").write("\n".join(out))
