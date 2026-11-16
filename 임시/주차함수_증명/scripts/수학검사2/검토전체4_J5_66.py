import math
c=(2*math.pi)**-0.5; e=math.e
Bor=lambda n: math.exp(-n)*n**(n-1)/math.factorial(n)
Psi=lambda d: sum(m*Bor(m) for m in range(1,d+1))
print("Psi(14)=",Psi(14),"Psi(14)/(2e)=",Psi(14)/(2*e))
k=3131
f1=math.sqrt(2*math.pi)*(k+15)**1.5*Bor(k+15) if False else math.exp(-0.0)  # Bor(3146) overflow; use Stirling-corrected ratio
# compute log Bor(n) via lgamma
def logBor(n): return -n+(n-1)*math.log(n)-math.lgamma(n+1)
f1=math.sqrt(2*math.pi)*math.exp(1.5*math.log(k+15)+logBor(k+15))
f=f1*(k/(k+15))**1.5*(k+1)/(k+14)
print("first three factors=",f,"product with Psi/(2e)=",f*Psi(14)/(2*e))
ups=lambda k:0.5+2.5/k+0.25/k**2
gW=2*math.exp(0.0031)/e
print("gamma_W=",gW,"ups*gW=",ups(k)*gW, "diff=",f*Psi(14)/(2*e)-ups(k)*gW)
u=lambda k:3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
d=lambda k: gW*ups(k)+u(k)/(e*2**1.5)
print("d(3131)=",d(3131),gW*ups(3131),u(3131)/(e*2**1.5),"d(10001)=",d(10001))
# max of (1-D)(1+0.7183D)/(2-D)
print("max=",max((1-D)*(1+0.7183*D)/(2-D) for D in [i/100000 for i in range(100001)]))
print("(e+.75)/3131=",(e+0.75)/3131, "6.03/3131=",6.03/3131, "3.51/3131=",3.51/3131, "0.5006*3.469^2=",0.5006*3.469**2)
print("2*3131/3129=",2*3131/3129, "k/(k-1)=",3131/3130)
# theorem-D numbers
m=701; dd=m**(2/3)/2
print("m^{-1/3}/2=",1/(2*m**(1/3)),"k=",dd**1.5/(m-dd),"es=",0.798*dd**1.5/(m-dd),"N=",math.exp(-1/(12*(m-dd))))
print("bracket=",0.99987*(0.5-0.2991)-0.7979*0.5*0.3747, "rhs=",0.025*m**(-2/3))
print("1.1212/m^(2/3)+1.3036/m^(1/3)=",1.1212*m**(-2/3)+1.3036*m**(-1/3), "0.135*0.7979+1.74*0.7979*1.000128=",0.135*0.7979+1.74*0.7979*(1+0.09/701))
print("(4/3)^1.5=",(4/3)**1.5, "2/3*(3/4)^(-1/3)=",2/3*(3/4)**(-1/3))
