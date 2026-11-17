# R2 검산: 보조정리 4:gauss-contraction, 4:hermite-nu의 기호 항등식
import sympy as sp
g, x, io = sp.symbols('gamma x iota', positive=True)
# iota = (1-g^2)/4 ; d/diota = -(2/g) d/dg
def D(expr, n=1):
    for _ in range(n):
        expr = sp.simplify(-(2/g)*sp.diff(expr, g))
    return expr
u0 = (1+g)/2
C1 = (1-u0)/g**2
C2 = -(1-u0)*(2+u0)/g**5
C3 = 5*(1-u0)*(6+g-g**2)/(2*g**8)
print('u0 4th deriv', sp.factor(D(u0,4)))
print("C1'''", sp.expand(D(C1,3)))
print("C2''", sp.expand(D(C2,2)))
print("C3'", sp.expand(D(C3,1)))
# Taylor of hat u(iota - x) to x^3
m1 = sp.simplify(C1 - D(u0,1))
m2 = sp.simplify(C2 - D(C1,1) + D(u0,2)/2)
m3 = sp.simplify(C3 - D(C2,1) + D(C1,2)/2 - D(u0,3)/6)
print('m1 - u0/g^2', sp.simplify(m1 - u0/g**2))
print('m2 - (C2-2/g^4)', sp.simplify(m2 - (C2 - 2/g**4)))
print('m3 - (C3+5(5-g^2)/(2g^7))', sp.simplify(m3 - (C3 + 5*(5-g**2)/(2*g**7))))
# residual coefficients x^0..x^3 of (hat u -1)*(u0 + x m1 + x^2 m2 + x^3 m3) + iota
iota = (1-g**2)/4
P = (u0-1 + x*C1 + x**2*C2 + x**3*C3)*(u0 + x*m1 + x**2*m2 + x**3*m3) + iota
P = sp.expand(P)
for j in range(0,7):
    print('x^%d'%j, sp.simplify(P.coeff(x,j)))
