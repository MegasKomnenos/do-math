# K5: 6.6절 상수 재계산
from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, findroot
mp.dps = 30
Bor = lambda n: exp(-n)*mpf(n)**(n-1)/factorial(n)
Ren = lambda n: n*Bor(n)
Psi = lambda d: sum(Ren(j) for j in range(1, d+1))
sB = e/sqrt(2*pi)
k = mpf(3131)
print("Psi(14)", Psi(14), "Psi(14)/(2e)", Psi(14)/(2*e))
f1 = sqrt(2*pi)*(k+15)**mpf(1.5)*Bor(3146)*(k/(k+15))**mpf(1.5)*(k+1)/(k+14)
print("factor at 3131", f1, "Fr/(sB k^-3/2)", f1*Psi(14)/(2*e))
gW = 2*exp(mpf('0.0031'))/e; ups = mpf('0.5')+5/(2*k)+1/(4*k*k)
print("gamma_W", gW, "ups", ups, "ups*gW", ups*gW)
def u(k):
    k = mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
def dk(k):
    k = mpf(k); return gW*(mpf('0.5')+5/(2*k)+1/(4*k*k)) + u(k)/(e*2**mpf(1.5))
print("u(3131)/(e 2^1.5)", u(3131)/(e*2**mpf(1.5)), "d(3131)", dk(3131), "d(10001)", dk(10001))
# max of (1-D)(1+0.7183D)/(2-D)
g = lambda D: (1-D)*(1+mpf('0.7183')*D)/(2-D)
print("max g:", max(g(mpf(i)/10000) for i in range(0,10001)))
print("(e+0.75)/3131", (e+mpf('0.75'))/k, "0.5006*k*(3.469/k)^2", mpf('0.5006')*k*(mpf('3.469')/k)**2)
print("3.51/3131", mpf('3.51')/k, "1+7/k times 0.509", (1+7/k)*mpf('0.509'))
print("log2+0.00113+0.00193", log(2)+mpf('0.00113')+mpf('0.00193'), "log2+0.0031", log(2)+mpf('0.0031'))
# check d=14 vs Ren/Psi >= 1/(5d)
for d in (14, 20, 100):
    print(d, Ren(d+1)/Psi(d), 1/(5*mpf(d)))
# far-window / small-k-bulk 수치
def Low(k, rho):
    k = mpf(k); rho = mpf(rho); eps = k**(-mpf(1)/3); c = 1/sqrt(2*pi)
    br = 2*sqrt(rho)-mpf('2.218')*eps
    return c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf(1.5)*exp(1/(4*(k+1)))/(c*br))
print("Low(10001,1.4)", Low(10001, mpf('1.4')), "Low(3131,0.75)", Low(3131, mpf('0.75')))
def Obar(k, coef):
    k = mpf(k); return dk(k)*exp(1+1/(12*k))*(1+coef*k**(-mpf(1)/3)+1/k)**mpf(1.5)
print("Obar(10001,1.4)", Obar(10001, mpf('1.4')), "Obar(3131,0.75)", Obar(3131, mpf('0.75')))
wp = lambda n: mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3)
k = mpf(3131); uu = k**(mpf(1)/3)
print("u=k^(1/3)", uu, "(6.49) diff", mpf('0.75')*k**(mpf(2)/3) - (wp(k+mpf('0.75')*k**(mpf(2)/3))-1), "quad", mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'))
print("large root", (mpf('1.54829')+sqrt(mpf('1.54829')**2+4*mpf('0.15037')*mpf('1.3314')))/(2*mpf('0.15037')))
print("wp'(1)", mpf('0.39975')*2**(-mpf(1)/3)+mpf('0.41616')*2**(-mpf(2)/3))
print("E3 coef 0.3951/(e 2^1.5)", mpf('0.3951')/(e*2**mpf(1.5)), "0.0648 e 2^1.5", mpf('0.0648')*e*2**mpf(1.5))
print("2.218/3131^(1/3)", mpf('2.218')/uu, "R(1/2) parts", mpf(3)/4-2*(mpf(1)/2)**mpf(1.5)*0+0, 2*(mpf(1)/2)**mpf(1.5), 2/sqrt(2*pi)*sqrt(mpf(1)/2), 1/sqrt(2*pi))
print("24000/2263^1.5", 24000/mpf(2263)**mpf(1.5), "10*10001^(2/3)", 10*mpf(10001)**(mpf(2)/3), "1.4*10001^(2/3)", mpf('1.4')*mpf(10001)**(mpf(2)/3))
print("10*2^(-2/3)", 10*2**(-mpf(2)/3))
