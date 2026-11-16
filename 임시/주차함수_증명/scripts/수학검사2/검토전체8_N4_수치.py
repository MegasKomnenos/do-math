# 검토전체8 N4: 장5B 5.5절 수치 검산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, e, floor, ceil, erfc, quad, inf
mp.dps = 50
R = lambda x: mp.nstr(x, 12)

print("== 5.5.2: t_0<=n 부등식, 10/2^(2/3) =", R(10/mpf(2)**(mpf(2)/3)))
n = 50001
print("   6n^(2/3)+2 vs 10((n+1)/2)^(2/3):", R(6*mpf(n)**(mpf(2)/3)+2), R(10*((mpf(n)+1)/2)**(mpf(2)/3)))
y = 25000
c = ceil(mpf('0.75')*(mpf('1.1')*y)**(mpf(2)/3))
print("   y=25000: ceil(0.75(1.1y)^(2/3)) =", c, " 0.1y =", mpf(y)/10, " t-1<=1.1y:", y + c <= mpf('1.1')*y)

print("== 5.5.4: 손실률 (m+d+2)/((w+2)(m+1)) <= z_m(d) 전수 m<=400")
bad = 0
for m in range(2, 401):
    for d in range(1, m//2+1):
        w = m-d
        loss = mpf(m+d+2)/((w+2)*(m+1))
        z = exp(mpf(d-1)/w)/(w+1) + mpf(3*d)/(2*(w+1)*(m+1))
        if loss > z: bad += 1
print("   위반 수:", bad)

print("== 5.5.5 (5-30) 상수")
n = mpf(50001)
v1 = (2*pi)**(-mpf(1)/2)*sqrt(2)*mpf(3)**mpf('1.5')*(1+1/n)**mpf('1.5')*n**(-mpf(1)/2)*exp(1/(12*(n+1)))
print("   y<=2n/3 경우 top_pi 상계 =", R(v1), "<=0.0133")
v2 = (mpf('1.5')/10)**mpf('1.5'); print("   (1.5/10)^(3/2) =", R(v2), "<=0.0581")
v3 = (2*pi)**(-mpf(1)/2)*mpf('0.0581')*(1+1/n)**mpf('1.5')*exp(1/(12*(n+1))); print("   top_pi 상계 =", R(v3), "<=0.0232")
v4 = exp(-2)*((n+1)/(n-1))**mpf('1.5')*exp(1/(12*(n-1))); print("   pi_n(n-1) 상계 =", R(v4), "<0.1354")
print("   e^-1-0.1354-0.0232 =", R(exp(-1)-mpf('0.1354')-mpf('0.0232')))

print("== borel-gf (다) 판별식, 5.5.6 상수")
h0 = mpf('0.0342'); print("   h0^3 =", R(h0**3), ">= 1/25000 =", R(mpf(1)/25000), h0**3 >= mpf(1)/25000)
um = sqrt(6*h0); c1 = 1/(2*(1-um)); print("   upsilon_max =", R(um), " c1 =", R(c1))
c2 = 1/sqrt(2) - um/3; print("   c2 =", R(c2), ">=0.556:", c2 >= mpf('0.556'))
f12 = mpf('0.556')*mpf(12)**mpf('1.5') - 12 - log(sqrt(2)*(1+6*h0)*12/mpf('0.556'))
print("   12^1.5 =", R(mpf(12)**mpf('1.5')), " sqrt2(1+6h0)12/c2 =", R(sqrt(2)*(1+6*h0)*12/mpf('0.556')), " f(12) >=", R(f12))
print("   6*Y^(2/3)<=Y/4 at Y=13824:", 6*mpf(13824)**(mpf(2)/3), mpf(13824)/4)

print("== bt-tail (나) ti 닫힌 꼴 수치 검증")
for (vs, b, W0) in [(mpf('0.3'), mpf(2), mpf(5)), (mpf('0.01'), mpf('0.5'), mpf(1)), (mpf(0), mpf(3), mpf(4))]:
    num = quad(lambda u: u**(-mpf(3)/2)*exp(-vs*u-b/u), [W0, inf])
    cf = mpf(1)/2*sqrt(pi/b)*(exp(-2*sqrt(vs*b))*erfc(sqrt(vs*W0)-sqrt(b/W0)) - exp(2*sqrt(vs*b))*erfc(sqrt(vs*W0)+sqrt(b/W0)))
    print("   ti num/closed:", R(num), R(cf))

print("== stop-lower 상수")
print("   1.5*0.95^-2.5 =", R(mpf('1.5')*mpf('0.95')**(-mpf('2.5'))), "<=1.706")
print("   (0.8^-1.5-1)/0.2 =", R((mpf('0.8')**(-mpf('1.5'))-1)/mpf('0.2')), "<=1.988")
U = mpf(25001); print("   e^(1/(12U)) <= 1+1/(11U):", exp(1/(12*U)) <= 1+1/(11*U))
print("   (1+1.706*0.05)/11 =", R((1+mpf('1.706')*mpf('0.05'))/11), " (1+1.988*0.2)/11 =", R((1+mpf('1.988')*mpf('0.2'))/11))
print("   4/sqrt(2pi) =", R(4/sqrt(2*pi)))

print("== hover-tail: z^3-16z+24>=0 for z>=2 (check z=2..10):", [int(z**3-16*z+24) for z in range(2,11)])
print("   (2/sqrt(pi))*2*sqrt(2) =", R(2/sqrt(pi)*2*sqrt(2)))

print("== band-inequality 조건 (n=50001)")
n = mpf(50001)
print("   0.4n/3 =", R(mpf('0.4')*n/3), " 6(2n/3)^(2/3)+1 =", R(6*(2*n/3)**(mpf(2)/3)+1))
print("   0.75(1.1*2n/3)^(2/3)+1 =", R(mpf('0.75')*(mpf('1.1')*2*n/3)**(mpf(2)/3)+1), " 0.7n/3 =", R(mpf('0.7')*n/3))
for lb in [mpf(1)/2, mpf(2)/3]:
    print("   c4 분모 도함수 at lambda_b=",R(lb),":", R(mpf('0.4')*(1-lb) - 4*lb**(mpf(2)/3)*n**(-mpf(1)/3)))
# D 항목 다섯 값의 곱
print("   D값 곱:", R(mpf('1.957')*mpf('0.71216')*mpf('0.49998')*(2*mpf('0.9885')-mpf('0.00714'))-mpf('0.0169')))

print("== right-part 상수")
n0 = 50001; ymin = floor(2*mpf(n0)/3)+1
print("   y > 2n/3 -> y >=", ymin)
for yv in [mpf(33334), mpf(33335)]:
    print("   y=",yv,": 10y^(2/3)-1 =", R(10*yv**(mpf(2)/3)-1))
y = mpf(33334); r = mpf(10356)
print("   0.2r-7.3 =", R(mpf('0.2')*r-mpf('7.3')))
hv = lambda chi: chi**(-mpf(1)/2)*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi))
print("   hv coef at 2064:", R(hv(mpf(2064))*sqrt(mpf(2064))), "<=1.6932")
t = y**(mpf(1)/3)
eh = mpf('1.6932')*(t/10+1)*(2*t**2-mpf('7.5'))**(-mpf(1)/2); print("   eps_hov at y=33334:", R(eh), "<=0.1573")
print("   sqrt(2/pi)/sqrt(2064) =", R(sqrt(2/pi)/sqrt(mpf(2064))), "<=0.01757")
print("   0.75*1.1^(2/3) =", R(mpf('0.75')*mpf('1.1')**(mpf(2)/3)), "<=0.7993")
print("   0.92007(r+1)-1 >= 0.9199(r+1) at r+1=10357:", R(mpf('0.92007')*10357-1), R(mpf('0.9199')*10357))
print("   (n+1)/y <= 1.5+1/33334 =", R(mpf('1.5')+1/mpf(33334)))
pc = (2*pi)**(-mpf(1)/2)*(mpf('1.50003')/mpf('0.9199'))**mpf('1.5')*exp(1/(12*mpf(50002))); print("   pi_n(t0-1) 계수:", R(pc), "<=0.8308")
print("   0.3*0.8308 =", R(mpf('0.3')*mpf('0.8308')), " /sqrt(10357) =", R(mpf('0.24924')/sqrt(mpf(10357))), "<=0.00245")
print("   1-0.01757-0.00245 =", R(1-mpf('0.01757')-mpf('0.00245')))
print("   1/156+1/(12*33334)+1/(12*50002) -> e^-c4 =", R(exp(-(mpf(1)/156+1/(12*mpf(33334))+1/(12*mpf(50002))))), ">=0.9936")
rho_up = lambda rp1: mpf('0.07993')*rp1+1
rp1 = mpf(10357)
print("   (r+1)/(r-rho0) <=", R(rp1/(rp1-1-rho_up(rp1))), "<=1.0872")
print("   (0.7993y^(2/3)+2)^(3/2)/y at y=33334:", R((mpf('0.7993')*y**(mpf(2)/3)+2)**mpf('1.5')/y), "<=0.7172")
print("   eps0 <= 1.5 rho0/(r+1-rho0) =", R(mpf('1.5')*rho_up(rp1)/(rp1-rho_up(rp1))), "<=0.1305")
print("   (1+rho0/y)^(3/2) =", R((1+(mpf('0.7993')*y**(mpf(2)/3)+1)/y)**mpf('1.5')), "<=1.0376")
W = (2*pi)**(-mpf(1)/2)*mpf(2)/3*mpf('0.7172')*mpf('1.5')*mpf('1.0872')*mpf('1.0376')*exp(mpf('0.1305')+mpf(1)/400008)
print("   (r+1)/y * W <=", R(W), "<=0.3678")
P = (1-mpf('0.1573'))*mpf('0.71216')*mpf('0.9936')*(2*mpf('0.9799')-mpf('0.0232')) - mpf('0.3678')
print("   0.8427*0.71216*0.9936*1.9366-0.3678 =", R(P), ">=0.7869")
print("   Psi_R at 2/3:", R(mpf('0.7869')*2/3 - mpf(1)/3 - mpf('2.5e-5')))
print("   2x0.9799-0.0232 =", R(2*mpf('0.9799')-mpf('0.0232')))

print("== 5.5.2 rho_0 <= 0.75(1.1y)^(2/3)+1 전수 y in [25000,60000]")
def t0(y):
    t = y+2
    while True:
        if y <= (t-1) - int(floor(mpf('0.75')*mpf(t-1)**(mpf(2)/3))): return t
        t += 1
mp.dps = 30
bad=0
for yv in range(25000, 60001, 97):
    t = t0(yv)
    if t-1-yv > mpf('0.75')*(mpf('1.1')*yv)**(mpf(2)/3)+1: bad+=1
print("   위반:", bad)
