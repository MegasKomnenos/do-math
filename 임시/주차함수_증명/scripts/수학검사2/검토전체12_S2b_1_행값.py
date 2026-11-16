# S2b 검산 1: 행 값(정리 2-6 재귀)과 4장 4.3·4.4의 수치 주장, 순열 열거로 e_n·J_n·B 확인
from fractions import Fraction
from math import comb, factorial
from itertools import permutations
import sys
sys.setrecursionlimit(10000)
NMAX=60
# A[n][l]
A=[[0]*(NMAX+2) for _ in range(NMAX+1)]
for l in range(NMAX+2): A[0][l]=1
for n in range(1,NMAX+1):
    for l in range(NMAX+2):
        A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
p=[(n+1)**(n-1) for n in range(200)]
out=[]
for n in range(1,NMAX+1):
    assert A[n][n-1]==p[n]
    assert all(b(n,l)>0 for l in range(n))
kn=lambda n:(n+1)//2
neg=[n for n in range(2,NMAX+1) if b(n,kn(n))-b(n,kn(n)-1)<0]
out.append(f"d_(n,k_n)<0 인 n(2..{NMAX}): {neg}")
for n in range(2,16):
    ok=all(b(n,j)>=b(n,j+1) for j in range(kn(n),n-1))
    out.append(f"n={n}: 오른쪽 절반 비증가(k_n<=j<=n-2)? {ok}; 엄격? {all(b(n,j)>b(n,j+1) for j in range(kn(n),n-1))}")
inc=[n for n in range(5,NMAX+1) if b(n,kn(n))<b(n,kn(n)+1)]
out.append(f"b_(n,k_n)<b_(n,k_n+1) 인 n(5..{NMAX}): 처음 {inc[:5]} ... 거짓인 n: {[n for n in range(5,NMAX+1) if n not in inc]}")
# 16<=n<=19: 오른쪽 절반에 증가 수준 있는가
for n in range(16,21):
    js=[j for j in range(kn(n),n-1) if b(n,j)<b(n,j+1)]
    out.append(f"n={n}: 오른쪽 절반 증가 수준 {js}; 행 단봉? {sorted(range(n),key=lambda l:(b(n,l)))[-1]}")
# Q_L(n), 3<=n<=15
for n in range(3,16):
    bad=[l for l in range(0,n-2) if 2*l<=n-2 and b(n,l)>b(n,l+1) and b(n,l+1)**2<b(n,l)*b(n,l+2)]
    if bad: out.append(f"Q_L({n}) 위반 {bad}")
out.append("Q_L(3..15) 확인 끝")
# 로그오목 n=80? (NMAX=60이라 생략)
# 순열 열거: h_i, K_{n,k}(y), E2, E, B, J
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        g=i+1
        for t in range(i-1,-1,-1):
            if sig[t]>sig[i]: g=i-t; break
        h.append(g)
    return h
def polyK(n,k):
    # returns dict power->coef for K_{n,k}(y)
    K={}
    for sig in permutations(range(1,n+1)):
        h=caps(sig); c=1; z=0
        for g in h:
            if g<=k: c*=g
            else: z+=1
        K[z]=K.get(z,0)+c
    return K
def Kval(K,y,der=0):
    s=Fraction(0)
    for z,c in K.items():
        f=1
        for t in range(der): f*=(z-t)
        if z-der>=0: s+=c*f*Fraction(y)**(z-der)
    return s
def BJ(n,k):
    B=0;J=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); c=1;z=0;H=0
        for g in h:
            if g<k: c*=g
            elif g==k: H+=1
            else: z+=1
        B+=c*(k-1)**z*(k**H-(k-1)**H)
        J+=c*H*k**(H-1)*(k-1)**z if H>0 else 0
    return B,J
for n in range(2,9):
    for k in range(1,n+1):
        K=polyK(n,k)
        assert Kval(K,k)==A[n][k-1], (n,k)
        assert Kval(K,k+1)==A[n][k]
        e=Kval(K,k,2)
        B,J=BJ(n,k)
        d=b(n,k)-b(n,k-1) if k<=n-1 else -b(n,n-1)
        E=(Kval(K,k+1)-2*Kval(K,k)+Kval(K,k-1)+B)/2  # from 2-28: d = 2E - B, and K(k+1)-2K(k)+K(k-1)-B = d
        assert Kval(K,k+1)-2*Kval(K,k)+Kval(K,k-1)-B==d, (n,k)
        assert B<=J
        if n<=2*k-1: assert B==J
        if n==2*k: assert J-B==comb(2*k-1,k-1)*p[k-1]**2,(n,k,J-B)
        assert e<=2*E
out.append("n<=8 순열 열거: K(k)=A, K(k+1)=A, 2-28 항등식, B<=J, n<=2k-1 등식, n=2k Xi, e_n<=2E 모두 확인")
# e_n>J_n(k-1) for n up to 120 via full recursion for K (polynomial) and J-egf (가) recursion
from functools import lru_cache
def e_and_J(n):
    k=kn(n)
    # K_j as poly in y: list coefs
    def pmul(a,b):
        r=[0]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b): r[i+j]+=x*y
        return r
    def padd(a,b):
        r=[0]*max(len(a),len(b))
        for i,x in enumerate(a): r[i]+=x
        for i,x in enumerate(b): r[i]+=x
        return r
    Kp=[[1]]
    for m in range(1,n+1):
        acc=[0]
        for j in range(m):
            t=pmul(Kp[j],Kp[m-1-j]); t=[comb(m-1,j)*c for c in t]
            if j+1<=k: t=[(j+1)*c for c in t]
            else: t=[0]+t
            acc=padd(acc,t)
        Kp.append(acc)
    Kn=Kp[n]
    e=sum(c*z*(z-1)*k**(z-2) for z,c in enumerate(Kn) if z>=2)
    Kk=sum(c*k**z for z,c in enumerate(Kn)); assert Kk==A[n][k-1] if n<=NMAX else True
    # J recursion (가) with z=k-1
    z=k-1
    J=[0]*(n+1)
    for m in range(0,n):
        if m+1<k: J[m+1]=0; continue
        s=sum(comb(m,i)*(z+i+1)*p[i]*J[m-i] for i in range(m+1))
        if m>=k-1: s+=comb(m,k-1)*p[k-1]*p[m-k+1]
        J[m+1]=s
    return e,J[n]
res=[]
for n in range(10,121):
    e,J=e_and_J(n)
    res.append((n,e>J,Fraction(int(e),int(J)) if J else None))
out.append("e_n>J_n(k-1) 성립 n(10..120): 거짓인 n = "+str([n for n,ok,_ in res if not ok]))
out.append("비 e_n/J_n 최소(16..120): "+str(min((float(r),n) for n,ok,r in res if n>=16)))
out.append("n=17 비: %.7f"%float([r for n,ok,r in res if n==17][0]))
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_S2b_1_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
