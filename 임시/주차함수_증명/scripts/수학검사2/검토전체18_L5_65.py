from fractions import Fraction as Fr
from math import comb
from mpmath import mp, mpf, sqrt, exp, log, findroot
mp.dps=25
c=1/sqrt(2*mp.pi)
print("50.62/sqrt3130=",mpf('50.62')/sqrt(3130))
T=mpf(3130); exm=(T+1)/(2*T+1); print("ex_max=",exm," 2-exm-20/(9T)=",2-exm-20/(9*T)," kappa_d>=",mpf('1.498')+2*T/(2*T+1))
# m(0.55,2.4978)
tp=mpf('0.55'); ka=mpf('2.4978')
chi=(ka*tp+2+sqrt((ka*tp+2)**2-4*tp*ka))/(2*tp); print("chi*=",chi," m=",(chi**2-ka*chi)*exp(-tp*chi))
x=mpf(3132)/3130; print("Gamma_tp=",x/((1+x)**(1-tp)-1))
JI,YI,JX,YX=mpf('8.133'),mpf('10.301'),mpf('17.951'),mpf('23.462'); G=mpf('2.7323'); ms=mpf('0.8051')
a=3*c*(JI+c*YI); b=mpf('1.5')*G*ms*c*(JX+c*YX); print("14.653 ->",a," 35.952 ->",b," sum",a+b)
def u(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def v(k):
    k=mpf(k); vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**(-mpf(3)/2))-2*u(k)-mpf('50.62')/sqrt(k-1), 2*min(1,3*vp*io**(-mpf(3)/2)), 2*u(k), mpf('50.62')/sqrt(k-1)
for k in (3131,3998,3999,6667,10000): print("v(",k,")=",v(k))
print("24000/2263^1.5=",24000/mpf(2263)**1.5)
# exact checks: (6.41) identity, DD=-Delta^2 X, and (6.37) for small d via walk enumeration
NMAX=140
A=[[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1): A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+1):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
p=[(n+1)**(n-1) if n>0 else 1 for n in range(NMAX+1)]
def s(m,yc): return Fr(A[m][yc-1],p[m]) if yc>=1 else Fr(0)
def cc(m,Y): return s(m,Y+1)-s(m,Y)
def DD(m,y): return (y+2)*s(m+2,y+2)-2*(y+1)*s(m+1,y+1)+y*s(m,y)
bad=[]
for k in range(3,68):
    V=sum((k+1)*cc(m,k)-(k-1)*cc(m,k-1) for m in range(k,2*k+1))
    Bd=2-2*s(2*k+1,k+1)-(k-1)*(s(2*k+1,k+1)-s(2*k,k))-(k-1)*cc(2*k,k-1)
    if V!=Bd+sum(DD(m,k-1) for m in range(k,2*k)): bad.append(k)
print("(6.41) failures:",bad)
print("V_k(k) sign small k (참고):",[(k,float(sum((k+1)*cc(m,k)-(k-1)*cc(m,k-1) for m in range(k,2*k+1)))) for k in (10,30,60)])
# (6.37) exact: Bor ratios rational after e cancels: Bor(n)=e^{-n} n^{n-1}/n!
def borr(n): return Fr(n**(n-1), __import__('math').factorial(n))  # Bor(n)*e^n
def X_formula(d,y):
    # enumerate walks: sequences of steps with partial sums <= d-1
    tot=Fr(0)
    def rec(R,j,prob,Pi):
        nonlocal tot
        # at state R_j=R with j>=1 contribute R_j(y) q_j Pi_j
        if j>=1:
            q=d-R
            Rj=borr(y+q)/borr(y+d)   # Bor(y+q)/Bor(y+d) * e^{(d-q)}... handle e powers: Bor(y+q)/Bor(y+d)= borr(y+q)/borr(y+d)*e^{d-q}
            tot+=prob*Rj*q*Pi   # prob carries e^{-R} where R=d-q -> e^{-(d-q)} cancels e^{d-q}
        for e in range(1,d-R):
            rec(R+e,j+1,prob*borr(e),Pi*Fr(y,y+(d-R-e)))
    rec(0,0,Fr(1),Fr(1))
    return tot
badx=[]
for d in range(2,9):
    for y in range(max(1,d-2),d+6):
        if y*(1-s(y+d-1,y))!=X_formula(d,y): badx.append((d,y))
print("(6.37) exact failures d=2..8:",badx)
