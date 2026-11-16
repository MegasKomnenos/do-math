# I6: 정리 self-consistent-S (다) 표와 따름정리 cor-S-prime 값의 재계산 (mpmath 60자리)
from mpmath import mp, mpf, e as E, exp, log, ceil, factorial, power
mp.dps = 60
def a0(m):  # 자유 계수 (m+1)^{m-1}/m!
    return power(mpf(m+1), m-1)/factorial(m)
def free_ratio(m):  # a0(m+1)/a0(m) = (1+1/(m+1))^m
    return power(1+mpf(1)/(m+1), m)
def xk(k):
    return power(mpf(k)/(k+1), k-1)
layers = [(mpf(267)/100, 25, 501, mpf(13)/100, (mpf('1.4708'), mpf('0.098505'))),
          (mpf(27)/10, 70, 1855, mpf(2)/25, (mpf('2.5335'), mpf('0.060259'))),
          (mpf(271)/100, 100, 6098, mpf(11)/200, (mpf('2.7354'), mpf('0.0422')))]
for vs, J, k0, y, (A0t, B0t) in layers:
    m = 0
    while free_ratio(m+1) < vs: m += 1
    jstar = m
    kR = max(2*jstar+2, int(ceil(power(vs, jstar+2)/a0(jstar+1))))
    xbar = [a0(kp)*power(vs, -(kp+1)) for kp in range(J)]
    qlow = []
    for kp in range(J):
        s = sum(a0(j)*power(vs, -(j+1)) for j in range(kp))
        qlow.append(max(mpf(0), 1-s))
    Elow = sum(a0(J+i)/a0(J)*exp(-i) for i in range(1, k0-jstar+1))
    r = vs/E
    Einf = r*(1-power(r, k0))/(1-r)
    R = max(1/(1+Elow), 1/(1+Einf))
    Xi = sum(max(mpf(0), xbar[kp]-R*qlow[kp]) for kp in range(J))
    Xik0 = sum(max(mpf(0), a0(kp)*xk(k0)*power(vs, -kp)-R*qlow[kp]) for kp in range(J))
    A0 = xk(k0)+Xik0/(vs*(1-Xi))
    B0 = R*(1+Xik0/(1-Xi))
    print(f"vs={vs} J={J} k0={k0}: j*={jstar} kR={kR} R={mp.nstr(R,8)} Xi={mp.nstr(Xi,8)} Xi(k0)={mp.nstr(Xik0,8)} A0={mp.nstr(A0,8)} B0={mp.nstr(B0,8)}  xk0={mp.nstr(xk(k0),6)}")
    xi = mpf(1)/k0
    nv = (3*xi+xi**2)/2+(1+xi)**2*B0t/2
    g_exact = (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    g_round = (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0t*xi+B0t*y)
    print(f"   yk^2-2k-1 at k0 = {mp.nstr(y*k0**2-2*k0-1,8)}; n_v/k^2={mp.nstr(nv,6)}; g/k^4 exact={mp.nstr(g_exact,6)} rounded={mp.nstr(g_round,6)}")
# 열 인증 (가)의 수치
print("40/41*(10/17)^2.1 =", mp.nstr(mpf(40)/41*power(mpf(10)/17, mpf(21)/10), 8))
print("10^21*400^10 =", 10**21*400**10, " 17^21*123^10 =", 17**21*123**10, 10**21*400**10 > 17**21*123**10)
print("1-2.1*(10/17)^3 =", mp.nstr(1-mpf(21)/10*power(mpf(10)/17,3),6))
# t_k, n#_k, n~_k 몇 개
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in [2,3,5,10,41,120,501,2000]:
    t=tk(k); print(f"k={k}: t_k={t} n#={k+(k+1)*t} n~={k*(2*t+1)}")
