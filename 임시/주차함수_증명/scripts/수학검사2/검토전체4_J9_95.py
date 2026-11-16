# 9.5절 수치 검산 (J9)
from mpmath import mp, mpf, sqrt, exp, pi, e, zeta, floor
mp.dps = 25
k = mpf(6668)
print("zeta(1/2) =", zeta(mpf(1)/2), " zeta(3/2) =", zeta(mpf(3)/2))
print("(2pi)^-1/2 =", 1/sqrt(2*pi), " 1.46036+2.61238/12 =", mpf('1.46036')+mpf('2.61238')/12)
print("gap: 0.3989423*1.67806-0.3989*1.678 =", (1/sqrt(2*pi))*mpf('1.67806')-mpf('0.3989')*mpf('1.678'), " coef 2*(0.3989423-0.3989)=", 2*(1/sqrt(2*pi)-mpf('0.3989')))
print("Psi(1)=1/e=", 1/e, " 0.3989*0.322=", mpf('0.3989')*mpf('0.322'))
print("0.367 check:", exp(-mpf(1)/12)/sqrt(2*pi))
print("a lower bound at 6668:", mpf('0.48')*k-1-8*k**(mpf(2)/3), " e^{-1/(12*366)}=", exp(-1/(12*mpf(366))))
print("(2/3)/6667 =", (mpf(2)/3)/6667, " (1+1/6667)^{2/3}-1 =", (1+1/mpf(6667))**(mpf(2)/3)-1)
print("0.08 k^{2/3}-1 =", mpf('0.08')*k**(mpf(2)/3)-1)
print("Psi^low zero:", (mpf('1.678')/2)**2)
print("0.0447 check: 1.678*0.08/3 =", mpf('1.678')*mpf('0.08')/3, " k^{2/3} threshold:", mpf('1.678')/(mpf('1.678')*mpf('0.08')/3))
# 9.4 old-7-26 numbers
nu = mpf('0.112')*k
print("k rhoL at 0.112k <=", 1.5*mpf('0.112')/mpf('1.112'), " k rhoH >=", (1-mpf('1.5')/k)*mpf('0.307')/mpf('1.112')-47/(24*k))
print("k rhoH(3k+1) >=", (1-mpf('1.5')/k)*mpf('0.1535')-47/(24*k))
print("1.2366 check 1.112^2 =", mpf('1.112')**2, " 1.5*0.7654/1.2366 =", mpf('1.5')*(1-mpf('1.2')/k)*mpf('0.7654')/mpf('1.2366'))
print("0.05/(1-1/k) =", mpf('0.05')*k/(k-1))
# Upsilon hat at 6668 and Y(3k+1)
u = (3/mpf('0.35'))*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
Uh = (k-1)*u/(2*k+1)
rhoH = ((1-mpf(3)/(2*k))*mpf('0.307')*k/(2*k)-47/(24*k))/k
print("Upsilon hat(6668) =", Uh, " Y(3k+1) with v=0.7654:", k*rhoH*mpf('0.7654')-Uh*(1-(k+1)*rhoH))
