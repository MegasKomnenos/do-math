# S2b 검산 3: 정리 4-7·따름정리·보조정리 two-corrections·borel-tail-arc의 수치 주장
import mpmath as mp
from fractions import Fraction
mp.mp.dps=30
out=[]
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
out.append(f"a0={mp.nstr(a0,12)} a1={mp.nstr(a1,12)}; a3-a0={mp.nstr(mp.quad(lambda w: w**3*mp.e**(-w**3/3),[0,mp.inf])-a0,5)}")
# (나) exact fraction
F=Fraction
val=F(699,100)-F(7,2)-F(6*699,100)/31-F(75,100)/31-F(13*699,200)/961-F(12*699,100)/30000
out.append(f"(나) exact: {val} = {float(val):.6f}; claimed 495594511/240250000 = {float(F(495594511,240250000)):.6f}; equal? {val==F(495594511,240250000)}")
# (다)
w=F(698,100); k13=F(464159,10**7); k23=k13*k13; a0u=F(12879,10**4); a1u=F(939,1000)
v=w-F(7,2)-(4*w+F(1,2))*a0u*k13-F(13,2)*w*a1u*k23-12*w/10000
out.append(f"(다) bound with k^-1/3<=0.0464159: {float(v):.6f} (claimed >=1.6809); exact 10000^-1/3={mp.nstr(mp.mpf(10000)**(-mp.mpf(1)/3),8)}")
v2=w-F(7,2)-(4*w+F(1,2))*a0u*F(1,10000)**F(1,3) if False else None
# final assembly
A1=F(11,2)*F(39,100)*2-F(7,2); out.append(f"(가) assembly: {A1}={float(A1)}")
A2=F(5642,1000)*F(16809,10000)*F(39893,100000)-F(163,10000)-F(3554,1000); out.append(f"(나) assembly: {float(A2):.6f} (>0.213?)")
out.append(f"Bor(k)k^1.5 >= (2pi)^-1/2 (1-1/120000) = {mp.nstr((2*mp.pi)**-0.5*(1-mp.mpf(1)/120000),7)}; (2pi)^-1/2 e^{{-1/120000}}={mp.nstr((2*mp.pi)**-0.5*mp.e**(-mp.mpf(1)/120000),7)}")
# M0 lower bound: sqrt2 (1-3/k)^2 e^{-11/(4k)-10/k}(4-26/k) >= 4 sqrt2 (1-26/k)?
for k in [10000,30000,10**6]:
    lhs=mp.sqrt(2)*(1-mp.mpf(3)/k)**2*mp.e**(-mp.mpf(11)/(4*k)-mp.mpf(10)/k)*(4-mp.mpf(26)/k); rhs=4*mp.sqrt(2)*(1-mp.mpf(26)/k)
    out.append(f"M0 chain k={k}: lhs={mp.nstr(lhs,8)} rhs={mp.nstr(rhs,8)} ok={lhs>=rhs}")
# two-corrections numbers
out.append(f"46sqrt2-12={mp.nstr(46*mp.sqrt(2)-12,8)}; minus 5000/173+0.02 = {mp.nstr(46*mp.sqrt(2)-12-mp.mpf(5000)/173-mp.mpf(2)/100,6)}")
out.append(f"sqrt2/pi e^(1/10000)={mp.nstr(mp.sqrt(2)/mp.pi*mp.e**(mp.mpf(1)/10000),7)}; sqrt(2pi)={mp.nstr(mp.sqrt(2*mp.pi),7)}")
out.append(f"(가) J: 0.451*3*2.51+1678/30000+0.01={mp.nstr(mp.mpf('0.451')*3*mp.mpf('2.51')+mp.mpf(1678)/30000+mp.mpf('0.01'),6)}")
out.append(f"(나) D: 46sqrt2-12-54.6828 = {mp.nstr(46*mp.sqrt(2)-12-mp.mpf('54.6828'),6)}; times (1+1/9999) = {mp.nstr((46*mp.sqrt(2)-12-mp.mpf('54.6828'))*(1+mp.mpf(1)/9999),6)}")
out.append(f"(나) J: 0.4503*3*2.50663+1675.2/10000 = {mp.nstr(mp.mpf('0.4503')*3*mp.mpf('2.50663')+mp.mpf('1675.2')/10000,6)}")
for k in [30000,10000]:
    out.append(f"k={k}: k^5 e^-k/520={mp.nstr(mp.mpf(k)**5*mp.e**(-mp.mpf(k)/520),4)}; 130(k/256)^6 e^-k/512={mp.nstr(130*(mp.mpf(k)/256)**6*mp.e**(-mp.mpf(k)/512),4)}; y_k(G=1/16) 255k/131072-511/262144={mp.nstr(mp.mpf(255)*k/131072-mp.mpf(511)/262144,6)} vs k/520={k/520}")
