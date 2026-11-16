# K3 검산 1: 행 재귀, 조각 수, 증인 상계, Cayley 비, 생일 평균, 원천 표현의 소규모 대조
import itertools, math, sys
from fractions import Fraction
from math import comb, factorial

sys.set_int_max_str_digits(0) if hasattr(sys,'set_int_max_str_digits') else None

def p(n): return (n+1)**(n-1) if n>=1 else 1

# --- brute force parking functions for small n ---
def brute(n):
    A = {}  # A[l]
    b = [0]*n
    E = [0]*(n+1); E2=[0]*(n+1); B=[0]*(n)
    for a in itertools.product(range(1,n+1), repeat=n):
        occ=[0]*(n+2); pos=[0]*n; ok=True
        for car,pref in enumerate(a):
            s=pref
            while s<=n and occ[s]: s+=1
            if s>n: ok=False;break
            occ[s]=car+1; pos[car]=s
        if not ok: continue
        disp=[pos[c]-a[c] for c in range(n)]
        M=max(disp); cnt=disp.count(M)
        b[M]+=1
        if cnt%2==0: E[M]+=1
        if cnt==2: E2[M]+=1
        # blocked: every car with disp M stands at i with h_i = M+1
        sigma=[occ[i] for i in range(1,n+1)]
        h=[0]*(n+1)
        for i in range(1,n+1):
            j=i-1
            while j>=1 and sigma[j-1]<sigma[i-1]: j-=1
            h[i]=i-j
        blocked=all(h[pos[c]]==M+1 for c in range(n) if disp[c]==M)
        if blocked: B[M]+=1
    return b,E,E2,B

# --- recurrence: A_{n,l} = sum_j min(j,l+1) C(n-1,j-1) A_{j-1,l} A_{n-j,l}
def A_table(N):
    # A[l][n]
    A=[[0]*(N+1) for _ in range(N+1)]
    for l in range(N+1):
        A[l][0]=1
        for n in range(1,N+1):
            s=0
            for j in range(1,n+1):
                s+=min(j,l+1)*comb(n-1,j-1)*A[l][j-1]*A[l][n-j]
            A[l][n]=s
    return A

N=7
A=A_table(N)
for n in range(1,N+1):
    b,E,E2,B=brute(n)
    rows=[A[l][n]-(A[l-1][n] if l>=1 else 0) for l in range(n)]
    assert rows==b, (n,rows,b)
    # 동률-막힘 항등식 d_{n,k}=2E_{n,k}-B_{n,k-1}
    for k in range(1,n):
        d=b[k]-b[k-1]
        assert d==2*E[k]-B[k-1], (n,k,d,E[k],B[k-1])
    print("brute ok n=",n,"row",b)
