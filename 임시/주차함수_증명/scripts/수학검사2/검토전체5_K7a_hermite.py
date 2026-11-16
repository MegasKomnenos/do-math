# K7a 검산: 보조정리 hermite-nu의 H_0,H_1,H_2 전개, U_r/V_r 닫힌 꼴, (마)의 M2/M0 식
import sympy as sp
w,nu,th=sp.symbols('w nu theta')  # w=1/k
Nk=3+(nu+1-th)*w
x=w*(1-th*w)/Nk**2
xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
g=sp.sqrt(1-4*xn)
up=(1+g)/2
C1=(1-up)/g**2; C2=-(1-up)*(2+up)/g**5; C3=sp.Rational(5,2)*(1-up)*(6+g-g**2)/g**8
uhat=up+x*C1+x**2*C2+x**3*C3
H=(Nk*uhat-2-nu*w)/w
ser=sp.series(H,w,0,3).removeO()
ser=sp.expand(ser)
for j in range(3):
    print("H_%d ="%j, sp.factor(sp.expand(ser.coeff(w,j))))
# U_r, V_r : M_r/M_0 with M_r ∝ [Y^n](1-Y)^{r+1} E, He_{j-1}=(N He_j - He_{j+1})/(y j)
n,y,d=sp.symbols('n y d')
N=n+y+1
He={}
He[n]=sp.Symbol('Hn'); He[n-1]=He[n]/(n+d)
def Hem(i):  # He_{n-i} for i>=0 using backward recurrence He_{j-1}=(N He_j - He_{j+1})/(y j)
    if i==0: return He[n]
    if i==1: return He[n-1]
    j=n-i+1
    return sp.simplify((N*Hem(i-1)-Hem(i-2))/(y*j))
def coef(r):
    # [Y^n](1-Y)^{r+1}E = sum_i C(r+1,i)(-1)^i He_{n-i}/(n-i)!
    tot=0
    for i in range(r+2):
        tot+=sp.binomial(r+1,i)*(-1)**i*Hem(i)/sp.factorial(n-i)*sp.factorial(n)
    return sp.simplify(tot)
M0=coef(0); M2=coef(2); M4=coef(4)
r2=sp.simplify(M2/M0); r4=sp.simplify(M4/M0)
# at y=k, n=2k+nu: express as U - V/d
k=sp.Symbol('k')
r2k=sp.simplify(r2.subs({y:k,n:2*k+nu}))
r4k=sp.simplify(r4.subs({y:k,n:2*k+nu}))
# U = limit d->oo, V = -(r - U)*d
U2=sp.simplify(sp.limit(r2k,d,sp.oo)); V2=sp.simplify(-(r2k-U2)*d)
U4=sp.simplify(sp.limit(r4k,d,sp.oo)); V4=sp.simplify(-(r4k-U4)*d)
for name,e in [("U2",U2),("V2",V2),("U4",U4),("V4",V4)]:
    print(name,"=",sp.expand(e))
# claimed
cU2=1+(2*nu+2)/k+nu*(nu+1)/k**2; cV2=4+(4*nu+2)/k+nu*(nu+1)/k**2
cU4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
cV4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
print("U2 ok",sp.simplify(U2-cU2)==0,"V2 ok",sp.simplify(V2-cV2)==0,"U4 ok",sp.simplify(U4-cU4)==0,"V4 ok",sp.simplify(V4-cV4)==0)
# (마) general y
print("M2/M0 general:", sp.simplify(r2 - (1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))))
# (마) k-coefficient 20 claim: n(n+1)-d[(n-y)^2+n] with d=4-(26+4nu+8th)/k, y=k-th, n=2k+nu
dy=4-(26+4*nu+8*th)*w
expr=sp.expand(((2+nu*w)*(2+(nu+1)*w) - dy*(((1+nu*w+th*w))**2 + (2+nu*w)*w))/w**2)  # divided by k^2
print("k^2 coeff:",expr.coeff(w,0)," k coeff:",expr.coeff(w,1))
