# R12 review check: D.window-mass-env test function values, integral 0.744, table facts
import sys, json, math, os
import numpy as np
work = sys.argv[1]
design = json.load(open(os.path.join(work,'design.json')))
print({k:design[k] for k in design if not isinstance(design[k],(list,dict))})
wK = np.load(os.path.join(work,'wKrig.npy')); xK=np.load(os.path.join(work,'xKrig.npy'))
print('len wK',len(wK),'xK last',xK[-1], 'wK[0]',wK[0])
K=design['K']; h=K**(-2/3); n=len(wK); xi=h*np.arange(n)
def ramp(t):
    return np.where(t<=-0.1,0.0,np.where(t>=0.1,t,(t+0.1)**2/0.4))
g=np.minimum(1.0,design['eta0']+design['eta1']*ramp(xi-design['x1']))
y=(1-g)*wK
print('monotone',bool(np.all(np.diff(y)<0)))
try:
    from scipy.interpolate import PchipInterpolator
    Om=PchipInterpolator(xi,y)
    print('Omega at 0,0.5,1,2,3,4,6:',[round(float(Om(t)),4) for t in (0,0.5,1,2,3,4,6)])
    s=np.linspace(0,6,600001); v=Om(s)*np.sqrt(2*s/math.pi)
    print('integral',np.trapz(v,s))
    d=Om.derivative()(s); print('max|Om\'|',np.abs(d).max())
except Exception as e:
    print('scipy unavailable',e)
qx=np.load(os.path.join(work,'qenv_fix_x.npy')); qv=np.load(os.path.join(work,'qenv_fix_v.npy'))
print('table len',len(qx),len(qv),'x[0],x[1],x[-1]',qx[0],qx[1],qx[-1],'v[0],v[-1]',qv[0],qv[-1])
lin=np.linspace(0,6.0005,12002)
print('x == linspace first 12001',bool(np.all(qx==lin[:len(qx)])), 'max|x-i/2000|',np.abs(qx-np.arange(len(qx))/2000).max())
print('max slope of T-hat',np.abs(np.diff(qv)).max()*2000,'TV of T\'',np.abs(np.diff(np.diff(qv)*2000)).sum())
print('12927/K^(2/3)',12927*h,'12926',12926*h)
# own PCHIP (equal spacing): interior slopes = harmonic mean of neighbouring secants
D=np.diff(y)/h
d=np.zeros(n); d[1:-1]=2*D[:-1]*D[1:]/(D[:-1]+D[1:])
d[0]=(3*D[0]-D[1])/2; d[-1]=(3*D[-1]-D[-2])/2
def Om(t):
    t=np.asarray(t,dtype=float); i=np.minimum((t/h).astype(int),n-2); u=(t-i*h)/h
    h00=2*u**3-3*u**2+1; h10=u**3-2*u**2+u; h01=-2*u**3+3*u**2; h11=u**3-u**2
    return h00*y[i]+h10*h*d[i]+h01*y[i+1]+h11*h*d[i+1]
print('Omega at 0,0.5,1,2,3,4,6:',[round(float(Om(t)),4) for t in (0,0.5,1,2,3,4,6)])
s=np.linspace(0,6,1200001); v=Om(s)*np.sqrt(2*s/math.pi)
print('integral',float(np.sum((v[1:]+v[:-1])/2)*(s[1]-s[0])))
