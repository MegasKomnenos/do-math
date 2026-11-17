# R2 검산(수치): 보조정리 4:gauss-contraction (나)(다)
import mpmath as mp
mp.mp.dps = 80
def run(k, nu, theta):
    n = 2*k + nu; y = mp.mpf(k) - theta; N = n + y + 1; x = y/N**2
    def vhat(io):
        g = mp.sqrt(1 - 4*io); u = (1+g)/2
        C1 = (1-u)/g**2; C2 = -(1-u)*(2+u)/g**5; C3 = 5*(1-u)*(6+g-g*g)/(2*g**8)
        return u + x*C1 + x*x*C2 + x**3*C3
    u = mp.mpf(1); worst = mp.mpf(0); logs = mp.mpf(0)
    for j in range(2, n+1):
        u = 1 - (j-1)*x/u
        logs += mp.log(u)
        e = abs(u - vhat((j-1)*x))
        if e > worst: worst = e
    q = n*x
    gq = mp.sqrt(1-4*q); uq = (1+gq)/2
    U = N*uq; W = N*gq
    lhs = n*mp.log(N) + logs
    rhs = mp.log(mp.sqrt(U/W)) + n*mp.log(U) + (N-U)**2/(2*y) - mp.mpf(11)/2*x - 350*n*x*x
    return mp.nstr(worst/x**4, 6), mp.nstr(lhs - rhs, 8), mp.nstr(q, 8), mp.nstr(x, 6)
for args in [(10000, -1, 1), (10000, 0, 0), (10000, 600, 0.5), (20000, 100, 0), (100000, 228, 1)]:
    print(args, run(*args))
