# hermite-nu (나): H = k((N/k) vhat(x_n) - 2 - nu/k) 의 1/k 전개 계수 H_0,H_1,H_2 확인
import sympy as sp
w,nu,th=sp.symbols('w nu theta')  # w = 1/k
Nk=3+(nu+1-th)*w
x=w*(1-th*w)/Nk**2            # x = y/N^2 = (k-theta)/N^2, over k^2 -> w*(1-th w)/(N/k)^2
xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
g=sp.sqrt(1-4*xn)
vo=(1+g)/2
C1=(1-vo)/g**2
C2=-(1-vo)*(2+vo)/g**5
C3=sp.Rational(5,2)*(1-vo)*(6+g-g**2)/g**8
vhat=vo+x*C1+x**2*C2+x**3*C3
H=(Nk*vhat-2-nu*w)/w
ser=sp.series(H,w,0,3).removeO()
for j in range(3):
    print('H_%d ='%j, sp.factor(sp.expand(ser.coeff(w,j))))
