# R11 검산: D.critical-window-rig 「식」의 구간 검증 상수와 † 문단의 수치 (비엄밀 수치 대조, mpmath 30자리)
from mpmath import mp, mpf, zeta, pi, sin, cos, tan, exp, log, sqrt, arg, re, im, mpc, e, degrees
mp.dps = 30
def lm(m): return (2+mpf(1)/m)*zeta(2*m)/pi**(2*m)
print("l1,l2,l3 =", lm(1), lm(2), lm(3), " 1/36 =", mpf(1)/36, " 1/405 =", mpf(1)/405)
print("sum 2m l_m 4^(1-m) =", sum(2*m*lm(m)*mpf(4)**(1-m) for m in range(1, 80)))
print("sum_{m>=2} l_m 4^(1-m) =", sum(lm(m)*mpf(4)**(1-m) for m in range(2, 80)))
def loget(phi): return 1 + log(phi/sin(phi)) - phi/tan(phi)
print("log et(1/2) =", loget(mpf(1)/2))
rot = exp(-1j*pi/8)
mx_lg = 0; mn_re = 10; args = []; mxL = 0; mxq = 0
N = 4000
for i in range(1, N+1):
    rr = mpf(i)/N/2
    phi = rr*rot
    L = loget(phi)
    lg = sum(2*m*lm(m)*phi**(2*m-2) for m in range(1, 60))
    mx_lg = max(mx_lg, abs(lg)); mn_re = min(mn_re, re(L)/rr**2)
    q = exp(L)-1
    args.append(degrees(arg(q))); mxL = max(mxL, abs(L)/rr**2); mxq = max(mxq, abs(q)/rr**2)
print("max|lg| =", mx_lg, " min Re L/|phi|^2 =", mn_re, " arg qy in [", min(args), ",", max(args), "]")
print("max |L|/|phi|^2 =", mxL, " max |qy|/|phi|^2 =", mxq)
lo = 10; hi = 0; imlo = 10
for i in range(1, N+1):
    a = mpf(i)/N
    xi = exp(1j*a)*exp(1-exp(1j*a))
    v = abs(xi-1)/a**2; lo = min(lo, v); hi = max(hi, v); imlo = min(imlo, im(xi-1)/a**3)
print("|xi-1|/a^2 in [", lo, ",", hi, "]  min Im(xi-1)/a^3 =", imlo)
lo28 = min(abs(exp(1j*a)*exp(1-exp(1j*a))-1)/a**2 for a in [mpf(i)/N*mpf('0.28') for i in range(1, N+1)])
print("min |xi-1|/a^2 on (0,0.28] =", lo28)
print("1-cos(0.39) =", 1-cos(mpf('0.39')), " e^0.085-e^0.0761 =", exp(mpf('0.085'))-exp(mpf('0.0761')), " 0.1666*0.39^3 =", mpf('0.1666')*mpf('0.39')**3)
print("1-cos(0.475) =", 1-cos(mpf('0.475')), " e^0.1267-e^0.1108 =", exp(mpf('0.1267'))-exp(mpf('0.1108')), " 0.1666*0.475^3 =", mpf('0.1666')*mpf('0.475')**3)
k = mpf(10001)
print("0.009*k^(2/3) =", mpf('0.009')*k**(mpf(2)/3))
print("arc coefficient pi/8*1.03/1.8/8 =", pi/8*mpf('1.03')/mpf('1.8')/8, " log bound =", log(mpf('0.029'))+1.5*log(k)-mpf('0.085')*k)
print("pi/0.0178 =", pi/mpf('0.0178'), " log(177 k^-1/6 e^-0.1267k) =", log(177)-log(k)/6-mpf('0.1267')*k, " code:", log(pi/mpf('0.0048'))-log(k)/6-mpf('0.1267')*k)
print("min (1-cos a)/a^2 on (0,1] =", (1-cos(mpf(1))), " (at a=1)")
print("-log(1-v)-v-v^2/2 at v=1/2 =", -log(mpf(1)/2)-mpf(1)/2-mpf(1)/8)
