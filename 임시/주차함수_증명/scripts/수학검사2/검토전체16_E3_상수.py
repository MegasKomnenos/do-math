# 검토전체16 E3: 5A의 수치 주장 재계산 (Cayley 비, m(n), L(10^4), 5.7 증명의 상수, Newton 인증 표본 등)
from fractions import Fraction as F
import math
from mpmath import mp, mpf, quad, exp, sqrt, pi, findroot, e as E
mp.dps = 30
out = []
# 보조정리 cayley-ratio: 1<=k<=9 values of cr_k(1+5/(2k)+2/k^2)
vals = []
for k in range(1, 10):
    cr = F(k+1, k)**(k-2)
    v = cr*(1+F(5,2*k)+F(2,k*k))
    vals.append(float(v))
out.append("cayley nine values: " + ", ".join(f"{v:.5f}" for v in vals) + f"; min>{87/32}? {min(vals) > 87/32}")
out.append(f"e < 65/24+1/100 = {65/24+0.01:.6f} < 87/32 = {87/32}: {math.e < 65/24+0.01 < 87/32}")
# m(n)
def mfrak(n):
    best = 170
    m = 171
    while m**1.5 + 9*m <= n:
        best = m; m += 1
    return best
out.append(f"m(20001)={mfrak(20001)}, m(50001)={mfrak(50001)}, m(20000)={mfrak(20000)}")
# 정리 5.2 (나) threshold check for n=20001..20010 equals m(n)
# L(10^4)
def M(i): return quad(lambda y: y**i*exp(-y-y*y/2), [0, mp.inf])
M26 = quad(lambda y: y**2*exp(-y-y*y/2), [0, 6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y - 1 - y = 0 -> y^2 + y - i = 0
    y0 = (-1+sqrt(1+4*i))/2
    return y0**i*exp(-y0-y0*y0/2)
C1 = 2*Mstar(2)+M(3)/2+M(5)/3
C2 = Mstar(3)/2+Mstar(5)/3+M(4)/2
C3 = Mstar(4)/2+M(3)/6
C4 = Mstar(3)/6
def L(r):
    s = sqrt(r)
    return (M26 - C1/s - C2/s**2 - C3/s**3 - C4/s**4)/(M(1)+(M(0)+exp(-0.5))/s+1/s**2)
out.append(f"L(10^4) = {L(10**4)}  (claim >= 0.845204)")
out.append(f"M0..M5 = {[float(M(i)) for i in range(6)]}, M2^(6)={float(M26)}, M*2..5={[float(Mstar(i)) for i in range(2,6)]}")
# 정리 5.5 (B) constants
s=100
br = 1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3
out.append(f"sqrt(3pi/2)={math.sqrt(3*math.pi/2):.6f}; 0.5+1.690408-sqrt(3pi/2)={0.5+1.690408-math.sqrt(3*math.pi/2):.6f}; bracket(s=100)={br:.6f}")
# 정리 5.7 constants
ratio = (9/16)*(169/400)*(144/121)*(88/1443)*(2.5+9/1058)**3
out.append(f"5.7 tail ratio bound = {ratio:.4f} (<0.28?) {ratio<0.28}")
out.append(f"rq* = {(13/20)*(1+3/529)/23:.5f} < 1/12={1/12:.5f}")
out.append(f"27.14^3={27.14**3:.1f}; 20001^(2/3)={20001**(2/3):.2f}; r0(20001)={math.floor(0.75*20001**(2/3))}; (149/200)^3={(149/200)**3:.5f} vs (16/25)^2={(16/25)**2:.5f}; (3/4)^3={(3/4)**3:.5f} vs (13/20)^2={(13/20)**2:.5f}")
out.append(f"(3/4)^1.5={(0.75)**1.5:.4f}; 27/(4*27.14)={27/(4*27.14):.4f}")
# kernel-bounds m=1
out.append(f"2sqrt2/e={2*math.sqrt(2)/math.e:.5f} > 26/25; 181/174={181/174:.5f}; sqrt2>181/128={math.sqrt(2)>181/128}; 312*4-374*2+25={312*4-374*2+25}")
# omitted-tail (나) constants
out.append(f"(12/5)(1+1/598)/sqrt(598)={(12/5)*(1+1/598)/math.sqrt(598):.4f}; (12/11)/(10e)={(12/11)/(10*math.e):.5f} vs 1/24={1/24:.5f}; (12/11)^1.5*(599/598)={(12/11)**1.5*599/598:.4f}; log10(1.15*598^3)={math.log10(1.15*598**3):.3f}; 598*log10(24)={598*math.log10(24):.1f}")
# 정리 5.12 premises
out.append(f"30001^(2/3)={30001**(2/3):.2f}; (5/12)sqrt(598)={(5/12)*math.sqrt(598):.3f}; rq values: {[1.2/math.sqrt(598),1.5/math.sqrt(833),1.8/math.sqrt(966),2.1/math.sqrt(2164),2.4/100]} all<1/16={1/16}")
out.append(f"(6/5)*20001 ^(2/3) = {(1.2*20001)**(2/3):.2f}; 1/(1+9/sqrt(598))={1/(1+9/math.sqrt(598)):.4f}; 1/sqrt(598)={1/math.sqrt(598):.5f}")
# cover-edge: 597^1.5+9*597
out.append(f"597^1.5+9*597={597**1.5+9*597:.1f}; 598^1.5+9*598={598**1.5+9*598:.1f}")
# 5.4.2 constants
out.append(f"10001^(-1/3)={10001**(-1/3):.6f}; 29*0.0015+0.00141+0.0015={29*0.0015+0.00141+0.0015:.5f}; 0.0015/1.25^12={0.0015/1.25**12:.3e}; 1-cos1={1-math.cos(1):.4f}; (9/5)^(2/3)={(9/5)**(2/3):.4f}; 10/2^(2/3)={10/2**(2/3):.4f}")
out.append(f"l_m: {[(2+1/m)*float(mp.zeta(2*m))/math.pi**(2*m) for m in (1,2,3)]} vs 1/2,1/36={1/36:.6f},1/405={1/405:.6f}")
out.append(f"x window: 0.64^(2/3)={0.64**(2/3):.4f}, 0.65^(2/3)={0.65**(2/3):.4f}")
# Newton 인증 표본: Gamma_d recursion, Nw_{r,d}(nv) for r=2..12, check Nw(0)>0 and forward differences >=0
def binom(n,k):
    return math.comb(n,k) if 0<=k<=n else 0
def Gamma(d, y, n):
    g=[F(1)]
    for dd in range(1,d+1):
        s = F(binom(n,dd)*((dd+1)**(dd-1) if dd>=1 else 1))
        t = F(0)
        for j in range(dd):
            pj = (j+1)**(j-1) if j>=1 else 1
            t += binom(n-dd+j,j)*pj*g[dd-1-j]
        g.append(s+y*t)
    return g[d]
e15 = sum(F(1, math.factorial(j)) for j in range(16))
def hg(d,y,n): return y*Gamma(d,y,n)
def sd(d,y,n): return hg(d,y+1,n)-2*hg(d,y,n)+hg(d,y-1,n)
fails=[]
for r in range(2, 13):
    for d in range(1, r):
        vals=[]
        for nv in range(0, 2*r+3):
            k=r+1+nv; n=k+r
            Nw = math.factorial(15)*(2*e15*k*k*(k+1)*Gamma(r-1,k+2,n)*sd(d,k,n)-(2*k*k+5*k+4)*Gamma(r,k-1,n)*sd(d,k+1,n))
            assert Nw.denominator==1
            vals.append(Nw.numerator)
        # forward differences at 0
        diffs=[]
        cur=vals[:]
        for i in range(2*r+3):
            diffs.append(cur[0])
            cur=[cur[t+1]-cur[t] for t in range(len(cur)-1)]
        if not (diffs[0]>0 and all(x>=0 for x in diffs[1:])): fails.append((r,d))
out.append(f"Newton check r=2..12: fails {fails}")
# inverse-renewal: gn_d recursion vs Gamma_d/(n)_d for small values; hb_d coefficient formula
tw = lambda j: F(1) if j==1 else F((j-1)**(j-1), math.factorial(j))
def falling(n,d):
    r=1
    for i in range(d): r*= (n-i)
    return r
bad=[]
for n in (8,11):
    for y in (F(3),F(5,2)):
        gn=[F(1)]
        for d in range(1,n):
            v=(1+y/(n-d+1))*gn[d-1]+sum(tw(j)*gn[d-j] for j in range(2,d+1))
            gn.append(v)
            if v != Gamma(d,y,n)/falling(n,d): bad.append((n,y,d))
out.append(f"inverse-renewal recursion mismatches: {bad}")
# hb_d(rho) coefficients: [rho^j]hb_d = (j+1)(d+1)^{d-j-1}/(d-j)!
import sympy
rho=sympy.symbols('rho')
hb=[sympy.Integer(1)]
for d in range(1,8):
    v=(1+rho)*hb[d-1]+sum(sympy.Rational((j-1)**(j-1), math.factorial(j))*hb[d-j] for j in range(2,d+1))
    hb.append(sympy.expand(v))
badh=[]
for d in range(1,8):
    P=sympy.Poly(hb[d],rho)
    for j in range(0,d+1):
        c=P.coeff_monomial(rho**j)
        want=sympy.Rational((j+1)*(d+1)**(d-j-1), math.factorial(d-j)) if j<d else 1
        if c!=want: badh.append((d,j,c,want))
out.append(f"hb_d coefficient mismatches: {badh}")
print("\n".join(out))
