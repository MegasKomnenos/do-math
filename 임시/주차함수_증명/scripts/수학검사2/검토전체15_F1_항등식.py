# 2장의 정확한 표현들을 직접 모사값과 대조한다 (어떤 본문 공식도 입력으로 쓰지 않는 DP/전수 열거가 기준).
from fractions import Fraction as Fr
from math import comb, factorial
from collections import defaultdict
import itertools
def rows(n):
    cur={(0,0):1}
    for car in range(n):
        nxt=defaultdict(int)
        for (occ,M),cnt in cur.items():
            for a in range(n):
                p=a
                while p<n and (occ>>p)&1: p+=1
                if p==n: continue
                nxt[(occ|(1<<p),max(M,p-a))]+=cnt
        cur=nxt
    b=[0]*n
    for (occ,M),cnt in cur.items(): b[M]+=cnt
    return b
NMAX=14
B={0:[]}
for n in range(1,NMAX+1): B[n]=rows(n)
def p(n): return (n+1)**(n-1) if n>=1 else 1
def b(n,l): return B[n][l] if 0<=l<n else (1 if (n==0 and l==0) else 0)
def A(n,l):
    if l<0: return 0
    if n==0: return 1
    return sum(B[n][:min(l,n-1)+1])
# (1) 마지막 차 재귀
ok=all(A(n,l)==sum(comb(n-1,j)*min(j+1,l+1)*A(j,l)*A(n-1-j,l) for j in range(n)) for n in range(1,13) for l in range(0,n+1))
print("old-2-6 마지막 차 재귀 n<=12:",ok)
# (2) 가장 큰 나무 사슬 공식 old-2-13: A_{n,l} = p_n pi0_n(l+1) + sum_{m=l+2}^n C(n,m)(l+1)A_{m-1,l}p_{n-m}, n<=2l+3
def forests_small(n,y):  # 나무 크기 모두 <= y 인 뿌리 숲 수 (지수 공식, 정확 유리수)
    # F[n] = sum_{t=1}^{min(n,y)} C(n-1,t-1) t^{t-1} F[n-t]  (라벨 1 을 담은 나무 크기 t)
    F=[1]+[0]*n
    for m in range(1,n+1):
        F[m]=sum(comb(m-1,t-1)*t**(t-1)*F[m-t] for t in range(1,min(m,y)+1))
    return F[n]
ok=True
for l in range(0,6):
    for n in range(1,min(2*l+3,NMAX)+1):
        lhs=A(n,l); rhs=forests_small(n,l+1)+sum(comb(n,m)*(l+1)*A(m-1,l)*p(n-m) for m in range(l+2,n+1))
        if lhs!=rhs: ok=False; print(" fail",l,n,lhs,rhs)
print("old-2-13 사슬 공식 (l<=5, n<=2l+3):",ok)
# (3) 다섯 몫 분해 old-2-40, k=2..4, 2k+1<=n<=3k-1 ; PAIR 는 명제 old-2-41 정수 꼴
def bT(t,l):  # 크기 t 나무 중 최대변위 정확히 l
    N=lambda t,l: (min(t,l+1)*A(t-1,l)) if t>=1 else 0
    return N(t,l)-N(t,l-1)
ok=True
for k in range(2,5):
    for n in range(2*k+1,3*k):
        d=b(n,k)-b(n,k-1)
        Theta=comb(n,k)*k**(k-2)*A(n-k,k-1)
        FL=sum(comb(n,t)*(bT(t,k)-bT(t,k-1))*A(n-t,k-1) for t in range(k+1,2*k+2))
        BV=sum(comb(n,m+1)*p(n-1-m)*(b(m,k)+b(m,k-1)) for m in range(2*k+1,n))
        KD=sum(comb(n,m+1)*p(n-1-m)*k*(b(m,k)-b(m,k-1)) for m in range(2*k+1,n))
        PAIR=Fr(1,2)*sum(Fr(factorial(n),factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1,k)*bT(t2,k)+bT(t1,k-1)*bT(t2,k-1))*p(n-t1-t2) for t1 in range(1,n) for t2 in range(1,n-t1+1))
        if d!=-Theta+FL+BV+KD+PAIR: ok=False; print(" fail",k,n,d,-Theta+FL+BV+KD+PAIR)
