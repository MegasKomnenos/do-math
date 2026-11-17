# R2 check: M_i/M_0 = U_i - V_i/vartheta (i=2,4) at y=k, n=2k+nu ; (ma) general y formula and coefficient 20
import sympy as sp
k,nu,vt,y,n,th=sp.symbols('k nu vartheta y n theta')
def ratio(i,nn,yy):
    N=nn+yy+1
    h={0:(nn+vt),1:sp.Integer(1)}   # He_{n-s} in units of He_{n-1}; s=0 -> n+vt, s=1 -> 1
    for s in range(2,i+2):
        # He_{j-1}=(N He_j - He_{j+1})/(y j) with j=n-s+1
        j=nn-s+1
        h[s]=sp.simplify((N*h[s-1]-h[s-2])/(yy*j))
    num=sum(sp.binomial(i+1,s)*(-1)**s*sp.ff(nn,s)*h[s] for s in range(i+2))
    den=h[0]-nn*h[1]
    return sp.simplify(num/den)
for i in (2,4):
    r=ratio(i,2*k+nu,k)
    r=sp.together(r)
    # write as U - V/vt
    num,den=sp.fraction(r)
    U=sp.simplify(sp.limit(r,vt,sp.oo))
    V=sp.simplify((U-r)*vt)
    print('i',i,'U',sp.expand(U)); print('   V',sp.expand(V))
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
print(sp.simplify(ratio(2,2*k+nu,k)-(U2-V2/vt)), sp.simplify(ratio(4,2*k+nu,k)-(U4-V4/vt)))
# (ma)
r2=ratio(2,n,y)
print('ma', sp.simplify(r2-(1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*vt))))
# difference n(n+1)-vt[(n-y)^2+n], with vt = 4 + H1/k + ..., n=2k+nu, y=k-theta
H1=-(26+4*nu)-8*th
H2=506+97*nu+5*nu**2+(168+16*nu)*th+12*th**2
nn=2*k+nu; yy=k-th
d=sp.expand(nn*(nn+1)-(4+H1/k+H2/k**2)*((nn-yy)**2+nn))
print('k^2 coeff',sp.simplify(d.coeff(k,2)),'k coeff',sp.simplify(d.coeff(k,1)))
