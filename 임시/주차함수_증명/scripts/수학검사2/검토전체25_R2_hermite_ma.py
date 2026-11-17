# R2 검산: 보조정리 4:hermite-nu (마)의 일반 y 식, 한가운데 두 쌍의 원판 상계
import sympy as sp, mpmath as mp
n, y, vt = sp.symbols('n y vartheta')
N = n+y+1
He = {0: n+vt, 1: sp.Integer(1)}
for i in range(2, 4):
    He[i] = sp.simplify((N*He[i-1] - He[i-2])/((n-i+1)*y))
def M(i):
    s = 0
    for j in range(i+2):
        f = sp.Integer(1)/n if j == 0 else sp.prod([(n-t) for t in range(1, j)])
        s += (-1)**j*sp.binomial(i+1, j)*He[j]*f
    return sp.simplify(s)
print(sp.simplify(M(2)/M(0) - (1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*vt))))
# 원판 |w|<=1/100 상계
lo = mp.sqrt(1-0.1207)/3.01; hi = mp.sqrt(1.1207)/2.99
print('gamma range', lo, hi)
u = (1+hi)/2; xb = 0.01*1.01/2.99**2
C1 = 0.678/lo**2; C2 = 0.678*2.678/lo**5; C3 = 5*0.678*(6+hi+hi**2)/(2*lo**8)
print('u', u, 'x', xb, 'C1', C1, 'C2', C2, 'C3', C3)
print('uhat', 0.678+0.00113*6.99+0.00113**2*620+0.00113**3*1.24e5, 'H', (3.01*0.7+2.01)*100)
k = mp.mpf(10000)
print('contr central', 2e7*(3*k+1)*k**4/(3*k-1)**8*k**3, 'nu<=600', 2e7*(3*k+601)*k**4/(3*k-1)**8*k**3, '3^-7', 2e7/3**7)
