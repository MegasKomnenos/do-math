import sympy as sp, mpmath as mp
# (4.9) symbolic
n,y,N,th=sp.symbols('n y N vartheta')
Hn=n+th; H1=sp.Integer(1)
H2=(N*H1-Hn)/((n-1)*y); H3=(N*H2-H1)/((n-2)*y)
num2=Hn-3*n*H1+3*n*(n-1)*H2-n*(n-1)*(n-2)*H3
ratio=sp.simplify((num2/th).subs(N,n+y+1))
target=1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*th)
print("(4.9) diff:",sp.simplify(ratio-target))
# numeric M_r/M_0 via Hermite ratios (mpmath, 60 digits)
mp.mp.dps=60
def Mratios(k,nu,y):
    n=2*k+nu; N=n+y+1
    # He_j ratios: u_j=He_j/(N He_{j-1}); compute He_{n-i}/He_n for i<=5
    u=[None, mp.mpf(1)]
    x=mp.mpf(y)/N**2
    for j in range(2,n+1):
        u.append(1-(j-1)*x/u[j-1])
    # He_{n-i}/He_{n-i+1} = 1/(N u_{n-i+1})
    rel=[mp.mpf(1)]
    for i in range(1,6):
        rel.append(rel[-1]/(N*u[n-i+1]))
    def coef(m): # [Y^n](1-Y)^m B * n!/He_n  = sum_i (-1)^i C(m,i) He_{n-i}/(n-i)! * n!/He_n
        s=mp.mpf(0)
        for i in range(0,m+1):
            s+= (-1)**i*mp.binomial(m,i)*rel[i]*mp.ff(n,i)
        return s
    M0=coef(1); M2=coef(3); M4=coef(5)
    th=N*u[n]-n
    return th, M2/M0, M4/M0
for k in [10000,30000,100000]:
    for nu in [0,-1]:
        th,r2,r4=Mratios(k,nu,k)
        print(k,nu,"theta",mp.nstr(th,12),"center",mp.nstr(4-(26+4*nu)/mp.mpf(k)+(506+97*nu+5*nu*nu)/mp.mpf(k)**2,12),
              "kM2/M0",mp.nstr(k*r2,10),"k^2M4/M0",mp.nstr(k*k*r4,10))
