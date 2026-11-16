# S10 검산 2: Sub 적분 수정, Stays^up 재현, j1 재계산(치환 s=u^4), D의 G 원시함수 대조
from math import log, exp, sqrt, pi
def integrate(f,a,b,n=400000):
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n): s+=(4 if i%2 else 2)*f(a+i*h)
    return s*h/3
q=lambda r: 1+0.7501*r/(1+r)
# j1 with rho = u^8 (s=u^4): drho = 8u^7 du; rho^{-1/2}=u^{-4}; integrand sqrt(1+rho)/sqrt(rho) q^3 (...) drho = sqrt(1+u^8) u^{-4} q^3(...) 8u^7 du
f1=lambda u: (sqrt(1+u**8)*8*u**3*0.70836*q(u**8)**3*(2.528571-log(q(u**8))+12*log(u))) if u>0 else 0.0
f2=lambda u: sqrt(1+u**8)*8*u**3*0.70836*q(u**8)**3
print("j1",integrate(f1,0,1),"j2",integrate(f2,0,1))
mS=1.15
cAb=lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
def Sub_num(k,nubar):
    xi=(nubar+4)/(k-1)
    if xi>=0.6: return 0.0
    g=lambda s: 2*(s*s-xi)*(1+s*s)/(s*s*(1-s*s)**2)   # rho=s^2
    return (k-1)/k*integrate(g,sqrt(xi),sqrt(0.6))
def Sub_D(k,nubar):
    xi=(nubar+4)/(k-1)
    G=lambda s: xi/s+(1-xi)*s/(1-s*s)-xi*log((1+s)/(1-s))
    return (k-1)/k*2*(G(sqrt(0.6))-G(sqrt(xi)))
def stays_up(k,nubar):
    tot=0; parts=[]
    for y in (k-1,k):
        abar=(mS*(y+2*y**(2/3)))**(2/3)
        flat=2*(abar-1)/(y+2-abar)
        z=0.6+1/y; sub=Sub_num(k,nubar)
        ab=mS*(1+1/y)*(4*((mS*y)**(2/3)-1)**-0.5+y**-0.5*(2*cAb(z)-4*z**-0.5-sub))
        tot+=flat+ab; parts.append((flat,ab,sub))
    top=integrate(lambda r: min(2,2+(nubar+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1)
    tot+=2*16.54*k**-0.5*top
    return tot,parts,2*16.54*k**-0.5*top
for (k,nb,name) in ((9705,1.3*9705**(2/3),"1a"),(9551,2*9551**(2/3),"1b"),(8065,0.48*8065,"2")):
    print(name,stays_up(k,nb),"SubD",Sub_D(k,nb))
u=lambda k: 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
BdT=lambda k,nu: (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
print("R'_1b",BdT(9551,2*9551**(2/3))+0.114039112+stays_up(9551,2*9551**(2/3))[0])
print("R'_1a",BdT(9705,1.3*9705**(2/3))+0.113284142+stays_up(9705,1.3*9705**(2/3))[0])
