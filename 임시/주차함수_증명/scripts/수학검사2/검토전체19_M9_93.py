import math
def quad(f,a,b,n=400000):
    h=(b-a)/n; return sum(f(a+(i+0.5)*h) for i in range(n))*h
k=6668
def J1(k):
    f=lambda t:(1+t+2/k)**-3.5*max(0,1-3*k**-0.5*(t-1/k)**-1.5)
    return 2.5*quad(f,1/k,1)
def J2(k):
    f=lambda t:(1+t+1/k)**-3.5*max(0,1-3*(k-1)*k**-1.5*(t-1/k)**-1.5)
    return 2.5*quad(f,1/k,(k-1)/k)
J3=(k/(2*k+1))**2.5*(1-3*k**-0.5); J4=(k/(2*k+1))**2.5*(1-3*(k-1)**-0.5)
print("L*",J1(k),J2(k),J3,J4,J1(k)+J2(k)+J3+J4)
# discrete check of H_k directly
om=lambda s:(k/s)**2.5
H=sum((om(E+1)-om(E+2))*max(0,1-3*k*(E-k)**-1.5) for E in range(k+1,2*k))+om(2*k+1)*(1-3*k**-0.5)
Hp=sum((om(E+1)-om(E+2))*max(0,1-3*(k-1)*min(E-k+1,k-1)**-1.5) for E in range(k,2*k))+om(2*k+1)*(1-3*(k-1)**-0.5)
print("H_k,H'_k",H,Hp,H+Hp)
# (2)
print("0.3826 check",(2*math.pi)**-0.5*math.exp(-1/24)*math.exp(-1/(12*3334)))
js=math.ceil((3*k)**(2/3)); print("j*",js, "first", 4.85*(math.sqrt(k)*((3*k)**(2/3)+2)**-0.5-math.sqrt(2)))
print("second",6/0.98*0.95**-1.5)
print("353.3",16.35*0.95**-1.5*20*(1+1/k)**1.5, "ratio at 0.05k * sqrt k",16.35*0.95**-1.5*20/k*math.sqrt(k))
print("endpoint2",5.45*(1+1/k)**1.5*k/(k-js-1), "12/0.734",12/0.734)
# (3)
d=6.62/math.sqrt(k); print("dbar",d,"band req",(1+d/2)/(1-d/2))
print("41.2",103*(2*math.pi)**-0.5*math.exp(1/(12*6669)), "3.394",(2*math.pi)**-0.5*math.exp(1/(12*6669))*(2/0.48)**1.5)
pi0=0.8825*k**-0.5+0.72/k; cov=41.2*(2/(0.48*k-102))**1.5
print("pi0 bound",pi0,"cov",cov,"bulk req",1+(1+1/1.48)*d/(2-d)+(pi0+cov)/1.48)
print("1/1.48",1/1.48, "0.26k+0.5 term", (0.26*k+0.5)*3.394*k**-1.5+0.676/k, 0.8825*k**-0.5+0.72/k)
