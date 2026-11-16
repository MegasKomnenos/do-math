# -*- coding: utf-8 -*-
"""5B 수학검사2 검산 1: 5.5절 상수·부등식 재계산 (mpmath)."""
import mpmath as mp
mp.mp.dps = 30
S2PI = mp.sqrt(2*mp.pi)
def p(label, val): print(f"{label}: {mp.nstr(val, 12)}")

print("== 5.5.2 ==")
n=50001
p("10/2^(2/3) - 6 = coef", 10/mp.mpf(2)**(mp.mpf(2)/3) - 6)
p("10((n+1)/2)^(2/3) - (6 n^(2/3)+2) at n=50001", 10*((n+1)/mp.mpf(2))**(mp.mpf(2)/3) - 6*mp.mpf(n)**(mp.mpf(2)/3) - 2)
y=25000
p("0.75(1.1y)^(2/3) at y=25000 (<=0.1y=2500?)", mp.mpf('0.75')*(mp.mpf('1.1')*y)**(mp.mpf(2)/3))

print("== 5.5.5 (lemma 5.30) ==")
n=mp.mpf(50001)
v=(1/S2PI)*mp.sqrt(2)*mp.mpf(3)**1.5*(1+1/n)**1.5*n**-0.5*mp.exp(1/(12*(n+1)))
p("case y<=2n/3 bound (<=0.0133)", v)
p("(0.15)^1.5 (<=0.0581)", mp.mpf('0.15')**1.5)
p("(2pi)^-1/2*0.0581*(1+1/n)^1.5*e^(1/(12(n+1))) (<=0.0232)", (1/S2PI)*mp.mpf('0.0581')*(1+1/n)**1.5*mp.exp(1/(12*(n+1))))
p("e^-2 ((n+1)/(n-1))^1.5 e^(1/(12(n-1))) (<0.1354)", mp.e**-2*((n+1)/(n-1))**1.5*mp.exp(1/(12*(n-1))))
p("e^-1 - 0.1354 - 0.0232 (>0.2)", mp.e**-1 - mp.mpf('0.1354') - mp.mpf('0.0232'))

print("== stop-lower ==")
p("1.5*0.95^(-2.5) (<=1.706)", mp.mpf('1.5')*mp.mpf('0.95')**-2.5)
p("(1.085.. )/11: (1+1.706*0.05)/11 (<=0.099)", (1+mp.mpf('1.706')*mp.mpf('0.05'))/11)
p("(0.8^-1.5 - 1)/0.2 (<=1.988)", (mp.mpf('0.8')**-1.5-1)/mp.mpf('0.2'))
p("(1+1.988*0.2)/11 (<=0.128)", (1+mp.mpf('1.988')*mp.mpf('0.2'))/11)
p("4/sqrt(2pi) (<1.596)", 4/S2PI)
U=mp.mpf(25000); p("e^(1/(12U)) - (1+1/(11U)) at U=25000 (<=0)", mp.exp(1/(12*U))-(1+1/(11*U)))

print("== scaled-integrand constants ==")
h0=mp.mpf('0.0342'); p("h0^3*25000 (>=1)", h0**3*25000)
umax=mp.sqrt(6*h0); p("upsilon_max", umax)
c1=1/(2*(1-umax)); p("c1", c1)
c2=1/mp.sqrt(2)-umax/3; p("c2 (>=0.556)", c2)
p("12^1.5 (>=41.5)", mp.mpf(12)**1.5)
p("sqrt2(1+6h0)12/c2 (<=36.8)", mp.sqrt(2)*(1+6*h0)*12/c2)
f12 = mp.mpf('0.556')*mp.mpf('41.5') - 12 - mp.log(mp.mpf('36.8')); p("f(12) lower (>7)", f12)
p("f'(12)", 1.5*c2*mp.sqrt(12)-1-mp.mpf(1)/12)
Y=mp.mpf(25000)
O = (1/Y**2)*mp.sqrt(12/mp.pi)*Y**(mp.mpf(1)/3)*mp.sqrt(2/Y)*(Y+1); p("O(25000)", O)
p("6 Y^(2/3) <= Y/4 threshold Y=24^3", mp.mpf(24)**3)
# w0 assembly from ul output
pos=mp.mpf('0.74411578'); neg=mp.mpf('0.031947769'); p("pos - neg (ul 1600x1200)", pos-neg)
p("e^(-12+h0)", mp.exp(-12+h0))

