# 9.3절 정리 old-7-16 (해석적 행 정리) 증명의 수치를 다시 센다.
from mpmath import mp, mpf, sqrt, exp, pi, quad, ceil, log
mp.dps = 20
k = mpf(6668)
def J1(k):
    c = 3/sqrt(k); t0 = 1/k + c**(mpf(2)/3)
    f = lambda t: mpf(2.5)*(1+t+2/k)**(-3.5)*max(0, 1-c*(t-1/k)**(-1.5))
    return quad(f, [t0, 1])
def J2(k):
    c = 3*(k-1)*k**(-1.5); t0 = 1/k + c**(mpf(2)/3)
    f = lambda t: mpf(2.5)*(1+t+1/k)**(-3.5)*max(0, 1-c*(t-1/k)**(-1.5))
    return quad(f, [t0, (k-1)/k])
J3 = (k/(2*k+1))**2.5*(1-3/sqrt(k)); J4 = (k/(2*k+1))**2.5*(1-3/sqrt(k-1))
L = J1(k)+J2(k)+J3+J4
print("J1,J2,J3,J4,L*", J1(k), J2(k), J3, J4, L)
print("limit per level", mpf(2.5)*quad(lambda t:(1+t)**(-3.5),[0,1]) + 2**(-2.5))
# (2)
print("(2pi)^-1/2 e^-1/24 e^-1/(12*3334)", exp(-mpf(1)/24-mpf(1)/(12*3334))/sqrt(2*pi), "0.3826*2", 0.3826*2)
js = ceil((3*k)**(mpf(2)/3)); print("j*", js, "(3k)^(2/3)", (3*k)**(mpf(2)/3))
print("first interval LHS", 4.85*(sqrt(k)*((3*k)**(mpf(2)/3)+2)**(-0.5)-sqrt(2)), "0.734*6.62", 0.734*6.62)
print("second interval", 6/0.98*mpf(0.95)**(-1.5))
print("12/0.734", 12/0.734)
print("iota=0.05k endpoint", 16.35/0.05*mpf(0.95)**(-1.5)*(1+1/k)**1.5, "-> 353.3/k vs 6.62/sqrt k: k>=", (353.3/6.62)**2)
print("iota=k-j*-1 endpoint", 16.35*((k+1)/(js+1))**1.5/(k-js-1)*sqrt(k), " formula 5.45(1+1/k)^1.5 k/(k-j*-1)", 5.45*(1+1/k)**1.5*k/(k-js-1))
# (3)
d = 6.62/sqrt(k)
print("dbar", d, "band req", (1+d/2)/(1-d/2))
cover = 103*exp(1/(12*(2*k-1)))/sqrt(2*pi); print("cover coeff", cover)
pc = exp(1/(12*(mpf(1.48)*k+1)))/sqrt(2*pi)*(2/0.48)**1.5; print("per-term const", pc)
print("0.26*3.394", 0.26*3.394, "tail", 1.697/sqrt(k)+0.676, "1/1.48", 1/1.48)
bulk = 1+1.676*d/(2-d)+0.676*(0.8825/sqrt(k)+0.72/k+41.2*(2/(0.48*k-102))**1.5)
print("bulk req", bulk)
# HC-style check for 9.3 (2): verify x_k/k < 6.62/sqrt k trivially
# Also 9.2: pi_2 bound
print("sqrt(8/(pi*6669))", sqrt(8/(pi*6669)))
