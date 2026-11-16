import math, numpy as np
K=6; eps=0.05; b=1.3; LN2=math.log(2); ZETA32=2.612375348685488; S1b=math.sqrt(2/math.pi)
h0=25000**(-1/3)
def terms(h):
    v=h**-3.0; k0=K*h**-2-1.0     # k0 >= K v^{2/3}-1 ; all terms decreasing in k0
    A1=2/(1-eps)/math.sqrt(LN2); A2=(1-eps)**-3*LN2**-1.5*ZETA32; sq=math.sqrt(2/math.pi)
    S1=S1b*v**0.5; S2=(2*math.pi)**-0.5*(2/3)*(v+1)**1.5; y=v+1
    I32=2*(k0**-0.5-v**-0.5); I52=(2/3)*(k0**-1.5-v**-1.5); I12=2*(v**0.5-k0**0.5); I_12up=(2/3)*((v+1)**1.5-k0**1.5)
    I3=0.5*k0**-2.0; I2=1.0/k0; I72=0.4*k0**-2.5
    TA=1.5*sq*(I32+S1*I52+I12/(v+1)+S1*I32/(v+1))
    TB=b*sq/y*(I12+I_12up/(v+1)+2*S1*(I32+I12/(v+1))+S2*(I52+I32/(v+1)))
    TC=sq*A1*4*(1.5/y*v*I3+2*b/y**2*v**2*I2+2*b*S1/y**2*v**2*I3)
    TD=b/y**2*A2*v**1.5*sq*2*v*I52
    TE=b/y**2*A1**2*v*2*4*v**2*sq*I72
    e=math.exp(h**3/12)
    return e*TA/h, e*(TB+TC+TD+TE)/h
hs=np.linspace(1e-7,h0,4001)
ta=np.array([terms(h)[0] for h in hs]); tr=np.array([terms(h)[1] for h in hs])
print("TA monotone decreasing:",bool(np.all(np.diff(ta)<=1e-15)),"rest increasing:",bool(np.all(np.diff(tr)>=-1e-15)))
# partition bound
m=400; grid=np.linspace(0,h0,m+1); grid[0]=1e-9
sup=max(terms(grid[j-1])[0]+terms(grid[j])[1] for j in range(1,m+1))
print("grid max of sum:",(ta+tr).max()," rigorous partition sup bound:",sup, " TA(0+)~",terms(1e-9)[0])
