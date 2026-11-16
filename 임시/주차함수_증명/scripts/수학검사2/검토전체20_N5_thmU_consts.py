# 정리 theorem-U 준비 상수: m(0.55, 2.4978), Gamma_tp at x=3132/3130, kappa lower bound, ex_max
from decimal import Decimal as D, getcontext
getcontext().prec = 40
import math
tp = 0.55; kap = 2.4978
# stationary eq tp chi^2 - (kap tp + 2) chi + kap = 0, larger root
b = kap*tp + 2
chi = (b + math.sqrt(b*b - 4*tp*kap))/(2*tp)
m = (chi*chi - kap*chi)*math.exp(-tp*chi)
print("chi*", chi, "m", m)
# check sup numerically on grid
best = max(((c*c-kap*c)*math.exp(-tp*c), c) for c in [kap + i*1e-4 for i in range(0, 200000)])
print("grid sup", best)
T = 3130.0
x = (T+2)/T
Gam = x/((1+x)**(1-tp) - 1)
print("Gamma", Gam)
print("kappa_d lower", 1.498 + 2*T/(2*T+1))
print("ex_max", (T+1)/(2*T+1), "2-ex-20/(9T)", 2-(T+1)/(2*T+1)-20/(9*T))
print("50.62/sqrt(3130)", 50.62/math.sqrt(3130))
