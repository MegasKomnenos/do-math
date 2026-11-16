import sympy as sp
n,y,k,nu,th,d,w=sp.symbols('n y k nu theta d w')
# Hermite recurrence: He_{j+1} = N He_j - y j He_{j-1}, N=n+y+1.  E_j = He_j/j!
# M_r proportional to [Y^n](1-Y)^{r+1} B(Y) = sum_i (-1)^i C(r+1,i) E_{n-i}
# Express E_{n-1},E_{n-2},... in terms of E_n, E_{n-1} via backward recurrence:
# He_{j-1} = (N He_j - He_{j+1})/(y j)
N=n+y+1
Hn, Hn1 = sp.symbols('Hn Hn1')  # He_n, He_{n-1}
He={n:Hn, n-1:Hn1}
for i in range(2,6):
    j=n-i+1  # He_{j-1} = (N He_j - He_{j+1})/(y j)
    He[n-i]=sp.simplify((N*He[n-i+1]-He[n-i+2])/(y*(n-i+1)))
def coef(r):
    # [Y^n](1-Y)^{r+1}B = sum_i (-1)^i C(r+1,i) He_{n-i}/(n-i)!
    # multiply by n!: sum_i (-1)^i C(r+1,i) n!/(n-i)! He_{n-i}
    s=0
    for i in range(r+2):
        s+=(-1)**i*sp.binomial(r+1,i)*sp.ff(n,i)*He[n-i]
    return sp.expand(s)
M0=coef(0); M2=coef(2); M4=coef(4)
# substitute He_n = (n+d) He_{n-1}
sub={Hn:(n+d)*Hn1}
r2=sp.simplify((M2/M0).subs(sub)); r4=sp.simplify((M4/M0).subs(sub))
# (마): claim M2/M0 = 1-2n/y+n(n+1)/y^2 - n(n+1)/(y^2 d)
claim=1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d)
print("M2/M0 general y ok:", sp.simplify(r2-claim)==0)
# (라) at y=k, n=2k+nu: U_r - V_r/d
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
s2=r2.subs({y:k,n:2*k+nu}); s4=r4.subs({y:k,n:2*k+nu})
print("U2,V2 ok:", sp.simplify(s2-(U2-V2/d))==0)
print("U4,V4 ok:", sp.simplify(s4-(U4-V4/d))==0)
# k-coefficient of n(n+1)-d[(n-y)^2+n] with d = 4-(26+4nu+8th)/k + H2/k^2
H2=506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2
dd=4-(26+4*nu+8*th)/k+H2/k**2
P=sp.expand((n*(n+1)-dd*((n-y)**2+n)).subs({n:2*k+nu,y:k-th}))
poly=sp.Poly(sp.expand(P*k**2),k)
print("coeffs in k (deg desc):",[sp.factor(c) for c in poly.all_coeffs()[:3]])
# H expansion: H(w)=((N/k) vhat(x_n) - 2 - nu w)/w with w=1/k
Nk=3+(nu+1-th)*w
x=w*(1-th*w)/Nk**2
xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
g=sp.sqrt(1-4*xn)
vo=(1+g)/2
C1=(1-vo)/g**2; C2=-(1-vo)*(2+vo)/g**5; C3=sp.Rational(5,2)*(1-vo)*(6+g-g**2)/g**8
vhat=vo+x*C1+x**2*C2+x**3*C3
H=(Nk*vhat-2-nu*w)/w
ser=sp.series(H,w,0,3).removeO()
ser=sp.expand(ser)
print("H0:",sp.simplify(ser.coeff(w,0)))
print("H1:",sp.factor(ser.coeff(w,1)))
print("H2:",sp.expand(ser.coeff(w,2)), " claim:",sp.expand(H2), " diff:",sp.simplify(ser.coeff(w,2)-H2))
# check nm
nm=1+(2*nu+10+2*th)*w+((nu+1)**2+2*(nu-3)*th+th**2)*w**2
print("nm ok:", sp.simplify((1-4*xn)*Nk**2-nm)==0)
# sqrt(nm) expansion first order
print("sqrt nm:", sp.series(sp.sqrt(nm),w,0,2))
