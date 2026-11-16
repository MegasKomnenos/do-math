# 검토전체6 L2: 보조정리 gauss-coeff의 (4.8)·(4.9)·M4/M0 식과 상하계를 정확 Hermite 수로 대조
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=40
def hermite(N,y,n):
    h0,h1=1,N
    hs=[h0,h1]
    for j in range(2,n+1):
        h0,h1=h1,N*h1-(j-1)*y*h0
        hs.append(h1)
    return hs
for k,nu in [(10000,0),(10000,-1),(30000,0),(30000,-1)]:
    n=2*k+nu; y=k; N=n+y+1
    H=hermite(N,y,n)
    th=Fr(H[n],H[n-1])-n
    center=4-Fr(26+4*nu,k)+Fr(506+97*nu+5*nu*nu,k*k)
    print(f"k={k} nu={nu}: theta={float(th):.12f} center={float(center):.12f} k^2*(theta-center)={float((th-center)*k*k):.4f}")
    num0=H[n]-n*H[n-1]
    num2=H[n]-3*n*H[n-1]+3*n*(n-1)*H[n-2]-n*(n-1)*(n-2)*H[n-3]
    r2=Fr(num2,num0)
    f49=(th*((n-y)**2+n)-n*(n+1))/(y*y*th)
    print("  M2/M0 =",float(r2)," (4.9)식 =",float(f49)," 일치:",r2==f49, " k*M2/M0=",float(r2*k), " 범위(-5,-4.99/-4.98):", -5<r2*k)
    # M4/M0
    from math import comb
    num4=sum((-1)**i*comb(5,i)*(mp.factorial(n)//mp.factorial(n-i) if False else 1)*0 for i in range(0))  # placeholder
    ff=[1]
    for i in range(1,6): ff.append(ff[-1]*(n-i+1))  # n!/(n-i)!
    num4=sum((-1)**i*comb(5,i)*ff[i]*H[n-i] for i in range(6))
    r4=Fr(num4,num0)
    if nu==0: f4=1+Fr(16,k)+Fr(18,k*k)+Fr(2,k**3)-(4+Fr(38,k)+Fr(22,k*k)+Fr(2,k**3))/th
    else: f4=1+Fr(12,k)-Fr(6,k*k)-(4+Fr(26,k)-Fr(14,k*k))/th
    print("  M4/M0 =",float(r4)," 본문식 =",float(f4)," 일치:",r4==f4," k^2*M4/M0=",float(r4*k*k))
    # M0 값
    logM0=-mp.mpf(k)/2+mp.log(mp.mpf(num0))-(n-1)*mp.log(n+1)
    M0=mp.e**logM0
    print("  M0 =",M0," 4sqrt2(1-26/k)=",4*mp.sqrt(2)*(1-mp.mpf(26)/k), " g_k=2-k M2/M0 =",float(2-r2*k))
