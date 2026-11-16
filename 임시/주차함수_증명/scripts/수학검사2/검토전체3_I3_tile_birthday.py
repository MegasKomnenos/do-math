# I3: 5.2.2의 수치 주장 검산 — tm_d(1)<=sqrt(pi d/2), suff-cond (가)(다)의 부등식(작은 r), lemma-L 상수와 L(10^4)
from fractions import Fraction as Fr
from math import comb, factorial, pi, sqrt, exp
import mpmath as mp
def p(n): return (n+1)**(n-1) if n>=1 else 1
def Gamma(d,y,n):
    g=[Fr(1)]
    for dd in range(1,d+1):
        s=comb(n,dd)*p(dd)+y*sum(comb(n-dd+j,j)*p(j)*g[dd-1-j] for j in range(dd))
        g.append(Fr(s))
    return g[d]
# tm_d(1) = sum_{j>=1} prod_{i<=j}(1-i/(d+1))
bad=0
for d in range(1,3001):
    s=0.0; pr=1.0
    for j in range(1,d+1):
        pr*= (1-j/(d+1)); s+=pr
    if s>sqrt(pi*d/2): bad+=1
print('tm_d(1)<=sqrt(pi d/2) violations:',bad)
# (가) V_r(k-1) <= (1+1/r)^r V_{r-1}(k): Gamma_r(k-1;n)/(n)_r <= (1+1/r)^r Gamma_{r-1}(k;n)/(n)_{r-1}
def falling(n,d):
    out=1
    for i in range(d): out*=n-i
    return out
viol=0
for r in range(2,13):
    for k in range(r+1,r+40):
        n=k+r
        lhs=Fr(Gamma(r,k-1,n),falling(n,r)); rhs=Fr(k+0, 1)  # placeholder
        rhs=Fr(r+1,r)**r*Fr(Gamma(r-1,k,n),falling(n,r-1))
        if lhs>rhs: viol+=1
print('(가) violations:',viol)
# (다) hg'''/hg'' <= (1+sqrt(3 pi d/2))/y on [k-1,k+1], and sd ratio
import sympy as sp
Y=sp.symbols('y')
def GammaSym(d,n):
    g=[sp.Integer(1)]
    for dd in range(1,d+1):
        s=comb(n,dd)*p(dd)+Y*sum(comb(n-dd+j,j)*p(j)*g[dd-1-j] for j in range(dd))
        g.append(sp.expand(s))
    return g[d]
viol2=0; viol3=0
for r in range(2,9):
    for k in range(r+1,r+8):
        n=k+r
        for d in range(1,r):
            hg=sp.expand(Y*GammaSym(d,n)); h2=sp.diff(hg,Y,2); h3=sp.diff(hg,Y,3)
            for yy in [k-1,k-0.5,k,k+0.5,k+1]:
                if float(h3.subs(Y,yy))/float(h2.subs(Y,yy))>(1+sqrt(3*pi*d/2))/yy+1e-12: viol2+=1
            sd=lambda y0: hg.subs(Y,y0+1)-2*hg.subs(Y,y0)+hg.subs(Y,y0-1)
            if float(sd(k+1))/float(sd(k))>exp((1+sqrt(3*pi*(r-1)/2))/(k-1))+1e-12: viol3+=1
print('(다) first violations:',viol2,'second violations:',viol3)
# lemma-L constants
mp.mp.dps=30
f=lambda q: mp.quad(lambda y: y**q*mp.e**(-y-y*y/2),[0,mp.inf])
M=[f(q) for q in range(6)]
M26=mp.quad(lambda y: y**2*mp.e**(-y-y*y/2),[0,6])
Ms={q: (lambda ys: ys**q*mp.e**(-ys-ys*ys/2))((-1+mp.sqrt(1+4*q))/2) for q in range(2,6)}
C1=2*Ms[2]+M[3]/2+M[5]/3; C2=Ms[3]/2+Ms[5]/3+M[4]/2; C3=Ms[4]/2+M[3]/6; C4=Ms[3]/6
print('M0..M5',[mp.nstr(x,6) for x in M],'C',mp.nstr(C1,6),mp.nstr(C2,6),mp.nstr(C3,6),mp.nstr(C4,6))
def L(r):
    s=mp.sqrt(r)
    return (M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M[0]+mp.e**(-0.5))/s+1/s**2)
print('L(1e4)=',mp.nstr(L(10**4),8),'L(2e4)=',mp.nstr(L(2*10**4),6),'L(1e5)=',mp.nstr(L(10**5),6))
# actual tm_{r-1}(e^{-1/s})/s for r=1e4
def tm(r,rho):
    Nu=mp.mpf(0); De=mp.mpf(0); X=mp.mpf(1)
    for j in range(0,r):
        w=(j+1)*rho**j*X
        Nu+=j*w; De+=w
        X*= (1-mp.mpf(j+1)/r)
        if w<1e-40 and j>10*int(mp.sqrt(r)): break
    return Nu/De
for r in [10**4]:
    s=mp.sqrt(r); print('tm/s at r=1e4:',mp.nstr(tm(r,mp.e**(-1/s))/s,6))
# Pc bound at s=100
s=mp.mpf(100)
br=1/(3*s)+8/(3*s**2)+mp.mpf('2.507')/s**2+(1+mp.mpf('2.1709')*s)/s**3
print('bracket(100)=',mp.nstr(br,6),'coef=',mp.nstr(mp.mpf('0.5')+2*mp.mpf('0.845204')-mp.sqrt(3*mp.pi/2),8),'sqrt(3pi/2)=',mp.nstr(mp.sqrt(3*mp.pi/2),8),'sqrt(pi/2)=',mp.nstr(mp.sqrt(mp.pi/2),8))
