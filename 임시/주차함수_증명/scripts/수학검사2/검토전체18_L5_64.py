from fractions import Fraction as Fr
from math import comb
from mpmath import mp, mpf, exp, sqrt
mp.dps=25
k=mpf(3131)
u=lambda k: 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
print("u(3131)=",u(k), "factors", 3/mpf('0.35'), mpf('1.35')+1/k, (mpf('0.65')-1/k)**(-mpf(3)/2), k**(-mpf(1)/2))
print("u(3131)/2=",u(k)/2)
print("(2k)^(2/3)=",(2*k)**(mpf(2)/3)," 0.65k-1=",mpf('0.65')*k-1, " 1.35k=",mpf('1.35')*k, " 0.65k=",mpf('0.65')*k)
n=mpf(20000); print("witness bound n=20000:", mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3))
print("9*(3/2)^1.5=",9*mpf(1.5)**1.5, " *4/3=",9*mpf(1.5)**1.5*4/3)
print("1.99+0.59963 a^2+1.24847 a <= a^2+2 at a=15:", mpf('1.99')+mpf('0.59963')*225+mpf('1.24847')*15, "vs", 227)
# exact A table
NMAX=130
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1): A[0][l]=1
for nn in range(1,NMAX+1):
    for l in range(NMAX+1):
        A[nn][l]=sum(comb(nn-1,j)*min(j+1,l+1)*A[j][l]*A[nn-1-j][l] for j in range(nn))
p=[(nn+1)**(nn-1) if nn>0 else 1 for nn in range(NMAX+1)]
def s(m,yc): return Fr(A[m][yc-1],p[m]) if yc>=1 else Fr(0)
def c(m,Y): return s(m,Y+1)-s(m,Y)
def b(m,Y): return A[m][Y]-(A[m][Y-1] if Y>=1 else 0)
# (6.31) and ratio bound
from math import exp as fexp
viol=[];badratio=[]
for d in range(1,60):
    for m in range(max(2,2*d-1),NMAX):
        w=m-d
        L=(w+2)*(m+1)*c(m+1,w+1); R=w*(m+2)*c(m,w)
        if not L>R: viol.append((d,m))
        if R>0 and float(L/R) < fexp(1/(4*(w+1)*(w+2))): badratio.append((d,m,float(L/R)))
print("(6.31) violations:",viol[:5],len(viol)," ratio-bound failures:",badratio[:5],len(badratio))
# (6.36) and D-bound (가) exact for y up to 64
def x(t,y):
    if t==y: return Fr(-1,y)
    return Fr((y+1)*b(t-1,y)-(y-1)*b(t-1,y-1), t**(t-1))
viol36=[]
for y in range(2,65):
    for nn in range(y+1,2*y+2):
        P=sum(x(t,y) for t in range(y,nn+1))
        if y*P < -1-Fr(y*(y-1),nn)*c(nn-1,y-1): viol36.append((y,nn))
print("(6.36) violations:",viol36)
# pair-rearrange identity exact for k=2..64
bad=[]
for kk in range(2,65):
    phi=kk*sum(x(t,kk) for t in range(kk+1,2*kk+2))
    Ppair=kk*sum(Fr((kk+1),m+2)*c(m+1,kk)-Fr((kk-1),m+1)*c(m,kk-1) for m in range(kk,2*kk))
    Ups=Fr(kk*(kk-1)*b(2*kk,kk-1),(2*kk+1)*p[2*kk])
    if phi!=Ppair-Ups: bad.append(kk)
print("(6.29) identity failures:",bad)
# sanity: k c_{2k}(k-1) vs u(k) for small k (outside theorem range)
print("k c_2k(k-1) / u(k) at k=30,60:", [float(kk*c(2*kk,kk-1)/u(mpf(kk))) for kk in (30,60)])
# (6.28) chain for small k: b_{2k,k-1}<b_{2k,k}<=...<=b_{2k,k+floor(.35k)}
bad28=[kk for kk in range(8,65) if not (b(2*kk,kk-1)<b(2*kk,kk) and all(b(2*kk,j)<=b(2*kk,j+1) for j in range(kk,kk+int(0.35*kk))))]
print("(6.28) failures small k (참고):",bad28)
