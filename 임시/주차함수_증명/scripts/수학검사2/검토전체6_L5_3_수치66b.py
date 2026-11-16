# 검토전체6 L5: 6.6절 Low(k,rho), O-bar, (6.49), lemma-M 상수
from mpmath import mp, mpf, sqrt, exp, log, e, pi
mp.dps = 30
def Low(k, rho):
    k = mpf(k); rho = mpf(rho); eps = k**(-mpf(1)/3); c = 1/sqrt(2*pi)
    br = 2*sqrt(rho) - mpf(2.218)*eps
    pre = c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))
    ex = rho**2*(1+rho*eps)**mpf(1.5)*exp(1/(4*(k+1)))/(c*br)
    return pre*exp(-ex)
print("Low(10001,1.4) =", Low(10001, 1.4), "(>=1.6813)")
print("Low(3131,0.75) =", Low(3131, 0.75), "(>=3.3537)")
def u(k):
    k=mpf(k); return 3/mpf(0.35)*(mpf(1.35)+1/k)*(mpf(0.65)-1/k)**(-mpf(1.5))/sqrt(k)
def dk(k):
    k=mpf(k); gW = 2*exp(mpf(0.0031))/e; up = mpf(0.5)+5/(2*k)+1/(4*k*k)
    return gW*up + u(k)/(e*2**mpf(1.5))
k = mpf(10001)
print("Obar(10001,1.4) =", dk(k)*exp(1+1/(12*k))*(1+mpf(1.4)*k**(-mpf(1)/3)+1/k)**mpf(1.5), "(<=1.1890)")
k = mpf(3131)
print("Obar(3131,0.75) =", dk(k)*exp(1+1/(12*k))*(1+mpf(0.75)*k**(-mpf(1)/3)+1/k)**mpf(1.5), "(<=1.2341)")
# (6.49)
wp = lambda m: mpf(1.99)+mpf(0.59963)*(m+1)**(mpf(2)/3)+mpf(1.24847)*(m+1)**(mpf(1)/3)
k = mpf(3131); uu = k**(mpf(1)/3)
print("u=k^(1/3) =", uu, " 이차식 =", mpf(0.15037)*uu**2-mpf(1.54829)*uu-mpf(1.3314), " 직접 차 =", mpf(0.75)*k**(mpf(2)/3) - (wp(k+mpf(0.75)*k**(mpf(2)/3))-1))
print("wp'(1) =", mpf(0.59963)*2/3*2**(-mpf(1)/3)+mpf(1.24847)/3*2**(-mpf(2)/3))
print("상수: 0.59963*2/3=", mpf(0.59963)*2/3, " 1.24847/3=", mpf(1.24847)/3, " 0.99+1.24847/4=", mpf(0.99)+mpf(1.24847)/4, " 0.59963/2+1.24847=", mpf(0.59963)/2+mpf(1.24847))
print("0.39976/14.629+0.41616/14.629^2 =", mpf(0.39976)/uu+mpf(0.41616)/uu**2)
a=mpf(0.15037); b=mpf(1.54829); c=mpf(1.3314)
print("큰 근 =", (b+sqrt(b*b+4*a*c))/(2*a))
# lemma-M
cc = 1/sqrt(2*pi); B = mpf(2.218)*mpf(3131)**(-mpf(1)/3)
print("B(3131) =", B, " R(1/2) consts:", 3/mpf(4)-2*cc*sqrt(mpf(0.5)), 2*(mpf(0.5))**mpf(1.5)-cc, " R(1/2)>=", mpf(0.18581)-mpf(0.30817)*mpf(0.152))
print("2.218*4^(-1/3) =", mpf(2.218)*4**(-mpf(1)/3), " 3*0.152=", 3*mpf(0.152), " c*sqrt2=", cc*sqrt(2))
# critical-front
print("0.3951/(e*2^1.5) =", mpf(0.3951)/(e*2**mpf(1.5)), " 0.0648*e*2^1.5 =", mpf(0.0648)*e*2**mpf(1.5))
# above-window
print("10*10001^(2/3) =", 10*mpf(10001)**(mpf(2)/3), " 10*2^(-2/3) =", 10*2**(-mpf(2)/3), " 1.4k^{2/3}<=(k+1)/2 at 10001:", mpf(1.4)*mpf(10001)**(mpf(2)/3), mpf(10002)/2)
print("far-window Low(k,1.4) increasing? Low(10001,1.4), Low(20000,1.4):", Low(10001,1.4), Low(20000,1.4))
