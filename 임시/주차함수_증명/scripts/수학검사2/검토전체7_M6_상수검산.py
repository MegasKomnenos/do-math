# 7A 검토(M6): 정리 self-consistent-S (다) 표, 따름정리 cor-S-prime 세 값, 보조정리 column-lemma (가) 상수,
# 반감 경계 지표 t_k, 보조정리 polar-N·명제 polar-W 수치, 명제 riccati 반례의 재계산.
# 큰 첨자의 자유 계수 비는 Decimal(60자리)로, 작은 첨자(kappa<J)는 정확 유리수로 계산한다.
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
import math

getcontext().prec = 60
D = Decimal
E = D(1).exp()

def a_circ(m):
    return Fr((m + 1) ** (m - 1), math.factorial(m)) if m >= 1 else Fr(1)

def free_ratio_dec(m):
    # e^{g(m+1)} = a°_{m+1}/a°_m = (1+1/(m+1))^m
    return (1 + D(1) / D(m + 1)) ** m

def layer(L, J, k0):
    Ld = D(L.numerator) / D(L.denominator)
    m = 0
    while free_ratio_dec(m + 1) < Ld:
        m += 1
    jstar = m
    kR = max(2 * jstar + 2, math.ceil(L ** (jstar + 2) / a_circ(jstar + 1)))
    # E_lower = sum_{i=1}^{k0-j*} (a°_{J+i}/a°_J) e^{-i}
    E_low = D(0); prod = D(1)
    for i in range(1, k0 - jstar + 1):
        prod *= free_ratio_dec(J + i - 1) / E
        E_low += prod
    r = Ld / E
    E_inf = r * (1 - r ** k0) / (1 - r)
    R_J = max(1 / (1 + E_low), 1 / (1 + E_inf))
    xk0 = Fr(k0, k0 + 1) ** (k0 - 1)
    xk0d = D(xk0.numerator) / D(xk0.denominator)
    Xi = D(0); Xik = D(0)
    for kap in range(J):
        xbar = a_circ(kap) * L ** (-(kap + 1))
        xbar_d = D(xbar.numerator) / D(xbar.denominator)
        q = max(Fr(0), Fr(1) - sum(a_circ(j) * L ** (-(j + 1)) for j in range(kap)))
        qd = D(q.numerator) / D(q.denominator)
        t = xbar_d - R_J * qd
        if t > 0: Xi += t
        xb_k = D((a_circ(kap) * L ** (-kap)).numerator) / D((a_circ(kap) * L ** (-kap)).denominator) * xk0d
        t2 = xb_k - R_J * qd
        if t2 > 0: Xik += t2
    A0 = xk0d + Xik / (Ld * (1 - Xi))
    B0 = R_J * (1 + Xik / (1 - Xi))
    return jstar, kR, R_J, Xi, Xik, A0, B0

layers = [(Fr(267, 100), 25, 501, Fr(13, 100)), (Fr(27, 10), 70, 1855, Fr(2, 25)), (Fr(271, 100), 100, 6098, Fr(11, 200))]
for L, J, k0, y in layers:
    jstar, kR, R_J, Xi, Xik, A0, B0 = layer(L, J, k0)
    print(f"L={L} J={J} k0={k0}: j*={jstar} kR={kR} R_J={R_J:.6f} Xi={Xi:.6f} Xi(k0)={Xik:.6f} A0={A0:.5f} B0={B0:.9f}")
    xi = D(1) / D(k0)
    yd = D(y.numerator) / D(y.denominator)
    g = (yd - xi) * (yd - 2 * xi - xi * xi) - (1 + xi) ** 2 * (A0 * xi + B0 * yd)
    vert = (3 * xi + xi * xi) / 2 + (1 + xi) ** 2 * B0 / 2
    print(f"   cor-S-prime value at k0: {g:.4e}; vertex/k^2={vert:.5f} <= y={yd}; y*k0^2-2k0-1={yd*k0*k0-2*k0-1:.1f}")

k = 41
o_k = -2 * math.log(1 - 1 / k) / math.log(1 + 1 / k)
print("o_41 =", o_k, "<= 2.1:", o_k <= 2.1, "; 2(k+1)/(k-1)=", 2 * 42 / 40)
print("phi'(1.7) lower:", 1 - 2.1 * (10 / 17) ** 3)
print("(40/41)(10/17)^2.1 =", (40 / 41) * (10 / 17) ** 2.1, "> 0.3")
print("10^21*400^10 > 17^21*123^10:", 10 ** 21 * 400 ** 10 > 17 ** 21 * 123 ** 10, "; 17^21=%.4e 123^10=%.4e" % (17 ** 21, 123 ** 10))

def t_k(k):
    j = 0
    while not ((k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) >= 2 * k ** (2 * j + 1)):
        j += 1
    return j
for k in (2, 3, 10, 41, 120, 500, 501, 2001):
    t = t_k(k); print(f"k={k}: t_k={t}, n#_k={k+(k+1)*t}, n#/k^2={(k+(k+1)*t)/k/k:.3f}")

k = 2001
print("2/sqrt(2001)=", 2 / math.sqrt(k), "; e^{-1+2/2002}=", math.exp(-1 + 2 / 2002), "; 2k^1.5+1=", 2 * k ** 1.5 + 1, "; 0.3476k^2=", 0.3476 * k * k)
print("0.955*0.991*0.3678=", 0.955 * 0.991 * 0.3678, "; e^{-0.0448}=", math.exp(-0.0448), "; 0.75/sqrt(2001)=", 0.75 / math.sqrt(k))
k = 10 ** 7
print("8*(1+0.91/sqrt k)^3 =", 8 * (1 + 0.91 / math.sqrt(k)) ** 3, "; (4.004+3+1.34)/sqrt(k)=", 8.344 / math.sqrt(k))
# riccati 반례 (k,z,n)=(3,1,2): 좌변 = sum_sigma prod*H_1 = 2*1+1*2 = 4 ; 우변 x^2 계수*2! = 2*(1+3/2) = 5
print("riccati counterexample: LHS =", 2 * 1 + 1 * 2, " RHS*2! =", 2 * (1 + Fr(3, 2)))
