# 검토전체6 L4: 장5B.md의 수치 상수·부등식 검산
# python -I 로 실행. 외부 자료를 읽지 않는다.
from mpmath import mp, mpf, sqrt, exp, log, pi, e, erfc, quad, floor, ceil, inf

mp.dps = 30

def Bor(m):
    m = mpf(m)
    return exp(-m) * m**(m-1) / mp.factorial(m)

def g(x):
    x = mpf(x)
    return (x-1)*log(1+1/x)

def pr(name, val, cond=None):
    print(f"{name}: {mp.nstr(val, 12)}" + ("" if cond is None else f"   -> {'OK' if cond else 'FAIL'}"))

print("== 5.5.2 line 60: 10((n+1)/2)^(2/3) > 6 n^(2/3)+2 at n=50001")
n = mpf(50001)
pr("lhs", 10*((n+1)/2)**(mpf(2)/3)); pr("rhs", 6*n**(mpf(2)/3)+2, 10*((n+1)/2)**(mpf(2)/3) > 6*n**(mpf(2)/3)+2)
pr("6n^(2/3)+1 vs 1+0.75(n-1)^(2/3)", 1+mpf(3)/4*(n-1)**(mpf(2)/3), 6*n**(mpf(2)/3)+1 > 1+mpf(3)/4*(n-1)**(mpf(2)/3))

print("== 5.5.2 line 62: t-1 <= 1.1 y at y=25000")
y = mpf(25000)
t1 = y + ceil(mpf('0.75')*(mpf('1.1')*y)**(mpf(2)/3))
pr("t-1", t1); pr("1.1y", mpf('1.1')*y, t1 <= mpf('1.1')*y)