print("old-2-40 다섯 몫 분해 k=2..4:",ok)
# (4) 지정 사슬 전개 chain-expansion (라): b_{n,n-r-1}-b_{n,n-r} = sum_j (-1)^{j+1} Q_{n,r,j}; 또 Q1-Q2 <= .. <= Q1
def W(n,g):
    tj=n+1-sum(g)
    num=factorial(n)*tj**(tj-1)*g[0]**(g[0]-1)
    for gi in g[1:]: num*=gi**gi
    den=factorial(tj)*factorial(g[0]-1)
    for gi in g[1:]: den*=factorial(gi)
    return Fr(num,den)
def compositions(total,j):
    if j==1: yield (total,); return
    for first in range(1,total-j+2):
        for rest in compositions(total-first,j-1): yield (first,)+rest
ok=True; ok2=True
for n in range(3,NMAX+1):
    for r in range(1,(n-1)//2+1):
        Q=[]
        for j in range(1,r+2):
            s=Fr(0)
            for tot in range(j,r+2):
                for g in compositions(tot,j):
                    ts=[n+1-sum(g[:i+1]) for i in range(j)]
                    def prod(d):
                        v=Fr(1)
                        for t in ts: v*=Fr(max(d-(n+1-t),0),t)
                        return v
                    s+=W(n,g)*(prod(r+2)-2*prod(r+1)+prod(r))
            Q.append(s)
        lhs=b(n,n-r-1)-b(n,n-r)
        rhs=sum((-1)**(j)*Q[j] for j in range(len(Q)))  # j index 0 -> sign +
        if lhs!=rhs: ok=False; print(" fail",n,r,lhs,rhs)
        if not (Q[0]-(Q[1] if len(Q)>1 else 0)<=lhs<=Q[0]): ok2=False; print(" bound fail",n,r)
        if Q[0]!=comb(n,r)*(n-r)**(n-r-2)*(r+1)**r: ok=False; print(" Q1 closed form fail",n,r)
print("chain-expansion (라) 항등식 n<=14:",ok," moving-tail (가) 상하계:",ok2)
# (5) 동률-막힘 항등식 old-2-28 과 보조정리 old-2-30 (B<=J, n<=2k-1 등식, n=2k 보정 Xi) : n<=7 전수
def h(sig):
    n=len(sig); out=[]
    for i in range(1,n+1):
        js=[j for j in range(1,i) if sig[j-1]>sig[i-1]]
        out.append(i-(max(js) if js else 0))
    return out
ok=True; okJ=True
for n in range(1,8):
    perms=list(itertools.permutations(range(1,n+1)))
    for k in range(1,n+1):
        E=0; Bk=0
        for sig in perms:
            hs=h(sig)
            # 섬유의 변위 벡터 전수
            for dv in itertools.product(*[range(x) for x in hs]):
                M=max(dv); cnt=sum(1 for x in dv if x==M)
                if M==k and cnt%2==0 and cnt>0: E+=1
                if M==k-1 and all(hs[i]==k for i,x in enumerate(dv) if x==M): Bk+=1
        d=b(n,k)-b(n,k-1)
        if d!=2*E-Bk: ok=False; print(" fail 2E-B",n,k,d,2*E,Bk)
        # J_n(k-1), 첫 식 B
        J=0; B1=0
        for sig in perms:
            hs=h(sig); Z=sum(1 for x in hs if x>k); H=sum(1 for x in hs if x==k)
            pr=1
            for x in hs:
                if x<k: pr*=x
            J+=H*k**(H-1)*(k-1)**Z*pr if H>0 else 0
            B1+=pr*(k-1)**Z*(k**H-(k-1)**H)
        if B1!=Bk or Bk>J: okJ=False; print(" fail B/J",n,k,Bk,B1,J)
        if n<=2*k-1 and Bk!=J: okJ=False; print(" fail eq",n,k)
        if n==2*k and J-Bk!=comb(2*k-1,k-1)*p(k-1)**2: okJ=False; print(" fail Xi",n,k,J-Bk)
print("old-2-28 2E-B (n<=7):",ok," old-2-30 B,J,Xi:",okJ)
# (6) b-top: b_{k,k-1}=k^{k-2}
print("b-top:",all(b(k,k-1)==k**(k-2) for k in range(2,NMAX+1)))
