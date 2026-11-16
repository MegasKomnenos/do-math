# D.band-check 첫 셀의 다섯 포락선과 비를 D의 식 그대로 다시 계산한다 (n=50001, lambda in [1/2, 1/2+1/24000]).
from mpmath import mp, mpf, sqrt, pi, exp, floor
mp.dps=30
n=mpf(50001); la=mpf(1)/2; lb=mpf(1)/2+mpf(1)/24000; w0=mpf('0.71216')
wid=mpf('0.75')*(mpf('1.1')*lb*n)**(mpf(2)/3)+1
c1=mpf('1.5')*((2*lb-1)*n+2*wid)/(la*n*((1-lb)*n-wid))
eps0=mpf('1.5')*wid*((2*lb-1)*n+2*wid)/((la*n-1)*((1-lb)*n-wid))
# hov lower
chi=floor(mpf('0.3')*(1-lb)*n-1)-1
hov=mpf(0); z=0
while True:
    t=1-2/sqrt(pi)*mpf(z)**(mpf(3)/2)/sqrt(chi)
    if t<=0: break
    hov+=(la-1/n)**z*t; z+=1
second=1-sqrt(2/pi)/sqrt(mpf('0.3')*(1-lb)*n-1)-mpf('0.3')*(1-la)*n/sqrt(2*pi)*((n+1)/(la*n*((1-lb)*n-wid)))**(mpf(3)/2)*exp(1/(12*(n+1)))
top=(1+1/n)**(mpf(3)/2)/sqrt(2*pi)/sqrt(la)*(1-lb)**(-mpf(3)/2)/sqrt(n)*exp(1/(12*n))
K=la*exp(-1/(12*(mpf('0.4')*(1-lb)*n-6*(lb*n)**(mpf(2)/3)+1))-1/(12*la*n)-1/(12*(n+1)))
W=mpf(2)/3/sqrt(2*pi)*(wid+1)**(mpf(3)/2)*c1*(1+wid/(la*n))**(mpf(3)/2)*exp(eps0+1/(12*la*n))
ratio=hov*w0*K*(2*second-top)-W
print("hov",hov," second",second," top",top," K",K," W",W)
print("ratio",ratio, " cond 0.4(1-lb)n >= 6(lb n)^{2/3}+1:", mpf('0.4')*(1-lb)*n >= 6*(lb*n)**(mpf(2)/3)+1)
