# F3: tilted birthday mean, lemma-L(나) constants, Pc(k_r)>0 at sample r, suff-cond (가) numeric, hb_d coefficients, inverse-renewal recurrence
import mpmath as mp
from fractions import Fraction
import math
mp.mp.dps=40
def p(m): return (m+1)**(m-1) if m>=1 else 1
# hb_d(rho) via recurrence with tw_j; compare coefficient formula
def tw(j): return mp.mpf(1) if j==1 else mp.mpf((j-1)**(j-1))/mp.factorial(j)
def hb_coeffs(d):
    # polynomials in rho as coefficient lists
    H=[[mp.mpf(1)]]
    for dd in range(1,d+1):
        prev=H[dd-1]
        new=[mp.mpf(0)]*(dd+1)
        for i,c in enumerate(prev):
            new[i]+=c; new[i+1]+=c
        for j in range(2,dd+1):
            for i,c in enumerate(H[dd-j]): new[i]+=tw(j)*c
        H.append(new)
    return H[d]
ok=True
for d in range(1,9):
    co=hb_coeffs(d)
    for j in range(d+1):
        f=(j+1)*mp.mpf(d+1)**(d-j-1)/mp.factorial(d-j)
        if abs(co[j]-f)>1e-25: ok=False; print("hb coeff mismatch",d,j,co[j],f)
    if abs(sum(co)-mp.mpf(d+1)**d/mp.factorial(d))>1e-25: ok=False
print("hb_d coefficient formula d<=8:",ok)
# inverse-renewal: Gamma_d(y;n)/(n)_d == V_d(y/n,...,y/(n-d+1)) via tile recurrence
def Gamma(d,yv,n):
    G=[mp.mpf(1)]
    for dd in range(1,d+1):
        G.append(mp.binomial(n,dd)*p(dd)+yv*sum(mp.binomial(n-dd+j,j)*p(j)*G[dd-1-j] for j in range(dd)))
    return G[d]
def V(co):
    d=len(co); Vs=[mp.mpf(1)]
    for dd in range(1,d+1):
        s=(1+co[dd-1])*Vs[dd-1]+sum(tw(j)*Vs[dd-j] for j in range(2,dd+1))
        Vs.append(s)
    return Vs[d]
ok=True
for n in (10,17,30):
    for d in range(0,8):
        for yv in (mp.mpf(3),mp.mpf('7.5')):
            lhs=Gamma(d,yv,n)/mp.ff(n,d); rhs=V([yv/(n-i+1) for i in range(1,d+1)])
            if abs(lhs-rhs)>1e-20*abs(lhs): ok=False; print("inverse-renewal mismatch",n,d,yv)
print("inverse-renewal identity:",ok)
# suff-cond (가): V_r(k-1) <= (1+1/r)^r V_{r-1}(k), n=k+r
ok=True
for r in range(2,15):
    for k in range(r+1,r+40):
        n=k+r
        lhs=V([mp.mpf(k-1)/(n-i+1) for i in range(1,r+1)]); rhs=(1+mp.mpf(1)/r)**r*V([mp.mpf(k)/(n-i+1) for i in range(1,r)])
        if lhs>rhs: ok=False; print("(가) fail",r,k)
print("suff-cond (가) numeric:",ok)
# tm_d(1) <= sqrt(pi d/2)
def bd_tail(d,j): return mp.ff(d,j)/mp.mpf(d+1)**j
ok=all(sum(bd_tail(d,j) for j in range(1,d+1))<=mp.sqrt(mp.pi*d/2) for d in range(1,400))
print("tm_d(1)<=sqrt(pi d/2):",ok)
# lemma-L (나) constants and L(10^4)
f=lambda i: lambda yv: yv**i*mp.exp(-yv-yv**2/2)
M=[mp.quad(f(i),[0,mp.inf]) for i in range(6)]
M26=mp.quad(f(2),[0,6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y=(-1+sqrt(1+4i))/2
    ys=(-1+mp.sqrt(1+4*i))/2; return f(i)(ys)
Ms={i:Mstar(i) for i in range(2,6)}
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
def Lfun(r):
    s=mp.sqrt(r)
    return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+mp.exp(-mp.mpf(1)/2))/s+1/s**2)