print("== 5.5.4 line 175: (m+d+2)/((w+2)(m+1)) <= z_m(d) sample check")
ok = True
for m in range(2, 400):
    for d in range(1, m//2+1):
        w = m-d
        lhs = mpf(m+d+2)/((w+2)*(m+1))
        z = exp(mpf(d-1)/w)/(w+1) + mpf(3*d)/(2*(w+1)*(m+1))
        if lhs > z: ok = False; print("fail", m, d)
print("loss-rate comparison all m<400:", "OK" if ok else "FAIL")

print("== 5-30 constants")
pr("Bor(1)", Bor(1), abs(Bor(1)-exp(-1)) < mpf(10)**-25)
pr("Bor(2)", Bor(2), abs(Bor(2)-exp(-2)) < mpf(10)**-25)
n = mpf(50001)
v1 = (2*pi)**(-mpf(1)/2)*sqrt(2)*mpf(3)**(mpf(3)/2)*(1+1/n)**(mpf(3)/2)*n**(-mpf(1)/2)*exp(1/(12*(n+1)))
pr("top_pi bound y<=2n/3", v1, v1 <= mpf('0.0133'))
pr("(1.5/10)^(3/2)", (mpf('1.5')/10)**(mpf(3)/2), (mpf('1.5')/10)**(mpf(3)/2) <= mpf('0.0581'))
v2 = (2*pi)**(-mpf(1)/2)*mpf('0.0581')*(1+1/n)**(mpf(3)/2)*exp(1/(12*(n+1)))
pr("top_pi bound y>2n/3", v2, v2 <= mpf('0.0232'))
v3 = exp(-2)*((n+1)/(n-1))**(mpf(3)/2)*exp(1/(12*(n-1)))
pr("pi_n(n-1) bound", v3, v3 < mpf('0.1354'))
pr("e^-1-0.1354-0.0232", exp(-1)-mpf('0.1354')-mpf('0.0232'), exp(-1)-mpf('0.1354')-mpf('0.0232') > mpf('0.2'))
# exact check of pi_n(n-1) <= bound at n=50001 via Robbins
pr("exact e^-2 Bor(n-1)/Bor(n+1) at n=50001", exp(-2)*Bor(50000)/Bor(50002))

print("== stop-lower constants")
pr("1.5*0.95^(-2.5)", mpf('1.5')*mpf('0.95')**(-mpf(5)/2), mpf('1.5')*mpf('0.95')**(-mpf(5)/2) <= mpf('1.706'))
pr("(0.8^(-1.5)-1)/0.2", (mpf('0.8')**(-mpf(3)/2)-1)/mpf('0.2'), (mpf('0.8')**(-mpf(3)/2)-1)/mpf('0.2') <= mpf('1.988'))
pr("4/sqrt(2pi)", 4/sqrt(2*pi), 4/sqrt(2*pi) < mpf('1.596'))
U = mpf(25000)
pr("e^(1/(12U)) <= 1+1/(11U)", exp(1/(12*U)) - (1+1/(11*U)), exp(1/(12*U)) <= 1+1/(11*U))
# (1+1.706p)(1+1/(11U)) <= 1+(1.706 i+0.099)/U with p=i/U<=0.05
pr("(1+1.706*0.05)/11", (1+mpf('1.706')*mpf('0.05'))/11, (1+mpf('1.706')*mpf('0.05'))/11 <= mpf('0.099'))
pr("(1+1.988*0.2)/11", (1+mpf('1.988')*mpf('0.2'))/11, (1+mpf('1.988')*mpf('0.2'))/11 <= mpf('0.128'))

print("== scaled-integrand constants")
h0 = mpf('0.0342')
pr("h0^3 >= 1/25000", h0**3, h0**3 >= mpf(1)/25000)
umax = sqrt(6*h0); c1 = 1/(2*(1-umax)); c2 = 1/sqrt(2) - umax/3
pr("upsilon_max", umax); pr("c1", c1); pr("c2", c2, c2 >= mpf('0.556'))
f12 = mpf('0.556')*mpf(12)**(mpf(3)/2) - 12 - log(sqrt(2)*(1+6*h0)*12/mpf('0.556'))
pr("f(12) with c2=0.556", f12, f12 > 7)
pr("sqrt2(1+6h0)12/0.556", sqrt(2)*(1+6*h0)*12/mpf('0.556'))
# g(theta)=0 for theta > threshold where 6 - theta h0 < theta^2/3
th = mp.findroot(lambda t: t**2/3 + t*h0 - 6, 4)
pr("theta where mu(theta,0)=theta^2/3", th)
Y = mpf(25000); h = Y**(-mpf(1)/3); qmax = floor(6*Y**(mpf(2)/3))
pr("theta at z=qmax+1, Y=25000", (qmax+1)*h, (qmax+1)*h > th)
pr("6 - theta*h0 at theta=(qmax+1)h", 6-(qmax+1)*h*h0)

print("== ti closed form vs quadrature")
for (vs, b, W0) in [(mpf('0.3'), mpf('2'), mpf('3')), (mpf('0.01'), mpf('0.5'), mpf('5.5')), (mpf(0), mpf('1'), mpf('2'))]:
    num = quad(lambda u: u**(-mpf(3)/2)*exp(-vs*u - b/u), [W0, inf])
    cf = mpf(1)/2*sqrt(pi/b)*(exp(-2*sqrt(vs*b))*erfc(sqrt(vs*W0)-sqrt(b/W0)) - exp(2*sqrt(vs*b))*erfc(sqrt(vs*W0)+sqrt(b/W0)))
    pr(f"ti({vs},{b};{W0}) quad", num); pr("closed", cf, abs(num-cf) < mpf(10)**-15)

print("== right-part constants")
y = mpf(33334)
pr("10 y^(2/3) - 1 at y=33334", 10*y**(mpf(2)/3)-1, 10*y**(mpf(2)/3)-1 >= 10356)
r = mpf(10356)
pr("0.2r-7.3", mpf('0.2')*r-mpf('7.3'))
pr("e^-c4 lower", exp(-(mpf(1)/156 + 1/(12*y) + 1/(12*mpf(50002)))), exp(-(mpf(1)/156 + 1/(12*y) + 1/(12*mpf(50002)))) >= mpf('0.9936'))
chi = mpf(2064)
hv = chi**(-mpf(1)/2)*(2/sqrt(pi)*(1+1/chi) + 1/sqrt(pi))
pr("hv*sqrt(chi) at chi=2064", hv*sqrt(chi), hv*sqrt(chi) <= mpf('1.6932'))
t = y**(mpf(1)/3)
eh = mpf('1.6932')*(t/10+1)*(2*t**2-mpf('7.5'))**(-mpf(1)/2)
pr("eps_hov at y=33334", eh, eh <= mpf('0.1573'))
pr("sqrt(2/pi)/sqrt(2064)", sqrt(2/pi)/sqrt(chi), sqrt(2/pi)/sqrt(chi) <= mpf('0.01757'))
pr("0.75*1.1^(2/3)", mpf('0.75')*mpf('1.1')**(mpf(2)/3), mpf('0.75')*mpf('1.1')**(mpf(2)/3) <= mpf('0.7993'))
pr("0.92007(r+1)-1 >= 0.9199(r+1) at r+1=10357", (mpf('0.92007')-mpf('0.9199'))*10357 - 1, (mpf('0.92007')-mpf('0.9199'))*10357 >= 1)
pr("(2pi)^-1/2 (1.50003/0.9199)^1.5", (2*pi)**(-mpf(1)/2)*(mpf('1.50003')/mpf('0.9199'))**(mpf(3)/2))
v = (2*pi)**(-mpf(1)/2)*(mpf('1.50003')/mpf('0.9199'))**(mpf(3)/2)*exp(1/(12*mpf(50002)))
pr("... * e^(1/(12*50002))", v, v <= mpf('0.8308'))
pr("0.3*0.8308", mpf('0.3')*mpf('0.8308'), mpf('0.3')*mpf('0.8308') <= mpf('0.24924'))
pr("0.24924/sqrt(10357)", mpf('0.24924')/sqrt(10357), mpf('0.24924')/sqrt(10357) <= mpf('0.00245'))
pr("1-0.01757-0.00245", 1-mpf('0.01757')-mpf('0.00245'), 1-mpf('0.01757')-mpf('0.00245') >= mpf('0.9799'))
# fourth
rp1 = mpf(10357)
rho0max = mpf('0.07993')*rp1 + 1
pr("(r+1)/(r-rho0)", rp1/(rp1-1-rho0max), rp1/(rp1-1-rho0max) <= mpf('1.0872'))
pr("(0.7993 y^(2/3)+2)^(3/2)/y", (mpf('0.7993')*y**(mpf(2)/3)+2)**(mpf(3)/2)/y, (mpf('0.7993')*y**(mpf(2)/3)+2)**(mpf(3)/2)/y <= mpf('0.7172'))
pr("eps0 bound 1.5 rho0/(r+1-rho0)", mpf('1.5')*rho0max/(rp1-rho0max), mpf('1.5')*rho0max/(rp1-rho0max) <= mpf('0.1305'))
pr("(1+rho0/y)^1.5", (1+(mpf('0.7993')*y**(mpf(2)/3)+1)/y)**(mpf(3)/2), (1+(mpf('0.7993')*y**(mpf(2)/3)+1)/y)**(mpf(3)/2) <= mpf('1.0376'))
W4 = (2*pi)**(-mpf(1)/2)*mpf(2)/3*mpf('0.7172')*mpf('1.5')*mpf('1.0872')*mpf('1.0376')*exp(mpf('0.1305')+mpf(1)/400008)
pr("(r+1)W/y bound", W4, W4 <= mpf('0.3678'))
v5 = (1-mpf('0.1573'))*mpf('0.71216')*mpf('0.9936')*(2*mpf('0.9799')-mpf('0.0232')) - mpf('0.3678')
pr("0.8427*0.71216*0.9936*1.9366-0.3678", v5, v5 >= mpf('0.7869'))
pr("0.7869*2/3 - 1/3 - 2.5e-5", mpf('0.7869')*2/3 - mpf(1)/3 - mpf('2.5e-5'), mpf('0.7869')*2/3 - mpf(1)/3 - mpf('2.5e-5') > mpf('0.191'))
# 2 rho0 <= r check, chi_2 <= r - rho0
pr("2 rho0max vs r", 2*rho0max, 2*rho0max <= 10356)
pr("0.3r + rho0max vs r", mpf('0.3')*10356 + rho0max, mpf('0.3')*10356 + rho0max <= 10356)

print("== band-inequality conditions at n=50001")
n = mpf(50001)
for lam in [mpf(1)/2, mpf(2)/3]:
    yv = lam*n
    pr(f"0.4(n-y) at lam={mp.nstr(lam,4)}", mpf('0.4')*(n-yv)); pr("6y^(2/3)+1", 6*yv**(mpf(2)/3)+1, mpf('0.4')*(n-yv) >= 6*yv**(mpf(2)/3)+1)
    rho = mpf('0.75')*(mpf('1.1')*yv)**(mpf(2)/3)+1
    pr("rho0 bound", rho); pr("0.7(n-y)", mpf('0.7')*(n-yv), rho <= mpf('0.7')*(n-yv))
pr("floor(0.3 n/3)", floor(mpf('0.3')*n/3))

print("== 5-38: r0(m)+1 <= m(m) check, i.e. (r0+1)^1.5+9(r0+1) <= m for m>=20001 sample")
ok = True
for m in [20001, 25002, 30000, 50001, 10**6, 10**8]:
    r0 = floor(mpf(3)/4*mpf(m)**(mpf(2)/3))
    if (r0+1)**(mpf(3)/2)+9*(r0+1) > m: ok = False; print("fail", m)
print("r0+1 in m-set:", "OK" if ok else "FAIL")

print("== 5-26: epsilon(r) increasing & c0 bound sanity sample (n=50001,y=26000)")
n=50001; y=26000
t0 = next(t for t in range(y+2, n+1) if y <= (t-1) - int(mpf(3)/4*mpf(t-1)**(mpf(2)/3)))
rho0 = t0-1-y
print("t0,rho0", t0, rho0, "bound 0.75(1.1y)^(2/3)+1 =", mp.nstr(mpf('0.75')*(mpf('1.1')*y)**(mpf(2)/3)+1, 8))
c0 = mpf(3)/2*(2*y+2*rho0-n)/(mpf(y)*(n-y-rho0))
ok=True
for t in range(y+1, t0):
    s = sum(g(i)-g(n-i) for i in range(y, t))
    eps = (t-y)*mpf(3)/2*(2*t-2-n)/(mpf(t-1)*(n-t+1))
    if s > eps or eps > c0*(t-y): ok=False
print("sum g diff <= eps(t-y) <= c0 (t-y):", "OK" if ok else "FAIL")
