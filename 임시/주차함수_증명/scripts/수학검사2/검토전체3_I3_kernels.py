# I3: 5.2.3 핵 상하계(kernel-C-bound, kernel-bounds)와 Z^{(3)}_2 감싸기·꼬리 상계를 수치/기호로 대조
import sympy as sp
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=40
def Ren(m): return mp.mpf(m)**m*mp.e**(-m)/mp.factorial(m) if m>=1 else mp.mpf(1)
def cb(m): return mp.binomial(2*m,m)/mp.mpf(4)**m
o=1/mp.sqrt(2)
bad=[0]*8
for m in range(1,3001):
    r=Ren(m)/(o*cb(m))
    if not (1<=r<=1+mp.mpf(1)/(12*(2*m-1))): bad[0]+=1
    if not (r<=1+mp.mpf(1)/(22*m)): bad[1]+=1
    if not (r>=1+mp.mpf(1)/(25*(2*m-1))): bad[2]+=1   # (K1)
    W=(m+1)*mp.e**(-1)*(1+mp.mpf(1)/m)**m-m
    if not (mp.mpf(1)/2-mp.mpf(1)/(24*m)<=W<=mp.mpf(1)/2-mp.mpf(1)/(44*m)): bad[3]+=1
    E=(m+1)*Ren(m+1)-m*Ren(m)
    if not (o*cb(m)*(mp.mpf(1)/2-mp.mpf(1)/(12*(2*m-1)))<=E<=o*cb(m)/2): bad[4]+=1  # (K2) coeffs
    lo3=o*cb(m)*(mp.mpf(1)/2-mp.mpf(1)/(2*m-1)) if m>=2 else 0
    if not (lo3<=E<=o*cb(m)*(mp.mpf(1)/2+mp.mpf(2)/(2*m-1))): bad[5]+=1
    if not ((1-mp.mpf(1)/(6*m))/mp.sqrt(mp.pi*m)<=cb(m)<=1/mp.sqrt(mp.pi*m)): bad[6]+=1
print('violations [Ren/ocb, 1+1/22m, K1, W_m, K2, E-bounds, cb]:',bad[:7])
print('E const:',mp.nstr(mp.e**-1,8),'o/2',mp.nstr(o/2,8),'21o/40',mp.nstr(21*o/40,8),'4/11',4/11, '720/1957',720/1957)
# Z^{(3)}_2 = z(1+z)C^2+z^2 C E  <= (11/8)(1-z)^{-1} coefficientwise, and Lp sandwich, up to N
N=120
C=[mp.mpf(0)]+[Ren(m) for m in range(1,N+1)]
Ecoef=[Ren(1)]+[(m+1)*Ren(m+1)-m*Ren(m) for m in range(1,N+1)]
def mul(a,b):
    out=[mp.mpf(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j,y in enumerate(b):
            if i+j<=N: out[i+j]+=x*y
    return out
def shift(a,s): return [mp.mpf(0)]*s+a[:N+1-s]
C2=mul(C,C); Z32=[a+b for a,b in zip([x+y for x,y in zip(shift(C2,1),shift(C2,2))], shift(mul(C,Ecoef),2))]
print('Z3_2 <= 11/8 violations:', sum(1 for m in range(N+1) if Z32[m]>mp.mpf(11)/8))
# Laurent polys in w: represent as dict exponent->coef; expand (1-z)^{i/2} coefficients
def wpow(i):  # coefficients of (1-z)^{i/2}
    return [mp.binomial(mp.mpf(i)/2,m)*(-1)**m for m in range(N+1)]
def laurent_to_series(poly):
    out=[mp.mpf(0)]*(N+1)
    for i,c in poly.items():
        wp=wpow(i)
        for m in range(N+1): out[m]+=c*wp[m]
    return out
def lmul(p,q):
    out={}
    for i,a in p.items():
        for j,b in q.items(): out[i+j]=out.get(i+j,0)+a*b
    return out
def ladd(p,q):
    out=dict(p)
    for j,b in q.items(): out[j]=out.get(j,0)+b
    return out
qm={-1:mp.mpf(1),0:-mp.mpf(24)/25,1:-mp.mpf(1)/25}; qp={-1:mp.mpf(1),0:-mp.mpf(11)/12,1:-mp.mpf(1)/12}
em={-1:mp.mpf(1)/2,0:-mp.mpf(1)/12,1:mp.mpf(1)/12}; ep={-1:mp.mpf(1)/2,0:mp.mpf(1)/40}
one_m_w2={0:mp.mpf(1),2:-mp.mpf(1)}; two_m_w2={0:mp.mpf(2),2:-mp.mpf(1)}
Lm=ladd(lmul(lmul(one_m_w2,two_m_w2),lmul(qm,qm)), lmul(lmul(one_m_w2,one_m_w2),lmul(qm,em)))
Lp=ladd(lmul(lmul(one_m_w2,two_m_w2),lmul(qp,qp)), lmul(lmul(one_m_w2,one_m_w2),lmul(qp,ep)))
sm=laurent_to_series(Lm); spl=laurent_to_series(Lp)
v=sum(1 for m in range(N+1) if not (o**2*sm[m]-1e-25<=Z32[m]<=o**2*spl[m]+1e-25))
print('Lp sandwich violations (j=2):',v, 'min coef Lp-:',mp.nstr(min(sm),5),'min coef Lp+:',mp.nstr(min(spl),5))
# P_Theta, Q_Theta identities
Psi=sp.symbols('Psi',positive=True)
th=2*Psi/(1-Psi)
Lth=2*sum(Psi**(2*i+1)/(2*i+1) for i in range(4)); Uth=Lth+2*Psi**9/(9*(1-Psi**2))
up=1+th/2-th**2/44; um=1+th/2-th**2/24
numP=sp.simplify(th**2*sp.diff(up,Psi)/sp.diff(th,Psi)-(th-Lth)*up)
numQ=sp.simplify(th**2*sp.diff(um,Psi)/sp.diff(th,Psi)-(th-Uth)*um)
P=175-665*Psi+581*Psi**2-427*Psi**3+375*Psi**4-309*Psi**5+150*Psi**6+15*Psi**7
Q=945+42*Psi-252*Psi**2+66*Psi**3-108*Psi**4+42*Psi**5-60*Psi**6-10*Psi**7
print('P identity:',sp.simplify(numP-2*Psi**3*P/(1155*(1-Psi)**3))==0,' Q identity:',sp.simplify(numQ+Psi**4*Q/(945*(1-Psi)**3*(1+Psi)))==0)
print('min P,Q on [0,1/3]:',min(float(P.subs(Psi,t/300)) for t in range(101)),min(float(Q.subs(Psi,t/300)) for t in range(101)))
