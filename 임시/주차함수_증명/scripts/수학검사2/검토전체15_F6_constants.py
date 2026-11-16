# F6: recompute numeric constants quoted in chapter 7A (7.2 self-consistent table, cor-S-prime, column lemma, t_k, polar-N)
from fractions import Fraction as Fr
import math
from decimal import Decimal, getcontext
getcontext().prec=60

def g(x): return (x-1)*math.log(1+1/x)
def ao(m): return Fr((m+1)**(m-1),math.factorial(m)) if m>0 else Fr(1)

print("== t_k and n^sharp_k, n^flat_k, n^circ_k samples")
def t_k(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1)>=2*k**(2*j+1)): j+=1
    return j
def xk(k): return (k/(k+1))**(k-1)
def phi(k,n):
    m=(n-k)/(k+1); return (1+1/k)**m+(1-1/k)**(m+xk(k)*n/k)-2
for k in [2,3,5,10,41,100,501,2001]:
    t=t_k(k); ns=k+(k+1)*t
    # n_flat
    n=2*k+1
    while phi(k,n)<0: n+=1
    nc=math.ceil(2*k**1.5)
    print(k,"t_k",t,"t_k/k=%.4f"%(t/k),"n#",ns,"n^flat",n,"n^circ",nc, "phi(n#)>=0:",phi(k,ns)>=0, "n^flat<=n#:",n<=ns, "n^circ<n^flat:",nc<n)

print("== column lemma (가) arithmetic")
print("10^21*400^10 =",10**21*400**10, "17^21*123^10 =",17**21*123**10, 10**21*400**10>17**21*123**10)
print("17^4",17**4, "17^21 < 6.95e25:",17**21<6.95e25, "123^10<7.93e20:",123**10<7.93e20)
print("(40/41)(10/17)^2.1 =",(40/41)*(10/17)**2.1, " >0.3")
print("o_41 =",-2*math.log(1-1/41)/math.log(1+1/41), "2(k+1)/(k-1) at 41 =",2*42/40)
print("hf'(1.7) lower:",1-2.1*(10/17)**3)

print("== self-consistent table")
def jstar(L):
    m=0
    while math.exp(g(m+2))<L: m+=1   # max m with e^{g(m+1)}<L : check m then m+1
    # ensure
    assert math.exp(g(m+1))<L and math.exp(g(m+2))>=L
    return m
rows=[(Fr(267,100),25,501),(Fr(27,10),70,1855),(Fr(271,100),100,6098)]
for L,J,k0 in rows:
    Lf=float(L); js=jstar(Lf)
    kR=max(2*js+2, math.ceil(float(L**(js+2)/ao(js+1))))
    # E lower
    E_low=sum(float(ao(J+i)/ao(J))*math.exp(-i) for i in range(1,k0-js+1))
    r=Lf/math.e; E_inf=r*(1-r**k0)/(1-r)
    R=max(1/(1+E_low),1/(1+E_inf))
    def fall(v): return float(ao(v))*Lf**(-(v+1))
    def qlow(v): return max(0.0,1-sum(float(ao(j))*Lf**(-(j+1)) for j in range(v)))
    Xi=sum(max(0.0,fall(v)-R*qlow(v)) for v in range(J))
    Xik=sum(max(0.0,float(ao(v))*xk(k0)*Lf**(-v)-R*qlow(v)) for v in range(J))
    A0=xk(k0)+Xik/(Lf*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    print("L",L,"J",J,"k0",k0,"j*",js,"k_R",kR,"R_J %.8f"%R,"(E_low %.5f E_inf %.5f)"%(E_low,E_inf),"Xi %.6f"%Xi,"Xi^(k0) %.6f"%Xik,"A0 %.5f"%A0,"B0 %.7f"%B0)

print("== cor-S-prime values with table (rounded-up) A0,B0")
for (y,k0,A0,B0) in [(0.13,501,1.4708,0.098505),(0.08,1855,2.5335,0.060259),(0.055,6098,2.7354,0.0422)]:
    xi=1/k0
    val=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    nv=((3*xi+xi*xi)/2+(1+xi)**2*B0/2)
    print("y",y,"k0",k0,"g_S(yk^2)/k^4 =",val,"n_v/k^2 =",nv, "yk^2-2k-1 =",y*k0*k0-2*k0-1)

print("== polar-N numbers")
k=2001
print("2*2001^1.5+1 =",2*k**1.5+1,"0.3476*k^2 =",0.3476*k*k, "2/sqrt(2001)=",2/math.sqrt(k), "e^{-1+2/2002}=",math.exp(-1+2/2002), "0.75/sqrt k=",0.75/math.sqrt(k), "x_2001=",xk(2001))
y=0.0448; print("(2cosh y -2 - y^2)/y^2 =",(2*math.cosh(y)-2-y*y)/(y*y), "e^-0.0448=",math.exp(-0.0448), "0.955*0.991*0.3678=",0.955*0.991*0.3678)
print("== polar-W dagger: k=1e7")
k=1e7; print("(1+0.91/sqrt k)^3*8 =",8*(1+0.91/math.sqrt(k))**3, "8.344/sqrt(k)=",8.344/math.sqrt(k), "0.001k+1.001>=2sqrt k:",0.001*k+1.001>=2*math.sqrt(k))
print("== x_k decreasing / o_k>2 / t_k<=k quick")
print([xk(k) for k in (2,3,4,10)])
print("x_501=",xk(501))
