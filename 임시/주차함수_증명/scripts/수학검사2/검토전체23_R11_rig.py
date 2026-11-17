import mpmath as mp
mp.mp.dps=30
l=lambda m: (2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m)
print("l1,l2,l3:",l(1),l(2),l(3), 1/mp.mpf(36), 1/mp.mpf(405))
print("sum 2m l_m 4^(1-m) =", mp.nsum(lambda m: 2*m*l(int(m))*mp.mpf(4)**(1-m),[1,60]))
print("sum_{m>=2} l_m 4^(1-m) =", mp.nsum(lambda m: l(int(m))*mp.mpf(4)**(1-m),[2,60]))
logeta=lambda ph: 1-ph*mp.cot(ph)+mp.log(ph/mp.sin(ph))
print("log et(1/2) =", logeta(mp.mpf(1)/2), " series:", mp.nsum(lambda m: l(int(m))*mp.mpf(4)**(-m),[1,60]))
# ray constants
M=60
def LG(ph): return sum(2*m*l(m)*ph**(2*m-2) for m in range(1,M))
def LL(ph): return sum(l(m)*ph**(2*m) for m in range(1,M))
mx_lg=0; mn_re=10; amin=0; amax=-100; mxL=0; mxq=0
w=mp.e**(-1j*mp.pi/8)
for i in range(1,2001):
    rho=mp.mpf(i)/4000
    ph=rho*w
    L=LL(ph); 
    mx_lg=max(mx_lg,abs(LG(ph))); mn_re=min(mn_re,mp.re(L)/rho**2)
    q=mp.e**L-1
    a=mp.arg(q)*180/mp.pi; amin=min(amin,a); amax=max(amax,a)
    mxL=max(mxL,abs(L)/rho**2); mxq=max(mxq,abs(q)/rho**2)
print("max|lg|",mx_lg,"min ReL/|phi|^2",mn_re,"arg qy in",amin,amax,"|L|/|phi|^2<=",mxL,"|qy|/|phi|^2<=",mxq)
# xi constants
xi=lambda a: mp.e**(1-mp.e**(1j*a)+1j*a)
lo=10; hi=0; imlo=10
for i in range(1,4001):
    a=mp.mpf(i)/4000
    x=xi(a)
    lo=min(lo,abs(x-1)/a**2); hi=max(hi,abs(x-1)/a**2); imlo=min(imlo,mp.im(x)/a**3)
print("|xi-1|/a^2 in",lo,hi," Im xi/a^3 >=",imlo)
et12=mp.e**logeta(mp.mpf(1)/2)
best=10
for i in range(1,100001):
    a=mp.mpf(i)/100000
    x=xi(a); v=max(mp.im(x), et12-abs(x))
    if v<best: best=v; at=a
print("min over (0,1] of max(Im xi, et(1/2)-|xi|) =",best,"at",at)
# with only the stated constant 0.1666 a^3:
best2=10
for i in range(1,100001):
    a=mp.mpf(i)/100000
    v=max(mp.mpf('0.1666')*a**3, et12-mp.e**(1-mp.cos(a)))
    if v<best2: best2=v; at2=a
print("with stated constant only:",best2,"at",at2)
# arc: |et|-|xi| at 0.39 etc
print(mp.e**mp.mpf('0.085')-mp.e**(1-mp.cos(mp.mpf('0.39'))), 1-mp.cos(mp.mpf('0.39')), mp.mpf('0.1666')*mp.mpf('0.39')**3, mp.mpf('0.009')*mp.mpf(10001)**(mp.mpf(2)/3))
k=mp.mpf(10001)
print("arc bound log:", mp.log(mp.mpf('0.029')*k**1.5)-mp.mpf('0.085')*k, " coefficient:", mp.pi/8*mp.mpf('1.03')/mp.mpf('1.8')/8)
print("real rest log:", mp.log(166*k**(-mp.mpf(1)/6))-mp.mpf('0.1267')*k, " pi/0.019=",mp.pi/mp.mpf('0.019'))
# ku-derivative constants
print(mp.nsum(lambda m: 6*m*(m-1)*l(int(m))*mp.mpf(4)**(1-m),[2,60]), mp.nsum(lambda m: 3*(m-1)*l(int(m))*mp.mpf(4)**(1-m),[2,60]), mp.nsum(lambda m: 2*m*(3*m-3)*(3*m-4)*l(int(m))*mp.mpf(4)**(1-m),[2,60]), mp.nsum(lambda m: (3*m-3)*(3*m-4)*l(int(m))*mp.mpf(4)**(1-m),[2,60]))
print("(1-cos1)=",1-mp.cos(1), " tail m>=5:", mp.nsum(lambda m: 2*m*l(int(m))*mp.mpf(2)**(2-2*m),[5,60]))
print(10001**(-1/3), 0.0015/1.25**12, (1.0307e-4)**-3)
