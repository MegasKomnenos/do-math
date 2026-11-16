# F2 검산: 행 b_{n,l} (n<=80)의 로그오목성, n=80의 첫 실패, n<=10의 증인 위치
from math import comb
N=80
# A[n][l] = 최대 변위 <= l 인 길이 n 주차함수 수 (정리 2.6 마지막 차 재귀)
A=[[0]*(N+1) for _ in range(N+1)]
for l in range(N+1):
    A[0][l]=1
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
def row(n):
    return [A[n][0]]+[A[n][l]-A[n][l-1] for l in range(1,n)]
def logconcave(b):
    return all(b[i]**2>=b[i-1]*b[i+1] for i in range(1,len(b)-1))
def unimodal_witnesses(b):
    m=max(b); W=[i for i,v in enumerate(b) if v==m]
    inc=all(b[i]<=b[i+1] for i in range(W[0]))
    dec=all(b[i]>=b[i+1] for i in range(W[-1],len(b)-1))
    return (inc and dec), W
for n in range(1,N+1):
    b=row(n)
    assert sum(b)==(n+1)**(n-1), n
    assert all(v>0 for v in b), n
    lc=logconcave(b)
    if n<=79: assert lc, n
    if n==80:
        assert not lc
        bad=[i for i in range(1,n-1) if b[i]**2<b[i-1]*b[i+1]]
        print("n=80 실패 첨자:",bad)
        print("b80[39..41] 증가?", b[39]<b[40]<b[41])
        u,W=unimodal_witnesses(b); print("n=80 단봉?",u,"증인",W)
print("n<=79 모두 로그오목 확인")
import math
for n in range(1,11):
    b=row(n); u,W=unimodal_witnesses(b)
    print(n, b, "단봉" if u else "비단봉", "증인",W, "ceil(n/2)=",math.ceil(n/2), "증인<ceil?", all(w<math.ceil(n/2) for w in W))
