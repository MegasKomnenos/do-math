# R11 검산: |w|=1/100 위 max|H(w)| (D.central-gap-rational-audit (ㄷ)의 Cauchy 상수 1000)
import cmath, math
def H(w, nu, th):
    Nt = 3 + (nu+1-th)*w
    xn = (2+(nu-1)*w)*(1-th*w)/Nt**2
    x = (1-th*w)*w/Nt**2
    g = cmath.sqrt(1-4*xn)
    u = (1+g)/2
    C1 = (1-u)/g**2; C2 = -(1-u)*(2+u)/g**5; C3 = 5*(1-u)*(6+g-g*g)/(2*g**8)
    uh = u + x*C1 + x*x*C2 + x**3*C3
    return (Nt*uh - 2 - nu*w)/w, abs(g), abs(uh)
mx = 0; gmin = 9; gmax = 0; umax = 0
for nu in (-1, 0):
    for it in range(0, 21):
        th = it/20
        for j in range(2000):
            w = 0.01*cmath.exp(2j*math.pi*j/2000)
            h, ag, au = H(w, nu, th)
            mx = max(mx, abs(h)); gmin = min(gmin, ag); gmax = max(gmax, ag); umax = max(umax, au)
print("max|H| on |w|=1/100:", mx, " |gamma| range:", gmin, gmax, " max|uhat|:", umax)
