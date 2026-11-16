# 정리 2-28 (d=2E-B), e_n=2E2, 보조정리 2-30 (B 식, B<=J, n=2k에서 B=J-Xi) 전수 검산 n<=7
import itertools,sys,io
from math import comb
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def park(a):
    n=len(a); occ=[0]*(n+2); pos=[0]*n
    for idx,x in enumerate(a):
        p=x
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=idx+1; pos[idx]=p
    return pos,occ
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=max([j for j in range(1,i) if sig[j-1]>sig[i-1]]+[0]); h.append(i-z)
    return h
p=lambda m:(m+1)**(m-1) if m>0 else 1
bad=0
for n in range(1,8):
    b=[0]*(n+1); E=[0]*(n+1); E2=[0]*(n+1); B=[0]*(n+1)
    for a in itertools.product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        pos,occ=r; d=[pos[i]-a[i] for i in range(n)]; M=max(d); cnt=d.count(M)
        b[M]+=1
        if cnt%2==0: E[M]+=1
        if cnt==2: E2[M]+=1
        sig=occ[1:n+1]; h=caps(sig)
        # 막힘: 변위 M인 모든 차의 자리 i에서 h_i=M+1
        if all(h[pos[i]-1]==M+1 for i in range(n) if d[i]==M): B[M]+=1
    for k in range(1,n+1):
        dnk=b[k]-b[k-1]
        if dnk!=2*E[k]-B[k-1]: bad+=1; print('2-28 FAIL',n,k)
        if 2*E2[k]-B[k-1]>dnk: bad+=1; print('2-29 FAIL',n,k)
        # J_n(k-1), B 식
        J=0; Bf=0
        for sig in itertools.permutations(range(1,n+1)):
            h=caps(sig); Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
            pr=1
            for x in h:
                if x<k: pr*=x
            J+=H*k**(H-1)*(k-1)**Z*pr if H>0 else 0
            Bf+=pr*(k-1)**Z*(k**H-(k-1)**H)
        if Bf!=B[k-1]: bad+=1; print('2-30 B식 FAIL',n,k,Bf,B[k-1])
        if B[k-1]>J: bad+=1; print('B<=J FAIL',n,k)
        if n<=2*k-1 and B[k-1]!=J: bad+=1; print('B=J FAIL',n,k)
        if n==2*k and J-B[k-1]!=comb(2*k-1,k-1)*p(k-1)**2: bad+=1; print('Xi FAIL',n,k,J-B[k-1])
    print(n,'b',b[:n],'E',E[:n],'E2',E2[:n],'B',B[:n])
print('bad',bad)
