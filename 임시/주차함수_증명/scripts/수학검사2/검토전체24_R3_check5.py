# R3 check 5: 5.4.2 lemma hat-normalization & cut-rep (ra) numerically for small k (formulas are exact identities for n<=2k-1).
import itertools, sys
import mpmath as mp
mp.mp.dps=20
def p(n): return 1 if n==0 else (n+1)**(n-1)
def caps(s):
    h=[]
    for i in range(len(s)):
        j=i-1
        while j>=0 and s[j]<s[i]: j-=1
        h.append(i-j if j>=0 else i+1)
    return h
def Kpoly(n,k):
    res=[0]*(n+1)
    for s in itertools.permutations(range(n)):
        w=1; z=0
        for x in caps(s):
            if x<=k: w*=x
            else: z+=1
        res[z]+=w
    return res
def A(n,l):
    return sum(__import__('math').prod(min(x,l+1) for x in caps(s)) for s in itertools.permutations(range(n))) if l>=0 else 0
k=int(sys.argv[1]) if len(sys.argv)>1 else 4
n=int(sys.argv[2]) if len(sys.argv)>2 else 6
r=n-k
K=Kpoly(n,k)
e_n=sum(c*i*(i-1)*k**(i-2) for i,c in enumerate(K) if i>=2)
B=sum(c*(k-1)**i for i,c in enumerate(K))-A(n,k-2)
print("k,n,r",k,n,r,"e_n",e_n,"B_{n,k-1}",B)
ku=mp.mpf(k)**(-mp.mpf(1)/3); xh=(r+1)*ku**2
Bor=lambda j: mp.exp(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def Btail(Zc): return 1-sum(mp.exp(-j*Zc)*(j*Zc)**(j-1)/mp.factorial(j) for j in range(1,k+1))
Af=lambda a:(1-mp.exp(1j*ku*a))/ku
def ph(a):
    ag=ku*a; pt=mp.exp(1j*ag); return k*(1j*ag+(1-pt)+(1-pt)**2/2)
def ph_series(a): return mp.nsum(lambda m:(2**(m-1)-2)*ku**(m-3)*(1j*a)**m/mp.factorial(m),[3,60])
def Bt(a):
    pt=mp.exp(1j*ku*a); return ku**2*Btail(pt)*mp.exp(k*(1-pt)**2/2)/Bor(k)
def Om_e(a):
    return 1j*ku*a-xh*a*a/2+mp.nsum(lambda m:(xh*ku**(m-2)-(2**(m-1)-2)*ku**(m-3))*(1j*a)**m/mp.factorial(m),[3,80])
def Om_e_closed(a):
    ag=ku*a; pt=mp.exp(1j*ag); return (n+1)*(pt-1)-1j*(n+1)*ag+1j*ag-k*(1-pt)**2/2
print("series vs closed Omega_e:",abs(Om_e(1.3)-Om_e_closed(1.3)),"ph:",abs(ph(0.9)-ph_series(0.9)))
Wr=[mp.quad(lambda v:v*v*Btail(1-v)*mp.exp(k*v*v/2)*(v*v/2)**j,[0,1])/Bor(k) for j in range(3)]
Wh=[Wr[j]/ku**(1+2*j) for j in range(3)]
Ik=mp.quad(lambda v:v/(1-v)*mp.exp(-v*v/2)*mp.exp(-k*(-mp.log(1-v)-v-v*v/2)),[0,1]); Ih=Ik/ku**2
def Ce(m,a): return mp.quad(lambda t:Af(t)**(2+2*m)*Bt(t)*1j*mp.exp(1j*ku*t),[0,a]) if a>0 else 0
def Cb(a): return mp.quad(lambda t:mp.exp((1-ku**3)*ph(t))*Af(t)*mp.exp(ku*Af(t))*1j*mp.exp(1j*ku*t),[0,a]) if a>0 else 0
def integ_e(a):
    c0,c1,c2=Ce(0,a),Ce(1,a),Ce(2,a)
    ch0=Wh[2]+2*ku*Wh[1]+c2/4+ku*c1; ch1=Wh[1]+ku*Wh[0]+c1/2+ku*c0; ch2=(Wh[0]+c0)/4
    Aa=Af(a); return Aa*mp.exp(Om_e_closed(a))*(ch0-Aa**2*ch1+Aa**4*ch2)
def integ_B(a):
    Aa=Af(a); return Aa*mp.exp(Om_e_closed(a)+ku**2*Aa**2/2)*(Ih+Cb(a))
top=mp.pi/ku
mp.mp.dps=15
Ue=mp.re(mp.quad(integ_e,mp.linspace(0,top,9)))
UB=mp.re(mp.quad(integ_B,mp.linspace(0,top,9)))
nn=mp.factorial(n)*mp.exp(n+1)/p(n)
pref=nn*Bor(k)/mp.pi*ku**4
print("e_n/p_n exact",mp.mpf(e_n)/p(n),"formula",pref*Ue)
print("B/p_n exact",mp.mpf(B)/p(n),"formula",pref*UB)
# cut-rep (ra): Bt = sqrt(2/pi) e^{rb_k} e^{ku A} e^{ph} hl
mp.mp.dps=20
rb=mp.loggamma(k+1)-(k+mp.mpf(1)/2)*mp.log(k)+k-mp.log(2*mp.pi)/2
a=mp.mpf('1.1'); pt=mp.exp(1j*ku*a); xi=pt*mp.exp(1-pt); Zh=(xi-1)/ku**2
def et(phi): return mp.e*phi*mp.exp(-phi*mp.cot(phi))/mp.sin(phi)
def nu_over(ph_hat):
    phi=ku**mp.mpf(1.5)*ph_hat
    if phi==0: return 0
    L=k*mp.log(et(phi)); lg=mp.diff(lambda t:mp.log(et(t)),phi)/phi
    qy=k*(et(phi)-1)
    return ph_hat**2*lg*mp.exp(-L)/(ku*qy-Zh)
hl=mp.quad(nu_over,mp.linspace(0,mp.pi*ku**(-mp.mpf(1.5)),13))
print("Bt direct",Bt(a),"via hl",mp.sqrt(2/mp.pi)*mp.exp(rb)*mp.exp(ku*Af(a))*mp.exp(ph(a))*hl)
