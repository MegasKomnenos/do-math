from mpmath import mp, mpf, sqrt, exp, log, pi, zeta
mp.dps=30
c=1/sqrt(2*pi)
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2)
cpsi=-z12+z32/12
def Psilow(r):
    if r<1: return mpf(0)
    return c*(2*sqrt(r)-cpsi+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
def pieces(xi,k):
    q=xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3)
    E=2*c*exp(-1/(12*q))/sqrt(xi)*(1+xi*eps)
    R1=mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    H=mpf(2)/3*p**(mpf(3)/2)+p**(mpf(1)/2)/2+zm12+p**(-mpf(1)/2)/24
    R2=mpf(15)/8*c*n**(mpf(5)/2)*H/(kk**(mpf(7)/2)*k**(mpf(2)/3))
    D1=p/k**(mpf(2)/3)
    D2=kk*sqrt(2/pi)*p**(-mpf(1)/2)*k**(-mpf(2)/3)
    D3=mpf(3)/2*kk*Psilow(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
k=mpf(6600)
for xi in ['0.2','2','2.1','6.001']:
    print(xi, qkk(mpf(xi),k), pieces(mpf(xi),k))
def s_(q): return mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
def Cr(q,kk): return mpf(3)/2*c*(kk+q)**(mpf(3)/2)/(kk+1)**(mpf(7)/2)*s_(q)
K=mpf(6.6e9)*mpf('1.02')
print("Cr at K_{L-1} up to 1.02*6.6e9, q=0.005684*K^(2/3):", Cr(mpf('0.005684')*K**(mpf(2)/3), mpf(6.6e9)), Cr(mpf('0.005684')*K**(mpf(2)/3), K))
