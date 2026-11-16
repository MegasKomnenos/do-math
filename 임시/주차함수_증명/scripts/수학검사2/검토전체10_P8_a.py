# P8: 8장 수치·식 재확인 (1) 8.1-8.2 초등 부등식
from mpmath import mp, mpf, sqrt, exp, log, zeta, pi, factorial, e, quad
mp.dps = 30
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2)
print("zeta", z12, zm12, z32)
def Bor(m): return exp(-m)*mpf(m)**(m-1)/factorial(m)
def Ren(j): return mpf(1) if j==0 else exp(-j)*mpf(j)**j/factorial(j)
def Psi(q): return sum(Ren(j) for j in range(1,q+1))
c=(2*pi)**(-mpf(1)/2)
# (나) Euler-Maclaurin
bad=[]
for r in range(1,200):
    s1=sum(mpf(j)**(-mpf(1)/2) for j in range(1,r+1)); s2=sum(sqrt(mpf(j)) for j in range(1,r+1)); s3=sum(mpf(j)**(-mpf(3)/2) for j in range(1,r+1))
    u1=2*sqrt(r)+z12+mpf(1)/2/sqrt(r); l1=u1-mpf(1)/24*r**(-mpf(3)/2)
    l2=mpf(2)/3*r**(mpf(3)/2)+sqrt(r)/2+zm12; u2=l2+mpf(1)/24/sqrt(r)
    if not (l1<=s1<=u1 and l2<=s2<=u2 and s3<=z32): bad.append(r)
print("(나) violations", bad)
# (가)
bad=[]
for m in range(1,300):
    if not (c*m**(-1.5)*exp(-mpf(1)/(12*m))<=Bor(m)<=c*m**(-1.5)*exp(-mpf(1)/(12*m+1))): bad.append(m)
    if not (c*m**(-0.5)*exp(-mpf(1)/(12*m))<=Ren(m)<=c*m**(-0.5)*exp(-mpf(1)/(12*m+1))): bad.append(-m)
print("(가) violations", bad)
# (다)
bad=[]
for q in range(1,400):
    ble=sum(Bor(m) for m in range(1,q+1)); bgt=1-ble
    if not (Psi(q)<=c*(2*sqrt(q)-1)): bad.append(('psi',q))
    if not (ble>=1-sqrt(2/pi)/sqrt(q)): bad.append(('ble',q))
    if not (2*c*exp(-mpf(1)/(12*(q+1)))/sqrt(q+1)<=bgt<=sqrt(2/pi)/sqrt(q)): bad.append(('bgt',q))
print("(다) violations", bad)
# (라)
cP=-z12+z32/12
def Plow(r):
    r=mpf(r)
    return mpf(0) if r<1 else c*(2*sqrt(r)-cP+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
bad=[r for r in range(1,400) if not (Psi(r)>=Plow(r))]
print("(라) violations", bad, "cPsi", cP, "Plow(1)", Plow(1), c*(mpf(59)/24-cP))
# (마)
def g(x): x=mpf(x); return (x-1)*log(1+1/x)
bad=[]
for i in range(1,300):
    if not (mpf(3)/(2*i)-mpf(5)/(6*i*i)<=1-g(i)<=mpf(3)/(2*i)): bad.append(i)
for ip in range(3,80):
    for j in range(1,ip-1):
        if not Bor(ip-j)/Bor(ip)<=((mpf(ip)-1)/(ip-1-j))**1.5: bad.append((ip,j))
print("(마) violations", bad[:5])
# 8.2 numbers
k=mpf(6600); qmin=mpf('0.2')*k**(mpf(2)/3); pmin=qmin-1
print("qmin",qmin,"pmin",pmin,"sqrt pmin",sqrt(pmin),"mu",1/qmin,"xieps",mpf('6.001')*k**(-mpf(1)/3),"eps0",k**(-mpf(1)/3),"k^-2/3",k**(-mpf(2)/3),(1-1/qmin)**-0.5,(1-1/qmin)**-1.5)
print("j_inf(0.2)",mpf(4)/3*c*mpf('0.2')**1.5)
def s_(q): return mpf(4)/15*q**2.5+mpf('0.385')*q**1.5
def Cr(q,k): return mpf(3)/2*c*(k+q)**1.5/(k+1)**3.5*s_(q)
print("Cr(qmin,6600)",Cr(qmin,k), "exp(-0.0477345)",exp(-mpf('0.0477345')))
E0=2*c/sqrt(mpf('0.2'))
print("E(0.2,6600) bound",E0*(1+mpf('0.2')*k**(-mpf(1)/3)), "den",mpf('0.168623')+E0, "ratio",E0*(1+mpf('0.2')*k**(-mpf(1)/3))/(mpf('0.168623')+E0))
print("0.2-k^-2/3-3c sqrt.2 eps0", mpf('0.2')-k**(-mpf(2)/3)-3*c*sqrt(mpf('0.2'))*k**(-mpf(1)/3))
print("Cr(2,6934.2)",Cr(2,mpf('6934.2')),"s(2)",s_(2),"2c sqrt(.0005)*.0005",2*c*sqrt(mpf('0.0005'))*mpf('0.0005'))
print("Cr(2e4,6.6e9)",Cr(mpf(2e4),mpf(6.6e9)))
print("Ks(0.0055)",(2/mpf('0.0055'))**1.5)