print("M_i:",[mp.nstr(v,10) for v in M]," M2^(6):",mp.nstr(M26,10)," M*:",{i:mp.nstr(v,8) for i,v in Ms.items()})
print("L(10^4) =",mp.nstr(Lfun(10**4),10)," >= 0.845204:",Lfun(10**4)>=mp.mpf('0.845204'))
# direct tm_{r-1}(rho) and comparison with s*L(r) for r=10^4
def tm(d,rho):
    # bd_d(j) = (j+1) (d)_j/(d+1)^{j+1}; tilted mean = sum j rho^j bd / sum rho^j bd
    num=mp.mpf(0); den=mp.mpf(0); bt=mp.mpf(1)
    for j in range(0,d+1):
        w=(j+1)*rho**j*bt
        num+=j*w; den+=w
        bt*= (1-mp.mpf(j+1)/(d+1))
        if w<1e-60*den and j>10: break
    return num/den
r=10**4; s=mp.sqrt(r)
print("tm_{r-1}(e^{-1/s}) / s at r=10^4:",mp.nstr(tm(r-1,mp.exp(-1/s))/s,8)," L(r)=",mp.nstr(Lfun(r),8))
# Pc(k_r) at sample r with eb = tm_{r-1}(rho_r)
def Pc(k,r,eb): return k*(mp.mpf(1)/(2*r)-mp.mpf(1)/(3*r*r))-mp.mpf(5)/2+2*eb*(1-mp.mpf(1)/k)-mp.mpf(k)/(k-1)*(1+mp.sqrt(3*mp.pi*(r-1)/2))
for r in (160,170,171,172,200,500,1000,5000,9999,10000):
    kr=int(mp.ceil(mp.mpf(r)**1.5+8*r)); rho=mp.mpf(kr)/(kr+r); eb=tm(r-1,rho)
    print(f"r={r}: k_r={kr}, tm={mp.nstr(eb,8)}, Pc(k_r)={mp.nstr(Pc(kr,r,eb),8)}")
# also Pc with eb=0.845204*s for r=10^4
r=10**4; kr=int(mp.ceil(mp.mpf(r)**1.5+8*r)); print("Pc(k_r) with eb=0.845204 s at r=10^4:",mp.nstr(Pc(kr,r,mp.mpf('0.845204')*mp.sqrt(r)),8), " lower bound 0.0196 s+0.496=",0.0196*100+0.496)
# suff-cond (다) numeric: hg'''/hg'' <= (1+sqrt(3 pi d/2))/y for small d, y in [k-1,k+1]
ok=True
import sympy as sp
Y=sp.symbols('y')
def GammaSym(d,n):
    G=[sp.Integer(1)]
    for dd in range(1,d+1):
        G.append(sp.expand(sp.binomial(n,dd)*p(dd)+Y*sum(sp.binomial(n-dd+j,j)*p(j)*G[dd-1-j] for j in range(dd))))
    return G[d]
for r in (3,5,8):
    for k in (r+1,r+5,r+20):
        n=k+r
        for d in range(1,r):
            hg=sp.expand(Y*GammaSym(d,n)); h2=sp.diff(hg,Y,2); h3=sp.diff(hg,Y,3)
            for yv in (k-1,k,k+1):
                if sp.N(h3.subs(Y,yv)/h2.subs(Y,yv))> (1+math.sqrt(3*math.pi*d/2))/yv+1e-12: ok=False; print("(다) fail",r,k,d,yv)
            sdk=hg.subs(Y,k+1)-2*hg.subs(Y,k)+hg.subs(Y,k-1); sdk1=hg.subs(Y,k+2)-2*hg.subs(Y,k+1)+hg.subs(Y,k)
            if sp.N(sdk1/sdk)>math.exp((1+math.sqrt(3*math.pi*(r-1)/2))/(k-1))+1e-12: ok=False; print("(다) second fail",r,k,d)
print("suff-cond (다) numeric:",ok)
