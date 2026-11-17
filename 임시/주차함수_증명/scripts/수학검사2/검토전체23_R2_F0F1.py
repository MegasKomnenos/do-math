# R2 check: int F_0 = 0, int F_1 = 46 sqrt2 - 12, J leading integral = 3 sqrt(2 pi)
import numpy as np, math
# Gauss-Legendre nodes
def gl(a,b,n):
    x,w=np.polynomial.legendre.leggauss(n)
    return 0.5*(b-a)*x+0.5*(b+a), 0.5*(b-a)*w
# Dawson-type D(b)=e^{-b^2/2} int_0^b e^{v^2/2} dv ; BorldR(b) e^{-b^2/2} = 2-2 b D(b)
def Dw(b):
    v,w=gl(0,1,60)
    return sum(w_*b*math.exp((v_*b)**2/2-b*b/2) for v_,w_ in zip(v,w))
ninf=2/math.sqrt(math.pi)
rs,rw=gl(0,1,80)
def F0(z):
    s=0
    for r,w in zip(rs,rw):
        mu=1-r*r; Pq=mu*z*z+mu*mu*z**4/4; b=r*z
        # e^{mu z^2/2} * BorldR(b) = e^{mu z^2/2} e^{b^2/2}(2-2bD) = e^{z^2/2}(2-2bD)
        s+=w*r*r*Pq*(2-2*b*Dw(b))/math.sqrt(2*math.pi)
    return -ninf*z**4*math.exp(-z*z/2)*s
def F1(z):
    s=0
    for r,w in zip(rs,rw):
        mu=1-r*r; Pq=mu*z*z+mu*mu*z**4/4
        s+=w*r*r*math.exp(-(1+r*r)*z*z/2)*Pq*(4/3*r*r*z*z-2/3*r*z**4)
    return -ninf*z**4*s
I0=0;I1=0
for a,b in [(0,2),(2,4),(4,6),(6,9),(9,13),(13,20),(20,40)]:
    zs,zw=gl(a,b,80)
    for z,w in zip(zs,zw):
        I0+=2*w*F0(z)      # F0 even in z
        I1+=w*(F1(z)+F1(-z))
print('int F0',I0,'int F1',I1,'46sqrt2-12',46*math.sqrt(2)-12)
# J leading: int_R z^3 e^{-z^2/2} int_0^1 rho c_rho(z) drho dz, c=(2-rho^3)/3 z^3 - rho z
J=0
for a,b in [(0,2),(2,4),(4,6),(6,9),(9,13),(13,20)]:
    zs,zw=gl(a,b,60)
    for z,w in zip(zs,zw):
        inner=sum(w2*r*((2-r**3)/3*z**3-r*z) for r,w2 in zip(rs,rw))
        J+=2*w*z**3*math.exp(-z*z/2)*inner
print('J leading',J,'3sqrt(2pi)',3*math.sqrt(2*math.pi))
