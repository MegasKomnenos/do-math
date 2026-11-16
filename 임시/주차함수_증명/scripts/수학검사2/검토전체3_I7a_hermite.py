import sympy as sp
n,y,d,nu,k,th=sp.symbols('n y d nu k theta')
N=n+y+1
# He_{j-1}=(N He_j - He_{j+1})/(y j); set He_n=1? Use He_n = (n+d) He_{n-1}; set He_{n-1}=1
He={}
He[n]= n+d; He[n-1]=1
# backward: He_{j-1} = (N He_j - He_{j+1})/(y*j)
He[n-2]=sp.simplify((N*He[n-1]-He[n])/(y*(n-1)))
He[n-3]=sp.simplify((N*He[n-2]-He[n-1])/(y*(n-2)))
He[n-4]=sp.simplify((N*He[n-3]-He[n-2])/(y*(n-3)))
He[n-5]=sp.simplify((N*He[n-4]-He[n-3])/(y*(n-4)))
# M_r proportional to [Y^n](1-Y)^{r+1}E = sum_i C(r+1,i)(-1)^i He_{n-i}/(n-i)!  -> multiply by n!: sum_i C(r+1,i)(-1)^i He_{n-i} * n!/(n-i)! 
def M(r):
    s=0
    for i in range(r+2):
        s+=sp.binomial(r+1,i)*(-1)**i*He[n-i]*sp.ff(n,i)
    return sp.simplify(s)
M0=M(0); M2=M(2); M4=M(4)
ratio2=sp.simplify(M2/M0)
print("M2/M0 general y:", sp.simplify(ratio2 - (1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))))
# y=k, n=2k+nu: U_r - V_r/d
sub={y:k,n:2*k+nu}
U2=1+(2*nu+2)/k+nu*(nu+1)/k**2; V2=4+(4*nu+2)/k+nu*(nu+1)/k**2
print("r=2 check:", sp.simplify((M2/M0).subs(sub)-(U2-V2/d)))
U4=1+(4*nu+16)/k+(6*nu**2+30*nu+18)/k**2+(4*nu**3+17*nu**2+15*nu+2)/k**3+nu*(nu+1)**3/k**4
V4=4+(12*nu+38)/k+(13*nu**2+49*nu+22)/k**2+(6*nu**3+21*nu**2+17*nu+2)/k**3+nu*(nu+1)**3/k**4
print("r=4 check:", sp.simplify((M4/M0).subs(sub)-(U4-V4/d)))
# H expansion: w=1/k
w=sp.symbols('w')
Nk=3+(nu+1-th)*w
x=w*(1-th*w)/Nk**2
xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
g=sp.sqrt(1-4*xn)
ups=(1+g)/2
C1=(1-ups)/g**2; C2=-(1-ups)*(2+ups)/g**5; C3=5*(1-ups)*(6+g-g**2)/(2*g**8)
hat=ups+x*C1+x**2*C2+x**3*C3
H=(Nk*hat-2-nu*w)/w
ser=sp.series(H,w,0,3).removeO()
ser=sp.expand(ser)
print("H0:",sp.simplify(ser.coeff(w,0)))
print("H1:",sp.simplify(ser.coeff(w,1)))
print("H2:",sp.factor(sp.simplify(ser.coeff(w,2))))
