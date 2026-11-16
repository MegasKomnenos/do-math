import sympy as sp
k,nu,d,y,n,N=sp.symbols('k nu d y n N')
# backward recurrence: He_{j-1} = (N He_j - He_{j+1})/(y j).  Express He_{n-l} in terms of He_n=:A, He_{n-1}=:B.
A,B=sp.symbols('A B')
He={0:A,1:B}  # He[l] = He_{n-l}
for l in range(2,6):
    # He_{n-l} = (N He_{n-l+1} - He_{n-l+2})/(y (n-l+1))
    He[l]=sp.simplify((N*He[l-1]-He[l-2])/(y*(n-l+1)))
def M(i):
    s=0
    for l in range(0,i+2):
        s+=sp.binomial(i+1,l)*(-1)**l*sp.ff(n,l)*He[l]
    return s
ratio={}
for i in (2,4):
    r=sp.simplify(M(i)/M(0))
    r=r.subs(A,(n+d)*B)
    r=sp.simplify(r)
    ratio[i]=r
# general y formula for i=2
r2=sp.simplify(ratio[2].subs(N,n+y+1))
print("M2/M0 general:", sp.simplify(r2-(1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))))
# y=k, n=2k+nu
subs={y:k,n:2*k+nu,N:3*k+nu+1}
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
print("i=2 diff:", sp.simplify(ratio[2].subs(subs)-(U2-V2/d)))
print("i=4 diff:", sp.simplify(ratio[4].subs(subs)-(U4-V4/d)))
