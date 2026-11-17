# R3 검산: 열 재귀 n a_n = sum_{j=1}^n min(j,k) a_{j-1} a_{n-j} (a_n=A_{n,k-1}/n!) 를 e^{-n} 눈금의 배정밀도로 계산해
# 몇 행의 봉우리 위치와 명제 witness-position-bound의 차를 다시 센다(표본 점검; 인증이 아니다).
import sys, numpy as np, math
def column(k,N):
    a=np.zeros(N+1); a[0]=1.0
    w=np.minimum(np.arange(1,N+1),k).astype(float)  # min(j,k), j=1..N
    einv=math.exp(-1.0)
    for n in range(1,N+1):
        # sum_{j=1}^n w[j-1]*a[j-1]*a[n-j]
        a[n]=einv*np.dot(w[:n]*a[:n],a[n-1::-1][:n])/n
    return a
def offset(n,ls):
    return n+1-ls-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3)
def peak_row(n,guess_r):
    # levels l around n-1-guess_r ; b_{n,l} ∝ a^{(l+1)}_n - a^{(l)}_n
    l0=int(n-1-guess_r)
    cols={}
    for k in range(l0-3,l0+6):
        cols[k]=column(k,n)[n]
    bs={l:cols[l+1]-cols[l] for l in range(l0-3,l0+5)}
    return bs
for n in [int(x) for x in sys.argv[1:]]:
    g=0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
    bs=peak_row(n,g)
    ls=max(bs,key=bs.get)
    ks=sorted(bs)
    assert ls not in (ks[0],ks[-1]), "peak at window edge"
    print(n,"l*=",ls,"offset=",offset(n,ls),"rel gaps:",[(bs[l]-bs[ls])/bs[ls] for l in (ls-1,ls+1)])