print("== band-inequality conditions ==")
n=mp.mpf(50001); y=2*n/3
p("0.4(n-y) - (6y^(2/3)+1) at lambda=2/3", mp.mpf('0.4')*(n-y)-(6*y**(mp.mpf(2)/3)+1))
p("0.75(1.1y)^(2/3)+1 vs 0.7(n-y)", mp.mpf('0.75')*(mp.mpf('1.1')*y)**(mp.mpf(2)/3)+1); p("0.7(n-y)", mp.mpf('0.7')*(n-y))
p("floor(0.3n/3)", mp.floor(mp.mpf('0.3')*n/3))

print("== right-part ==")
y=mp.mpf(33334)
y23=y**(mp.mpf(2)/3); p("y^(2/3) at 33334", y23); p("10y^(2/3)-1 (>=10356?)", 10*y23-1)
r=10*y23-1
p("Q_w >= 0.2r-7.3", mp.mpf('0.2')*r-mp.mpf('7.3'))
Q=mp.mpf(2064)
p("hv_Q*sqrt(Q) at Q=2064 (<=1.6932)", (2/mp.sqrt(mp.pi))*(1+1/Q)+1/mp.sqrt(mp.pi))
t=y**(mp.mpf(1)/3)
p("eps_hov at y=33334 (<=0.1573)", mp.mpf('1.6932')*(t/10+1)/mp.sqrt(2*t**2-mp.mpf('7.5')))
p("sqrt(2/pi)/sqrt(2064) (<=0.01757)", mp.sqrt(2/mp.pi)/mp.sqrt(Q))
p("(2pi)^-1/2 (1.50003/0.9199)^1.5", (1/S2PI)*(mp.mpf('1.50003')/mp.mpf('0.9199'))**1.5)
p("  * e^(1/(12*43691)) (<=0.8308)", (1/S2PI)*(mp.mpf('1.50003')/mp.mpf('0.9199'))**1.5*mp.exp(1/(12*mp.mpf(43691))))
p("0.3*0.8308", mp.mpf('0.3')*mp.mpf('0.8308'))
R=r+1
p("0.24924/sqrt(r+1) (<=0.00245)", mp.mpf('0.24924')/mp.sqrt(R))
p("1-0.01757-0.00245 (>=0.9799)", 1-mp.mpf('0.01757')-mp.mpf('0.00245'))
rho0 = mp.mpf('0.75')*(mp.mpf('1.1')*y)**(mp.mpf(2)/3)+1
p("rho0 bound at y=33334", rho0); p("0.08(r+1)+1", mp.mpf('0.08')*R+1)
p("(r+1)/(r-rho0) (<=1.0871)", R/(r-rho0)); p("(r+1)/(0.92(r+1)-1)", R/(mp.mpf('0.92')*R-1))
p("(rho0+1)^1.5 / y (<=0.7171)", (rho0+1)**1.5/y); p("(0.7992 y^(2/3)+2)^1.5/y", (mp.mpf('0.7992')*y23+2)**1.5/y)
p("1.5 rho0/(r+1-rho0) (<=0.1305)", mp.mpf('1.5')*rho0/(R-rho0))
p("  with rho0<=0.08(r+1)+1, r+1-rho0>=0.92(r+1)-1, r+1=10357", mp.mpf('1.5')*(mp.mpf('0.08')*10357+1)/(mp.mpf('0.92')*10357-1))
p("(1+rho0/y)^1.5 (<=1.0375?)", (1+rho0/y)**1.5)
W = (1/S2PI)*(mp.mpf(2)/3)*mp.mpf('0.7171')*mp.mpf('1.5')*mp.mpf('1.0871')*mp.mpf('1.0375')*mp.exp(mp.mpf('0.1305')+1/mp.mpf(400008))
p("(r+1)W/y product (<=0.3677)", W)
W2 = (1/S2PI)*(mp.mpf(2)/3)*mp.mpf('0.7171')*mp.mpf('1.5')*mp.mpf('1.0871')*(1+rho0/y)**1.5*mp.exp(mp.mpf('0.1305')+1/mp.mpf(400008))
p("  same with exact (1+rho0/y)^1.5", W2)
p("e^-c4 lower: exp(-1/156-1/(12*33334)-1/(12*50002)) (>=0.9936)", mp.exp(-mp.mpf(1)/156-1/(12*y)-1/(12*mp.mpf(50002))))
p("0.8427*0.71216*0.9936*1.9366-0.3677 (>=0.7870)", mp.mpf('0.8427')*mp.mpf('0.71216')*mp.mpf('0.9936')*mp.mpf('1.9366')-mp.mpf('0.3677'))
p("0.7870*2/3 (>=0.5246)", mp.mpf('0.7870')*2/3)
p("0.5246-0.3334-0.0001", mp.mpf('0.5246')-mp.mpf('0.3334')-mp.mpf('0.0001'))

