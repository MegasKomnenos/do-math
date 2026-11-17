# R3 검산: 보조정리 hat-normalization의 두 식 e_n/p_n=(n_n Bor(k)/pi) ku^4 Ups_e, B_{n,k-1}/p_n=(...) Ups_B 를
# 작은 (n,k)에서 정의식 그대로의 수치 적분과 정확한 개수로 대조한다. Bt는 Borel 꼬리의 정의식(유한합)으로 계산하고,
# 보조정리 cut-rep (다)의 가지 절단 적분과도 대조한다.
import itertools, math, sys
import mpmath as mp
mp.mp.dps=25
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        d=i+1
        for j in range(i-1,-1,-1):
            if s[j]>s[i]: d=i-j; break
        h.append(d)
    return h
def counts(n,k):
    # e_n = K''_{n,k}(k), B_{n,k-1}=K_{n,k}(k-1)-A_{n,k-2}
    e=0;Kkm1=0;Akm2=0
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s); small=1; Zc=0
        for x in h:
            if x<=k: small*=x
            else: Zc+=1
        e+=small*Zc*(Zc-1)*k**(Zc-2) if Zc>=2 else 0
        Kkm1+=small*(k-1)**Zc
        Akm2+=math.prod(min(x,k-1) for x in h)
    return e,Kkm1-Akm2
n,k=int(sys.argv[1]),int(sys.argv[2])
r=n-k; ku=mp.mpf(k)**(-mp.mpf(1)/3); xh=(r+1)*ku**2
Bor=lambda j: mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def BorZ(j,Z): return mp.e**(-j*Z)*(j*Z)**(j-1)/mp.factorial(j)
def Btail(Z): return 1-sum(BorZ(j,Z) for j in range(1,k+1))
A=lambda a:(1-mp.e**(1j*ku*a))/ku
def ph(a):
    pt=mp.e**(1j*ku*a); return k*(1j*ku*a+(1-pt)+(1-pt)**2/2)
def Bt(a):
    pt=mp.e**(1j*ku*a); return ku**2*Btail(pt)*mp.e**(k*(1-pt)**2/2)/Bor(k)
def Om_e(a):
    ag=ku*a; pt=mp.e**(1j*ag)
    return (n+1)*(pt-1)-1j*n*ag-k*(1-pt)**2/2
def Om_e_series(a,M=60):
    s=1j*ku*a-xh*a*a/2
    for m in range(3,M): s+=(xh*ku**(m-2)-(2**(m-1)-2)*ku**(m-3))*(1j*a)**m/mp.factorial(m)
    return s
print("Omega_e closed form vs series at a=1.3:",mp.nstr(Om_e(1.3),12),mp.nstr(Om_e_series(mp.mpf('1.3')),12))
Wr=lambda j: mp.quad(lambda v:v**2*Btail(1-v)*mp.e**(k*v*v/2)*(v*v/2)**j,[0,1])/Bor(k)
Wh=[Wr(j)/ku**(1+2*j) for j in range(3)]
Ik=mp.quad(lambda v:v/(1-v)*mp.e**(-v*v/2)*mp.e**(-k*(-mp.log(1-v)-v-v*v/2)),[0,1]); Ih=Ik/ku**2
top=mp.pi/ku
# cumulative inner integrals on a grid via Gauss-Legendre panels
NP=int(sys.argv[3]) if len(sys.argv)>3 else 60
xs,ws=mp.gauss_quadrature(8,'legendre') if hasattr(mp,'gauss_quadrature') else (None,None)
import numpy as np
gx,gw=np.polynomial.legendre.leggauss(10)
edges=[top*i/NP for i in range(NP+1)]
def panel(f,a,b):
    return sum(mp.mpf(float(w))*f((a+b)/2+(b-a)/2*mp.mpf(float(x))) for x,w in zip(gx,gw))*(b-a)/2
fCe=[lambda a,m=m: A(a)**(2+2*m)*Bt(a)*1j*mp.e**(1j*ku*a) for m in range(3)]
fCb=lambda a: mp.e**((1-ku**3)*ph(a))*A(a)*mp.e**(ku*A(a))*1j*mp.e**(1j*ku*a)
# outer integral with inner cumulative evaluated at outer nodes: integrate inner from panel start to node with its own quadrature
cumCe=[mp.mpc(0)]*3; cumCb=mp.mpc(0); Ue=mp.mpc(0); Ub=mp.mpc(0)
for i in range(NP):
    a0,a1=edges[i],edges[i+1]
    for x,w in zip(gx,gw):
        a=(a0+a1)/2+(a1-a0)/2*mp.mpf(float(x))
        Ce=[cumCe[m]+panel(fCe[m],a0,a) for m in range(3)]
        Cb=cumCb+panel(fCb,a0,a)
        ch0=Wh[2]+2*ku*Wh[1]+Ce[2]/4+ku*Ce[1]
        ch1=Wh[1]+ku*Wh[0]+Ce[1]/2+ku*Ce[0]
        ch2=(Wh[0]+Ce[0])/4
        AA=A(a)
        Ue+=mp.mpf(float(w))*(a1-a0)/2*AA*mp.e**Om_e(a)*(ch0-AA**2*ch1+AA**4*ch2)
        Ub+=mp.mpf(float(w))*(a1-a0)/2*AA*mp.e**(Om_e(a)+ku**2*AA**2/2)*(Ih+Cb)
    cumCe=[cumCe[m]+panel(fCe[m],a0,a1) for m in range(3)]; cumCb+=panel(fCb,a0,a1)
pn=mp.mpf(n+1)**(n-1); nn=mp.factorial(n)*mp.e**(n+1)/pn
pref=nn*Bor(k)/mp.pi*ku**4
e,B=counts(n,k)
print("n=%d k=%d r=%d xhat=%s"%(n,k,r,mp.nstr(xh,6)))
print(" e_n/p_n exact =",mp.nstr(e/pn,15)," formula =",mp.nstr(pref*Ue.real,15))
print(" B/p_n  exact =",mp.nstr(B/pn,15)," formula =",mp.nstr(pref*Ub.real,15))
# cut-rep (다): Bor^tail_k(pt') vs branch-cut integral, with phi parametrisation
def et(phi): return mp.e*phi*mp.e**(-phi*mp.cot(phi))/mp.sin(phi)
for agp in (mp.mpf('0.3'),mp.mpf('1.1'),mp.mpf('2.5')):
    pt=mp.e**(1j*agp); xi=pt*mp.e**(1-pt)
    integ=mp.quad(lambda phi: phi*et(phi)**(-k-1)/(et(phi)-xi)*mp.diff(et,phi),[0,mp.pi/4,mp.pi/2,3*mp.pi/4,mp.pi-mp.mpf('1e-12')])
    print(" cut-rep(da) ag'=%s:"%mp.nstr(agp,3),mp.nstr(Btail(pt),12),mp.nstr(xi**(k+1)/(mp.pi*pt)*integ,12))
