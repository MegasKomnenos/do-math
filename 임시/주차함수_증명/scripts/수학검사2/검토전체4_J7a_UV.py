# J7a: hermite-nu (라)(마)의 닫힌 꼴을 역방향 점화식으로 기호 검산
import sympy as sp
n,y,d,k,nu=sp.symbols('n y d k nu')
N=n+y+1
# He_n = (n+d) He_{n-1}; He_{j-1} = (N He_j - He_{j+1})/(y j)
He={}; He[n]=(n+d); He[n-1]=sp.Integer(1)
for i in range(1,5):
    j=n-i  # compute He_{j-1} = (N He_j - He_{j+1})/(y j)
    He[n-i-1]=sp.simplify((N*He[n-i]-He[n-i+1])/(y*(n-i)))
def coeff(r):
    # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i binom(r+1,i)(-1)^i n!/(n-i)! He_{n-i}
    s=0
    for i in range(0,r+2):
        ff=sp.prod([n-t for t in range(i)]) if i>0 else 1
        s+=sp.binomial(r+1,i)*(-1)**i*ff*He[n-i]
    return sp.simplify(s)
M0=coeff(0); M2=coeff(2); M4=coeff(4)
r2=sp.simplify(M2/M0); r4=sp.simplify(M4/M0)
# (마) general y
target2=1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d)
print("(마) M2/M0 identity:", sp.simplify(r2-target2)==0)
# (라) at y=k, n=2k+nu
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
sub={y:k,n:2*k+nu}
print("(라) r=2:", sp.simplify(r2.subs(sub)-(U2-V2/d))==0)
print("(라) r=4:", sp.simplify(r4.subs(sub)-(U4-V4/d))==0)
# 20k coefficient: n(n+1) - d[(n-y)^2+n] with d = 4-(26+4nu+8th)/k, y=k-th
th=sp.symbols('theta')
expr=sp.expand((n*(n+1)-(4-(26+4*nu+8*th)/k)*((n-y)**2+n)).subs({n:2*k+nu,y:k-th}))
print("diff poly in k:", sp.collect(expr,k))
