from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, zeta
mp.dps = 30
def Bor(d): d=mpf(d); return exp(-d)*d**(d-1)/factorial(d)
def Ren(j): return j*Bor(j)
def Psi(d): return sum(Ren(j) for j in range(1,d+1))
print("Psi(14)=",Psi(14)," /2e=",Psi(14)/(2*e))
k=mpf(3131)
f1 = sqrt(2*pi)*mpf(3146)**mpf('1.5')*Bor(3146)*(k/(k+15))**mpf('1.5')*(k+1)/(k+14)
print("first three factors k=3131:",f1, " *Psi/2e=",f1*Psi(14)/(2*e))
gW = 2*exp(mpf('0.0031'))/e; print("gamma_W=",gW)
def ups(k): k=mpf(k); return mpf('0.5')+mpf(5)/(2*k)+1/(4*k*k)
def u(k):
    k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
for kk in (3131,10001):
    print("k=%d: gW*ups="%kk, gW*ups(kk), " u/(e 2^1.5)=",u(kk)/(e*2**mpf('1.5')), " d(k)=",gW*ups(kk)+u(kk)/(e*2**mpf('1.5')))
print("E3 const:", mpf('0.3951')/(e*2**mpf('1.5')), " 0.0648*e*2^1.5=",mpf('0.0648')*e*2**mpf('1.5'))
# f(D) max
from mpmath import findroot
f=lambda D:(1-D)*(1+(e-2)*D)/(2-D)
import numpy as np
print("max f:", max(f(mpf(x)) for x in np.linspace(0,1,100001)))
# Low
def Low(k,rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3)
    A=(2*pi)**(-mpf('0.5'))*k**(mpf(1)/3)*(2*sqrt(rho)-mpf('2.218')*eps)/(1+rho*eps)
    return A*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf('1.5')*exp(1/(4*(k+1)))/((2*pi)**(-mpf('0.5'))*(2*sqrt(rho)-mpf('2.218')*eps)))
print("Low(10001,1.4)=",Low(10001,'1.4'), " Low(3131,0.75)=",Low(3131,'0.75'))
def dk(k): return gW*ups(k)+u(k)/(e*2**mpf('1.5'))
k=mpf(10001); print("Obar far-window k=10001:", dk(k)*exp(1+1/(12*k))*(1+mpf('1.4')*k**(-mpf(1)/3)+1/k)**mpf('1.5'))
k=mpf(3131); print("Obar small-k k=3131:", dk(k)*exp(1+1/(12*k))*(1+mpf('0.75')*k**(-mpf(1)/3)+1/k)**mpf('1.5'))
# (6.50) at k=3131
k=3131
for d in range(1,15):
    L=(k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/(k+d))
    R=2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print(d, mp.nstr(L,8), mp.nstr(R,8))
# zeta 3/2
print("zeta(3/2)=",zeta(mpf('1.5')), " 2+z/12=",2+zeta(mpf('1.5'))/12)
# witness wp check (6.49) at k=3131
k=mpf(3131); d=mpf('0.75')*k**(mpf(2)/3)
wp=lambda m: mpf('1.99')+mpf('0.59963')*(m+1)**(mpf(2)/3)+mpf('1.24847')*(m+1)**(mpf(1)/3)
print("(6.49) diff:", d-(wp(k+d)-1), " u=",k**(mpf(1)/3), " quad:", mpf('0.15037')*k**(mpf(2)/3)-mpf('1.54829')*k**(mpf(1)/3)-mpf('1.3314'))
# small-k ratio check prop-W: 3.469/k, 6.03/k
print("(e+0.75)/3131=",(e+mpf('0.75'))/3131, " 0.5006*3.469^2=",mpf('0.5006')*mpf('3.469')**2, " /3131=",mpf('0.5006')*mpf('3.469')**2/3131)
print("3.51/3131=",mpf('3.51')/3131)
# theorem D numbers
print("1.4963 check:", mpf('0.09')*mpf('1.5')*mpf('0.7979')+(1+mpf('0.09')/701)*mpf('1.74')*mpf('0.7979'), " 2.4604 check:",(1+mpf('0.09')/701)*mpf('3.28')*mpf('1.5')/2)
m=mpf(701); print("0.161 check:", mpf('1.1212')*m**(-mpf(2)/3)+mpf('1.3036')*m**(-mpf(1)/3), " kfrak:",(m**(mpf(2)/3)/2)**mpf('1.5')/(m-m**(mpf(2)/3)/2), " N:",exp(-1/(12*(m-m**(mpf(2)/3)/2))))
kf=mpf('0.3747'); print("bracket:", mpf('0.99987')*(1-mpf('0.5')-mpf('0.798')*kf)-mpf('0.7979')*mpf('0.5')*kf, " rhs:", mpf('0.7979')*mpf('0.5')*sqrt(m**(mpf(2)/3)/2)/(12*(m-m**(mpf(2)/3)/2)))
