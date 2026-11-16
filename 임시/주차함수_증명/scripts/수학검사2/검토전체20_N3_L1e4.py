import math
from mpmath import mp, quad, exp, sqrt, pi, findroot, mpf
mp.dps=30
g=lambda i: (lambda y: y**i*exp(-y-y*y/2))
M=[quad(g(i),[0,6,mp.inf]) for i in range(6)]
M26=quad(g(2),[0,6])
# max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0 -> y=(-1+sqrt(1+4i))/2
Ms=[g(i)((-1+sqrt(1+4*i))/2) if i>0 else mpf(1) for i in range(6)]
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
s=mpf(100)
L=(M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+exp(-mpf(1)/2))/s+1/s**2)
print("L(1e4)=",L, L>=mpf('0.845204'))
print("sqrt(3pi/2)=",sqrt(3*pi/2), "sqrt(pi/2)=",sqrt(pi/2))
print("1/2+2*0.845204-sqrt(3pi/2)=", mpf('0.5')+2*mpf('0.845204')-sqrt(3*pi/2))
