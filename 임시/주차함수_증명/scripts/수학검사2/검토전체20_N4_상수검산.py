# N4: 5.5절의 명시 상수 검산 (5-30, right-part, band-inequality 첫 셀, 5-26의 wid 상계)
import math
def Bor(m): return math.exp(-m + (m-1)*math.log(m) - math.lgamma(m+1))
def pi_n(n,t): return Bor(t)*Bor(n+1-t)/Bor(n+1)
out=[]
# 5-30 constants
n=50001
c1=(2*math.pi)**-0.5*math.sqrt(2)*3**1.5*(1+1/n)**1.5*n**-0.5*math.exp(1/(12*(n+1)))
out.append(f"5-30 y<=2n/3 top_pi bound = {c1:.5f} (<=0.0133?)")
c2=(2*math.pi)**-0.5*(0.15)**1.5*(1+1/n)**1.5*math.exp(1/(12*(n+1)))
out.append(f"5-30 y>2n/3 top_pi bound = {c2:.5f} (<=0.0232?)  (0.15)^1.5={0.15**1.5:.5f}")
c3=math.exp(-2)*((n+1)/(n-1))**1.5*math.exp(1/(12*(n+1)))
out.append(f"5-30 pi_n(n-1) bound = {c3:.5f} (<0.1354?) ; bracket>= {math.exp(-1)-0.1354-0.0232:.5f}")
# t0(y) and wid check for a few y
def t0(y):
    t=y+2
    while not (y <= (t-1)-math.floor(0.75*(t-1)**(2/3))): t+=1
    return t
for y in [25000,25001,33334,100000,10**6]:
    w=t0(y)-1-y; out.append(f"y={y}: wid={w}, bound 0.75(1.1y)^(2/3)+1={0.75*(1.1*y)**(2/3)+1:.2f}")
# right-part constants at y=33334, r=10357
y=33334; t=y**(1/3)
out.append(f"right: r>10y^(2/3)-1 = {10*y**(2/3)-1:.2f}; eps_hov={1.6932*(t/10+1)/math.sqrt(2*t*t-7.5):.5f}")
out.append(f"right: sqrt(2/pi)/sqrt(2064)={math.sqrt(2/math.pi)/math.sqrt(2064):.5f}; (1.50003/0.9199)^1.5/sqrt(2pi)={(1.50003/0.9199)**1.5/math.sqrt(2*math.pi):.6f}; 0.24924/sqrt(10358)={0.24924/math.sqrt(10358):.5f}")
rp1=10358
out.append(f"right: (r+1)/(r-wid)<= {1/(0.92007-2/rp1):.5f}; (0.7993+2y^-2/3)^1.5={(0.7993+2*y**(-2/3))**1.5:.5f}; eps0<= {1.5*(0.07993*rp1+1)/(0.92007*rp1-1):.5f}; (1+wid/y)^1.5={(1+(0.7993*y**(2/3)+1)/y)**1.5:.5f}")
W=(2*math.pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*math.exp(0.1305+1/400008)
out.append(f"right: (r+1)/y*W <= {W:.5f} (<=0.3678?) ; e^-c4>= {math.exp(-1/156-1/(12*33334)-1/(12*50002)):.5f}")
out.append(f"right: 0.8427*0.71216*0.9936*1.9366-0.3678 = {0.8427*0.71216*0.9936*1.9366-0.3678:.5f}; at lambda=2/3: {0.7869*2/3-1/3-2.5e-5:.4f}")
# band-inequality first cell, n=50001
la=0.5; lb=0.5+1/24000; n=50001
wbar=0.75*(1.1*lb*n)**(2/3)+1
chi_lb=math.floor(0.3*(1-lb)*n-1)
hov=sum((la-1/n)**z*max(0.0,1-2/math.sqrt(math.pi)*z**1.5*(chi_lb-1)**-0.5) for z in range(0,100000))
bw=1-math.sqrt(2/math.pi)*(0.3*(1-lb)*n-1)**-0.5-0.3*(1-la)*n*(2*math.pi)**-0.5*((n+1)/(la*n*((1-lb)*n-wbar)))**1.5*math.exp(1/(12*(n+1)))
toppi=(2*math.pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb)**-1.5*n**-0.5*math.exp(1/(12*n))
Kt=la*math.exp(-1/(12*(0.4*(1-lb)*n-6*(lb*n)**(2/3)+1))-1/(12*la*n)-1/(12*(n+1)))
cb1=1.5*((2*lb-1)*n+2*wbar)/(la*n*((1-lb)*n-wbar))
eb0=1.5*wbar*((2*lb-1)*n+2*wbar)/((la*n-1)*((1-lb)*n-wbar))
Wc=(2*math.pi)**-0.5*(2/3)*(wbar+1)**1.5*cb1*(1+wbar/(la*n))**1.5*math.exp(eb0+1/(12*la*n))
lhs=hov*0.71216*Kt*(2*bw-toppi)-Wc
out.append(f"band first cell: hov>={hov:.4f}, weight-sum>={bw:.5f}, top_pi<={toppi:.5f}, K~>={Kt:.5f}, W<={Wc:.5f}, LHS>={lhs:.5f} (>=1.3558?)")
print("\n".join(out))
