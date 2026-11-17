# R2 검산: 보조정리 4:gauss-contraction(나)의 잔차 계수, 4:hermite-nu의 H_j, U_i, V_i
import sympy as sp
from fractions import Fraction as Fr
io, x = sp.symbols('iota x', positive=True)
g = sp.symbols('gamma', positive=True)
# gamma 로 매개화: iota = (1-g^2)/4
def vhat_g(gam, xx):
    u = (1+gam)/2
    C1 = (1-u)/gam**2
    C2 = -(1-u)*(2+u)/gam**5
    C3 = 5*(1-u)*(6+gam-gam**2)/(2*gam**8)
    return u + xx*C1 + xx**2*C2 + xx**3*C3
iota_of_g = (1-g**2)/4
# vhat(iota - x): gamma' = sqrt(1-4(iota-x)) = sqrt(g^2+4x)
g2 = sp.sqrt(g**2 + 4*x)
R = (vhat_g(g, x) - 1)*vhat_g(g2, x) + iota_of_g
ser = sp.series(R, x, 0, 5).removeO()
for j in range(5):
    c = sp.simplify(ser.coeff(x, j))
    print("residual coeff x^%d:" % j, c if j < 4 else sp.factor(c))
# H_j 전개
w, nu, th = sp.symbols('w nu theta')
Nk = 3 + (nu+1-th)*w
nm = 1 + (2*nu+10+2*th)*w + ((nu+1)**2 + 2*(nu-3)*th + th**2)*w**2
gam = sp.sqrt(nm)/Nk
xx = w*(1-th*w)/Nk**2
H = (Nk*vhat_g(gam, xx) - 2 - nu*w)/w
Hs = sp.series(H, w, 0, 4).removeO()
claims = [4, -(26+4*nu)-8*th, 506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2,
          -(11016+3187*nu+239*nu**2+6*nu**3)-(5362+762*nu+26*nu**2)*th-(594+36*nu)*th**2-16*th**3]
for j in range(4):
    c = sp.expand(Hs.coeff(w, j))
    print("H_%d ok:" % j, sp.expand(c - claims[j]) == 0)
# U_i, V_i 수치(정확 유리수) 확인
def check(k, nuv):
    n = 2*k + nuv; y = Fr(k); N = n + y + 1
    He = [Fr(1), N]
    for j in range(2, n+1):
        He.append(N*He[j-1] - (j-1)*y*He[j-2])
    from math import comb, factorial
    def M(i):
        # [Y^n] (1-Y)^{i+1} B(Y) * n!   (공통 인자 e^{-k/2}/p_n 생략)
        s = Fr(0)
        for j in range(i+2):
            if n-j >= 0:
                s += (-1)**j*comb(i+1, j)*He[n-j]*Fr(factorial(n), factorial(n-j))
        return s
    th_ = He[n]/He[n-1] - n
    kk = Fr(k); v = Fr(nuv)
    U2 = 1 + (2*v+2)/kk + v*(v+1)/kk**2
    V2 = 4 + (4*v+2)/kk + v*(v+1)/kk**2
    U4 = 1 + (4*v+16)/kk + (6*v*v+30*v+18)/kk**2 + (4*v**3+17*v*v+15*v+2)/kk**3 + v*(v+1)**3/kk**4
    V4 = 4 + (12*v+38)/kk + (13*v*v+49*v+22)/kk**2 + (6*v**3+21*v*v+17*v+2)/kk**3 + v*(v+1)**3/kk**4
    r2 = M(2)/M(0); r4 = M(4)/M(0)
    return r2 == U2 - V2/th_, r4 == U4 - V4/th_, float(th_), float(2 - kk*r2), float(r4)
for (k, nuv) in [(7, -1), (7, 0), (12, 3), (30, 5), (200, 0), (200, -1), (150, 40)]:
    print(k, nuv, check(k, nuv))
