# R2 검산: 보조정리 4:hermite-nu (나)의 H_0..H_3, (라)의 U_i, V_i
import sympy as sp
k, nu, th, e = sp.symbols('k nu theta epsilon')
# --- (라): y=k, n=2k+nu, N=3k+nu+1
n = 2*k+nu; N = 3*k+nu+1; y = k
vt = sp.symbols('vartheta')
# He_{n-1}=1, He_n = n+vt ; backwards: He_{j-2} = (N He_{j-1} - He_j)/((j-1) y)
He = {0: n+vt, 1: sp.Integer(1)}   # He[i] = He_{n-i}
for i in range(2, 6):
    # j = n-i+2 : He_{n-i} = (N He_{n-i+1} - He_{n-i+2})/((n-i+1) y)
    He[i] = sp.simplify((N*He[i-1] - He[i-2])/((n-i+1)*y))
def M(i):
    # proportional: sum_{j=0}^{i+1} (-1)^j C(i+1,j) He_{n-j}/(n-j)!  ; multiply by (n-1)! 
    s = 0
    for j in range(i+2):
        # (n-1)!/(n-j)! 
        if j == 0: f = sp.Integer(1)/n
        else:
            f = sp.Integer(1)
            for t in range(1, j): f *= (n-t)
        s += (-1)**j*sp.binomial(i+1, j)*He[j]*f
    return sp.simplify(s)
M0 = M(0)
print('M0 ~', sp.factor(M0))
for i, U, V in ((2, 1+(2*nu+2)/k+nu*(nu+1)/k**2, 4+(4*nu+2)/k+nu*(nu+1)/k**2),
                (4, 1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4,
                    4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4)):
    r = sp.simplify(M(i)/M0 - (U - V/vt))
    print('M%d/M0 - (U-V/vt) =' % i, r)
# --- (나): H expansion, y=k-theta, eps=1/k
Nk = 3+(nu+1-th)*e
nm = 1+(2*nu+10+2*th)*e+((nu+1)**2+2*(nu-3)*th+th**2)*e**2
xn = (2+(nu-1)*e)*(1-th*e)/Nk**2
print('nm check', sp.simplify(1-4*xn - nm/Nk**2))
gam = sp.sqrt(nm)/Nk
x = e*(1-th*e)/Nk**2
u0 = (1+gam)/2
C1 = (1-u0)/gam**2; C2 = -(1-u0)*(2+u0)/gam**5; C3 = 5*(1-u0)*(6+gam-gam**2)/(2*gam**8)
uh = u0 + x*C1 + x**2*C2 + x**3*C3
H = (Nk*uh - 2 - nu*e)/e
ser = sp.series(H, e, 0, 4).removeO()
tgt = [4, -(26+4*nu)-8*th, 506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2,
       -(11016+3187*nu+239*nu**2+6*nu**3)-(5362+762*nu+26*nu**2)*th-(594+36*nu)*th**2-16*th**3]
for j in range(4):
    print('H_%d diff:' % j, sp.expand(sp.simplify(ser.coeff(e, j)) - tgt[j]))
