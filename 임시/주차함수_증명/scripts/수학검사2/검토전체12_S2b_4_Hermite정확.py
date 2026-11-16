# S2b 검산 4: k=10000, 30000에서 Hermite 수를 정확히 세어 (4.8)·M_2/M_0·M_4/M_0·M_0·g_k 확인
from fractions import Fraction
from math import comb, log, lgamma, exp, sqrt, pi
import mpmath as mp
mp.mp.dps=50
out=[]
def He_list(n,y,N):
    He=[1,N]
    for j in range(2,n+1):
        He.append(N*He[-1]-(j-1)*y*He[-2])
    return He
def check(k,nu,theta):
    n=2*k+nu; y=k-theta; N=n+y+1
    He=He_list(n,y,N)
    vt=Fraction(He[n],He[n-1])-n
    center=Fraction(4)-Fraction(26+4*nu+8*theta,k)+Fraction(506+97*nu+5*nu**2+(168+16*nu)*theta+12*theta**2,k**2)
    dev=(vt-center)*k*k
    # M_r numerators: n![Y^n](1-Y)^{r+1}B = sum_j (-1)^j C(r+1,j) n!/(n-j)! He_{n-j}
    def num(r):
        s=0;ff=1
        for j in range(r+2):
            s+=(-1)**j*comb(r+1,j)*ff*He[n-j]; ff*=(n-j)
        return s
    M0n,M2n,M4n=num(0),num(2),num(4)
    r2=Fraction(M2n,M0n); r4=Fraction(M4n,M0n)
    # M0 value: e^{-y/2} M0n / p_n
    logM0=-y/2+mp.log(mp.mpf(M0n))-(n-1)*mp.log(n+1)
    M0=mp.e**logM0
    gk=2-k*r2
    out.append(f"k={k} nu={nu} theta={theta}: vt={float(vt):.9f} (vt-center)k^2={float(dev):.5f}; k*M2/M0={float(k*r2):.6f}; k^2*M4/M0={float(k*k*r4):.5f}; M0={mp.nstr(M0,10)}; g_k={float(gk):.6f}; 4sqrt2(1-26/k)={4*sqrt(2)*(1-26/k):.6f}")
    return vt
for k in [10000]:
    for nu in [0,-1]:
        for theta in [0,1]:
            check(k,nu,theta)
for k in [30000]:
    for nu in [0,-1]:
        check(k,nu,0)
# contraction (나) numerics at k=10000, y=k, n=2k: |ups_j - hat(x_j)| <= 2e7 x^4 ?
k=10000;n=2*k;y=k;N=n+y+1
xx=mp.mpf(y)/N**2
def hat(t):
    gg=mp.sqrt(1-4*t);u=(1+gg)/2
    c1=(1-u)/gg**2;c2=-(1-u)*(2+u)/gg**5;c3=mp.mpf(5)/2*(1-u)*(6+gg-gg**2)/gg**8
    return u+xx*c1+xx**2*c2+xx**3*c3
ups=mp.mpf(1);maxerr=0
for j in range(2,n+1):
    ups=1-(j-1)*xx/ups
    err=abs(ups-hat((j-1)*xx)); maxerr=max(maxerr,err)
out.append(f"contraction: max|eps_j|/x^4 = {mp.nstr(maxerr/xx**4,6)} (bound 2e7); x={mp.nstr(xx,6)}; q=n x={mp.nstr(n*xx,6)}")
# (다) lower bound check at k=10000,n=2k,y=k
He=He_list(n,y,N)
q=n*xx; upq=(1+mp.sqrt(1-4*q))/2; U=N*upq; W=N*(2*upq-1)
lb=mp.sqrt(U/W)*U**n*mp.e**((N-U)**2/(2*y)-mp.mpf(11)/2*xx-350*n*xx**2)
out.append(f"(다): log He_n - log lb = {mp.nstr(mp.log(mp.mpf(He[n]))-mp.log(lb),8)} (>=0 expected); 11/2 x+350 n x^2 = {mp.nstr(mp.mpf(11)/2*xx+350*n*xx**2,6)} vs 10/k={10/k}")
l=U-n; out.append(f"l={mp.nstr(l,8)}, 2-2/k={2-2/k}")
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_S2b_4_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
