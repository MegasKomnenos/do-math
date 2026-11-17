# R2 check (fast, double precision): TV of G(w)=w^{-3/2}(e^{-phi w}-1+phi w) on [0,1] vs |phi|^2 e^{-Re phi}
import numpy as np
def G(phi,w):
    z=phi*w
    out=np.empty_like(z)
    small=np.abs(z)<1e-2
    zs=z[small]
    h=np.zeros_like(zs); term=np.ones_like(zs)/2  # sum_{m>=0} (-z)^m/(m+2)!
    for m in range(0,14):
        h+=term; term=term*(-zs)/(m+3)
    out[small]=h
    zl=z[~small]
    out[~small]=(np.exp(-zl)-1+zl)/zl**2
    return phi**2*np.sqrt(w)*out
t=np.linspace(0,1,2_000_001); w=t**2   # finer near 0
worst=0;arg=None
for r in [1e-3,1e-2,0.1,0.3,0.5,1,1.5,2,2.5,3,3.5,4,5,6,8,10,15,20,30,50,100,200]:
    for ang in [0,10,20,30,40,50,55,60]:
        phi=-r*np.exp(1j*np.radians(ang))
        g=G(phi,w); tv=np.abs(np.diff(g)).sum()
        b=abs(phi)**2*np.exp(-phi.real)
        if tv/b>worst: worst=tv/b;arg=(r,ang)
    print(r,'ratio at 0deg/60deg done; current worst',worst,arg)
