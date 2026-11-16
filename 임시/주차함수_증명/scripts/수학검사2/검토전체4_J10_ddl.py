# J10: 명제 old-8-23의 적분값 j1, j2와 DDL^natural(k) 값을 재계산 (배정밀도, Simpson; 특이점은 rho=t^2 치환)
import math
def q(r): return 1+0.7501*r/(1+r)
def dn(r): return math.sqrt((1+r)/r)
def simpson(f,a,b,n=200000):
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n): s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3
# rho=t^2, drho = 2t dt ; dn(rho)=sqrt(1+t^2)/t  -> integrand*2t cancels 1/t
j2=simpson(lambda t: 2*math.sqrt(1+t*t)*0.70836*q(t*t)**3, 1e-12, 1)
j1=simpson(lambda t: 2*math.sqrt(1+t*t)*0.70836*q(t*t)**3*(2.528571-math.log(q(t*t))+1.5*math.log(t*t)) if t>0 else 0.0, 1e-9, 1)
print("j2=",j2," j1=",j1)
def DDL(k):
    d=2*k**(2/3); c=(2*math.pi)**-0.5
    eps=-math.log(1-math.sqrt(k+1)/(0.485917*k)); epsp=2.26/k+0.47/(d-1)
    gam=2.6047*(2.53+0.5*math.log(k)+eps+1.5/k)/k
    t1=0.457143*c*q(d/k)*math.sqrt(1+d/k)*(d+1)**3.5/k**3
    t2=2*c*k**-0.5*(1+epsp)*(j1+(0.5*math.log(k)+eps)*j2+gam)
    t3=3.9*c/k
    return t1+t2+t3, t1, t2, t3
for k in (6667,6668,8065,9551,9705,20000):
    print(k, ["%.5f"%x for x in DDL(k)])
# 몇 가지 단계 상수 확인
k=6667
print("1.00057 check:", (1+1/k)*(1+2/k)/(1-3/(4*k)))
print("0.16696 check:", 1.00057**2*(1+2/k)**2/6)
print("0.7501 check:", 3/8*(1+math.exp(3/(2*k))))
print("2.528571 check:", 2.5-math.log(2)-math.log(0.485917))
print("sqrt2*0.16696=",math.sqrt(2)*0.16696, " 3*that=",3*math.sqrt(2)*0.16696, " g^2<=sqrt2 c:",0.485917**2, math.sqrt(2)*0.16696)
print("sigma0:",math.exp(-3.4964/1.5), " 6*(1-1.0288)*sqrt(s0)+2*3.4964-6:", 2*3.4964-6+6*math.sqrt(math.exp(-3.4964/1.5))*(1-1.0288))
print("k=6667 j-sum check:", j1+j2*(0.5*math.log(6667)-1))
