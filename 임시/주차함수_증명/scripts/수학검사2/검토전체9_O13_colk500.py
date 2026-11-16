from math import ceil, factorial, exp, log
from fractions import Fraction
# integer inequality
L=10**21*400**10; R=17**21*123**10
print("L",L,"R",R,L>R, float(L), float(R))
# comparison counts
def B(k): return (k*k+3)//4 if k%2 else k*k//4  # ceil(k^2/4)
def B2(k):
    import math; return math.ceil(k*k/4)
dd1=sum(2*B2(k)-2*k for k in range(121,161)); dd2=sum(2*B2(k)-2*k for k in range(161,501))
rr1=sum(B2(k)+1 for k in range(121,161)); rr2=sum(B2(k)+1 for k in range(161,501))
print("direct",dd1,dd2,"ratio",rr1,rr2)
# c formula
for k in (121,500): print(k, 0.34+0.65*log(k))
# verify recurrences for g,h,e with exact rationals: A_{n,y-1} via last-car recurrence
def A_table(y,N):
    # A[n] = A_{n,y-1}: parking functions length n with max displacement <= y-1
    # last car recurrence: n e_n = sum_{j=0}^{n-1} min(j+1,y) e_j e_{n-1-j}, e_n=A_n/n!
    e=[Fraction(1)]
    for n in range(1,N+1):
        s=sum(min(j+1,y)*e[j]*e[n-1-j] for j in range(n))
        e.append(s/n)
    return e
def check(y,N,xx=Fraction(1)):
    e=A_table(y,N)
    # scaled
    es=[e[n]*xx**n for n in range(N+1)]
    a0=[Fraction((m+1)**(m-1), factorial(m)) if m>0 else Fraction(1) for m in range(N+1)]
    f=[Fraction(0)]+[Fraction(m**(m-1),factorial(m))*xx**m if m<=y else Fraction(0) for m in range(1,N+1)]
    g=[Fraction(1)]
    for n in range(1,N+1):
        g.append(sum(j*f[j]*g[n-j] for j in range(1,min(y,n)+1))/n)
    # check g_n = a0_n x^n for n<=y
    for n in range(0,min(y,N)+1):
        assert g[n]==a0[n]*xx**n,(n,g[n],a0[n])
    h=[Fraction(0)]
    for n in range(1,N+1):
        s=y*xx*sum(a0[j-1]*xx**(j-1)*h[n-j] for j in range(1,min(y,n)+1))
        if n>=y+1: s+=y*xx*g[n-1]
        h.append(s/n)
    # e = g/(1-h): e_n = g_n + sum_{j=1}^n h_j e_{n-j}
    for n in range(0,N+1):
        rhs=g[n]+sum(h[j]*es[n-j] for j in range(1,n+1))
        assert rhs==es[n],(y,n,rhs,es[n])
    # also check h_n = [x^n](1 - g/e)
    # compute 1 - g/e series: q=g/e
    q=[]
    for n in range(N+1):
        q.append((g[n]-sum(q[j]*es[n-j] for j in range(n)))/es[0])
    for n in range(N+1):
        assert h[n]==((1 if n==0 else 0)-q[n]),(n,h[n],q[n])
    print("ok y=",y,"N=",N)
for y in (2,3,5,7):
    check(y,30, Fraction(3,7))
# second difference identity
y=6;N=25;xx=Fraction(2,5)
E={yy:A_table(yy,N) for yy in (y-1,y,y+1)}
for n in range(1,N+1):
    lhs=(E[y+1][n]-2*E[y][n]+E[y-1][n])*xx**n
    # d_{n,k}= A_{n,k}-2A_{n,k-1}+A_{n,k-2} with k=y : A_{n,k}=A_table(k+1)
    d=(E[y+1][n]-2*E[y][n]+E[y-1][n])*factorial(n)
    assert lhs==xx**n*d/factorial(n)
print("second diff ok")
