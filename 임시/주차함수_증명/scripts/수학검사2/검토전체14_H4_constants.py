# 검토전체14 H4: 장5B 상수 검산
import math
pi=math.pi
n=50001
print("10((n+1)/2)^(2/3) vs 6n^(2/3)+2:", 10*((n+1)/2)**(2/3), 6*n**(2/3)+2)
# 5.5.2 varrho_0 bound at y=25000
y=25000; t=y+1+math.ceil(0.75*(1.1*y)**(2/3)); print("t-1<=1.1y:", t-1, 1.1*y, "ceil=",math.ceil(0.75*(1.1*y)**(2/3)))
# old-5-30 constants
v1=(2*pi)**-0.5*math.sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*math.exp(1/(12*(n+1))); print("case y<=2n/3:",v1)
v2=(2*pi)**-0.5*0.15**1.5*(1+1/n)**1.5*math.exp(1/(12*(n+1))); print("0.15^1.5=",0.15**1.5," case y>2n/3:",v2)
v3=math.exp(-2)*((n+1)/(n-1))**1.5*math.exp(1/(12*(n+1))); print("pi_n(n-1) bound:",v3, "sum:",math.exp(-1)-0.1354-0.0232)
# scaled: h0
print("0.0342^3=",0.0342**3, "1/25000=",1/25000, "25000^(-1/3)=",25000**(-1/3))
umax=math.sqrt(6*0.0342); c2=1/(2*(1-umax)); c3=1/math.sqrt(2)-umax/3; print("umax,c2,c3",umax,c2,c3)
f12=c3*12**1.5-12-math.log(math.sqrt(2)*(1+6*0.0342)*12/c3); print("12^1.5=",12**1.5,"f(12)=",f12, "sqrt2(1+6h0)12/c3=",math.sqrt(2)*(1+6*0.0342)*12/c3)
print("fprime(12)=",1.5*c3*math.sqrt(12)-1-1/12)
# q_max<=Y/4 threshold
print("Y with 6Y^(2/3)=Y/4:", 24**3)
# O(25000)
Y=25000; O=Y**-2*math.sqrt(12/pi)*Y**(1/3)*math.sqrt(2/Y)*(Y+1); print("O(25000)=",O)
# band-inequality conditions at n=50001
print("n/3 vs 10(2n/3)^(2/3):", n/3, 10*(2*n/3)**(2/3))
print("0.4n/3 vs 6(2n/3)^(2/3)+1:", 0.4*n/3, 6*(2*n/3)**(2/3)+1)
print("rho0 bound 0.75(1.1*2n/3)^(2/3)+1 vs 0.7n/3:", 0.75*(1.1*2*n/3)**(2/3)+1, 0.7*n/3)
print("deriv 0.4(1-lb)-4lb^(2/3)n^(-1/3) at lb=2/3:", 0.4/3-4*(2/3)**(2/3)*n**(-1/3))
# right-part constants
y=33334; r=10357
print("10y^(2/3)-1 =",10*y**(2/3)-1)
hv=lambda c: c**-0.5*((2/math.sqrt(pi))*(1+1/c)+1/math.sqrt(pi))
print("hv coefficient at 2064:", hv(2064)*math.sqrt(2064))
print("0.2r-7.3=",0.2*r-7.3)
t3=y**(1/3); e_hov=1.6932*(t3/10+1)*(2*t3**2-7.5)**-0.5; print("eps_hov=",e_hov)
print("sqrt(2/pi)/sqrt(2064)=",math.sqrt(2/pi)/math.sqrt(2064))
print("0.75*1.1^(2/3)=",0.75*1.1**(2/3))
print("(n+1)/y max=",(50001+1)/33334)
print("(2pi)^-1/2 (1.50003/0.9199)^1.5 =",(2*pi)**-0.5*(1.50003/0.9199)**1.5*math.exp(1/(12*50002)))
print("0.3*0.8308/sqrt(10358)=",0.3*0.8308/math.sqrt(10358))
print("0.92007(r+1)-1 >= 0.9199(r+1)? r+1=",r+1, 0.92007*(r+1)-1, 0.9199*(r+1))
print("(r+1)/(0.92007(r+1)-2)=",(r+1)/(0.92007*(r+1)-2))
print("(0.7993+2*y^(-2/3))^1.5=",(0.7993+2*y**(-2/3))**1.5)
print("eps0 bound=",1.5*(0.07993*(r+1)+1)/(0.92007*(r+1)-1))
print("(1+0.7993y^(-1/3)+1/y)^1.5=",(1+0.7993*y**(-1/3)+1/y)**1.5)
W=(2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*math.exp(0.1305+1/400008); print("(r+1)/y*W<=",W)
print("e^-c4 >=",math.exp(-(1/156+1/(12*33334)+1/(12*50002))))
print("0.8427*0.71216*0.9936*1.9366-0.3678=",0.8427*0.71216*0.9936*1.9366-0.3678)
print("at lambda=2/3: ",0.7869*2/3-(1/3)-2.5e-5)
# hover lemma: z^(3/2)/(2z-3)^(1/2) at z=2,3 and (2/sqrt(pi))*2sqrt2
print("hover trivial:", (2/math.sqrt(pi))*2*math.sqrt(2))
# stop-lower
print("1.5*0.95^-2.5=",1.5*0.95**-2.5, "chord:",(0.8**-1.5-1)/0.2)
print("4/sqrt(2pi)=",4/math.sqrt(2*pi))
# D band first cell product check
print("band product:",1.957*0.71216*0.49998*(2*0.9885-0.00714)-0.0169)
