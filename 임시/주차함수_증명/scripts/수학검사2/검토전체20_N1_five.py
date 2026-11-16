# 정리 2-40 다섯 몫 분해 + 명제 2-41 정수 꼴 수치 검산 (k=2..6, 2k+1<=n<=3k-1), 보조정리 b-top, delta_t=t^{t-1}x_t(k)
import sys,io
from math import comb, factorial
from fractions import Fraction as Fr
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
N=20
A={}
for l in range(0,N+1):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
def Af(n,l): return 0 if l<0 else A[(n,l)]
def b(n,l): return Af(n,l)-Af(n,l-1)
p=lambda m:(m+1)**(m-1) if m>0 else 1
def Ncal(l,t): return min(t,l+1)*Af(t-1,l)
def bT(t,l): return Ncal(l,t)-Ncal(l-1,t)
bad=0
for k in range(2,7):
    assert b(k,k-1)==p(k-1)==k**(k-2)
    for n in range(2*k+1,3*k):
        d=b(n,k)-b(n,k-1)
        Theta=comb(n,k)*k**(k-2)*Af(n-k,k-1)
        delta=lambda t:bT(t,k)-bT(t,k-1)
        FL=sum(comb(n,t)*delta(t)*Af(n-t,k-1) for t in range(k+1,2*k+2))
        BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
        KD=sum(comb(n,m+1)*p(n-1-m)*k*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        PAIR=Fr(0)
        for t1 in range(1,n):
            for t2 in range(1,n-t1+1):
                PAIR+=Fr(factorial(n),factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1,k)*bT(t2,k)+bT(t1,k-1)*bT(t2,k-1))*p(n-t1-t2)
        PAIR/=2
        if d!=-Theta+FL+BV+KD+PAIR: bad+=1; print('FAIL',k,n,d,-Theta+FL+BV+KD+PAIR)
        # delta_t = (k+1)b_{t-1,k}-(k-1)b_{t-1,k-1} 확인
        for t in range(k+1,n+1):
            if delta(t)!=(k+1)*b(t-1,k)-(k-1)*b(t-1,k-1): bad+=1; print('delta FAIL',k,t)
    print('k',k,'ok')
print('bad',bad)
