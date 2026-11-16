# hermite-nu (라)(마): M_r/M_0 를 He 점화식으로 d의 일차 분수식으로 적어 U_r, V_r 와 대조
import sympy as sp
n,y,d,nu,k=sp.symbols('n y d nu k')
N=n+1+y
He={n-1:sp.Integer(1), n:n+d}
# He_{j-1}=(N He_j - He_{j+1})/(y j)
for i in range(2,7):
    j=n-i+1  # compute He_{j-1} from He_j, He_{j+1}
    He[n-i]=sp.simplify((N*He[n-i+1]-He[n-i+2])/(y*(n-i+1)))
def M(r):
    # n! [Y^n] (1-Y)^{r+1} exp(...)  = sum_i C(r+1,i)(-1)^i n!/(n-i)! He_{n-i}
    s=0
    for i in range(r+2):
        s+=sp.binomial(r+1,i)*(-1)**i*sp.ff(n,i)*He[n-i]
    return sp.simplify(s)
M0=M(0); print('M0 =',sp.factor(M0))
for r in (2,4):
    ratio=sp.simplify(M(r)/M0)
    # write as U - V/d
    ratio=sp.apart(sp.together(ratio),d)
    print('r=',r, sp.simplify(ratio))
    gen=sp.simplify(ratio.subs({y:k,n:2*k+nu}))
    gen=sp.apart(sp.together(gen),d)
    print('  at y=k,n=2k+nu:', sp.expand(gen))
