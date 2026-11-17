import sympy as sp
w,nu,th = sp.symbols('w nu theta')
Nt = 3+(nu+1-th)*w
xn = (2+(nu-1)*w)*(1-th*w)/Nt**2
x = (1-th*w)*w/Nt**2
nm = 1+(2*nu+10+2*th)*w+((nu+1)**2+2*(nu-3)*th+th**2)*w**2
assert sp.simplify(Nt**2*(1-4*xn)-nm)==0
g = sp.sqrt(nm)/Nt   # gamma = sqrt(1-4 x_n)
u0 = (1+g)/2
C1 = (1-u0)/g**2
C2 = -(1-u0)*(2+u0)/g**5
C3 = 5*(1-u0)*(6+g-g**2)/(2*g**8)
uh = u0 + x*C1 + x**2*C2 + x**3*C3
H = (Nt*uh-2-nu*w)/w
ser = sp.series(H, w, 0, 4).removeO()
for j in range(4):
    c = sp.factor(sp.expand(ser.coeff(w,j)))
    print(j, sp.collect(sp.expand(c), th))
H3 = -(6*nu**3+239*nu**2+3187*nu+11016)-(26*nu**2+762*nu+5362)*th-(36*nu+594)*th**2-16*th**3
print('H3 match:', sp.expand(ser.coeff(w,3)-H3)==0)
