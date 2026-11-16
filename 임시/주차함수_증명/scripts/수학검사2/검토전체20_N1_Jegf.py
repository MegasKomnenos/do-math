# 보조정리 J-egf (가) 재귀와 (나) 닫힌 꼴을 z=k-1 에서 전수 J_n과 대조 (k<=4, n<=2k)
import itertools,sys,io
from fractions import Fraction as Fr
from math import comb, factorial
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=max([j for j in range(1,i) if sig[j-1]>sig[i-1]]+[0]); h.append(i-z)
    return h
p=lambda m:(m+1)**(m-1) if m>0 else 1
def Jbrute(n,k,z):
    J=0
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        pr=1
        for x in h:
            if x<k: pr*=x
        if H>0: J+=H*k**(H-1)*z**Z*pr
    return J
# 멱급수 유틸 (계수 리스트, 길이 N+1)
N=10
def mul(a,b):
    c=[Fr(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j,y in enumerate(b):
            if i+j<=N: c[i+j]+=x*y
    return c
def expser(a):  # a[0]=0
    r=[Fr(0)]*(N+1); r[0]=Fr(1)
    # exp via recurrence: r' = a' r
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(1,n+1): s+=j*a[j]*r[n-j]
        r[n]=s/n
    return r
T=[Fr(0)]+[Fr(t**(t-1),factorial(t)) for t in range(1,N+1)]
Gr=[T[i]-mul(T,T)[i]/2 for i in range(N+1)]
def integ(a): return [Fr(0)]+[a[i-1]/i for i in range(1,N+1)]
bad=0
for k in range(1,5):
    z=k-1
    eT=expser(T); ezG=expser([z*g for g in Gr]); emzG=expser([-z*g for g in Gr])
    xk=[Fr(0)]*(N+1); xk[k-1]=Fr(1,factorial(k-1))
    inner=integ(mul(emzG,xk))
    Y=mul(mul(eT,ezG),inner)
    Jrec={0:0}
    for n in range(0,2*k):
        Jrec[n+1]=sum(comb(n,i)*(z+i+1)*p(i)*Jrec[n-i] for i in range(0,n+1))+(comb(n,k-1)*p(k-1)*p(n-k+1) if n>=k-1 else 0)
    for n in range(0,min(2*k,7)+1):
        jb=Jbrute(n,k,z); jc=p(k-1)*Y[n]*factorial(n); jr=Jrec.get(n)
        if jb!=jc or (jr is not None and jr!=jb): bad+=1; print('FAIL',k,n,jb,jc,jr)
    # n=2k+1에서 닫힌 꼴이 어긋나는지(일치는 n<=2k까지라는 서술 확인)
    if 2*k+1<=7: print('k',k,'n=2k+1 brute vs closed:',Jbrute(2*k+1,k,z),p(k-1)*Y[2*k+1]*factorial(2*k+1))
print('bad',bad)
