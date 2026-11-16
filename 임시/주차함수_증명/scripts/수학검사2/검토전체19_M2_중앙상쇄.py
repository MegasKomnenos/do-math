# 4.3절 두 보정의 선도 적분 확인: int F0 = 0 (중앙 상쇄), int F1 = 46 sqrt2 - 12, 그리고 20<=n<=120 에서 b_{n,k_n} < b_{n,k_n+1}.
import math
try:
    import numpy as np
    from scipy import integrate, special
    have=True
except Exception as e:
    have=False; print('scipy/numpy 없음', e)
if have:
    ninf = 2/math.sqrt(math.pi)
    def dawson_half(b):  # D(b) = e^{-b^2/2} int_0^b e^{v^2/2} dv = sqrt2 * dawsn(b/sqrt2)
        return math.sqrt(2)*special.dawsn(b/math.sqrt(2))
    def BorldR(b):
        return math.exp(b*b/2)*(2-2*b*dawson_half(b))
    def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
    def F0(z):
        inner,_=integrate.quad(lambda r: r*r*math.exp((1-r*r)*z*z/2)*Pq(z,r)*BorldR(r*z)/math.sqrt(2*math.pi),0,1)
        return -ninf*z**4*math.exp(-z*z)*inner
    def F1(z):
        inner,_=integrate.quad(lambda r: r*r*math.exp((1-r*r)*z*z/2)*Pq(z,r)*((4/3)*r*r*z*z-(2/3)*r*z**4),0,1)
        return -ninf*z**4*math.exp(-z*z)*inner
    I0,_=integrate.quad(F0,-12,12,limit=400); I1,_=integrate.quad(F1,-12,12,limit=400)
    print('int F0 =',I0,'(claimed 0)'); print('int F1 =',I1,'claimed 46sqrt2-12 =',46*math.sqrt(2)-12)
    # Bor^ld_R identity check at a point via direct integral
    b=1.3
    direct = 2+integrate.quad(lambda w: w**-1.5*(1-math.exp(b*b*w/2)),0,1)[0]
    print('BorldR direct',direct,'via Dawson',BorldR(b))
# rows up to 120: check b_{n,k_n} < b_{n,k_n+1} for 20<=n<=120
from math import comb, ceil
NMAX=120
A={}
for l in range(0,NMAX):
    A[(0,l)]=1
    for n in range(1,NMAX+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def b(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
bad=[n for n in range(20,NMAX+1) if not (b(n,ceil(n/2))<b(n,ceil(n/2)+1) and ceil(n/2)+1<=n-2)]
print('20<=n<=120 에서 b_{n,k_n}<b_{n,k_n+1} 어긋나는 n:', bad)
# also Q_L(n) for 3<=n<=15 (log-concavity after a decrease in left half) and all rows logconcave up to 120?
lc_fail=[n for n in range(1,NMAX+1) if not all(b(n,l)**2>=b(n,l-1)*b(n,l+1) for l in range(1,n-1))]
print('n<=120 로그오목 실패 n:', lc_fail[:5])
