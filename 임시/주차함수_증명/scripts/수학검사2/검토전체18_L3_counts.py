from fractions import Fraction as F
from math import ceil, floor, e, pi, sqrt, exp, log, factorial
import mpmath as mp
out=[]
# counts
c4=sum(n-2-ceil((n-1)/2) for n in range(5,20001)); out.append(("4th piece positions (5..20000)",c4))
pairs20=sum(n-1-ceil((n-1)/2) for n in range(5,20001)); out.append(("adjacent pairs 5..20000",pairs20))
c50=sum(n-2-ceil((n-1)/2) for n in range(20001,50001)); out.append(("positions 20001..50000",c50))
p50=sum(n-1-ceil((n-1)/2) for n in range(20001,50001)); out.append(("pairs 20001..50000",p50))
c2=sum(ceil(n/2)-1 for n in range(10001,20001)); out.append(("2nd piece comparisons",c2))
# cayley ratio values
for k in range(1,10):
    v=F(k+1,k)**(k-2)*(1+F(5,2*k)+F(2,k*k)); out.append((f"cr_{k}(1+5/2k+2/k^2)",float(v), v>F(87,32)))
out.append(("e<65/24+1/100", e<65/24+0.01, 65/24+0.01, "87/32", 87/32))
out.append(("sqrt(3pi/2)", sqrt(3*pi/2), sqrt(3*pi/2)<2.170804, "1/2+1.690408-sqrt", 0.5+1.690408-sqrt(3*pi/2)))
# m(n)
def mfun(n):
    m=170
    for t in range(171, 2000):
        if t**3 <= (n-9*t)**2 and n-9*t>0: m=t
    return m
out.append(("m(20001)",mfun(20001),"m(50001)",mfun(50001)))
# bracket at s=100
s=100.0; br=1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3; out.append(("bracket s=100",br))
# tail ratio 5-7
rt=9/16*169/400*144/121*88/1443*(2.5+9/1058)**3; out.append(("tail ratio j=13",rt))
# rq* 
out.append(("rq*",13/20*(1+3/529)/23, 1/12))
# r0 claims
out.append(("27.14^3",27.14**3, "(149/200)^3",(149/200)**3,"(16/25)^2",(16/25)**2,"(3/4)^3",(3/4)**3,"(13/20)^2",(13/20)**2))
out.append(("20001^(2/3)",20001**(2/3), "r0(20001)", floor(0.75*20001**(2/3))))
out.append(("(12/11)^1.5*(1+1/598)",(12/11)**1.5*(1+1/598), "12/(110e)",12/(110*e), 1/24))
out.append(("log10(1.15*598^3)",log(1.15*598**3,10),"598log10(24)",598*log(24,10)))
# 833 and 966
out.append(("832^1.5",832**1.5,"833^1.5",833**1.5,"6/5*20001",1.2*20001))
out.append(("965^1.5",965**1.5,"966^1.5",966**1.5,"1.5*20001",1.5*20001))
out.append(("597^1.5+9*597",597**1.5+9*597,"598:",598**1.5+9*598))
out.append(("1/(1+9/sqrt598)",1/(1+9/sqrt(598))))
out.append(("rq bounds",1.2/sqrt(598),1.5/sqrt(833),1.8/sqrt(966),1/16))
out.append(("5/9*sqrt(598)",5/9*sqrt(598)))
out.append(("(9/5)^(2/3)",1.8**(2/3),"10/2^(2/3)",10/2**(2/3)))
out.append(("1-cos1",1-mp.cos(1)))
# Xi for j'=25,31 at x=1.8 rq=1/12 r=966
for jp in (25,31):
    Xi=9/16*(1.8**2)/((11/12)**2)*2*(3*jp+5)/(3*jp*(3*jp-2))*(2.5+1.5/966)**3; out.append((f"Xi j'={jp}",Xi))
# et(1/2)
mp.mp.dps=30
phi=mp.mpf(1)/2; et=mp.e*phi*mp.exp(-phi*mp.cot(phi))/mp.sin(phi); out.append(("log et(1/2)",mp.log(et)))
# L(10^4)
M=[mp.quad(lambda y: y**i*mp.exp(-y-y*y/2),[0,mp.inf]) for i in range(6)]
M26=mp.quad(lambda y: y**2*mp.exp(-y-y*y/2),[0,6])
Ms=[None]+[ (lambda i: (lambda ys: ys**i*mp.exp(-ys-ys*ys/2))((-1+mp.sqrt(1+4*i))/2))(i) for i in range(1,6)]
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
st=mp.mpf(1)/100
L=(M26-st*C1-st**2*C2-st**3*C3-st**4*C4)/(M[1]+st*(M[0]+mp.exp(-0.5))+st**2)
out.append(("M0..M5",[mp.nstr(x,6) for x in M],"C1..C4",[mp.nstr(x,6) for x in (C1,C2,C3,C4)],"L(1e4)",mp.nstr(L,8)))
# tm_{r-1}(rho) check at r=1e4
r=10000; rho=mp.exp(-mp.mpf(1)/100)
bt=mp.mpf(1); Nu=mp.mpf(0); De=mp.mpf(0)
for j in range(0,r):
    w=(j+1)*rho**j*bt; Nu+=j*w; De+=w; bt*= (1-mp.mpf(j+1)/r)
out.append(("tm_{9999}(e^-0.01)/100",mp.nstr(Nu/De/100,6)))
for o in out: print(o)
