# N12 검산: D.exact-n20000 (ㅁ) n<=300 전 행 단봉성, 왼쪽 사슬이 깨지는 n, (ㄹ) Q_R, (ㅂ) 50<=n<=300의 증인 위치 차, ℓ=0 비교, 비교 수 세기
from math import comb
from mpmath import mp, mpf, iv
import time
t0=time.time()
N=300
A={}
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        if l>=n-1: A[(n,l)]=(n+1)**(n-1); continue
        s=0
        for j in range(0,n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)]
        A[(n,l)]=s
print("table built %.0fs"%(time.time()-t0))
def b(n,l): return A[(n,l)]-(A[(n,l-1)] if l>=1 else 0)
def row(n): return [b(n,l) for l in range(n)]
def unimodal(r):
    i=0
    while i+1<len(r) and r[i]<=r[i+1]: i+=1
    while i+1<len(r) and r[i]>=r[i+1]: i+=1
    return i==len(r)-1
print("non-unimodal rows n<=300:",[n for n in range(1,N+1) if not unimodal(row(n))])
brk=[n for n in range(2,N+1) if not all(b(n,l)<b(n,l+1) for l in range(0,(n+1)//2-1))]
print("left chain b0<...<b_{kn-1} broken for n in:",brk)
# (ㄹ) Q_R and stronger: on (n-1)/2<=l<=n-3 either b_l<=b_{l+1} or (strict dec, strict logconcave, strict concave); increases precede decreases
bad=[]
for n in range(5,N+1):
    lo=(n-1+1)//2  # ceil((n-1)/2)
    seen_dec=False
    for l in range(lo,n-2):
        if b(n,l)<=b(n,l+1):
            if seen_dec: bad.append((n,l,'inc after dec'))
        else:
            seen_dec=True
            if not (b(n,l+1)**2>b(n,l)*b(n,l+2) and b(n,l)+b(n,l+2)<2*b(n,l+1)): bad.append((n,l,'not strict lc/concave'))
print("(ㄹ) violations n<=300:",bad)
# ℓ=0: b_{n,1} >= (n-1) n!/2 for n>=4 and > n!
from math import factorial
print("b_{n,1}>=(n-1)n!/2 for 4<=n<=300:",all(b(n,1)*2>=(n-1)*factorial(n) for n in range(4,N+1)), " b_{n,1}>n! fails:",[n for n in range(1,N+1) if not b(n,1)>factorial(n)])
# (ㅂ) witness offset 50<=n<=300
mp.dps=30
def peak(n):
    r=row(n); m=max(r); return r.index(m), r.count(m)
vals=[]
for n in range(50,N+1):
    ls,cnt=peak(n)
    assert cnt==1
    x=iv.mpf(n+1)
    v=(n+1-ls)-iv.mpf('0.59963')*x**(iv.mpf(2)/3)-iv.mpf('1.24847')*x**(iv.mpf(1)/3)
    vals.append((n,v))
lo=min(vals,key=lambda t:t[1].a); hi=max(vals,key=lambda t:t[1].b)
print("(ㅂ) 50<=n<=300: min lower end",lo[1].a,"at n=",lo[0],"; max upper end",hi[1].b,"at n=",hi[0]," all in [0.85,1.99]:",all(t[1].a>=0.85 and t[1].b<=1.99 for t in vals))
print("(ㅂ) n=51 value:",[t[1] for t in vals if t[0]==51][0])
# counts
cnt_r=sum((n-2)-((n-1+1)//2) for n in range(5,20001))
print("(ㄹ) positions 5..20000:",cnt_r)
cnt_g=sum(9989 for k in range(2,6))+sum(10000-2*k for k in range(6,121)); print("(ㄱ) direct comparisons k=2..120:",cnt_g)
def B(k): return -(-k*k//4)
d1=sum(2*B(k)-2*k for k in range(161,501)); r1=sum(B(k)+1 for k in range(161,501))
d2=sum(2*B(k)-2*k for k in range(121,161)); r2=sum(B(k)+1 for k in range(121,161))
print("column cert k=161..500 direct",d1,"ratio",r1," ; k=121..160 direct",d2,"ratio",r2)
print("row cert 501<=k<=4999, n<=10000: count", sum(10000-2*k for k in range(501,5000)))
print("(ㄴ) count:",sum(((n+1)//2)-1 for n in range(10001,20001)))
print("elapsed %.0fs"%(time.time()-t0))
