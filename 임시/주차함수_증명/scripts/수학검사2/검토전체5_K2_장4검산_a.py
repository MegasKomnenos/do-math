# K2 장4 검산 (a): 기호 계산 — (4.9), M4/M0, P의 계수, 잔차 R의 계수
import sympy as sp, sys
n,y,th = sp.symbols('n y vartheta', positive=True)
N = n+y+1; a = n+th
H = {1:sp.Integer(1), 0:a}
H[2]=(N*H[1]-H[0])/((n-1)*y); H[3]=(N*H[2]-H[1])/((n-2)*y); H[4]=(N*H[3]-H[2])/((n-3)*y); H[5]=(N*H[4]-H[3])/((n-4)*y)
def num(r): return sum(sp.binomial(r+1,j)*(-1)**j*sp.ff(n,j)*H[j] for j in range(r+2))
r2 = sp.cancel(num(2)/num(0)); claim2 = 1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*th)
print("(4.9) ok:", sp.cancel(r2-claim2)==0, flush=True)
k = sp.symbols('k', positive=True)
for nu,claim,center in [(0, 1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/th, 4-26/k+506/k**2),
                 (-1, 1+12/k-6/k**2-(4+26/k-14/k**2)/th, 4-22/k+414/k**2)]:
    r4 = sp.cancel((num(4)/num(0)).subs({n:2*k+nu, y:k}))
    print(f"M4/M0 nu={nu} ok:", sp.cancel(r4-claim)==0, flush=True)
    print(f"  center expansion nu={nu}:", sp.series(claim.subs(th,center), k, sp.oo, 4), flush=True)
nu_s, theta = sp.symbols('nu theta')
Q = 506+97*nu_s+5*nu_s**2+(168+16*nu_s)*theta+12*theta**2
vth = 4-(26+4*nu_s+8*theta)/k+Q/k**2
P = sp.expand(vth*((2*k+nu_s-(k-theta))**2+2*k+nu_s)-(2*k+nu_s)*(2*k+nu_s+1))
print("P k^2:", sp.simplify(P.coeff(k,2)), "| k^1:", sp.simplify(P.coeff(k,1)), "| k^0:", sp.expand(P.coeff(k,0)), flush=True)
E1 = sp.expand(k*P+5*(k-theta)**2*vth); print("kP+5y^2vth: k^2", sp.simplify(E1.coeff(k,2)), "k^1", sp.expand(E1.coeff(k,1)), flush=True)
E2 = sp.expand(100*k*P+499*(k-theta)**2*vth); print("100kP+499y^2vth k^2:", sp.simplify(E2.coeff(k,2)), flush=True)
# 잔차 R: rational iota values, series in x
x = sp.symbols('x')
def ups(g): return (1+g)/2
def Cs(g):
    u=ups(g); return (1-u)/g**2, -(1-u)*(2+u)/g**5, sp.Rational(5,2)*(1-u)*(6+g-g**2)/g**8
def uhat(g):
    C1,C2,C3=Cs(g); return ups(g)+x*C1+x**2*C2+x**3*C3
for io in [sp.Rational(2,9), sp.Rational(1,5), sp.Rational(1,10), sp.Rational(1,50)]:
    R = (uhat(sp.sqrt(1-4*io))-1)*uhat(sp.sqrt(1-4*(io-x)))+io
    Rs = sp.series(R, x, 0, 5).removeO()
    cs = [sp.nsimplify(sp.simplify(Rs.coeff(x,j))) for j in range(5)]
    print("iota=",io," coeffs x^0..x^4:", cs, " x^4 float:", float(cs[4]), flush=True)
g=sp.symbols('gamma'); print("C at gamma=1/3:", [c.subs(g,sp.Rational(1,3)) for c in Cs(g)])
