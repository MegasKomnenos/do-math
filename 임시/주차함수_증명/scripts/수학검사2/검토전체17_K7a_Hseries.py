# K7a: 보조정리 hermite-nu (나)의 멱급수 계수 H_0..H_3 를 sympy로 독립 전개 (w=1/k)
import sympy as sp
w,nu,th=sp.symbols('w nu theta')
Nk=3+(nu+1-th)*w                      # N/k
x=w*(1-th*w)/Nk**2                    # frak x = y/N^2 (y=k-theta), as function of w=1/k
xn=(2+(nu-1)*w)*(1-th*w)/Nk**2        # frak x_n
g=sp.sqrt(1-4*xn)                     # gamma
ups=(1+g)/2
C1=(1-ups)/g**2
C2=-(1-ups)*(2+ups)/g**5
C3=sp.Rational(5,2)*(1-ups)*(6+g-g**2)/g**8
uhat=ups+x*C1+x**2*C2+x**3*C3
H=(Nk*uhat-2-nu*w)/w
ser=sp.series(H,w,0,4).removeO()
coeffs=[sp.simplify(sp.expand(ser.coeff(w,j))) for j in range(4)]
for j,c in enumerate(coeffs): print("H_%d ="%j, sp.factor(c) if j<3 else sp.expand(c))
H3=sp.Poly(sp.expand(coeffs[3]),nu,th)
# 부호 검사: nu in [1,600], theta in [0,1] 격자 + 극값
import itertools
mx=max(float(coeffs[3].subs({nu:n,th:t})) for n in range(1,601) for t in [0,0.25,0.5,0.75,1])
print("max H_3 on grid:", mx)
