# H6 검산: 7A 7.1-7.2의 작은 크기 전수 확인
import itertools, math
from fractions import Fraction as Fr

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)
    return h

def A(n,l):
    # A_{n,l}: 누적 개수, 따름정리 2-4
    if l<0: return 0
    if n==0: return 1
    s=0
    for sg in itertools.permutations(range(1,n+1)):
        p=1
        for hi in caps(sg): p*=min(hi,l+1)
        s+=p
    return s

# 1) 정수 부등식 (column-lemma (가))
L=10**21*400**10; R=17**21*123**10
print("정수부등식", L>R, L, R, "%.4e %.4e"%(L,R))

# 2) t_k, n#_k, ñ_k
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1)>=2*k**(2*j+1)): j+=1
    return j
for k in [2,3,5,10,41,100,500,501]:
    t=tk(k); print("k",k,"t_k",t,"n#",k+(k+1)*t,"ñ",k*(2*t+1), "1<=t<=k", 1<=t<=k)

# 3) 정리 6-6: E[Z_k] >= (n-k)/(k+1); 따름 factorial: E[Z(Z-1)] >= m(m-1) (n>=2k+1); 정리 6-10: E[kH_k] <= x_k n; 명제 6-7
for n in range(1,9):
    for k in range(2,n+1):
        W=0; EZ=0; EZZ=0; EH=0; Ak=0; Ak2=0
        for sg in itertools.permutations(range(1,n+1)):
            h=caps(sg); w=1
            for hi in h: w*=min(hi,k)
            Z=sum(1 for hi in h if hi>k); H=sum(1 for hi in h if hi==k)
            W+=w; EZ+=w*Z; EZZ+=w*Z*(Z-1); EH+=w*H
            wk=1; wk2=1
            for hi in h: wk*=min(hi,k+1); wk2*=min(hi,k-1)
            Ak+=wk; Ak2+=wk2
        m=Fr(n-k,k+1)
        ok66 = Fr(EZ,W)>=m
        okfm = (n<2*k+1) or Fr(EZZ,W)>=m*(m-1)
        xk=Fr(k,k+1)**(k-1)
        ok610 = Fr(k*EH,W)<=xk*n
        Rr=Fr(Ak,W); Zz=Fr(Ak2,W)
        xf=1-Fr(1,k); xs=1+Fr(1,k)
        ok=float(math.log(float(Zz))) > float(math.log(float(xf)) - (-2*math.log(float(xf))/math.log(float(xs)))*math.log(float(Rr)))
        # 모멘트 판정 d >= T/k^2
        d=Ak-2*W+Ak2; T=EZZ-k*EH
        okmom = d*k*k >= T
        # 등호 n=k in 6-10
        eq = (n!=k) or Fr(k*EH,W)==xk*n
        if not (ok66 and okfm and ok610 and ok and okmom and eq):
            print("FAIL",n,k,ok66,okfm,ok610,ok,okmom,eq)
print("전수 검사 끝 (n<=8)")

# 4) C_{n,n} = (n-1)^{n-1}: 소인 주차함수 전수 (n<=6)
def is_pf(a):
    n=len(a); return all(sum(1 for x in a if x<=b)>=b for b in range(1,n+1))
def prime(a):
    n=len(a); return all(sum(1 for x in a if x<=b)!=b for b in range(1,n))
for n in range(1,7):
    c=sum(1 for a in itertools.product(range(1,n+1),repeat=n) if is_pf(a) and prime(a))
    print("C_{n,n}",n,c,(n-1)**(n-1) if n>1 else 1)

# 5) 1/(1-T) = sum m^m x^m/m!  (계수 비교, 10항)
N=10
T=[Fr(0)]+[Fr(m**(m-1),math.factorial(m)) for m in range(1,N+1)]
def mul(a,b):
    c=[Fr(0)]*(N+1)
    for i in range(N+1):
        for j in range(N+1-i): c[i+j]+=a[i]*b[j]
    return c
inv=[Fr(0)]*(N+1); inv[0]=Fr(1)
# 1/(1-T) = sum T^j
acc=[Fr(1)]+[Fr(0)]*N; tot=acc[:]
for j in range(1,N+1):
    acc=mul(acc,T); tot=[tot[i]+acc[i] for i in range(N+1)]
print("1/(1-T) 계수", all(tot[m]==Fr(m**m,math.factorial(m)) for m in range(1,N+1)))
# sum_{y=0}^k y^y/y! * a_{k-y} = (k+1)^k/k!  with a_i=(i+1)^{i-1}/i!
for k in range(1,8):
    s=sum(Fr(y**y if y>0 else 1,math.factorial(y))*Fr((k-y+1)**(k-y-1) if k-y>0 else 1,math.factorial(k-y)) for y in range(0,k+1))
    print("합", k, s==Fr((k+1)**k,math.factorial(k)))
