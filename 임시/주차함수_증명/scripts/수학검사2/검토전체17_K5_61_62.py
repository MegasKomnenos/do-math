# K5: 6.1 (6.8) 상수와 6.2 B_2 상수의 검산
from math import sqrt, exp, log, pi, ceil, e
from fractions import Fraction
from math import factorial
out=[]
# 6.1
C=3; k=4000
qs=ceil((C*k)**(2/3)); out.append(f"q*={qs}, (Ck)^(2/3)={(C*k)**(2/3):.4f}")
lhs=1-1.6/sqrt(525); out.append(f"lhs={lhs:.6f}")
t1=0.8*sqrt(2)/3*(1+1/(2*524)); t2=(1.212+1.203+1.508)*3**(-4/3)*4000**(-1/3); t3=1.5/(3*sqrt(525))
out.append(f"t1={t1:.6f} t2={t2:.6f} t3={t3:.6f} sum={t1+t2+t3:.6f} x2={2*(t1+t2+t3):.6f}")
out.append(f"1.2(1-2/525)^-2.5={1.2*(1-2/525)**-2.5:.6f}; 1.2(1+2/525)^.5={1.2*(1+2/525)**.5:.6f}; 1.5(1-1/525)^-2.5={1.5*(1-1/525)**-2.5:.6f}")
out.append(f"2/sqrt(2pi)={2/sqrt(2*pi):.6f}")
# 6.2 B_2
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
out.append(f"B2(43)={B2(43):.6f} B2(42)={B2(42):.6f} B2(2000)={B2(2000):.6f} B2(4)={B2(4):.4f} B2(3)={B2(3):.4f}")
# exact small k
def Bor_q_sum(k):
    x=Fraction(k,k+1)**(k-1)
    s=Fraction(0)
    for n in range(2,k+2):
        s+=Fraction(n**(n-1),factorial(n))*x**n
    return s
mx=max((Bor_q_sum(k),k) for k in range(2,43))
out.append(f"max over 2..42: {float(mx[0]):.6f} at k={mx[1]}; k=2:{Bor_q_sum(2)}; k=42:{float(Bor_q_sum(42)):.6f}")
# direct check of (6.3) for k=4000, small range, exact-ish floats
import math
def Bor(d): return math.exp(-d+ (d-1)*math.log(d) - math.lgamma(d+1))
k=4000
Bt=[0.0]*(k+2)
# Bor_> (q)
tail=1.0
Bg=[0.0]*(k+2)
cum=0.0
for q in range(0,k+1):
    if q>=1: cum+=Bor(q)
    Bg[q]=1-cum
def Bc(q): return 1.0 if q==0 else min(1.0,3*k*q**-1.5)
worst=1e9
for q in range(1,k+1):
    rhs=Bg[q]+sum(Bor(N+1)*k/(k+q-N)*Bc(q-1-N) for N in range(0,q))
    worst=min(worst,Bc(q)-rhs)
    if q%1000==0 or q in (524,525,526,600): out.append(f"q={q}: B={Bc(q):.6f} rhs={rhs:.6f} diff={Bc(q)-rhs:.3e}")
out.append(f"min diff over q=1..k: {worst:.3e}")
open(__import__('os').path.join(__import__('os').path.dirname(__file__),'검토전체17_K5_61_62.out'),'w',encoding='utf-8').write("\n".join(out))
