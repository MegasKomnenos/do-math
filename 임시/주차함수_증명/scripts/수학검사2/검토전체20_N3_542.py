from mpmath import mp, mpf, zeta, pi, sqrt, log, exp
mp.dps=25
print("832^1.5=",mpf(832)**1.5, "833^1.5=",mpf(833)**1.5, "6/5*20001=",mpf(6)/5*20001)
l=lambda m:(2+mpf(1)/m)*zeta(2*m)/pi**(2*m)
print("l1,l2,l3=",l(1),l(2),l(3), 1/mpf(36), 1/mpf(405))
print("sum m>=5:", sum(2*m*l(m)*mpf(2)**(2-2*m) for m in range(5,40)))
print("log et(1/2)=", sum(l(m)*mpf(4)**(-m) for m in range(1,40)))
print("1/(1+9/sqrt598)=",1/(1+9/sqrt(598)))
print("rq bounds:", mpf(6)/5/sqrt(598), mpf(3)/2/sqrt(833), mpf(9)/5/sqrt(966), 1/mpf(16))
print("1/sqrt(598)=",1/sqrt(598), "rect count:", round((1.2-0.73)/0.002)*round(0.041/0.002+0.5))
print("966 check:", mpf(30001.5)**(mpf(2)/3))
print("(5/9)sqrt(598)=", mpf(5)/9*sqrt(598))
print("log10(1.15*598^3)=", log(1.15*598**3,10), "598*log10 24=", 598*log(24,10))
print("12/(110e)=",12/(110*exp(1)), 1/mpf(24), "(12/11)^1.5*(1+1/598)=",(mpf(12)/11)**1.5*(1+mpf(1)/598))
