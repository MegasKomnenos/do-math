# 검토전체5 K1: 장1·장2의 수치 재계산
# (1) 1.3절 표(n<=10)와 가장 작은 증인 ell*_n; 브루트포스(n<=7)와 마지막 차 재귀의 대조
# (2) 1.4절: 로그오목성이 n=80에서 처음 깨짐, 누적 행 n=780 (재귀로 n<=120)
# (3) 정리 2-5 섬유 행, 2.4절 나무 라벨 개수열
# (4) 명제 2-20의 유한 n 상계 네 값 (lgamma 사용, 배정밀도)
# (5) 보조정리 2-16 i=3 조건, 보조정리 2-14 마지막 문장 점검(작은 범위)
import itertools, math
from fractions import Fraction

def park(pref):
    n=len(pref); occ=[False]*(n+1); pos=[0]*n
    for i,a in enumerate(pref):
        j=a
        while j<=n and occ[j]: j+=1
        if j>n: return None
        occ[j]=True; pos[i]=j
    return pos

def brute_row(n):
    row=[0]*n
    for pref in itertools.product(range(1,n+1),repeat=n):
        pos=park(pref)
        if pos is None: continue
        M=max(p-a for p,a in zip(pos,pref))
        row[M]+=1
    return row

def A_table(N):
    # A[n][l] for 0<=n<=N, 0<=l<=N (l>=n-1 gives p_n)
    A=[[0]*(N+1) for _ in range(N+1)]
    for l in range(N+1): A[0][l]=1
    for n in range(1,N+1):
        for l in range(N+1):
            s=0
            for j in range(n):
                s+=math.comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
            A[n][l]=s
    return A

def rows_from_A(A,N):
    rows={}
    for n in range(1,N+1):
        rows[n]=[A[n][0]]+[A[n][l]-A[n][l-1] for l in range(1,n)]
    return rows

def is_unimodal(z):
    m=len(z); i=0
    while i+1<m and z[i]<=z[i+1]: i+=1
    while i+1<m and z[i]>=z[i+1]: i+=1
    return i==m-1

def smallest_witness(z):
    m=len(z)
    for l in range(m):
        if all(z[i]<=z[i+1] for i in range(0,l)) and all(z[i]>=z[i+1] for i in range(l,m-1)):
            return l
    return None

def log_concave(z):
    return all(z[i]*z[i]>=z[i-1]*z[i+1] for i in range(1,len(z)-1))

print("== (1) 1.3절 표 ==")
N=120
A=A_table(N)
rows=rows_from_A(A,N)
for n in range(1,11):
    print(n, rows[n], sum(rows[n]), (n+1)**(n-1), "ell*=",smallest_witness(rows[n]))
for n in range(1,8):
    b=brute_row(n)
    print("brute n=%d"%n, b, "match" if b==rows[n] else "MISMATCH")

print("== (2) 로그오목성 ==")
first=None
for n in range(1,N+1):
    if not log_concave(rows[n]):
        first=n; break
print("행의 로그오목성이 처음 깨지는 n:", first)
bad=[n for n in range(1,N+1) if not log_concave(rows[n])]
print("n<=120에서 로그오목이 아닌 행의 수:", len(bad), "첫 10개:", bad[:10])
firstA=None
for n in range(1,N+1):
    Arow=[A[n][l] for l in range(n)]
    if not log_concave(Arow):
        firstA=n; break
