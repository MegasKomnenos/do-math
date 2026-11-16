# K5: 6.5절 상수 재계산 (c_*, Gamma_*, 50.62/sqrt(3130), ex_max, kappa_d)
from mpmath import mp, mpf, sqrt, exp, log, findroot
mp.dps = 30
tp = mpf('0.55'); kap = mpf('2.4978')
# stationary: tp x^2 - (kap tp + 2) x + kap = 0
a, b, c = tp, -(kap*tp+2), kap
r = (-b + sqrt(b*b-4*a*c))/(2*a)
print("large root", r, "c(tp,kap)=", (r*r-kap*r)*exp(-tp*r))
x = mpf(3132)/3130
G = x/((1+x)**(1-tp)-1); print("Gamma_tp at x=3132/3130:", G)
print("50.62/sqrt(3130)=", mpf('50.62')/sqrt(3130))
t = mpf(3130)
print("ex_max", (t+1)/(2*t+1), "20/(9t)", 20/(9*t), "2-exmax-20/9t", 2-(t+1)/(2*t+1)-20/(9*t))
print("kappa_d lower", mpf('1.498')+2*t/(2*t+1))
print("3t/(2t+1)", 3*t/(2*t+1), "10/(3t)", 10/(3*t))
