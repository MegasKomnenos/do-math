import math
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def Ups(k): return (k-1)*u(k)/(2*k+1)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/math.sqrt(k-1)
def rhoH(k,nu): return (1/k)*((1-1.5/k)*0.307*k/(k+nu-1)-47/(24*k))
def rhoL(k,nu): return 1.5*nu/(k*(k+nu))*(1-1.2/k)
def rhomin(k,nu):
    if nu>k: return max(0,rhoH(k,nu))
    return max(0,min(rhoH(k,nu),rhoL(k,nu)))
def Y(k,nu): r=rhomin(k,nu); return k*r*v(k)-Ups(k)*(1-(k+1)*r)
def mu(k): return Ups(k)/(1.5*(1-1.2/k)*(v(k)+Ups(k)*(k+1)/k))
def F(k,nu): return Y(k,nu)+(1-1/k)**nu/20
k=6668
print("v(6668)",v(k),"Ups",Ups(k),"u",u(k))
m=mu(k); print("k mu/(1-mu)",k*m/(1-m), "0.1113k",0.1113*k, "k^1/3 mu/(1-mu)",k**(1/3)*m/(1-m))
print("Y(3k+1)",Y(k,k+1),"k rhoH(3k+1)",k*rhoH(k,k+1))
print("(i) at .112k: k rhoL",k*rhoL(k,0.112*k),"k rhoH",k*rhoH(k,0.112*k))
# nu0
nu0=next(n for n in range(1,k+2) if Y(k,n)>=0); print("nu0(6668)",nu0, "3.6k^2/3",3.6*k**(2/3))
# monotonic claims on grid
import itertools
ks=[6668,7000,10000,20000,50000,10**5,10**6]
print("mu",[mu(x) for x in ks]); print("k^1/3 mu/(1-mu)",[x**(1/3)*mu(x)/(1-mu(x)) for x in ks])
print("Y(3k+1)",[Y(x,x+1) for x in ks])
# rates
def A(x): return 1.5*(1-1.2/x)*v(x)/(Ups(x)*x**(1/3))
def B(x): return (1.5*(1-1.2/x)*(1+1/x)-1)/x**(1/3)
for x in [6668,10000,100000]:
    h=1; print(x,"dA",(A(x+h)-A(x-h))/2,"0.017k^-5/6",0.017*x**(-5/6),"dB",(B(x+h)-B(x-h))/2,"0.17k^-4/3",0.17*x**(-4/3))
# (3)
for kk in [48965,48966]: print(kk,"Ups",Ups(kk),"(1/20)(1-1/k)^103",(1-1/kk)**103/20)
for kk in [38886,38887,38888,40000,48965]: print(kk,"F(103)",F(kk,103))
# F increasing on [103,nu0]: dY/dnu bound
print("dY/dnu bound",1.5*(1-1.2/k)*k*v(k)/(1.2366*k*k)*k, "0.0501",k/(20*(k-1)))
# Y_k >= -Ups check and 7-23(b)
print("1/5-Ups(3132)",0.2-Ups(3132), "Ups(3131)",Ups(3131), "u(3131)/2",u(3131)/2)