print("== hover-tail integer check ==")
for z in (2,3,4): p(f"z^1.5/sqrt(2z-3) z={z}", mp.mpf(z)**1.5/mp.sqrt(2*z-3))
p("2sqrt2", 2*mp.sqrt(2)); p("(2/sqrt pi) 2 sqrt2", (2/mp.sqrt(mp.pi))*2*mp.sqrt(2))

print("== zeta ==")
N=2000
S = mp.fsum(mp.mpf(j)**-1.5 for j in range(1,N))
z32 = mp.zeta(1.5)
p("zeta(3/2)", z32); p("S+2N^-1/2+N^-3/2/2 (lower)", S+2*mp.mpf(N)**-0.5+0.5*mp.mpf(N)**-1.5)
p("S+2(N-1/2)^-1/2 (upper)", S+2*(N-mp.mpf('0.5'))**-0.5)
p("coarse: S+2(N+1)^-1/2", S+2*mp.mpf(N+1)**-0.5)
p("zeta(-1/2)", mp.zeta(-0.5)); p("zeta(1/2)", mp.zeta(0.5))
p("0.2078862250607 - |zeta(-1/2)|", mp.mpf('0.2078862250607')+mp.zeta(-0.5))

print("== induction rows ==")
m=10001; f=max(f for f in range(0,2000) if 64*f**3 <= 27*m*m); print("floor(0.75 m^(2/3)) m=10001:", f, "lower:", m-f)

print("== 5.6 ==")
for k in (25001,10001):
    k=mp.mpf(k); p(f"omega coef k={k}", 1-4*mp.mpf('1.2879')*k**(-mp.mpf(1)/3)-mp.mpf('6.5')*mp.mpf('0.939')*k**(-mp.mpf(2)/3)-12/k)
p("gamma* = (1000/25001)^(1/6)", (mp.mpf(1000)/25001)**(mp.mpf(1)/6)); p("(1000/10001)^(1/6)", (mp.mpf(1000)/10001)**(mp.mpf(1)/6))
p("ex_H min = 5*6^(2/3)*2^(-2/3) (>=10.40)", 5*mp.mpf(6)**(mp.mpf(2)/3)*mp.mpf(2)**(-mp.mpf(2)/3))
p("6*60^1.5", 6*mp.mpf(60)**1.5)
p("4/3(1+e^-2)", mp.mpf(4)/3*(1+mp.e**-2)); p("8/3*1.514-2", mp.mpf(8)/3*mp.mpf('1.514')-2)
p("sqrt(17/16)", mp.sqrt(mp.mpf(17)/16))
p("(2/12)/(1-1/32) (<=0.172)", (mp.mpf(2)/12)/(1-mp.mpf(1)/32))

print("== zeta coarse method: which partial sum gives 2.6123698 ==")
S1=mp.fsum(mp.mpf(j)**-1.5 for j in range(1,N)); S2=mp.fsum(mp.mpf(j)**-1.5 for j in range(1,N+1))
p("sum_{j<N}+2(N+1)^-1/2", S1+2*mp.mpf(N+1)**-0.5); p("sum_{j<=N}+2(N+1)^-1/2", S2+2*mp.mpf(N+1)**-0.5)
p("sum_{j<=N}+2(N+1/2)^-1/2", S2+2*(N+mp.mpf('0.5'))**-0.5)
