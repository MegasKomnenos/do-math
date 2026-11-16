# F5 검산 1: 6.1 (6.8) 수치, 6.2 tilt-sum 작은 k 정확 유리수, B_2(43), B_2(2000), 6.3 lemma-omega 상수
from fractions import Fraction as Fr
from math import e, sqrt, pi, exp, log, ceil, factorial

# --- 6.1 (6.8)
C=3; k=4000
qs=ceil((C*k)**(2/3)); print("q*=",qs, (C*k)**(2/3))
lhs=1-1.6/sqrt(qs)+0.8/qs
br=0.8*sqrt(2)/C*(1+1/(2*(qs-1)))+(1.212+1.203+1.508)*C**(-4/3)*k**(-1/3)+1.5/(C*sqrt(qs))
print("6.8 lhs>=",1-1.6/sqrt(525),"bracket terms",0.8*sqrt(2)/3*(1+1/1048),3.923*3**(-4/3)*4000**(-1/3),1.5/(3*sqrt(525)),"sum",br,"2*br",2*br)
print("1.2(1-2/525)^-2.5=",1.2*(1-2/525)**-2.5, "1.2(1+2/525)^.5=",1.2*(1+2/525)**.5, "1.5(1-1/525)^-2.5=",1.5*(1-1/525)**-2.5)

# --- 6.2 tilt-sum small k exact: sum_{n=2}^{k+1} n^{n-1} x_k^n / n!  (Bor(n) q^n = n^{n-1} x^n/n!)
def S(k):
    x=Fr(k,k+1)**(k-1)
    return sum(Fr(n**(n-1))*x**n/factorial(n) for n in range(2,k+2))
mx=max((S(k),k) for k in range(2,43))
print("tilt-sum small k: all<1:", all(S(k)<1 for k in range(2,43)), "max",mx[1],mx[0],float(mx[0]))
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)=",B2(43),"B2(2000)=",B2(2000),"B2(42)=",B2(42))
# compare S(k) for k=43 float vs B2
print("S(43)~",float(S(43)))

# --- 6.3 lemma-omega constants
X=(5-sqrt(7))/6; print("X*",X, X*(1-X)*(3-2*X), (10+7*sqrt(7))/54)
print("tl^-1<=",1/(1-0.75/51), "e^(1/24+1/612)=",exp(1/24+1/612), "1+1/51=",1+1/51)
u=exp(1/24+1/612)/(1-0.75/51)*(1+1/51)*4/3; print("u<=",u, "M/G<=",0.5282*u)
print("L/G V>=2:",1.5/53*(4/3)*0.5*(1+1/51)*1.0150, "V=1:",1.5/52*2.02*0.51*(1+1/51)*1.0150)
print("d=2: e^-2=",exp(-2),"1.545/e=",1.545/e, "e^{3/102}=",exp(1.5/51))
print("c_{y+2} lower:",(2*exp(-2)+exp(-1)-1.03*exp(-2)/51), "0.2/e*0.6=",0.2*exp(-1)*0.6)
y=50; print("d=3 compare:",0.0441*(y-1)/(y+3)**2, 1.2*(y+1)/((y+2)**2*(y+3)), 0.0441*(y-1)/(y+3)**2/(1.2*(y+1)/((y+2)**2*(y+3))))
print("d=y+2 ratio:",1.03*exp(-1)/2)