# (나) arc with G=1/8: exponents -(k-1)f - y_k, y_k>=63k/8192-127/16384 ; check k^5 e^{-63k/8192} at k=10000
k=10000; out.append(f"k=10000: k^5 e^-(63k/8192)={mp.nstr(mp.mpf(k)**5*mp.e**(-mp.mpf(63)*k/8192),4)}; 130(k/64)^6 e^-k/128={mp.nstr(130*(mp.mpf(k)/64)**6*mp.e**(-mp.mpf(k)/128),4)}")
# T_R / T_I coefficient derivations
eps=mp.mpf(1)/173
out.append(f"beta^4 coef (G=1/16): 7/6+(13/12)(25/48)^2+(31/18)sqrt(2pi)/173 = {mp.nstr(mp.mpf(7)/6+mp.mpf(13)/12*(mp.mpf(25)/48)**2+mp.mpf(31)/18*mp.sqrt(2*mp.pi)*eps,6)} <= 1.5 ; beta^2: {mp.nstr(2+mp.mpf(2)/3*mp.mpf(25)/48,6)}<=2.4")
out.append(f"beta^4 coef (G=1/8, eps=1/100): {mp.nstr(mp.mpf(7)/6+mp.mpf(13)/12*(mp.mpf(13)/24)**2+mp.mpf(31)/18*mp.sqrt(2*mp.pi)/100,6)} <= 1.6 ; beta^2: {mp.nstr(2+mp.mpf(2)/3*mp.mpf(13)/24,6)}")
# phi bounds on vertical line: Z=1+i t, t=beta*eps in [0,G]; phi=-k(log Z+1-Z); with beta^2 = t^2 k ; bound |phi|<= c beta^2 -> |log Z+1-Z| <= c t^2
for G,c in [(mp.mpf(1)/16,mp.mpf(25)/48),(mp.mpf(1)/8,mp.mpf(13)/24)]:
    mx=0;mxim=0;mxre=0;ratio=0
    for t in mp.linspace(mp.mpf('1e-6'),G,400):
        Z=1+1j*t; ph=-(mp.log(Z)+1-Z)   # = phi/k
        mx=max(mx,abs(ph)/t**2); mxim=max(mxim,abs(mp.im(ph))/t**3); mxre=max(mxre,(mp.re(ph)+t**2/2)/t**4); ratio=max(ratio,abs(ph)/(-mp.re(ph)))
    out.append(f"G={mp.nstr(G,4)}: max|phi|/beta^2={mp.nstr(mx,5)} (claim {mp.nstr(c,5)}); max|Im phi|/(eps beta^3)={mp.nstr(mxim,5)} (claim 1/3); max(Re phi-phi0)/(eps^2 beta^4)={mp.nstr(mxre,5)} (claim 1/4); max|phi|/(-Re phi)={mp.nstr(ratio,5)} (<=2)")
# Dawson identity: Bor^ld_R(beta) e^{-beta^2/2} = 2 - 2 beta D(beta)
def Borld(phi): return 2+mp.quad(lambda w: w**-1.5*(1-mp.e**(-phi*w)),[0,1])
for b in [0.3,1.0,2.0]:
    b=mp.mpf(b); D=mp.e**(-b**2/2)*mp.quad(lambda v: mp.e**(v**2/2),[0,b])
    out.append(f"Dawson id beta={b}: {mp.nstr(Borld(-b**2/2)*mp.e**(-b**2/2)-(2-2*b*D),5)}; beta*D={mp.nstr(b*D,5)}")
