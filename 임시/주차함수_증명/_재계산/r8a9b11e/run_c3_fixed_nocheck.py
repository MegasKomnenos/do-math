# Driver: runs c3_iv_fixed.py's main loop WITHOUT its check_against_float() (that assert compares with the old float formula
# of c3sup.py, which has the pre-fix first TC term 1.5/y*v*I3; the fixed first term is 1.5/y*v^2*I3).
# Also checks the fixed total(h) against the float formula with v**2 in the first TC term.
import sys, math, time, importlib.util
t0=time.time()
spec = importlib.util.spec_from_file_location('c3f', r'C:\math\임시\주차함수_증명\_재계산\r8a9b11e\c3_iv_fixed.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from mpmath import iv, mp, mpf
NCELL = int(sys.argv[1])
# float check with corrected first TC term
K=6; e_=0.05; b_=1.3; L=math.log(2); Z=2.612375348685488; S=math.sqrt(2/math.pi)
for hf in [0.005,0.02,0.0342]:
    v=hf**-3.0; k0=K*hf**-2-1.0
    A1f=2/(1-e_)/math.sqrt(L); A2f=(1-e_)**-3*L**-1.5*Z
    S1=S*v**0.5; S2=(2*math.pi)**-0.5*(2/3)*(v+1)**1.5; y=v+1
    I32=2*(k0**-0.5-v**-0.5); I52=(2/3)*(k0**-1.5-v**-1.5); I12=2*(v**0.5-k0**0.5)
    I_12up=(2/3)*((v+1)**1.5-k0**1.5); I3=0.5*k0**-2.0; I2=1.0/k0; I72=0.4*k0**-2.5
    TA=1.5*S*(I32+S1*I52+I12/(v+1)+S1*I32/(v+1))
    TB=b_*S/y*(I12+I_12up/(v+1)+2*S1*(I32+I12/(v+1))+S2*(I52+I32/(v+1)))
    TC=S*A1f*4*(1.5/y*v**2*I3+2*b_/y**2*v**2*I2+2*b_*S1/y**2*v**2*I3)
    TD=b_/y**2*A2f*v**1.5*S*2*v*I52
    TE=b_/y**2*A1f**2*v*2*4*v**2*S*I72
    f=math.exp(hf**3/12)*(TA+TB+TC+TD+TE)/hf
    g=m.total(iv.mpf(hf))
    print(f"  check(v^2 first TC term) h={hf}: float {f:.10f}  interval mid {mp.nstr(g.mid,11)}  relerr {abs(f-float(g.mid))/f:.2e}")
best=mpf(0); arg=None
for i in range(NCELL):
    a=m.H0*i/NCELL; c=m.H0*(i+1)/NCELL
    t=m.total(iv.mpf([a.a,c.b]))
    if t.b>best: best=mpf(t.b); arg=i
print(f"C_III <= {mp.nstr(best,8)}  (sup over (0, 0.0342] by {NCELL} interval cells; worst cell {arg})")
print(f"elapsed {time.time()-t0:.1f}s")
