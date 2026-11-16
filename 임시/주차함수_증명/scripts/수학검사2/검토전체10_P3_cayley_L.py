import sympy as sp, mpmath as mp
t=sp.Symbol('t')
lhs=sp.expand((2+sp.Rational(5,2)*t+2*t**2)*(-sp.Rational(5,2)*t+sp.Rational(4,3)*t**2-sp.Rational(11,12)*t**3+sp.Rational(1,2)*t**4)+5*t+4*t**2)
rhs=sp.expand(t**2*(sp.Rational(5,12)-sp.Rational(7,2)*t+sp.Rational(11,8)*t**2-sp.Rational(7,12)*t**3+t**4))
print("cayley poly identity:", sp.simplify(lhs-rhs)==0)
# (1/t-2)(t - t^2/2 + t^3/3 - t^4/4)
print(sp.expand((1/t-2)*(t-t**2/2+t**3/3-t**4/4)))
# L(10^4)
mp.mp.dps=30
f=lambda y,i: y**i*mp.e**(-y-y**2/2)
M=[mp.quad(lambda y: f(y,i),[0,mp.inf]) for i in range(6)]
M26=mp.quad(lambda y: f(y,2),[0,6])
Ms={}
for i in range(2,6):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0
    y0=(-1+mp.sqrt(1+4*i))/2
    Ms[i]=f(y0,i)
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
s=mp.mpf(100)
L=(M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+mp.e**(-0.5))/s+1/s**2)
print("L(1e4)=",L)
# direct tm_{r-1}(rho) for r=10^4, rho=e^{-1/100}
r=10000; rho=mp.e**(-mp.mpf(1)/100)
bt=mp.mpf(1); Nu=mp.mpf(0); De=mp.mpf(0)
for j in range(0,r):
    Nu+=j*(j+1)*rho**j*bt; De+=(j+1)*rho**j*bt
    bt*= (1-mp.mpf(j+1)/r)
print("tm_{r-1}(rho)/s =", Nu/De/100)
# r=171: rho_r, tm, Pc
def Pc_check(r):
    kr=int(mp.ceil(mp.mpf(r)**1.5+8*r)); rho=mp.mpf(kr)/(kr+r)
    bt=mp.mpf(1); Nu=mp.mpf(0); De=mp.mpf(0)
    for j in range(0,r):
        Nu+=j*(j+1)*rho**j*bt; De+=(j+1)*rho**j*bt
        bt*=(1-mp.mpf(j+1)/r)
    eb=Nu/De; k=kr
    Pc=k*(mp.mpf(1)/(2*r)-mp.mpf(1)/(3*r*r))-mp.mpf(5)/2+2*eb*(1-mp.mpf(1)/k)-mp.mpf(k)/(k-1)*(1+mp.sqrt(3*mp.pi*(r-1)/2))
    return kr,eb,Pc,Pc/mp.sqrt(r)
for r in [171,172,500,1000,9999]:
    print(r,Pc_check(r))
# check r=170 would fail?
print(170,Pc_check(170))