# central cancellation: int F0 = 0 ; int F1 = 46 sqrt2 - 12 (normalized by n_inf = 2/sqrt(pi))
ninf=2/mp.sqrt(mp.pi)
def BorldR(b): 
    b=mp.mpf(b); D=mp.e**(-b**2/2)*mp.quad(lambda v: mp.e**(v**2/2),[0,b]); return (2-2*b*D)*mp.e**(b**2/2)
def F0(z):
    return -ninf*z**4*mp.e**(-z**2)*mp.quad(lambda r: r**2*mp.e**((1-r**2)*z**2/2)*((1-r**2)*z**2+(1-r**2)**2*z**4/4)*(2*mp.pi)**-0.5*BorldR(r*z),[0,1])
def F1(z):
    return -ninf*z**4*mp.e**(-z**2)*mp.quad(lambda r: r**2*mp.e**((1-r**2)*z**2/2)*((1-r**2)*z**2+(1-r**2)**2*z**4/4)*(mp.mpf(4)/3*r**2*z**2-mp.mpf(2)/3*r*z**4),[0,1])
mp.mp.dps=15
I0=2*mp.quad(F0,[0,2,4,8]); I1=2*mp.quad(F1,[0,2,4,8])
out.append(f"int F0 = {mp.nstr(I0,6)} (claim 0); int F1 = {mp.nstr(I1,8)} vs 46sqrt2-12={mp.nstr(46*mp.sqrt(2)-12,8)}")
# leading J integral 3 sqrt(2 pi)
IJ=mp.quad(lambda z: z**3*mp.e**(-z**2/2)*(mp.mpf(4)/15*z**3-z/3),[-mp.inf,mp.inf]); out.append(f"J leading = {mp.nstr(IJ,8)} vs 3sqrt(2pi)={mp.nstr(3*mp.sqrt(2*mp.pi),8)}")
# Ph_k bounds: Ph=(n+1)(t - arctan t), t=z/sqrt k; claim |Ph|<=0.667 eps |z|^3 ; |Ph - 2/3 eps z^3| <= eps^3(|z|^3/3+0.401|z|^5) for n in {2k-1,2k}, |z|<=sqrt(k)/8, k>=1000
worst1=0;worst2=0
for k in [1000,10000,30000]:
    for n in [2*k-1,2*k]:
        eps=1/mp.sqrt(k)
        for z in mp.linspace(mp.mpf('0.01'),mp.sqrt(k)/8,300):
            t=z*eps; Ph=(n+1)*(t-mp.atan(t))
            worst1=max(worst1,Ph/(eps*z**3)); worst2=max(worst2,abs(Ph-mp.mpf(2)/3*eps*z**3)/(eps**3*(z**3/3+mp.mpf('0.401')*z**5)))
out.append(f"Ph bounds: max Ph/(eps z^3)={mp.nstr(worst1,5)} (<=0.667); max ratio of second={mp.nstr(worst2,5)} (<=1)")
# Mag bound: |Mag - e^{-z^2}| <= eps^2/2 (z^2+z^4) e^{-(1-G^2/2) z^2}; Mag e^{mu z^2/2} e^{beta^2/2} <= e^{-0.49 z^2}
worst=0;worstm=0
for k in [1000,10000]:
    for n in [2*k-1,2*k]:
        for G in [mp.mpf(1)/16,mp.mpf(1)/8]:
            for z in mp.linspace(mp.mpf('0.01'),mp.sqrt(k)*G,300):
                Mag=(1+z**2/k)**(-(n+1)/mp.mpf(2))
                worst=max(worst,abs(Mag-mp.e**(-z**2))/((z**2+z**4)/(2*k)*mp.e**(-(1-G**2/2)*z**2)))
                # mu z^2/2 + beta^2/2 = (1-r^2) z^2/2 + r^2 z^2/2 = z^2/2 for any rho
                worstm=max(worstm,Mag*mp.e**(z**2/2)/mp.e**(-mp.mpf('0.49')*z**2))
out.append(f"Mag bounds: max ratio={mp.nstr(worst,5)} (<=1); max Mag e^(z^2/2)/e^(-0.49z^2)={mp.nstr(worstm,5)} (<=1)")
# Am bound: 1 - beta^4/(4k) <= Am <= 1
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_S2b_3_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
