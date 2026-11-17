# 검토전체22 R7b: 둘째 층 n<3k에서 (star)(n) = 2Left - sum_{m>N} w_m[(k-n+m)d/p + c2] - u_n + Quad + Stem (N=n-k) 정확 확인
# 그리고 가벼운 뿌리 몫 (n-m) w_m d_{m,k}/p_m 의 부호를 본다.
from fractions import Fraction as F
from math import comb
def p(n): return (n+1)**(n-1) if n>=1 else 1
def run(k):
    nmax=3*k
    A={}
    for l in (k-2,k-1,k):
        a=[1]
        for m in range(1,nmax+1):
            a.append(sum(comb(m-1,j-1)*min(j,l+1)*a[j-1]*a[m-j] for j in range(1,m+1)))
        A[l]=a
    Ak=A[k-1]
    b=lambda m,l: A[k][m]-A[k-1][m] if l==k else A[k-1][m]-A[k-2][m]
    clp=lambda m: F(b(m,k),Ak[m]); clm=lambda m: F(b(m,k-1),Ak[m]); mu=lambda m: clp(m)-clm(m)
    d=lambda m: b(m,k)-b(m,k-1)
    Pk=lambda m,j: F(min(j,k)*comb(m-1,j-1)*Ak[j-1]*Ak[m-j],Ak[m])
    def chi(m,j):
        L,R=j-1,m-j; v=F(0)
        if j==k: v-=F(1,k)*(1-clm(m-k))
        if j>k: v+=F(1,k)*(clp(L)+clm(L)+clp(R)+clm(R))
        hv=1 if j>k else 0
        return v+(1+F(hv,k))*clp(L)*clp(R)+(1-F(hv,k))*clm(L)*clm(R)
    for n in range(2*k+1,3*k+1):
        N=n-k
        star=sum(Pk(n,j)*chi(n,j) for j in range(1,n+1))+sum(Pk(n,j)*((mu(j-1) if k<=j-1<=2*k else 0)+(mu(n-j) if k<=n-j<=2*k else 0)) for j in range(1,n+1))
        w=lambda m: F(comb(n-1,m)*p(m)*Ak[n-1-m],Ak[n])
        pm=lambda m: F((k+1)*b(m,k)-(k-1)*b(m,k-1),p(m))
        c2=lambda m: F(b(m,k)+b(m,k-1),p(m))
        Left=sum(w(m)*pm(m) for m in range(k,2*k+1))
        u=w(N)*F(A[k][N],p(N))
        Quad=sum(Pk(n,j)*((1+F(1,k))*clp(j-1)*clp(n-j)+(1-F(1,k))*clm(j-1)*clm(n-j)) for j in range(k+1,n+1))
        Stem=F(1,k)*sum(Pk(n,j)*(((clp(j-1)+clm(j-1)) if j-1>2*k else 0)+((clp(n-j)+clm(n-j)) if n-j>2*k else 0)) for j in range(k+1,n+1))
        short=sum(w(m)*((k-n+m)*F(d(m),p(m))+c2(m)) for m in range(N+1,2*k+1))
        assert star==2*Left-short-u+Quad+Stem,(k,n)
        light=[(m, (n-m)*w(m)*F(d(m),p(m))) for m in range(N+1,2*k+1)]
        neg=[m for m,v in light if v<0]
        print('k=%d n=%d(nu=%d): light-root children m in [%d,%d]; negative-difference children: %s' % (k,n,n-2*k,N+1,2*k,neg))
    print('k=%d identity OK on all second-layer rows'%k)
for k in (6,10,14): run(k)
