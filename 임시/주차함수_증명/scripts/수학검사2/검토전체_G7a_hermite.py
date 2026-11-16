# G7a: hermite-nu (라) U_r, V_r 검산 및 pair-check-10000 경우 수·최솟값 검산
import sympy as sp
from fractions import Fraction
k, nu, d, h = sp.symbols('k nu d h', positive=True)
n = 2*k + nu
y = k
N = n + y + 1
He = {}
He[n] = (n + d) * h
He[n - 1] = h
# reverse recurrence He_{j-1} = (N He_j - He_{j+1})/(y j)
def he(j):
    # j = n - s
    if j in He: return He[j]
    s = sp.simplify(n - j)
    # He_{j} = (N He_{j+1} - He_{j+2})/(y (j+1))
    He[j] = sp.simplify((N*he(j+1) - he(j+2))/(y*(j+1)))
    return He[j]
def falling(nn, j):
    r = 1
    for i in range(j): r *= (nn - i)
    return r
def M(r):
    # n! [Y^n] (1-Y)^{r+1} exp(...) = sum_j C(r+1,j) (-1)^j (n)_j He_{n-j}
    tot = 0
    for j in range(r+2):
        tot += sp.binomial(r+1, j) * (-1)**j * falling(n, j) * he(n - j)
    return sp.simplify(tot)
M0 = M(0); M2 = M(2); M4 = M(4)
ratio2 = sp.simplify(M2/M0); ratio4 = sp.simplify(M4/M0)
U2 = 1 + (2*nu+2)/k + nu*(nu+1)/k**2
V2 = 4 + (4*nu+2)/k + nu*(nu+1)/k**2
U4 = 1 + (4*nu+16)/k + (6*nu**2+30*nu+18)/k**2 + (4*nu**3+17*nu**2+15*nu+2)/k**3 + nu*(nu+1)**3/k**4
V4 = 4 + (12*nu+38)/k + (13*nu**2+49*nu+22)/k**2 + (6*nu**3+21*nu**2+17*nu+2)/k**3 + nu*(nu+1)**3/k**4
print('M2/M0 - (U2 - V2/d) =', sp.simplify(ratio2 - (U2 - V2/d)))
print('M4/M0 - (U4 - V4/d) =', sp.simplify(ratio4 - (U4 - V4/d)))
# pair-check-10000
K = 10000
def pish(q): return Fraction(q*(q-1), 2*(K+1))
def exbar(q):
    p = pish(q); return q + (K+q)*p/(1-p)
cnt = 0; cnt_sym = 0; mn = None; arg = None
for q in range(1, 50):
    for qp in range(1, 50):
        for j in range(0, 51):
            if q+qp+j > 50: continue
            cnt += 1
            if q <= qp: cnt_sym += 1
            rhs = 1 - Fraction(j, K)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/Fraction(2*K)
            if mn is None or rhs < mn: mn = rhs; arg = (q, qp, j)
print('cases (ordered):', cnt, ' cases (q<=q\'):', cnt_sym, ' min:', float(mn), arg)