print("누적 행 A_{n,.}의 로그오목성이 처음 깨지는 n:", firstA)
print("n<=120 모든 행 단봉:", all(is_unimodal(rows[n]) for n in range(1,N+1)))
print("가운데 비교 d_{n,k_n} 부호: n에서 처음 양이 되는 n과 2..15에서 음인지")
def kn(n): return -(-n//2)
neg=[n for n in range(2,41) if rows[n][kn(n)]-rows[n][kn(n)-1]<0]
print("  d_{n,k_n}<0 인 n (2..40):", neg)
print("  ell*_n for n=16..30:", [(n,smallest_witness(rows[n])) for n in range(16,31)])
# n>=1000: 증인 >= ceil(n/2)? 작은 n에서 증인 위치 확인
print("  증인 < k_n 인 n (1..800):", [n for n in range(1,N+1) if smallest_witness(rows[n])<kn(n)][:20])

print("== (3) 정리 2-5 섬유 행 ==")
h=[1,2,3,4,1,6,7]
As=[math.prod(min(x,l+1) for x in h) for l in range(7)]
bs=[As[0]]+[As[l]-As[l-1] for l in range(1,7)]
print("A^sigma:",As,"b^sigma:",bs,"unimodal:",is_unimodal(bs))
print("5배:",[5*x for x in bs], " 7!/1008=",math.factorial(7)//1008)
# sigma' 용량 확인 n=9
def caps(sig):
    n=len(sig); return [i+1-max([j+1 for j in range(i) if sig[j]>sig[i]]+[0]) for i in range(n)]
print("caps of (1,2,3,5,4,6,7):",caps([1,2,3,5,4,6,7]))
n=10; sp=[n-6,n-5,n-4,n-2,n-3,n-1,n]+list(range(n-7,0,-1))
print("sigma' n=10:",sp,"caps:",caps(sp))
# n<=6 모든 섬유 단봉?
for n in range(1,7):
    allu=True
    for sig in itertools.permutations(range(1,n+1)):
        hh=caps(list(sig)); Al=[math.prod(min(x,l+1) for x in hh) for l in range(n)]
        bl=[Al[0]]+[Al[l]-Al[l-1] for l in range(1,n)]
        if not is_unimodal(bl): allu=False
    print("n=%d 모든 섬유 단봉:"%n, allu)
# n=7 비단봉 섬유 개수
cnt=0
for sig in itertools.permutations(range(1,8)):
    hh=caps(list(sig)); Al=[math.prod(min(x,l+1) for x in hh) for l in range(7)]
    bl=[Al[0]]+[Al[l]-Al[l-1] for l in range(1,7)]
    if not is_unimodal(bl): cnt+=1
print("n=7 비단봉 섬유 수:",cnt)

print("== (4) 명제 2-20 상계 ==")
def v(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
def logP_Sb(n,c,b):
    # Pr(S_b=c) = n!/c! c^{c-1} b (n-c+1)^{n-c-b} / ((n-c-b+1)! (n+1)^{n-1})
    kap=n-c-b+1
    if kap<0: return None
    return (math.lgamma(n+1)-math.lgamma(c+1)+(c-1)*math.log(c)+math.log(b)
            +(n-c-b)*math.log(n-c+1)-math.lgamma(kap+1)-(n-1)*math.log(n+1))
def logP_Sb_o0(n,c,b):
    kap=n-c-b+1
    if kap<0: return None
    return (math.lgamma(n+1)-math.lgamma(c+1)+(c-1)*math.log(c)+math.log(2)
            +(n-c-b)*math.log(n-c-b+3)-math.lgamma(kap+1)-(n-1)*math.log(n+1))
def bound(n,b):
    s1=0.0; s2=0.0
    for c in range(n//2+1,n+1):
        l1=logP_Sb(n,c,b); l2=logP_Sb_o0(n,c,b)
        if l1 is not None: s1+=math.exp(l1)
        if l2 is not None: s2+=math.exp(l2)
    return 1-s1+s2
def cond_ok(n,b):
    return all(v(k,i-1,1)<0 for i in range(3,b+1) for k in range(n//2+1,n+1))
for n in [17,100,1000,10000]:
    best=None
    for b in range(3,60):
        if not cond_ok(n,b): continue
        val=bound(n,b)
        if best is None or val<best[1]: best=(b,val)
    print("n=%d: 최적 b=%d, 상계=%.5f"%(n,best[0],best[1]))
# 극한 e^{-(b-2)} 확인은 자명. n=17에서 b=3 조건: v_k(2,1)<0 for k=9..17
print("v_k(2,1) k=4..9:",[round(v(k,2,1),5) for k in range(4,10)], " v_3(2,1)=",round(v(3,2,1),5))
print("== (5) 보조정리 2-14 마지막 문장: H>=1, k>=4Z^2 => v<0 (Z<=6, k<=200) ==")
ok=all(v(k,Z,H)<0 for Z in range(0,7) for k in range(max(4*Z*Z,1),201) for H in range(1,6))
print("성립:",ok)
print("2-16 i=3: v_k(2,1)<0 iff k>=4:", [ (k, v(k,2,1)<0) for k in range(1,6)])
# 2-13 셋째 식 수치 확인: n<=2y+1, s_n(y)=A/p 와 재귀식 비교 (y=5,n=11)
y=5; nn=11
def p(m): return 1 if m==0 else ((m+1)**(m-1) if m>0 else 0)
def pi0(n,y):
    # 쪼개짐 확률: 크기 y 넘는 나무 없음 = 모든 나무 크기<=y; 숲 수를 지수공식으로 세자: 나무 수열 t^{t-1}, t<=y
    # egf F=exp(sum_{t<=y} t^{t-1}x^t/t!) ; 계수 n! [x^n]
    from fractions import Fraction
    T=[Fraction(0)]*(n+1)
    for t in range(1,min(y,n)+1): T[t]=Fraction(t**(t-1),math.factorial(t))
    F=[Fraction(0)]*(n+1); F[0]=Fraction(1)
    # F' = T' F
    for m in range(1,n+1):
        s=Fraction(0)
        for t in range(1,m+1): s+=t*T[t]*F[m-t]
        F[m]=s/m
    return F[n]*math.factorial(n)/p(n)
lhs=Fraction(A[nn][y-1],p(nn))
rhs=pi0(nn,y)+sum(Fraction(math.comb(nn,m)*m**(m-1)*p(nn-m),p(nn))*Fraction(y,m)*Fraction(A[m-1][y-1],p(m-1)) for m in range(y+1,nn+1))
print("2-13 둘째 식 (y=5,n=11):",lhs==rhs, float(lhs))
# b-top: b_{k,k-1}=k^{k-2}
print("b-top k=2..12:", all(rows[k][k-1]==k**(k-2) for k in range(2,13)))
# 2-28 항등식 수치 확인 n=5 (E_{n,k}, B_{n,k-1} 직접 셈)
def stats(n):
    E={};B={}
    for pref in itertools.product(range(1,n+1),repeat=n):
        pos=park(pref)
        if pos is None: continue
        d=[pp-a for pp,a in zip(pos,pref)]; M=max(d); Msh=d.count(M)
        sig=[0]*n
        for i,pp in enumerate(pos): sig[pp-1]=i+1
        hh=caps(sig)
        if Msh%2==0: E[M]=E.get(M,0)+1
        if all(hh[pp-1]==M+1 for i,pp in enumerate(pos) if d[i]==M): B[M]=B.get(M,0)+1
    return E,B
for n in [4,5,6]:
    E,B=stats(n)
    ok=all(rows[n][k]-rows[n][k-1]==2*E.get(k,0)-B.get(k-1,0) for k in range(1,n))
    print("2-28 n=%d:"%n, ok, " B_{n,0}=",B.get(0))
# 2-30 Xi at n=2k: B = J(k-1) - C(2k-1,k-1) p_{k-1}^2 ; 직접 J 계산 n=6,k=3
def J_and_B(n,k):
    J=0;B=0
    for sig in itertools.permutations(range(1,n+1)):
        hh=caps(list(sig)); Z=sum(1 for x in hh if x>k); H=sum(1 for x in hh if x==k)
        prod=math.prod(x for x in hh if x<k)
        J+=H*k**(H-1)*(k-1)**Z*prod if H>0 else 0
        B+=prod*(k-1)**Z*(k**H-(k-1)**H)
    return J,B
for (n,k) in [(5,3),(6,3),(8,4)]:
    J,B=J_and_B(n,k); E,Bs=stats(n)
    print("2-30 n=%d k=%d: J=%d B=%d J-B=%d Xi=%d  B직접=%d"%(n,k,J,B,J-B, math.comb(2*k-1,k-1)*p(k-1)**2 if n==2*k else 0, Bs.get(k-1,0)))
# moving-tail (아) 작은 확인: D=2, n>=20*2^{1.5}=56.6 -> n>=57: b_{n,n-2}>b_{n,n-1}
print("(아) D=2: b_{n,n-2}>b_{n,n-1} for n=57..200:", all(rows[n][n-2]>rows[n][n-1] for n in range(57,121)))
print("    처음 성립 n:", next(n for n in range(2,121) if all(rows[m][m-2]>rows[m][m-1] for m in range(n,121))))
# zeta 상수
try:
    import mpmath
    print("zeta(1/2),zeta(-1/2),zeta(3/2):",mpmath.zeta(0.5),mpmath.zeta(-0.5),mpmath.zeta(1.5))
except Exception as e:
    print("mpmath 없음:",e)
