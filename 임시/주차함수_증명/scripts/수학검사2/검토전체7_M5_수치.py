# 검토전체7 M5: 6장 수치 재계산 (python -I)
from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, ceil, quad, findroot
mp.dps = 40

def Bor(n):
    n = mpf(n)
    return exp(-n) * n**(n-1) / factorial(n)
def Ren(n):
    return mpf(n) * Bor(n)
def Psi(d):
    return sum(Ren(j) for j in range(1, d+1))
def g(x):
    x = mpf(x)
    return (x-1) * log(1 + 1/x)

print("== 6.1 정리 old-7-13 상수")
print("12000^(2/3)=", mpf(12000)**(mpf(2)/3), " ceil=", ceil(mpf(12000)**(mpf(2)/3)))
print("1-1.6/sqrt525=", 1 - mpf('1.6')/sqrt(525))
t1 = mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048)
t2 = mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3)
t3 = mpf('1.5')/(3*sqrt(525))
print("세 항:", t1, t2, t3, " 합:", t1+t2+t3, " x2:", 2*(t1+t2+t3))
print("1.2(1-2/525)^-5/2=", mpf('1.2')*(1-mpf(2)/525)**(-mpf(5)/2))
print("1.2(1+2/525)^1/2=", mpf('1.2')*(1+mpf(2)/525)**(mpf(1)/2))
print("1.5(1-1/525)^-5/2=", mpf('1.5')*(1-mpf(1)/525)**(-mpf(5)/2))
print("Up max sqrt2 check at 1/2:", (1-mpf(1)/2)**mpf('0.5')*(1+1))

