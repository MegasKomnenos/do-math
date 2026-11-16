# L10 검산: 10.1–10.2절의 항등식(장부 항등식, 꼬리합 꼴, 머묾 꼴, 분할 무게 비)을 작은 k에서 정확 유리수로 확인.
from fractions import Fraction as F
from math import comb
from functools import lru_cache
@lru_cache(None)
def A(m,l):
    if l<0: return 0
    if m==0: return 1
    return sum(comb(m-1,j-1)*min(j,l+1)*A(j-1,l)*A(m-j,l) for j in range(1,m+1))
def p(m): return (m+1)**(m-1) if m>=1 else 1
def b(m,l): return A(m,l)-A(m,l-1)
def s(m,y): return F(A(m,y-1),p(m))
def c(m,Y): return F(b(m,Y),p(m))
bad=0
for k in (3,4,5,6):
  for n in range(2*k+1,3*k+1):
    nu=n-2*k; N=k+nu
    cl=lambda m,sg: F(b(m,k if sg>0 else k-1),A(m,k-1)) if m>=1 else F(0)
    mu=lambda m: F(b(m,k)-b(m,k-1),A(m,k-1)) if m>=1 else F(0)
    P=lambda j: F(min(j,k)*comb(n-1,j-1)*A(j-1,k-1)*A(n-j,k-1),A(n,k-1))
    def chi(j):
        L=F(1,k)*(-(1 if j==k else 0)*(1-cl(n-j,-1))+(1 if j>k else 0)*(cl(j-1,1)+cl(j-1,-1)+cl(n-j,1)+cl(n-j,-1)))
        e=F(1 if j>k else 0,k)
        return L+(1+e)*cl(j-1,1)*cl(n-j,1)+(1-e)*cl(j-1,-1)*cl(n-j,-1)
    src=sum(P(j)*chi(j) for j in range(1,n+1))
    inh=sum(P(j)*(mu(j-1)*(1 if k<=j-1<=2*k else 0)+mu(n-j)*(1 if k<=n-j<=2*k else 0)) for j in range(1,n+1))
    star=src+inh
    # (7.25)
    KD=sum((k+n-m)*comb(n-1,m)*p(n-1-m)*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
    assert A(n,k-1)*star==(b(n,k)-b(n,k-1))-KD, (k,n,'7.25')
    w=lambda m: F(comb(n-1,m)*p(m)*A(n-1-m,k-1),A(n,k-1))
    def f(m):
        if m<=N: return 2*((k+1)*c(m,k)-(k-1)*c(m,k-1))
        return (k+n-m+1)*c(m,k)-(k+n-m-1)*c(m,k-1)
    u=w(N)*F(A(N,k),p(N))
    Quad=sum(P(j)*((1+F(1,k))*cl(j-1,1)*cl(n-j,1)+(1-F(1,k))*cl(j-1,-1)*cl(n-j,-1)) for j in range(k+1,n+1))
    Stem=sum(w(m)*(c(m,k)+c(m,k-1)) for m in range(2*k+1,n))
    rhs=sum(w(m)*f(m) for m in range(k,2*k+1))-u+Quad+Stem
    if star!=rhs: bad+=1; print("장부 항등식 불일치",k,n)
    T=lambda m: sum(f(i) for i in range(m,2*k+1)) if m<=2*k else F(0)
    abel=w(k)*T(k)+sum((w(m)-w(m-1))*T(m) for m in range(k+1,2*k+1))
    if abel!=sum(w(m)*f(m) for m in range(k,2*k+1)): bad+=1; print("꼬리합 꼴 불일치",k,n)
    # old-8-3 (d),(e)
    from math import factorial, e as E
    for m in range(k,n-1):
        lhs=w(m+1)/w(m)
        g=lambda x: F(x-1)*0  # 사용 안 함
        rr=F(A(n-1-m,k-1),(n-1-m)*A(n-2-m,k-1))  # r_{n-2-m}
        eg=F(p(m+1),(m+1)*p(m))  # e^{g(m+1)}
        if lhs!=eg/rr: bad+=1; print("(a) 불일치",k,n,m)
    for m in range(N,n):
        # w_m/w_N = Bor(m+1)Bor(n-m)/(Bor(N+1)Bor(k)) ; Bor(j)=e^{-j} j^{j-1}/j! → e 소거, 비는 유리수
        def borq(j): return F(j**(j-1),factorial(j))  # Bor(j)*e^j
        lhs=w(m)/w(N); rhs2=borq(m+1)*borq(n-m)/(borq(N+1)*borq(k))  # e 지수: (m+1)+(n-m) - (N+1) - k = n+1-N-1-k = 0
        if lhs!=rhs2: bad+=1; print("(d) 불일치",k,n,m)
    # (e)
    for m in range(k,N+1):
        gL=F(1)
        for i in range(k,m):
            gL*=F(p(i+1),(i+1)*p(i))/F(p(n-1-i),(n-1-i)*p(n-2-i))
        if w(m)/w(k)!=gL*s(n-1-m,k)/s(N-1,k): bad+=1; print("(e) 불일치",k,n,m)
    if u/w(k)!=F(p(N),N*p(N-1))/F(p(k),k*p(k-1))*s(N,k+1)/s(N-1,k): bad+=1; print("(e) u_n 불일치",k,n)
    # 머묾 꼴 (명제 old-8-8), nu<=k-1
    if nu<=k-1:
        vs=lambda m,l: s(m+1,l+1)-s(m,l)
        DD=lambda m: (k+1)*s(m+1,k+1)-2*k*s(m,k)+(k-1)*s(m-1,k-1)
        om=lambda m: F(2) if m<=N+1 else 2-F(m-N,k)
        Stays=2*vs(N+1,k)+sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(N+2,2*k+1))
        Bd=-(k+nu)*(vs(2*k,k)+c(2*k,k-1))-s(2*k,k-1)
        for m0 in range(k,N+1):
            rhs3=2*k*c(m0,k)+2*s(m0,k+1)+2*s(m0,k)+(2*k+2)*vs(m0,k)-2*s(N+1,k+1)-s(N+2,k+1)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-Stays
            if T(m0)!=rhs3: bad+=1; print("머묾 꼴 (가) 불일치",k,n,m0)
        for m0 in range(N+1,2*k+1):
            mf=3*k+nu-m0
            rhs4=mf*c(m0,k)+s(m0,k)+(s(m0,k+1)-s(m0+1,k+1))+(mf+1)*vs(m0,k)+Bd+sum(om(m)*DD(m) for m in range(m0+1,2*k+1))-sum((2-F(m-N,k))*(vs(m,k)+vs(m-1,k-1)) for m in range(m0+1,2*k+1))
            if T(m0)!=rhs4: bad+=1; print("머묾 꼴 (나) 불일치",k,n,m0)
        # 정리 old-8-10 증명의 Θ_n 식과 Stem 하계 꼴
        Theta=comb(n,k)*k**(k-2)*A(n-k,k-1)
        if F(Theta)!=F(n,k)*A(n,k-1)*u*F(A(N,k-1),A(N,k)): bad+=1; print("Theta 식 불일치",k,n)
        BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
        if not (A(n,k-1)*Stem>=F(2*k+2,n)*BV): bad+=1; print("Stem>=BV 꼴 불일치",k,n)
print("불일치 수:",bad)
