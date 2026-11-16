# 검토전체7 M2: 3장·4장 수치 검산
from fractions import Fraction as Fr
from math import gamma, sqrt, pi, exp, log
import sympy as sp

print("== 3.6 유리수 ==")
lam=Fr(751,1000); J=8
val=lam**J+Fr(1,31)*sum(i*lam**(i-1) for i in range(1,J+1))+Fr(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print(val, val==Fr(7309649993107890414228499,15500000000000000000000000), float(val))
# E_n omega_n small n: sum_{j<=n/2} C(n,j) j^j p_{n-j}/p_n
from math import comb
p=lambda m:(m+1)**(m-1) if m>0 else 1
for n in range(1,6):
    print(n, sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1)))
print("9n^2-48n-32 at 6:",9*36-48*6-32)

print("== Mellin/곱표현 일관성 ==")
def EX(s): return (1.5)**(s/3)*gamma(1+2*s/3)*gamma(5/6-s/3)/gamma(5/6)*gamma(0.5-s/3)*gamma(2/3)/(gamma(0.5)*gamma(2/3-s/3))
# E X^sigma = Gamma(1+2s/3) E B^{-2s/3}; s=-3/2 -> E B^1 =(2/3)sqrt(2/pi)
s=-1.5+1e-9
print("E B ~", EX(s)/gamma(1+2*s/3), (2/3)*sqrt(2/pi))
# tail const: (3/2-s) E X^s -> (3/2) c, c=sqrt(2/pi)
s=1.5-1e-7
print("residue", (1.5-s)*EX(s), 1.5*sqrt(2/pi))
print("Legendre", gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))

print("== 따름정리 수치 ==")
w=Fr(699,100)
v=w-Fr(7,2)-(6*w+Fr(3,4))/31-(13*w/2)/961-12*w/30000
print(v, v==Fr(495594511,240250000), float(v))
w=Fr(698,100); a0=Fr(12879,10000); a1=Fr(939,1000)
k13=10000**(-1/3); k23=10000**(-2/3)
v2=float(w-Fr(7,2))-float((4*w+Fr(1,2))*a0)*k13-float(13*w/2*a1)*k23-float(12*w)/10000
print("(다)", v2, v2>=1.6809)
# a0,a1
import mpmath as mp
mp.mp.dps=30
print("a0", mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]), "a1", mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf]))
print("Wi margin k>=10000:", 5.642*1.6809*0.39893-0.0163-3.554)
print("46sqrt2-12=",46*sqrt(2)-12, " -5468.28/100 ->", 46*sqrt(2)-12-54.6828)
print("0.4503*3*2.50663+0.16752=",0.4503*3*2.50663+0.16752)
print("Bn bound sqrt2/pi=",sqrt(2)/pi)
print("arc 30000:",30000**5*exp(-30000/520))
print("T(1/2): 1/2+2/9? g_k", 2+4.99)

print("== M_2/M_0, M_4/M_0 기호 검산 ==")
n,y,th,N=sp.symbols('n y vartheta N')
He=sp.symbols('He_n He_nm1')  # He_n, He_{n-1}
Hn,Hm1=He
# backward recurrence: He_{j} = N He_{j-1} - (j-1) y He_{j-2} -> He_{j-2} = (N He_{j-1} - He_j)/((j-1) y)
def lower(seq):  # seq: dict j->expr for j=n, n-1; extend downward
    pass
H={n:Hn, n-1:Hm1}
for m in range(2,6):
    j=n-m+2  # compute He_{j-2}
    H[n-m]=sp.simplify((N*H[n-m+1]-H[n-m+2])/((n-m+1)*y))
def numer(r):
    # n! [Y^n] (1-Y)^{r+1} B = sum_i C(r+1,i)(-1)^i n!/(n-i)! He_{n-i}
    tot=0
    for i in range(r+2):
        ff=sp.prod([n-t for t in range(i)]) if i>0 else 1
        tot+=sp.binomial(r+1,i)*(-1)**i*ff*H[n-i]
    return tot
M0=numer(0); M2=numer(2); M4=numer(4)
sub={Hn:(n+th)*Hm1, N:n+y+1}
r2=sp.simplify((M2/M0).subs(sub))
claim2=(th*((n-y)**2+n)-n*(n+1))/(y**2*th)
print("M2/M0 ok:", sp.simplify(r2-claim2)==0)
r4=sp.simplify((M4/M0).subs(sub))
k=sp.symbols('k')
for nu in (0,-1):
    e=sp.simplify(r4.subs({n:2*k+nu,y:k}))
    if nu==0:
        cl=1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/th
    else:
        cl=1+12/k-6/k**2-(4+26/k-14/k**2)/th
    print("nu",nu,"M4/M0 ok:", sp.simplify(e-cl)==0)
    center = 4-26/k+506/k**2 if nu==0 else 4-22/k+414/k**2
    ser=sp.series(e.subs(th,center),k,sp.oo,4)
    print("  series at center:", ser)
# P coefficients
for nu in (0,-1):
    a=26+4*nu+8*th; b=506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2
    vt=4-a/k+b/k**2
    P=sp.expand((vt*((2*k+nu-(k-th))**2+(2*k+nu))-(2*k+nu)*(2*k+nu+1)))
    print("nu",nu,"P:", sp.collect(P,k))
    den=sp.expand((k-th)**2*vt); print("  den k^1:",sp.collect(den,k).coeff(k,1))
    print("  kP+5den k^1:", sp.expand(k*P+5*den).coeff(k,1), " 100kP+499den k^2:", sp.expand(100*k*P+499*den).coeff(k,2))
