# J2: Dawson identity, central cancellation integrals, J leading integral (fixed-grid check, numpy only)
import numpy as np
def simps(y, x, axis=-1):
    y=np.moveaxis(y,axis,-1); h=x[1]-x[0]; n=len(x)-1
    return h/3*(y[...,0]+y[...,-1]+4*y[...,1:-1:2].sum(-1)+2*y[...,2:-1:2].sum(-1))
# D(b)=e^{-b^2/2} int_0^b e^{v^2/2} dv on a fine grid (cumulative Simpson via trapezoid, fine step)
vg=np.linspace(0,12,240001); cum=np.concatenate([[0],np.cumsum((np.exp(vg[1:]**2/2)+np.exp(vg[:-1]**2/2))/2*(vg[1]-vg[0]))])
def D(b): return np.exp(-b*b/2)*np.interp(np.abs(b),vg,cum)*np.sign(b)
def BorldR_int(b):
    i=np.linspace(1e-12,1,2000001); return 2+simps(i**-1.5*(1-np.exp(b*b*i/2)),i)  # singular at 0 ~ i^{-1/2}: crude
for b in (0.3,1.0,2.0,4.0):
    print("Dawson identity b=%g : %.6f  vs  %.6f" % (b, BorldR_int(b)*np.exp(-b*b/2), 2-2*b*D(b)))
bs=np.linspace(0.01,10,1000); print("max b*D(b) = %.6f" % max(float(b*D(b)) for b in bs))
def BorldR(b): return np.exp(b*b/2)*(2-2*b*D(b))
ninf=2/np.sqrt(np.pi); c=1/np.sqrt(2*np.pi)
z=np.linspace(-8,8,1601); r=np.linspace(0,1,401)
Z,R=np.meshgrid(z,r,indexing='ij'); MU=1-R*R; PQ=MU*Z*Z+MU*MU*Z**4/4
BR=BorldR(R*Z)
F0=-ninf*Z**4*np.exp(-Z*Z)*R*R*np.exp(MU*Z*Z/2)*PQ*c*BR
F1=-ninf*Z**4*np.exp(-Z*Z)*R*R*np.exp(MU*Z*Z/2)*PQ*(4/3*R*R*Z*Z-2/3*R*Z**4)
I0=simps(simps(F0,r,axis=1),z); I1=simps(simps(F1,r,axis=1),z)
print("int F0 = %.6f (expect 0)   int F1 = %.6f (expect 46sqrt2-12 = %.6f)" % (I0,I1,46*np.sqrt(2)-12))
CJ=(2-R**3)/3*Z**3-R*Z
IJ=simps(simps(Z**3*np.exp(-Z*Z/2)*R*CJ,r,axis=1),z)
print("J leading = %.6f (expect 3sqrt(2pi) = %.6f)" % (IJ,3*np.sqrt(2*np.pi)))
