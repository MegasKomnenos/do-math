# J7a: 보조정리 hermite-nu의 (나)(다)(라)(마) 수치·기호 검산
import math, sympy as sp
def dval(k,nu,theta=0.0):
    n=2*k+nu; y=k-theta; N=n+y+1; x=y/N**2
    u=1.0; logHe=math.log(N)  # j=1
    for j in range(2,n+1):
        u=1-(j-1)*x/u; logHe+=math.log(N)+math.log(u)
    d=N*u-n
    # M0 = e^{-k/2} He_n d /((n+d) p_n), p_n=(n+1)^{n-1}
    logM0=-y/2+logHe+math.log(d)-math.log(n+d)-(n-1)*math.log(n+1)
    return d, math.exp(logM0)
for k,nu in [(10000,1),(10000,19),(10000,100),(10000,300),(10000,600),(20000,600),(100000,600)]:
    d,M0=dval(k,nu)
    lb=4-(26+4*nu)/k; H2=506+97*nu+5*nu**2
    M0lb=4*math.sqrt(2)*(1-(23.75+2.5*nu)/k)
    U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
    U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
    V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
    r2=U2-V2/d; r4=U4-V4/d
    print(f"k={k} nu={nu}: d={d:.6f} lb={lb:.6f} d-lb={d-lb:.3e} (H2/k^2={H2/k**2:.3e}); M0={M0:.5f} M0lb={M0lb:.5f} ok={M0>=M0lb}; kM2/M0={k*r2:.4f} g_k={2-k*r2:.4f}; M4/M0*k^2={r4*k*k:.3f}")
# theta=1 check for (마): d_y[(n-y)^2+n] < n(n+1)
for k,nu,th in [(10000,600,1.0),(10000,1,1.0),(10000,600,0.5)]:
    d,_=dval(k,nu,th); n=2*k+nu; y=k-th
    print(f"(마) k={k} nu={nu} theta={th}: n(n+1)-d[(n-y)^2+n] = {n*(n+1)-d*((n-y)**2+n):.3f}  (20k={20*k})")
# symbolic: H series
w,nu_,th_=sp.symbols('w nu theta')
Nt=3+(nu_+1-th_)*w
xx=w*(1-th_*w)/Nt**2
xn=(2+(nu_-1)*w)*(1-th_*w)/Nt**2
g=sp.sqrt(1-4*xn); uo=(1+g)/2
C1=(1-uo)/g**2; C2=-(1-uo)*(2+uo)/g**5; C3=sp.Rational(5,2)*(1-uo)*(6+g-g**2)/g**8
uhat=uo+xx*C1+xx**2*C2+xx**3*C3
H=(Nt*uhat-2-nu_*w)/w
ser=sp.series(H,w,0,4).removeO()
for j in range(0,4):
    print("H_%d ="%j, sp.factor(sp.expand(ser.coeff(w,j))))
H3=sp.expand(ser.coeff(w,3))
for nuv,thv in [(600,0),(600,1),(1,0),(300,1)]:
    H2v=506+97*nuv+5*nuv**2+(168+16*nuv)*thv+12*thv**2
    H3v=float(H3.subs({nu_:nuv,th_:thv}))
    print(f"nu={nuv} theta={thv}: H2={H2v} H3={H3v:.1f} H2+H3/1e4={H2v+H3v/1e4:.1f}")
