# -*- coding: utf-8 -*-
# H5 검토용 검산: 장6.md 6.1~6.3절의 상수와 \mathsf 없는 C 자리
import re, math, sys
p = r"C:\math\임시\주차함수_증명\장v2\장6.md"
lines = open(p, encoding="utf-8").read().split("\n")
print("== mathsf 없는 C 상수 (19~111행) ==")
for i, l in enumerate(lines[18:111], start=19):
    for m in re.finditer(r"(?<!\\mathsf )(?<![A-Za-z\\])C(?=[kq])", l):
        print(i, l[max(0,m.start()-20):m.end()+12].replace("\n"," "))
print("== 6.1 상수 ==")
print("0.8*sqrt2/3 =", 0.8*math.sqrt(2)/3)
print("0.8*sqrt2/3*(1+1/1048) =", 0.8*math.sqrt(2)/3*(1+1/1048), " 0.3772*(1+1/1048)=", 0.3772*(1+1/1048))
print("3.923*3^-4/3*4000^-1/3 =", 3.923*3**(-4/3)*4000**(-1/3))
print("1.5/(3 sqrt525) =", 1.5/(3*math.sqrt(525)))
print("1-1.6/sqrt525 =", 1-1.6/math.sqrt(525), " +0.8/525:", 1-1.6/math.sqrt(525)+0.8/525)
print("q* for k=4000:", math.ceil(12000**(2/3)))
print("1.2(1-2/525)^-2.5 =", 1.2*(1-2/525)**-2.5, " 1.2(1+2/525)^.5 =", 1.2*(1+2/525)**.5, " 1.5(1-1/525)^-2.5 =", 1.5*(1-1/525)**-2.5)
print("== 6.2 ==")
def B2(k): return (1-1/math.e)+(math.exp(1.5+1/k)-1)*2*(math.sqrt(k+1)-1)/(math.sqrt(2*math.pi)*(k+1))
print("B2(43)=",B2(43)," B2(42)=",B2(42)," B2(2000)=",B2(2000))
print("3k/(2k+1) k=2000:", 3*2000/4001)
print("== 6.3 ==")
X=(5-math.sqrt(7))/6; print("X*=",X," f(X*)=",X*(1-X)*(3-2*X)," (10+7sqrt7)/54=",(10+7*math.sqrt(7))/54)
print("tl^-1 bound:",1/(1-0.75/51)," e^(1/24+1/612)=",math.exp(1/24+1/612)," 1+1/51=",1+1/51)
u=math.exp(1/24+1/612)*(1/(1-0.75/51))*(1+1/51)*4/3; print("u<=",u," 0.5282*1.449=",0.5282*1.449)
print("L/G V>=2:",1.5/53*(4/3)*0.5*1.01961*1.0150)
print("L/G V=1:",1.5/52*2.02*0.51*1.01961*1.0150)
print("e^-2=",math.exp(-2)," 1.545/e=",1.545/math.e, " e^{3/102}=",math.exp(3/102))
print("c_{y+2} lower y=50:",(2*math.exp(-2)+math.exp(-1)-1.03*math.exp(-2)/51), " 0.2/e*0.6=",0.2/math.e*0.6)
y=50; print("d=3 ratio y=50:",0.0441*(y-1)/(y+3)**2/(1.2*(y+1)/((y+2)**2*(y+3))))
print("1.03/e/2=",1.03/math.e/2, " 3.09/e=",3.09/math.e)
print("== 6.4~6.6 ==")
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(3131)=",u(3131)," u(6667)=",u(6667)," u(10000)=",u(10000)," u(10001)=",u(10001))
print("u(3131)/2=",u(3131)/2)
print("(2k)^(2/3) k=3131:",(6262)**(2/3)," 0.65k-1=",0.65*3131-1)
n=20000; print("wp(20000)=",1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3))
print("9*1.5^1.5=",9*1.5**1.5," *4/3=",9*1.5**1.5*4/3)
# tp constant
import math
tp=0.55; ka=2.4978
a=tp; b=-(ka*tp+2); c=ka; r=(-b+math.sqrt(b*b-4*a*c))/(2*a); print("big root=",r," c*=",(r*r-ka*r)*math.exp(-tp*r))
x=3132/3130; print("Gamma*=",x/((1+x)**0.45-1))
cc=1/math.sqrt(2*math.pi)
print("3c(J_I+cY_I)=",3*cc*(8.133+cc*10.301)," 1.5G c* c(J_X+cY_X)=",1.5*2.7323*0.8051*cc*(17.951+cc*23.462))
print("50.62/sqrt(3130)=",50.62/math.sqrt(3130))
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/math.sqrt(k-1)
print("v(3131)=",v(3131)," v(6667)=",v(6667)," v(10000)=",v(10000))
print("24000/2263^1.5=",24000/2263**1.5)
# Psi(14), gamma_W, upsilon
def Bor(n): return math.exp(-n+(n-1)*math.log(n)-math.lgamma(n+1))
Psi=lambda d: sum(j*Bor(j) for j in range(1,d+1))
print("Psi(14)=",Psi(14)," Psi(14)/(2e)=",Psi(14)/(2*math.e))
k=3131; f1=math.sqrt(2*math.pi)*(k+15)**1.5*Bor(k+15); print("first factor=",f1," prod=",f1*(k/(k+15))**1.5*(k+1)/(k+14)," *Psi/(2e)=",f1*(k/(k+15))**1.5*(k+1)/(k+14)*Psi(14)/(2*math.e))
gW=2*math.exp(0.0031)/math.e; ups=lambda k:0.5+2.5/k+0.25/k**2
print("gamma_W=",gW," gW*ups(3131)=",gW*ups(3131)," u/(e 2^1.5)=",u(3131)/(math.e*2**1.5))
dk=lambda k: gW*ups(k)+u(k)/(math.e*2**1.5)
print("d(3131)=",dk(3131)," d(10001)=",dk(10001))
Obar=lambda k,x: dk(k)*math.exp(1+1/(12*k))*(1+x)**1.5
print("Obar(10001,1.4)=",Obar(10001,1.4*10001**(-1/3)+1/10001)," Obar(3131,.75)=",Obar(3131,0.75*3131**(-1/3)+1/3131))
def Low(k,rho):
    eps=k**(-1/3); c=1/math.sqrt(2*math.pi); A=2*math.sqrt(rho)-2.218*eps
    return c*k**(1/3)*A/(1+rho*eps)*math.exp(-1/(12*(k+1)))*math.exp(-rho**2*(1+rho*eps)**1.5*math.exp(1/(4*(k+1)))/(c*A))
print("Low(10001,1.4)=",Low(10001,1.4)," Low(3131,.75)=",Low(3131,0.75))
print("0.0648*e*2^1.5=",0.0648*math.e*2**1.5," 0.3951/(e 2^1.5)=",0.3951/(math.e*2**1.5))
uu=3131**(1/3); print("u=",uu," quad=",0.15037*uu**2-1.54829*uu-1.3314, " direct diff=",0.75*3131**(2/3)-(1.99+0.59963*(3131+0.75*3131**(2/3)+1)**(2/3)+1.24847*(3131+0.75*3131**(2/3)+1)**(1/3)-1))
print("B=2.218/u=",2.218/uu," R(1/2)=",0.18581-0.30817*2.218/uu)
print("ex_max=",3131/6261," 2-exmax-20/(9*3130)=",2-3131/6261-20/(9*3130))
print("1.4*10001^(2/3)=",1.4*10001**(2/3), " 10*10001^(2/3)=",10*10001**(2/3))
