# H2: 중앙 상쇄 항등식 int F0 = 0, int F1 = 46 sqrt2 - 12, J 선도 적분 = 3 sqrt(2pi), 호 상계 수치 (numpy+mpmath)
import numpy as np
from mpmath import mp, erfi, mpf, exp as mexp, sqrt as msqrt, pi as mpi
mp.dps=20
ninf=2/np.sqrt(np.pi); c=1/np.sqrt(2*np.pi)
def BorldR(b):  # e^{b^2/2}(2-2 b D(b)), D(b)=e^{-b^2/2} sqrt(pi/2) erfi(b/sqrt2)
    b=mpf(b); D=mexp(-b*b/2)*msqrt(mpi/2)*erfi(b/msqrt(2))
    return float(mexp(b*b/2)*(2-2*b*D))
def simpson(y,x):
    h=x[1]-x[0]; return h/3*(y[0]+y[-1]+4*y[1:-1:2].sum()+2*y[2:-1:2].sum())
zs=np.linspace(0,14,2801); rs=np.linspace(0,1,801)
R,Z=np.meshgrid(rs,zs)
MU=1-R*R; PQ=MU*Z*Z+MU*MU*Z**4/4
vB=np.vectorize(BorldR)
# BorldR(r z) on grid: compute via vectorize (2.2M points too many) -> use interpolation on 1-D grid of beta in [0,14]
bg=np.linspace(0,14,14001); Bg=vB(bg)
BR=np.interp(R*Z,bg,Bg)
inner0=np.array([simpson(R[i]**2*np.exp(MU[i]*Z[i]**2/2)*PQ[i]*c*BR[i],rs) for i in range(len(zs))])
F0=-ninf*zs**4*np.exp(-zs**2)*inner0
inner1=np.array([simpson(R[i]**2*np.exp(MU[i]*Z[i]**2/2)*PQ[i]*(4/3*R[i]**2*Z[i]**2-2/3*R[i]*Z[i]**4),rs) for i in range(len(zs))])
F1=-ninf*zs**4*np.exp(-zs**2)*inner1
print("int F0 (even, x2) =",2*simpson(F0,zs),"  int F1 =",2*simpson(F1,zs),"  target 46sqrt2-12 =",46*np.sqrt(2)-12)
innerJ=np.array([simpson(rs*((2-rs**3)/3*z**3-rs*z),rs) for z in zs])
print("J leading (x2) =",2*simpson(zs**3*np.exp(-zs**2/2)*innerJ,zs)," target 3sqrt(2pi) =",3*np.sqrt(2*np.pi))
for k in (10000,30000):
    print("k",k,"k^5 e^{-k/520}=",k**5*np.exp(-k/520)," 130(k/256)^6 e^{-k/512}=",130*(k/256)**6*np.exp(-k/512), " k^5 e^{-63k/8192}=",k**5*np.exp(-63*k/8192))
print("(가) D lower:",46*np.sqrt(2)-12-5000/173-0.02)
print("(나) D lower:",46*np.sqrt(2)-12-54.6828, " J:",0.4503*3*2.50663+1675.2/10000)
print("(가) J:",0.451*3*2.51+1678/30000+0.01)
print("k>=10000 chain:",5.642*1.6809*0.39893-0.0163-3.554, " k>=30000:",5.5*0.39*2-3.5)
print("Bor lower const:",(2*np.pi)**-0.5*np.exp(-1/120000), (2*np.pi)**-0.5*(1-1/120000))
print("sum 7 parts (가):",176+2304+118+935+533+455+243," (나):",183.51+2303.07+203.57+983.74+920.70+454.86+418.83)
for k,G2,n in ((30000,1/256,59999),(10000,1/64,19999)):
    yk=n*np.log(np.sqrt(1+G2))-k*G2/2; print("y_k",k,yk, (255*k/131072-511/262144) if G2==1/256 else (63*k/8192-127/16384), k/520)
