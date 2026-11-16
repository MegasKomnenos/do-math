# O4: (1) 명제 band-inequality 첫 셀 포락선 재계산 (독립 구현, mpmath 40자리, 구간 아님)
#     (2) 보조정리 5-26 창 항 상계의 수치 대조 (n=50001, 여러 y)
from mpmath import mp, mpf, sqrt, exp, log, pi, floor, ceil, loggamma, quad, inf
mp.dps = 40
def Bor(m): m=mpf(m); return exp(-m)*m**(m-1)/exp(loggamma(m+1))
n = mpf(50001); w0 = mpf('0.71216')
la = mpf(1)/2; lb = la + mpf(1)/24000
rb0 = mpf('0.75')*(mpf('1.1')*lb*n)**(mpf(2)/3)+1
# hov
chi_lb = floor(mpf('0.3')*(1-lb)*n-1)-1
hov = mpf(0); z=0
while True:
    term = (1-2/sqrt(pi)*mpf(z)**1.5*chi_lb**-0.5)
    if term <= 0: break
    hov += (la-1/n)**z*term; z+=1
sec = 1-sqrt(2/pi)*(mpf('0.3')*(1-lb)*n-1)**-0.5 - mpf('0.3')*(1-la)*n*(2*pi)**-0.5*((n+1)/(la*n*((1-lb)*n-rb0)))**1.5*exp(1/(12*(n+1)))
top = (2*pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb)**-1.5*n**-0.5*exp(1/(12*n))
K = la*exp(-1/(12*(mpf('0.4')*(1-lb)*n-6*(lb*n)**(mpf(2)/3)+1))-1/(12*la*n)-1/(12*(n+1)))
cb1 = mpf('1.5')*((2*lb-1)*n+2*rb0)/(la*n*((1-lb)*n-rb0))
eb0 = mpf('1.5')*rb0*((2*lb-1)*n+2*rb0)/((la*n-1)*((1-lb)*n-rb0))
W = (2*pi)**-0.5*mpf(2)/3*(rb0+1)**1.5*cb1*(1+rb0/(la*n))**1.5*exp(eb0+1/(12*la*n))
ratio = hov*w0*K*(2*sec-top)-W
print("first cell: hov=",hov," sec=",sec," top=",top," K=",K," W=",W," ratio=",ratio)
# (2) 5-26: WIN^V_0 exact-ish vs closed bound
g = lambda x: (x-1)*log(1+1/x)
def pin(nn,t): return Bor(t)*Bor(nn+1-t)/Bor(nn+1)
def t0(y):
    t = y+2
    while not (y <= (t-1)-floor(mpf(3)/4*(t-1)**(mpf(2)/3))): t+=1
    return t
for y in [25001, 28000, 33334, 40000, 45000, 48000]:
    y=mpf(y); T0=t0(y); r0=T0-1-y
    winV = sum((pin(n,t)-pin(n,y))*( (t-y)*Bor(t-y)*Bor(y)/Bor(t) ) for t in range(int(y)+1,int(T0)))/y
    c1 = mpf(3)/2*(2*y+2*r0-n)/(y*(n-y-r0)); e0 = mpf(3)/2*r0*(2*y+2*r0-2-n)/((y+r0-1)*(n-y-r0+1))
    bound = pin(n,y)/y/sqrt(2*pi)*mpf(2)/3*(r0+1)**1.5*c1*(1+r0/y)**1.5*exp(e0+1/(12*y))
    print("y=",y," rho0=",r0," 0.75(1.1y)^(2/3)+1=",mpf('0.75')*(mpf('1.1')*y)**(mpf(2)/3)+1, " WIN^V/(pi/y)=",winV/(pin(n,y)/y), " bound/(pi/y)=",bound/(pin(n,y)/y), bound>=winV)
