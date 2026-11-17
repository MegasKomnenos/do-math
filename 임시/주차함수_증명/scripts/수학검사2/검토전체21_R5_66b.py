from mpmath import mp, mpf, sqrt, pi, log, exp, e, polyroots
mp.dps=20
def u(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def dd(k): return 1/e+u(k)/(e*2**mpf(1.5))
def Low(k,rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3)
    A=(2*pi)**(-mpf(0.5))*k**(mpf(1)/3)*(2*sqrt(rho)-mpf('2.218')*eps)/(1+rho*eps)
    return A*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf(1.5)*exp(1/(4*(k+1)))/((2*pi)**(-mpf(0.5))*(2*sqrt(rho)-mpf('2.218')*eps)))
print("Low(10001,1.4)=",Low(10001,mpf('1.4')), "Low(2001,0.75)=",Low(2001,mpf('0.75')))
def Obar(k,c): k=mpf(k); return dd(k)*exp(1+1/(12*k))*(1+c*k**(-mpf(1)/3)+1/k)**mpf(1.5)
print("Obar(10001,1.4)=",Obar(10001,mpf('1.4')), "Obar(2001,0.75)=",Obar(2001,mpf('0.75')))
# (6.45)
def wp(n): n=mpf(n); return mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3)
k=mpf(2001); d0=mpf('0.75')*k**(mpf(2)/3)
print("direct diff (6.45):", d0-(wp(k+d0)-1))
uu=k**(mpf(1)/3); print("u=",uu)
tail=mpf('0.39976')/uu+mpf('0.41616')/uu**2
print("1.30212+tail=",mpf('1.30212')+tail)
for c in ['1.3314','1.33647']:
    r=polyroots([mpf('0.15037'),-mpf('1.54829'),-mpf(c)]); print("c",c,"roots",r, "quad at u:", mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf(c))
print("wp'(1)=", mpf(2)/3*mpf('0.59963')*2**(-mpf(1)/3)+mpf(1)/3*mpf('1.24847')*2**(-mpf(2)/3))
print("1.4*10001^(2/3)",mpf('1.4')*mpf(10001)**(mpf(2)/3), "10*10001^(2/3)", 10*mpf(10001)**(mpf(2)/3), "10/2^(2/3)",10/2**(mpf(2)/3))