print("== 6.2 B2")
def B2(k):
    k = mpf(k)
    return (1-1/e) + (exp(mpf(3)/2+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(42)=", B2(42), " B2(43)=", B2(43), " B2(2000)=", B2(2000), " 1-B2(2000)=", 1-B2(2000))
def tiltsum(k):
    xk = (mpf(k)/(k+1))**(k-1)
    q = e*xk
    return sum(Bor(n)*q**n for n in range(2, k+2))
print("tiltsum k=2:", tiltsum(2), " 8/9=", mpf(8)/9, " k=42:", tiltsum(42), " k=43:", tiltsum(43))
print("k*rho^L(3k) at k=2000:", mpf(3)/4*(1-mpf('1.2')/2000), " k*rho^H(3k)<=", mpf('0.307')*2000/3999)

print("== 6.3 lemma-omega 상수")
Xs = (5-sqrt(7))/6
print("X*=", Xs, " max=", Xs*(1-Xs)*(3-2*Xs), " (10+7sqrt7)/54=", (10+7*sqrt(7))/54)
print("tl^-1 bound:", 1/(1-mpf('0.75')/51), " e^(1/24+1/612)=", exp(mpf(1)/24+mpf(1)/612), " 1+1/51=", 1+mpf(1)/51)
u = exp(mpf(1)/24+mpf(1)/612)*(1/(1-mpf('0.75')/51))*(1+mpf(1)/51)*mpf(4)/3
print("u=", u, " 0.5282*1.449=", mpf('0.5282')*mpf('1.449'))
print("L/G V>=2:", mpf('1.5')/53*mpf(4)/3*mpf('0.5')*mpf('1.01961')*mpf('1.0150'))
print("L/G V=1:", mpf('1.5')/52*mpf('2.02')*mpf('0.51')*mpf('1.01961')*mpf('1.0150'))
print("e^(3/(2*51))=", exp(mpf(3)/102), " e^-2=", exp(-2), " 1.545/e=", mpf('1.545')/e)
y = 50
print("d=3 ratio at y=50:", mpf('0.0441')*(y-1)/(y+3)**2 / (mpf('1.2')*(y+1)/((y+2)**2*(y+3))))
print("c_{y+2} lower const:", 2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/51, " 0.2/e*0.6=", mpf('0.2')/e*mpf('0.6'))
print("d=y+2 ratio:", mpf('1.03')*exp(-1)/2)

print("== 6.4 u(k)")
def u_k(k):
    k = mpf(k)
    return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
print("u(3131)=", u_k(3131), " 2u=", 2*u_k(3131), " u/2=", u_k(3131)/2)
print("8.5715*1.35032*1.9097*0.017872=", mpf('8.5715')*mpf('1.35032')*mpf('1.9097')*mpf('0.017872'))
print("(2*3131)^(2/3)=", mpf(6262)**(mpf(2)/3), " 0.65*3131-1=", mpf('0.65')*3131-1)
print("9*(3/2)^1.5=", 9*mpf('1.5')**mpf('1.5'), " *4/3=", 9*mpf('1.5')**mpf('1.5')*4/3)
print("20001^(1/3)=", mpf(20001)**(mpf(1)/3), " wp(20000)=", mpf('1.99')+mpf('0.59963')*mpf(20001)**(mpf(2)/3)+mpf('1.24847')*mpf(20001)**(mpf(1)/3))

print("== 6.5 V-핵심 상수")
print("24000/2263^1.5=", 24000/mpf(2263)**mpf('1.5'))
print("50.62/sqrt3130=", mpf('50.62')/sqrt(3130))
def v_k(k):
    k = mpf(k)
    vp = max(k+1, mpf(4000)); io = 2*k+1-vp
    a = 2*min(mpf(1), 3*vp*io**(-mpf(3)/2)); b = 2*u_k(k); c = mpf('50.62')/sqrt(k-1)
    return 2-a-b-c, a, b, c
for k in (3131, 6667, 10000):
    print("v(%d)=" % k, v_k(k))
print("c*=", mpf(1)/sqrt(2*pi))
c = 1/sqrt(2*pi)
print("3c(8.133+10.301c)=", 3*c*(mpf('8.133')+mpf('10.301')*c))
print("1.5*2.7323*0.8051*c*(17.951+23.462c)=", mpf('1.5')*mpf('2.7323')*mpf('0.8051')*c*(mpf('17.951')+mpf('23.462')*c))
# c(tp,kappa) and Gamma
tp = mpf('0.55'); ka = mpf('2.4978')
root = (ka*tp+2 + sqrt((ka*tp+2)**2 - 4*tp*ka))/(2*tp)
print("큰 근=", root, " c(0.55,2.4978)=", (root**2-ka*root)*exp(-tp*root))
x = mpf(3132)/3130
print("Gamma_0.55(3132/3130)=", x/((1+x)**(1-tp)-1))
print("ex_max at 3130:", mpf(3131)/6261, " 2-ex-20/(9t):", 2-mpf(3131)/6261-mpf(20)/(9*3130), " kappa_d min:", mpf('1.498')+2*mpf(3130)/6261)
# lemma-N derivatives
import mpmath
def kI(s): L = log(s); return s**mpf('1.5')*(1+3*L+mpf('1.125')*L**2)
def kX(s): L = log(s); return s**mpf('1.5')*(1+mpf('1.5')*L)
print("kI'(1),kI''(1)=", mpmath.diff(kI, 1), mpmath.diff(kI, 1, 2), " kI''' max over [1,2]:", max(mpmath.diff(kI, 1+mpf(i)/20, 3) for i in range(21)))
print("kX'(1),kX''(1)=", mpmath.diff(kX, 1), mpmath.diff(kX, 1, 2))
print("12.15 check:", mpf('4.5')*2+mpf('4.5')*mpf(2)/3+mpf('0.375')*mpf(2)/5, " 4.908 check:", mpf('4.5')*mpf(2)/3+mpf('4.5')*mpf(2)/5+mpf('0.375')*mpf(2)/7)

print("== 6.6 prop-W / prop-R / Low / O-bar")
print("Psi(14)=", Psi(14), " Psi(14)/(2e)=", Psi(14)/(2*e))
k = mpf(3131)
f1 = sqrt(2*pi)*(k+15)**mpf('1.5')*Bor(k+15)*(k/(k+15))**mpf('1.5')*(k+1)/(k+14)
print("첫 세 인자 곱 k=3131:", f1, " Fr/(sB k^-3/2)=", f1*Psi(14)/(2*e))
ups = mpf('0.5')+mpf('5')/(2*k)+1/(4*k**2)
gW = 2*exp(mpf('0.0031'))/e
print("gamma_W=", gW, " ups=", ups, " ups*gW=", ups*gW)
print("(e+3/4)/3131=", (e+mpf('0.75'))/3131, " 0.5006*3.469^2=", mpf('0.5006')*mpf('3.469')**2, " 6.03/3131=", mpf('6.03')/3131)
print("max (1-D)(1+0.7183D)/(2-D):", max((1-D)*(1+mpf('0.7183')*D)/(2-D) for D in [mpf(i)/1000 for i in range(1001)]))
print("3.51/3131=", mpf('3.51')/3131)
d_3131 = ups*gW + u_k(3131)/(e*2**mpf('1.5'))
print("d(3131)=", d_3131, " u/(e 2^1.5)=", u_k(3131)/(e*2**mpf('1.5')))
k2 = mpf(10001)
ups2 = mpf('0.5')+mpf('5')/(2*k2)+1/(4*k2**2)
d_10001 = ups2*gW + u_k(10001)/(e*2**mpf('1.5'))
print("d(10001)=", d_10001)
print("Obar(10001,1.4):", d_10001*exp(1+1/(12*k2))*(1+mpf('1.4')*k2**(-mpf(1)/3)+1/k2)**mpf('1.5'))
print("Obar(3131,0.75):", d_3131*exp(1+1/(12*k))*(1+mpf('0.75')*k**(-mpf(1)/3)+1/k)**mpf('1.5'))
def Low(k, rho):
    k = mpf(k); rho = mpf(rho); eps = k**(-mpf(1)/3); c = 1/sqrt(2*pi)
    br = 2*sqrt(rho) - mpf('2.218')*eps
    return c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf('1.5')*exp(1/(4*(k+1)))/(c*br))
print("Low(10001,1.4)=", Low(10001, '1.4'), " Low(3131,0.75)=", Low(3131, '0.75'))
print("E3 const 0.0648*e*2^1.5=", mpf('0.0648')*e*2**mpf('1.5'), " 0.3951/(e 2^1.5)=", mpf('0.3951')/(e*2**mpf('1.5')))
print("R(1/2) consts: 3/4-2c/sqrt2=", mpf(3)/4-2/sqrt(2*pi)/sqrt(mpf('0.5')), " 2*(1/2)^1.5-c=", 2*mpf('0.5')**mpf('1.5')-1/sqrt(2*pi), " 2.218*3131^-1/3=", mpf('2.218')*mpf(3131)**(-mpf(1)/3))
# small-k-bulk (6.49)
uu = mpf(3131)**(mpf(1)/3)
print("u=k^(1/3)=", uu, " 0.15037u^2-1.54829u-1.3314=", mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'))
def wp(m): m = mpf(m); return mpf('1.99')+mpf('0.59963')*(m+1)**(mpf(2)/3)+mpf('1.24847')*(m+1)**(mpf(1)/3)
print("0.75k^(2/3)-(wp(k+0.75k^(2/3))-1)=", mpf('0.75')*k**(mpf(2)/3) - (wp(k+mpf('0.75')*k**(mpf(2)/3))-1))
print("wp'(1)=", mpf('0.39976')*2**(-mpf(1)/3)+mpf('0.41616')*2**(-mpf(2)/3))
print("큰 근:", (mpf('1.54829')+sqrt(mpf('1.54829')**2+4*mpf('0.15037')*mpf('1.3314')))/(2*mpf('0.15037')))
print("10*10001^(2/3)=", 10*mpf(10001)**(mpf(2)/3))
# v-negative LHS/RHS at k=3131
k = 3131
for d in range(1, 15):
    L = (k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/(k+d))
    R = 2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1, d)))
    print("d=%d L=%s R=%s" % (d, mpmath.nstr(L, 6), mpmath.nstr(R, 4)))
# theorem-D (ㄷ) constants
print("0.7979*int sqrt from1 to d-1 coefficient 2/3*0.7979=", mpf(2)/3*mpf('0.7979'))
print("Robbins: 1.732 vs (1+1/3)^1.5-1 over 1/3:", ((1+mpf(1)/3)**mpf('1.5')-1)*3, " e^(1/(12*702))-1 times 701:", (exp(1/(12*mpf(702)))-1)*701)
m = mpf(701); d = m**(mpf(2)/3)/2
print("k=d^1.5/(m-d) at m=701:", d**mpf('1.5')/(m-d), " es<=0.798k:", mpf('0.798')*d**mpf('1.5')/(m-d), " 0.0563:", mpf(701)**(-mpf(1)/3)/2)
