# R2 check: lemma 4:hermite-nu (H_j coefficients, U_i, V_i, (ma) formula, coefficient 20)
import sympy as sp
u,nu,th=sp.symbols('u nu theta')
# H = k((N/k) vhat(x_n) - 2 - nu/k), u=1/k
Nk=3+(nu+1-th)*u
nm=1+(2*nu+10+2*th)*u+((nu+1)**2+2*(nu-3)*th+th**2)*u**2
g=sp.sqrt(nm)/Nk
v0=(1+g)/2
C1=(1-v0)/g**2
C2=-(1-v0)*(2+v0)/g**5
C3=5*(1-v0)*(6+g-g**2)/(2*g**8)
x=u*(1-th*u)/Nk**2
vhat=v0+x*C1+x**2*C2+x**3*C3
H=(Nk*vhat-2-nu*u)/u
ser=sp.series(H,u,0,4).removeO()
for j in range(4):
    c=sp.expand(ser.coeff(u,j))
    print('H',j,sp.collect(c,th))
# residual R(iota) coefficient check x^0..x^3 symbolic
io,xx=sp.symbols('iota x')
gam=sp.sqrt(1-4*io)
w0=(1+gam)/2
def vh(i):
    gg=sp.sqrt(1-4*i); ww=(1+gg)/2
    return ww+xx*(1-ww)/gg**2-xx**2*(1-ww)*(2+ww)/gg**5+xx**3*5*(1-ww)*(6+gg-gg**2)/(2*gg**8)
R=(vh(io)-1)*vh(io-xx)+io
Rs=sp.series(R,xx,0,4).removeO()
print('R coeffs',[sp.simplify(Rs.coeff(xx,j)) for j in range(4)])
