# 검토전체11 Q7a: 보조정리 hermite-nu (나)의 H_0,H_1,H_2 와 (라)의 U_r,V_r, (마)의 M_2/M_0 일반 y 꼴을 sympy로 확인
import sympy as sp
w, th, nu, k, y, n, d = sp.symbols('w theta nu k y n d')
# (나): 1/k -> w
Nk = 3 + (nu+1-th)*w            # N/k
x = w*(1-th*w)/Nk**2            # frak x = y/N^2 with y=k-theta, scaled by 1/k... check: y/N^2 = (k-th)/(k^2 Nk^2) = w(1-th w)/Nk^2
xn = (2 + (nu-1)*w)*(1-th*w)/Nk**2
g = sp.sqrt(1-4*xn)
ups = (1+g)/2
C1 = (1-ups)/g**2
C2 = -(1-ups)*(2+ups)/g**5
C3 = sp.Rational(5,2)*(1-ups)*(6+g-g**2)/g**8
uhat = ups + x*C1 + x**2*C2 + x**3*C3
H = (Nk*uhat - 2 - nu*w)/w
ser = sp.series(H, w, 0, 3).removeO()
ser = sp.expand(ser)
print("H0 =", sp.simplify(ser.coeff(w,0)))
print("H1 =", sp.factor(sp.simplify(ser.coeff(w,1))))
print("H2 =", sp.expand(sp.simplify(ser.coeff(w,2))))
# (라): He recurrence He_{j-1} = (N He_j - He_{j+1})/(y j); M_r/M_0 with y=k, n=2k+nu, He_n/He_{n-1} = n+d
N = n + y + 1
He_n, He_nm1 = sp.symbols('He_n He_nm1')
# coefficient of Y^n in (1-Y)^{r+1} E(Y) = sum_i C(r+1,i)(-1)^i He_{n-i}/(n-i)!, times n!
def He_list(r):
    # express He_{n-i}, i=0..r+1 in terms of He_n, He_{n-1}
    L = {0: He_n, 1: He_nm1}
    for i in range(2, r+2):
        j = n - i + 1   # He_{j-1} = (N He_j - He_{j+1})/(y j), j-1 = n-i
        L[i] = sp.simplify((N*L[i-1] - L[i-2])/(y*j))
    return L
def Mr(r):
    L = He_list(r)
    s = 0
    for i in range(r+2):
        s += sp.binomial(r+1,i)*(-1)**i*L[i]*sp.ff(n, i)   # n!/(n-i)! = falling factorial
    return sp.simplify(s)
M0 = Mr(0); M2 = Mr(2); M4 = Mr(4)
ratio2 = sp.simplify((M2/M0).subs(He_n, (n+d)*He_nm1))
ratio4 = sp.simplify((M4/M0).subs(He_n, (n+d)*He_nm1))
# general y: M2/M0 = 1 - 2n/y + n(n+1)/y^2 - n(n+1)/(y^2 d)?
print("M2/M0 general y check:", sp.simplify(ratio2 - (1 - 2*n/y + n*(n+1)/y**2 - n*(n+1)/(y**2*d))))
r2 = sp.simplify(ratio2.subs({y:k, n:2*k+nu}))
r4 = sp.simplify(ratio4.subs({y:k, n:2*k+nu}))
U2 = 1 + (2*nu+2)/k + nu*(nu+1)/k**2; V2 = 4 + (4*nu+2)/k + nu*(nu+1)/k**2
U4 = 1 + (4*nu+16)/k + (6*nu**2+30*nu+18)/k**2 + (4*nu**3+17*nu**2+15*nu+2)/k**3 + nu*(nu+1)**3/k**4
V4 = 4 + (12*nu+38)/k + (13*nu**2+49*nu+22)/k**2 + (6*nu**3+21*nu**2+17*nu+2)/k**3 + nu*(nu+1)**3/k**4
print("U2-V2/d check:", sp.simplify(r2 - (U2 - V2/d)))
print("U4-V4/d check:", sp.simplify(r4 - (U4 - V4/d)))
# (마) k-coefficient of n(n+1) - d_y[(n-y)^2+n] with d_y = 4 + H1/k, y=k-theta, n=2k+nu
H1 = -(26+4*nu) - 8*th
expr = sp.expand((n*(n+1) - (4 + H1/k)*((n-y)**2+n)).subs({n:2*k+nu, y:k-th}))
print("k^2 coeff:", sp.expand(expr).coeff(k,2), " k^1 coeff:", sp.expand(expr).coeff(k,1))
