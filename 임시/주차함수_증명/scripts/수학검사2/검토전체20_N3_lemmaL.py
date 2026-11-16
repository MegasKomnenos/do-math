import math
from fractions import Fraction as F
def integ(f,a,b,N=200000):
    h=(b-a)/N; s=0.5*(f(a)+f(b))
    for i in range(1,N): s+=f(a+i*h)
    return s*h
g=lambda i: (lambda y: y**i*math.exp(-y-y*y/2))
M=[integ(g(i),0,40) for i in range(6)]
M26=integ(g(2),0,6)
Ms=[max(g(i)(y/10000) for y in range(1,200000)) for i in range(6)]
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
print("M",[round(x,6) for x in M]); print("M2^(6)",round(M26,6)); print("M*",[round(x,6) for x in Ms])
print("C",[round(x,5) for x in (C1,C2,C3,C4)])
def L(r):
    s=math.sqrt(r); return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+math.exp(-0.5))/s+1/r)
def tm(r,rho):
    # tm_{r-1}(rho) = Nu/De with bt_j
    bt=1.0; Nu=0.0; De=0.0; j=0
    while True:
        Nu+=j*(j+1)*rho**j*bt; De+=(j+1)*rho**j*bt
        j+=1
        if j>r-1: break
        bt*=1-j/r
    return Nu/De
for r in (144,171,200,500,1000,5000):
    s=math.sqrt(r); rho=math.exp(-1/s)
    print(r, "L(r)=",round(L(r),5), "tm/s=",round(tm(r,rho)/s,5), "ok", tm(r,rho)/s>=L(r))
