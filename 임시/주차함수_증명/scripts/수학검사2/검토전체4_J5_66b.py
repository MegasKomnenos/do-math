import math
e=math.e; c=(2*math.pi)**-0.5
def logBor(n): return -n+(n-1)*math.log(n)-math.lgamma(n+1)
Bor=lambda n: math.exp(logBor(n))
Ren=lambda j: j*Bor(j)
def Low(k,rho):
    eps=k**(-1/3)
    a=2*math.sqrt(rho)-2.218*eps
    return c*k**(1/3)*a/(1+rho*eps)*math.exp(-1/(12*(k+1)))*math.exp(-rho**2*(1+rho*eps)**1.5*math.exp(1/(4*(k+1)))/(c*a))
print("Low(10001,1.4)=",Low(10001,1.4),"Low(3131,0.75)=",Low(3131,0.75))
u=lambda k:3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
ups=lambda k:0.5+2.5/k+0.25/k**2
gW=2*math.exp(0.0031)/e
d=lambda k: gW*ups(k)+u(k)/(e*2**1.5)
k=10001; print("Obar far=",d(k)*math.exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5)
k=3131; print("Obar small=",d(k)*math.exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5)
# (6.49)
wp=lambda m: 1.99+0.59963*(m+1)**(2/3)+1.24847*(m+1)**(1/3)
print("6.49 diff at 3131:",0.75*k**(2/3)-(wp(k+0.75*k**(2/3))-1), "quad:",0.15037*k**(2/3)-1.54829*k**(1/3)-1.3314, "k^(1/3)=",k**(1/3))
# (6.50) at k=3131
k=3131
for dd in range(1,14):
    m=k+dd
    L=(k-1)*(e*Ren(dd+1)-60*(dd+1)/m)
    R=2*(1+sum(e*Ren(r+1)+60*(r+1)/m for r in range(1,dd)))
    print(dd, round(L,1), round(R,2))
print("0.0648*e*2^1.5=",0.0648*e*2**1.5, "u(3131)/(e2^1.5)=",u(3131)/(e*2**1.5))
print("2.218/3131^(1/3)=",2.218/3131**(1/3), "R(1/2) coeffs:",0.75-2*c/math.sqrt(2), 2*0.5**1.5-c)
print("10*10001^(2/3)=",10*10001**(2/3), "6.2996:",10*2**(-2/3))
