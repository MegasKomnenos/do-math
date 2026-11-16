# L12 검산(부록 D 장4): (1) 정리 old-4-5 네 재귀를 순열 전수(k=3,4; n<=2k)로 확인, K''=e_n을 선호 수열 전수(n<=7)로 확인,
# (2) (ㄴ) n<=60 정확 행에서 d_{n,k_n} 부호와 오른쪽 절반 비증가, (3) 넘는 수 재귀(D.crossing-small-n)의 식을 정확 행과 대조하고
# 20<=n<=N0에서 b_{n,k_n}<b_{n,k_n+1}, (4) 3<=n<=15의 Q_L(n), (5) S=2918732888의 s=S/2^30 값, a_0·a_1의 닫힌 꼴.
from math import comb, factorial, gamma
from fractions import Fraction as Fr
from itertools import permutations, product
import sys
def caps(p):
    st=[];h=[]
    for i,c in enumerate(p):
        while st and p[st[-1]]<c: st.pop()
        h.append(i-st[-1] if st else i+1); st.append(i)
    return h
def pn(n): return 1 if n==0 else (n+1)**(n-1)
out=[]
# (1) recurrences
for k in (3,4):
    N=2*k
    A={};Kp={};Kpp={};J={}
    for n in range(0,N+1):
        a=kp=kpp=j=0
        for perm in permutations(range(1,n+1)):
            h=caps(perm)
            Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
            small=1
            for x in h:
                if x<k: small*=x
            # K(y)=small*k^H*y^Z  (W(g)=g for g<=k)
            a+=small*k**H*k**Z
            kp+=small*k**H*(Z*k**(Z-1) if Z>=1 else 0)
            kpp+=small*k**H*(Z*(Z-1)*k**(Z-2) if Z>=2 else 0)
            # J_n(z)=sum d/dy[small*y^H*z^Z] at y=k, z=k-1
            j+=small*(H*k**(H-1) if H>=1 else 0)*(k-1)**Z
        A[n]=a;Kp[n]=kp;Kpp[n]=kpp;J[n]=j
    # normalized with s=1: r_i=p_i/i!, frak values = X_n/n!
    r=lambda i: Fr(pn(i),factorial(i))
    fA=lambda n: Fr(A[n],factorial(n)); fd=lambda n: Fr(Kp[n],factorial(n)); fz=lambda n: Fr(Kpp[n],factorial(n)); fj=lambda n: Fr(J[n],factorial(n))
    ok=True
    for n in range(k+1,2*k+1):
        rr=n-k
        RA=Fr(1,n)*(sum((k+i+1)*r(i)*fA(n-1-i) for i in range(0,rr-1))+sum(min(i+1,k)*r(i)*r(n-1-i) for i in range(rr-1,k+1)))
        Rd=Fr(1,n)*(sum((k+i+1)*r(i)*fd(n-1-i) for i in range(0,rr-1))+sum(r(i)*fA(n-1-i) for i in range(0,rr)))
        Rz=Fr(1,n)*(sum((k+i+1)*r(i)*fz(n-1-i) for i in range(0,rr-1))+2*sum(r(i)*fd(n-1-i) for i in range(0,rr-1)))
        Rj=Fr(1,n)*(sum((k+i)*r(i)*fj(n-1-i) for i in range(0,rr))+r(k-1)*r(n-k))
        ok&= RA==fA(n) and Rd==fd(n) and Rz==fz(n) and Rj==fj(n)
    init= all(fA(i)==r(i) for i in range(0,k+1)) and all(fd(i)==0 and fz(i)==0 for i in range(0,k+1)) and all(fj(i)==0 for i in range(0,k)) and fj(k)==r(k-1)/k
    out.append(f"k={k}: four recurrences hold for k<n<=2k: {ok}; initial values: {init}")
    # e_n brute: 2*#{alpha in PF_n: M=k, M#=2}
    for n in range(k+1,min(2*k,7)+1):
        e=0
        for al in product(range(1,n+1),repeat=n):
            occ=[False]*(n+2); ds=[]; bad=False
            for a_ in al:
                s=a_
                while s<=n and occ[s]: s+=1
                if s>n: bad=True;break
                occ[s]=True; ds.append(s-a_)
            if bad: continue
            M=max(ds)
            if M==k and ds.count(M)==2: e+=1
        out.append(f"  n={n}: 2*E2={2*e}  K''(k)={Kpp[n]}  equal={2*e==Kpp[n]}")
# (2),(3),(4): exact rows via last-car recursion
N0=int(sys.argv[1]) if len(sys.argv)>1 else 200
Arow=[[1]*(N0+1)]
for n in range(1,N0+1):
    w=[comb(n-1,j) for j in range(n)]
    row=[sum(w[j]*min(j+1,l+1)*Arow[j][l]*Arow[n-1-j][l] for j in range(n)) for l in range(n-1)]
    row+=[pn(n)]*(N0+1-len(row)); Arow.append(row)
def b(n,l): return Arow[n][l]-(Arow[n][l-1] if l>0 else 0)
neg=[n for n in range(2,N0+1) if b(n,-(-n//2))-b(n,-(-n//2)-1)<0]
out.append(f"(2) n in [2,{N0}] with d_(n,k_n)<0: {neg}")
rh=all(all(b(n,j)>=b(n,j+1) for j in range(-(-n//2),n-1)) for n in range(2,16))
out.append(f"(2) right half nonincreasing for 2<=n<=15: {rh}")
# (3) deficit recurrence check vs exact for n<=min(N0,60)
def Ac_formula(n,l,Ac):
    s=sum(comb(n-1,j)*(j-l)*pn(j)*pn(n-1-j) for j in range(l+1,n))
    s+=sum(Ac[(i,l)]*comb(n-1,i)*pn(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
    return s
okf=True
Ac={}
for l in range(0,N0):
    for n in range(0,min(2*l+4,N0)+1):
        Ac[(n,l)]=0 if n<=l+1 else Ac_formula(n,l,Ac)
        if n<=60 and l<=n-1: okf&= Ac[(n,l)]==pn(n)-Arow[n][l]
out.append(f"(3) deficit recurrence equals p_n-A_(n,l) for n<=60 (all l, n<=2l+4): {okf}")
cross_false=[n for n in range(5,N0+1) if not (b(n,-(-n//2))<b(n,-(-n//2)+1))]
out.append(f"(3) n in [5,{N0}] where b_(n,k_n)<b_(n,k_n+1) is FALSE: {cross_false}")
# (4) Q_L(n) 3<=n<=15
ql=True; strict=True
for n in range(3,16):
    for l in range(0,n-2):
        if 2*l<=n-2 and b(n,l)>b(n,l+1):
            ql&= b(n,l+1)**2>=b(n,l)*b(n,l+2); strict&= b(n,l+1)**2>b(n,l)*b(n,l+2)
out.append(f"(4) Q_L(n) for 3<=n<=15: {ql}; strict: {strict}")
# (5)
S=2918732888
out.append(f"(5) S/2^30 = {S/2**30!r}; a_0=3^(-2/3)Gamma(1/3)={3**(-2/3)*gamma(1/3)!r}; a_1=3^(-1/3)Gamma(2/3)={3**(-1/3)*gamma(2/3)!r}")
out.append(f"(5) 495594511/240250000={495594511/240250000!r}; 5.642*1.6809*0.39893-0.0163-3.554={5.642*1.6809*0.39893-0.0163-3.554!r}; 30000^5 e^(-30000/520)={30000**5*2.718281828459045**(-30000/520)!r}")
print("\n".join(out))
