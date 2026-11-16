import math
c=1/math.sqrt(2*math.pi)
def Bor(n): return math.exp(-n+(n-1)*math.log(n)-math.lgamma(n+1))
def Ren(j): return j*Bor(j)
Psi=lambda d: sum(Ren(j) for j in range(1,d+1))
print("Psi(14)=",Psi(14),"Psi(14)/(2e)=",Psi(14)/(2*math.e))
k=3131
f1=math.sqrt(2*math.pi)*(k+15)**1.5*Bor(k+15)*(k/(k+15))**1.5*(k+1)/(k+14)
print("first factors k=3131:",f1, f1*Psi(14)/(2*math.e))
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
ups=lambda k: 0.5+2.5/k+1/(4*k*k)
gW=2*math.exp(0.0031)/math.e
print("gamma_W=",gW,"ups*gW 3131=",ups(3131)*gW,"u/(e 2^1.5) 3131=",u(3131)/(math.e*2**1.5))
d=lambda k: gW*ups(k)+u(k)/(math.e*2**1.5)
print("d(3131)=",d(3131),"d(10001)=",d(10001))
print("E3 bound:",0.3951/(math.e*2**1.5),"0.0648*e*2^1.5=",0.0648*math.e*2**1.5)
def Low(k,rho):
    eps=k**(-1/3)
    A=c*k**(1/3)*(2*math.sqrt(rho)-2.218*eps)/(1+rho*eps)*math.exp(-1/(12*(k+1)))
    B=rho**2*(1+rho*eps)**1.5*math.exp(1/(4*(k+1)))/(c*(2*math.sqrt(rho)-2.218*eps))
    return A*math.exp(-B)
print("Low(10001,1.4)=",Low(10001,1.4),"Low(3131,0.75)=",Low(3131,0.75))
k=10001; print("Obar far:",d(k)*math.exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5)
k=3131; print("Obar small:",d(k)*math.exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5)
# f(D) max
mx=max(((1-D)*(1+(math.e-2)*D)/(2-D)) for D in [i/100000 for i in range(0,100001)])
print("max (1-D)(1+(e-2)D)/(2-D)=",mx, "(1+7/3131)*0.509=",(1+7/3131)*0.509)
print("(e+0.75)/3131=",(math.e+0.75)/3131, "0.5006*3.469^2=",0.5006*3.469**2)
print("2.218/3131^(1/3)=",2.218/3131**(1/3), "R(1/2) coeffs:",0.75-2*c*math.sqrt(0.5), 2*0.5**1.5-c, 0.18581-0.30817*0.152)
print("wp quad at u=3131^(1/3):",(lambda uu:0.15037*uu*uu-1.54829*uu-1.3314)(3131**(1/3)), 3131**(1/3))
wp=lambda m: 1.99+0.59963*(m+1)**(2/3)+1.24847*(m+1)**(1/3)
print("(6.49) diff at 3131:",0.75*3131**(2/3)-(wp(3131+0.75*3131**(2/3))-1))
print("wp'(1)=",2/3*0.59963*2**(-1/3)+1/3*1.24847*2**(-2/3))
print("large root:",(1.54829+math.sqrt(1.54829**2+4*0.15037*1.3314))/(2*0.15037))
print("10*10001^(2/3)=",10*10001**(2/3), "10*2^(-2/3)=",10*2**(-2/3))
print("Ren(15)/Psi(14)=",Ren(15)/Psi(14),"1/70=",1/70)
print("3.51/3131, 2.0013*3129:",3.51/3131,2.0013*3129)
# v-negative check (6.50) at k=3131
for dd in range(1,15):
    m=3131+dd
    L=(3130)*(math.e*Ren(dd+1)-60*(dd+1)/m); R=2*(1+sum(math.e*Ren(r+1)+60*(r+1)/m for r in range(1,dd)))
    print(dd,round(L,2),round(R,2))
# first factor monotone check n>=3
ok=all((((n+1)/n)**1.5*math.exp((n-1)*math.log(1+1/n)-1))>=1 for n in range(3,2000))
print("sqrt(2pi)n^1.5 Bor(n) increasing n>=3:",ok, "n=2:",(1.5)**1.5*math.exp(math.log(1.5)-1))
