# R2 검산: 보조정리 4:hermite-nu (나) H_j, (라) U_i,V_i, (마) 계수 20
import sympy as sp
w, nu, th = sp.symbols('w nu theta')
Nk = 3 + (nu+1-th)*w
nm = 1 + (2*nu+10+2*th)*w + ((nu+1)**2 + 2*(nu-3)*th + th**2)*w**2
g = sp.sqrt(nm)/Nk
x = w*(1-th*w)/Nk**2
u0 = (1+g)/2
C1 = (1-u0)/g**2
C2 = -(1-u0)*(2+u0)/g**5
C3 = 5*(1-u0)*(6+g-g**2)/(2*g**8)
hat = u0 + x*C1 + x**2*C2 + x**3*C3
H = (Nk*hat - 2 - nu*w)/w
ser = sp.series(H, w, 0, 4).removeO()
for j in range(4):
    print('H_%d ='%j, sp.factor(sp.expand(ser.coeff(w, j))) if j==3 else sp.expand(ser.coeff(w,j)))
H3 = sp.expand(ser.coeff(w,3))
# (라): M_i/M_0 in terms of vartheta
n, y, N, vt, k = sp.symbols('n y N vartheta k')
# He_n = (n+vt) * He_{n-1}; set He_{n-1}=1
He = {0: n+vt, 1: sp.Integer(1)}   # He[d] = He_{n-d}
# backward: He_{j-1} = (N He_j - He_{j+1})/(y j)  -> He_{n-d-1} = (N He_{n-d} - He_{n-d+1})/(y (n-d))
for d in range(1,6):
    He[d+1] = sp.simplify((N*He[d] - He[d-1])/(y*(n-d)))
def M(i):
    # n! [Y^n] (1-Y)^{i+1} B(Y) = sum_d C(i+1,d)(-1)^d n!/(n-d)! He_{n-d}
    s = 0
    for d in range(0, i+2):
        s += sp.binomial(i+1,d)*(-1)**d*sp.ff(n,d)*He[d]
    return sp.simplify(s)
M0, M2, M4 = M(0), M(2), M(4)
for i,Mi in ((2,M2),(4,M4)):
    r = sp.simplify((Mi/M0).subs(N, n+y+1))
    # general y formula check for i=2
    if i==2:
        gen = 1 - 2*n/y + n*(n+1)/y**2 - n*(n+1)/(y**2*vt)
        print('M2/M0 general-y identity:', sp.simplify(r-gen))
    rk = sp.simplify(r.subs({y:k}).subs(n, 2*k+nu))
    # write as U - V/vt
    U = sp.limit(rk, vt, sp.oo)
    V = sp.simplify((U - rk)*vt)
    print('U_%d ='%i, sp.expand(sp.simplify(U)))
    print('V_%d ='%i, sp.expand(sp.simplify(V)))
# (마): n(n+1) - vt_y[(n-y)^2+n], with vt_y = H0 + H1/k + ..., n=2k+nu, y=k-theta
kk = sp.symbols('kk', positive=True)
vty = 4 + (-(26+4*nu)-8*th)/kk + sp.Symbol('H2')/kk**2
nn = 2*kk+nu; yy = kk-th
expr = sp.expand(nn*(nn+1) - vty*((nn-yy)**2+nn))
print('k^2 coeff:', sp.simplify(expr.coeff(kk,2)), ' k^1 coeff:', sp.simplify(expr.coeff(kk,1)))
