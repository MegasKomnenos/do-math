# 검토전체25 R4: 여유가 좁은 상수 셋을 50자리 십진으로 다시 셈
from decimal import Decimal as D, getcontext
getcontext().prec = 60
def pi_():
    # Machin
    def atan_inv(x):
        x = D(x); s = D(0); t = 1/x; x2 = x*x; k = 0
        while abs(t) > D(10)**-58:
            s += t/(2*k+1) if k % 2 == 0 else -t/(2*k+1)
            t /= x2; k += 1
        return s
    return 4*(4*atan_inv(5)-atan_inv(239))
PI = pi_()
sp = PI.sqrt()
hv = D(5000).sqrt()**-1*(2/sp*(1+D(1)/5000)+1/sp)
print("hv_5000 =", hv, " <= 0.02394:", hv <= D('0.02394'))
n = D(50001)
w23 = ((2*n/3).ln()*D(2)/3).exp()
val = (2*PI).sqrt()**-1*(((n+1)/((n/2)*(n/3-1-w23))).ln()*D('1.5')).exp()*(1/(12*(n+1))).exp()
print("pi_n(t0-1) bound =", val, " <= 5.775e-7:", val <= D('5.775e-7'))
print("denominator =", D('0.4')*n/3-6*w23+1)
wb = w23+2
print("(n/3+1)/(n/3-wb) =", (n/3+1)/(n/3-wb))
e0 = D('1.5')*wb/(n/2+wb-1)*(n/3+2*wb)/(n/3+1-wb)
print("eps0 =", e0)
pre = (2*PI).sqrt()**-1*D('1.0053')*D('1.0665')*D('1.0630')*(D('0.0717')+D(1)/300006).exp()
print("prefactor =", pre)
y = D(33334); y23 = (y.ln()*2/3).exp()
print("10 y^(2/3) - 1 =", 10*y23-1)
win = (2*PI).sqrt()**-1*D(2)/3*D('1.0044')*D('1.5')*D('1.1116')*D('1.0472')*(D('0.1671')+D(1)/400008).exp()
print("win right =", win)
print("hv coef 2064 =", 2/sp*(1+D(1)/2064)+1/sp)
u = (y.ln()/3).exp()
print("eps_hov right =", D('1.6932')*(u/10+1)/(2*u*u-D('7.5')).sqrt())
