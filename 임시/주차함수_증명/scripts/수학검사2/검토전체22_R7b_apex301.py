# 검토전체22 R7b: 정리 apex-positive (7.12)를 k=301, n=904..906에서 정확 정수로 세어 비교
from fractions import Fraction as F
from math import comb, sqrt
import time
k=301; nmax=906
t0=time.time()
A={}
for l in (k-2,k-1,k):
    a=[1]
    for m in range(1,nmax+1):
        row=0
        c=1  # comb(m-1,j-1)
        for j in range(1,m+1):
            row+=c*min(j,l+1)*a[j-1]*a[m-j]
            c=c*(m-j)//j
        a.append(row)
    A[l]=a
print('built', time.time()-t0)
def p(n): return (n+1)**(n-1) if n>=1 else 1
Ak=A[k-1]
def b(m,l): return A[k][m]-A[k-1][m] if l==k else A[k-1][m]-A[k-2][m]
def Pk(m,j): return F(min(j,k)*comb(m-1,j-1)*Ak[j-1]*Ak[m-j],Ak[m])
def P(m,j): return F(j*comb(m-1,j-1)*p(j-1)*p(m-j),p(m))
for n in (904,905,906):
    apex=F(1,k)*(sum(Pk(n,j)*F(b(j-1,k)+b(j-1,k-1),Ak[j-1]) for j in range(n-k+1,n+1))-Pk(n,k)*(1-F(b(n-k,k-1),Ak[n-k])))
    ratio=float(apex/(P(n,k)/k))
    # hazard at N=n-1-U
    hzmin=min(float(1-F(Ak[N+1]*p(N),Ak[N]*p(N+1))) for N in range(n-301,n))
    print('n=%d apex/(P_n(k)/k)=%.4f  text lower=%.4f  min hz*2k over U<=300 = %.4f' % (n, ratio, 0.528*sqrt(k)-151/k-1, hzmin*2*k))
