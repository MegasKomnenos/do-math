# R2 검산(수치): (4.9) 를 작은 k 와 원뿔 |phi|<=2(-Re phi) 의 무작위 점에서 대조
import mpmath as mp, random
mp.mp.dps = 30
random.seed(7)
c = 1/mp.sqrt(2*mp.pi)
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def Bsum(k, phi): return mp.fsum(Bor(j)*mp.e**(-phi*j/k) for j in range(1, k+1))
def Bld(phi): return 2 + mp.quad(lambda w: w**(-1.5)*(1 - mp.e**(-phi*w)), [0, 0.001, 0.01, 0.1, 0.5, 1])
worst = 0
for k in (1, 2, 3, 5, 8, 20, 50, 200):
    for t in range(40):
        a = 10**random.uniform(-3, 1.3)            # -Re phi
        b = random.uniform(-1, 1)*a*mp.sqrt(3)     # |Im| <= sqrt3 a  <=> |phi|<=2a
        phi = mp.mpc(-a, b)
        lhs = abs(Bsum(k, phi) - 1 + c*k**-0.5*Bld(phi) - mp.mpf(2)/3*phi/k)
        rhs = c*k**-1.5*mp.e**(a)*(mp.mpf(5)/9 + mp.mpf(2)/3*abs(phi) + mp.mpf(13)/12*abs(phi)**2)
        r = lhs/rhs
        if r > worst: worst = r; wk = (k, phi)
print("max lhs/rhs:", mp.nstr(worst, 6), wk)
