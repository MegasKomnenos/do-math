import math
from fractions import Fraction
c=1/math.sqrt(2*math.pi)
print("2/sqrt(2pi)=",2*c)
# 6.1
print("(1-2/525)^-2.5*1.2=",1.2*(1-2/525)**-2.5)
print("(1+2/525)^.5*1.2=",1.2*(1+2/525)**.5)
print("(1-1/525)^-2.5*1.5=",1.5*(1-1/525)**-2.5)
print("LHS 525:",1-1.6/math.sqrt(525)+0.8/525, 1-1.6/math.sqrt(525))
b1=0.8*math.sqrt(2)/3*(1+1/1048); b2=3.923*3**(-4/3)*4000**(-1/3); b3=1.5/(3*math.sqrt(525))
print("bracket:",b1,b2,b3,b1+b2+b3, 2*(b1+b2+b3))
print("q*=ceil(12000^(2/3))=",math.ceil(12000**(2/3)), 12000**(2/3))
# 6.2 B2
def B2(k): return (1-1/math.e)+(math.exp(1.5+1/k)-1)*2*(math.sqrt(k+1)-1)/(math.sqrt(2*math.pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000),"1-B2(2000)=",1-B2(2000))
print("e^{3/2+1/43}-1=",math.exp(1.5+1/43)-1, "2(sqrt44-1)=",2*(math.sqrt(44)-1), "sqrt(2pi)*44=",math.sqrt(2*math.pi)*44)
# exact tilt sum small k
def Bor(n): return Fraction(n**(n-1),math.factorial(n))  # times e^{-n}
# sum_{n=2}^{k+1} Bor(n) q^n with q=e*x_k, Bor(n)=e^{-n} n^{n-1}/n!, so Bor(n) q^n = n^{n-1}/n! * x_k^n exactly rational
mx=0
for k in range(2,43):
    xk=Fraction(k,k+1)**(k-1)
    s=sum(Fraction(n**(n-1),math.factorial(n))*xk**n for n in range(2,k+2))
    if s>=1: print("FAIL k",k,float(s))
    mx=max(mx,s) if k>2 else s
    if k==2: print("k=2 sum=",s)
print("max over 2..42:",float(mx))
# lemma old-7-24 numbers
print("1.5*1.0150*... u:",1.0443*1.0150*1.01961*4/3, "exp(1/24+1/612)=",math.exp(1/24+1/612), "0.5282*1.449=",0.5282*1.449)
print("L/G V>=2:",1.5/53*4/3*0.5*1.01961*1.0150, " V=1:",1.5/52*2.02*0.51*1.01961*1.0150)
print("(10+7sqrt7)/54=",(10+7*math.sqrt(7))/54, "X*=",(5-math.sqrt(7))/6)
print("e^{3/102}=",math.exp(3/102), "1.545/e=",1.545/math.e,"e^-2=",math.exp(-2))
y=50
print("d=3 ratio:",0.0441*(y-1)*(y+2)**2/(1.2*(y+1)*(y+3)))
print("c_{y+2} bound:",(2*math.exp(-2)+math.exp(-1)-1.03*math.exp(-2)/51), 0.6*52/53)
print("1.03e^-1/2=",1.03/math.e/2)
# 6.4 u(k)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(3131)=",u(3131),"2u=",2*u(3131),"u/2=",u(3131)/2, "factors:",3/0.35,1.35+1/3131,(0.65-1/3131)**-1.5,3131**-0.5)
print("u(6667)=",u(6667),"2u=",2*u(6667),"u(10000)=",u(10000),"2u=",2*u(10000))
print("(6262)^(2/3)=",6262**(2/3),"0.65*3131-1=",0.65*3131-1)
print("witness 20000:",1.99+0.59963*20001**(2/3)+1.24847*20001**(1/3))
print("9*(3/2)^1.5=",9*1.5**1.5, "*4/3=",9*1.5**1.5*4/3)
print("8001^(2/3)*1.5=",1.5*8001**(2/3))
# 6.5
print("50.62/sqrt(3130)=",50.62/math.sqrt(3130))
print("ex_max=",3131/6261, "2-exmax-20/(9*3130)=",2-3131/6261-20/(9*3130))
print("kappa_d min=",1.498+2*3130/6261)
tp=0.55;ka=2.4978
r=((2+tp*ka)+math.sqrt((2+tp*ka)**2-4*tp*ka))/(2*tp)
print("root=",r,"m=",(r*r-ka*r)*math.exp(-tp*r))
x=3132/3130
print("Gamma=",x/((1+x)**0.45-1))
print("3c(JI+cYI)=",3*c*(8.133+c*10.301),"1.5 Gm c(JX+cYX)=",1.5*2.7323*0.8051*c*(17.951+c*23.462))
print("24000/2263^1.5=",24000/2263**1.5)
print("2*3*6668/6667^1.5=",6*6668/6667**1.5,"50.62/sqrt(6666)=",50.62/math.sqrt(6666))
print("v(3131)=",2-24000/2263**1.5-2*u(3131)-50.62/math.sqrt(3130))
print("v(6667)=",2-6*6668/6667**1.5-2*u(6667)-50.62/math.sqrt(6666))
print("v(10000)=",2-6*10001/10000**1.5-2*u(10000)-50.62/math.sqrt(9999))
print("12.15 check:",4.5*2+4.5*2/3+0.375*2/5, 4.5*2/3+4.5*2/5+0.375*2/7)
print("3T/(2T+1) vs 10/(3T):",3*3130/6261,10/(3*3130))
