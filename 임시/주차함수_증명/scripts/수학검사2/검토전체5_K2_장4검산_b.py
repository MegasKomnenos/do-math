# K2 장4 검산 (b): 수치 — 중앙 상쇄 항등식, J 선도 적분, a0·a1, 조립 수치, -2/3 상수, 작은 n의 행
from fractions import Fraction as F
from math import comb, sqrt, pi, exp, gamma
import mpmath as mp
mp.mp.dps=15
ninf = 2/sqrt(pi)
def BorldR(b):  # e^{b^2/2}(2-2 b D(b)), D(b)=e^{-b^2/2} int_0^b e^{v^2/2} dv = sqrt(pi/2) e^{-b^2/2} erfi(b/sqrt2)
    D = float(mp.sqrt(mp.pi/2)*mp.exp(-b*b/2)*mp.erfi(b/mp.sqrt(2)))
    return exp(b*b/2)*(2-2*b*D)
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z):
    inner = float(mp.quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*BorldR(r*z)/sqrt(2*pi), [0,1]))
    return -ninf*z**4*exp(-z*z)*inner
def F1(z):
    inner = float(mp.quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*((4/3)*r*r*z*z-(2/3)*r*z**4), [0,1]))
    return -ninf*z**4*exp(-z*z)*inner
I0 = 2*float(mp.quad(F0,[0,1,2,3,4,6,9])); I1 = 2*float(mp.quad(F1,[0,1,2,3,4,6,9]))
print("int F0 =", I0, "| int F1 =", I1, "| 46sqrt2-12 =", 46*sqrt(2)-12)
IJ = float(mp.quad(lambda z: z**3*mp.exp(-z*z/2)*((mp.mpf(4)/15)*z**3-z/3), [-mp.inf,mp.inf]))
print("J leading:", IJ, "| 3sqrt(2pi) =", 3*sqrt(2*pi))
a0 = 3**(1/3)*gamma(4/3); a1 = 3**(-1/3)*gamma(2/3)
print("a0 =", repr(a0), " in (1.287899,1.2879):", 1.287899<a0<1.2879, "| a1 =", repr(a1), " in (0.938892,0.939):", 0.938892<a1<0.939)
v = F(699,100)-F(7,2)-(6*F(699,100)+F(3,4))/31-(13*F(699,100)/2)/961-12*F(699,100)/30000
print("(나) value:", v, float(v), "equals claimed:", v==F(495594511,240250000))
om=6.98; k0=10000
val = om-3.5-(4*om+0.5)*1.2879*k0**(-1/3)-(13*om/2)*0.939*k0**(-2/3)-12*om/k0
print("(다) value >=1.6809?", val)
print("assembly k>=10000:", 5.642*1.6809*0.39893-0.0163-3.554, "| k>=30000:", 5.5*0.39*2-3.5)
print("D vert k>=30000:", 46*sqrt(2)-12-5000/173-0.02, "| k>=10000:", 46*sqrt(2)-12-54.6828)
print("bJ k>=30000:", 0.451*3*sqrt(2*pi)+1678/30000+0.01, "| k>=10000:", 0.4503*3*2.50663+1675.2/10000)
print("sqrt2/pi =", sqrt(2)/pi, "| k^5 e^{-k/520} at 30000:", 30000**5*exp(-30000/520), "| 255/131072 vs 1/520:", 255/131072, 1/520)
print("4sqrt2(1-26/k) at 1e4, 3e4:", 4*sqrt(2)*(1-26/1e4), 4*sqrt(2)*(1-26/3e4))
print("(2pi)^{-1/2}(1-1/120000) =", (2*pi)**-0.5*(1-1/120000))
# -2/3 constant
mp.mp.dps=20
def Bor(j): j=int(j); return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
S = mp.nsum(lambda j: j*Bor(j) - 1/mp.sqrt(2*mp.pi)/mp.sqrt(j), [1,mp.inf])
print("const check:", S + mp.zeta(0.5)/mp.sqrt(2*mp.pi), " target -2/3 =", -2/3)
# 작은 n
def p(n): return (n+1)**(n-1) if n>=1 else 1
Nmax=40; A={}
for l in range(Nmax):
    A[(0,l)]=1
    for m in range(1,Nmax+1):
        A[(m,l)] = p(m) if l>=m-1 else sum(comb(m-1,j)*min(j+1,l+1)*A[(j,l)]*A[(m-1-j,l)] for j in range(m))
out=[]
for m in range(2,Nmax+1):
    row=[A[(m,l)]-(A[(m,l-1)] if l>=1 else 0) for l in range(m)]
    kn=-(-m//2); d=row[kn]-row[kn-1]
    rh = all(row[j]>=row[j+1] for j in range(kn,m-1))
    cross = (row[kn]<row[kn+1]) if kn+1<m else None
    out.append((m, '+' if d>0 else '-', 'R' if rh else '.', 'X' if cross else '.'))
print("n: d_center sign, right-half nonincreasing(R), b_kn<b_kn+1 (X):")
print(out)
# 보조: -2/3 상수의 직접 부분합 + 점근 꼬리
from math import lgamma, log
c=(2*pi)**-0.5
def term(j):
    # j Bor(j) - c j^{-1/2},  Bor(j)=e^{-j} j^{j-1}/j!
    lb = -j + (j-1)*log(j) - lgamma(j+1)
    return j*exp(lb) - c/sqrt(j)
J=2_000_000
S=sum(term(j) for j in range(1,J+1))
tail = -(c/12)*2/sqrt(J) + (c/288)*(2/3)*J**-1.5   # int_J^inf of -(c/12) j^{-3/2} + (c/288) j^{-5/2}
zeta_half = -1.4603545088095868
print("direct const:", S+tail+c*zeta_half, " target -2/3")
