# N12 검산: D.central-gap-rational-audit의 (ㄱ)(ㄴ)(나)(다)(ㅅ)와 본문 산술
import sympy as sp
from fractions import Fraction as Fr
from mpmath import mp, mpf, quad, exp, sqrt, pi, e
mp.dps=30
# (ㄴ) 잔차 R(iota) = (uhat(iota)-1) uhat(iota-x) + iota, x의 급수. gamma = sqrt(1-4 iota)
g,x=sp.symbols('gamma x',positive=True)
def ups(gm): return (1+gm)/2
def C1(gm): return (1-gm)/(2*gm**2)
def C2(gm): return -(1-gm)*(5+gm)/(4*gm**5)
def C3(gm): return 5*(1-gm)*(6+gm-gm**2)/(4*gm**8)
def uhat(gm): return ups(gm)+x*C1(gm)+x**2*C2(gm)+x**3*C3(gm)
iota=(1-g**2)/4
gm2=g*sp.sqrt(1+4*x/g**2)   # gamma(iota - x)
R=(uhat(g)-1)*uhat(gm2)+iota
ser=sp.series(R,x,0,5).removeO()
coeffs=[sp.simplify(ser.coeff(x,i)) for i in range(5)]
print("coeff x^0..x^3 simplify:",coeffs[:4])
c4=sp.simplify(coeffs[4]); print("x^4 coeff (Laurent in gamma):",sp.factor(c4))
print("x^4 coeff at gamma=1/3:",c4.subs(g,sp.Rational(1,3)))
# C_i values at gamma=1/3
print("C1,C2,C3 at 1/3:",[sp.nsimplify(f(sp.Rational(1,3))) for f in (C1,C2,C3)])
# (ㄱ) a0, a1
a0=quad(lambda w: exp(-w**3/3),[0,4,mp.inf]); a1=quad(lambda w: w*exp(-w**3/3),[0,4,mp.inf])
print("a0=",a0," in (1.287899,1.2879):",1.287899<a0<1.2879," a1=",a1," in (0.938892,0.939):",0.938892<a1<0.939)
# (나) exact rational
w=Fr(699,100); val=w-Fr(7,2)-(6*w+Fr(3,4))/31-(13*w/2)/961-12*w/30000
print("(나) exact:",val,"== 495594511/240250000:",val==Fr(495594511,240250000)," >2:",val>2, float(val))
# (다) with a0<1.2879, a1<0.939, k=10000
w=mpf('6.98'); k=mpf(10000); k13=k**(-mpf(1)/3)
lb=w-mpf(3.5)-(4*w+mpf(0.5))*mpf('1.2879')*k13-(13*w/2)*mpf('0.939')*k13**2-12*w/k
print("(다) lower bound at k=10000:",lb," >=1.6809:",lb>=mpf('1.6809'), " k^{-1/3}=",k13)
# (ㅅ)
print("(ㅅ) 5.642*1.6809*0.39893-0.0163-3.554 =",5.642*1.6809*0.39893-0.0163-3.554)
print("sum G=1/16:",176+2304+118+935+533+455+243," sum G=1/8:",round(183.51+2303.07+203.57+983.74+920.70+454.86+418.83,2))
print("46sqrt2-12 =",46*sqrt(2)-12," -5000/173-0.02 ->",46*sqrt(2)-12-mpf(5000)/173-mpf('0.02')," ; -54.6828 ->",46*sqrt(2)-12-mpf('54.6828'))
print("k^5 e^{-k/520} at 30000:",mpf(30000)**5*exp(-mpf(30000)/520))
print("0.4503*3*2.50663+1675.2/10000 =",mpf('0.4503')*3*mpf('2.50663')+mpf('1675.2')/10000)
print("Bn bound sqrt2/pi e^{1/k}:",sqrt(2)/pi*exp(mpf(1)/10000), sqrt(2)/pi*exp(mpf(1)/30000))
print("4sqrt2(1-26/k) k=1e4:",4*sqrt(2)*(1-mpf(26)/10000)," k=3e4:",4*sqrt(2)*(1-mpf(26)/30000))
print("Cauchy terms k=30000:",16988/30000,404903/30000**2,1000*100**5/30000**3/(1-100/30000),9300/30000)
