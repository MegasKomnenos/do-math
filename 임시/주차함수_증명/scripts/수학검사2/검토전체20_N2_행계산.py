# N2 검산: A_{n,l} 정확 정수 표 (n<=N) -> 3.4(로그오목 첫 실패), 4.5(d_{n,k_n} 부호), 4.8(나)(b_{n,k_n}<b_{n,k_n+1}), 1.3 표 증인
import sys
from math import comb
N = int(sys.argv[1]) if len(sys.argv)>1 else 300
p = [ (m+1)**(m-1) if m>=1 else 1 for m in range(N+1) ]
# A[l][m] for l in 0..N-1
A = {}
for l in range(0, N):
    row = [0]*(N+1)
    for m in range(0, N+1):
        if m <= l+1:
            row[m] = p[m]
        else:
            s = 0
            for t in range(1, m+1):
                Nt = min(t, l+1)*row[t-1]
                s += comb(m-1, t-1)*Nt*row[m-t]
            row[m] = s
    A[l] = row
def b(n,l):
    if l<0 or l>n-1: return 0
    return A[l][n] - (A[l-1][n] if l>=1 else 0)
out = []
# 합 검사
for n in range(1, N+1):
    assert sum(b(n,l) for l in range(n)) == p[n], n
out.append("row sums ok up to N=%d"%N)
# 1.3 표 증인
for n in range(1, 11):
    row = [b(n,l) for l in range(n)]
    mx = max(row); wit = [l for l in range(n) if row[l]==mx]
    out.append("n=%d row=%s witnesses=%s ceil(n/2)=%d"%(n,row,wit,(n+1)//2))
# 로그오목 첫 실패
first = None
for n in range(1, N+1):
    bad = [l for l in range(1, n-1) if b(n,l)**2 < b(n,l-1)*b(n,l+1)]
    if bad:
        out.append("logconcave fails n=%d at l=%s"%(n,bad))
        if first is None: first=n
        if n>=84: break
out.append("first logconcavity failure n=%s"%first)
l=40; out.append("n=80: b39=%d b40=%d b41=%d ; b40^2<b39*b41: %s ; increasing: %s"%(b(80,39),b(80,40),b(80,41), b(80,40)**2<b(80,39)*b(80,41), b(80,39)<b(80,40)<b(80,41)))
# 누적 로그오목 n<=N
cum_bad=[n for n in range(1,N+1) if any(A[l][n]**2 < A[l-1][n]*A[l+1][n] for l in range(1,n-1))]
out.append("cumulative logconcavity failures n<=%d: %s"%(N,cum_bad))
# d_{n,k_n}
neg=[]; pos_from=None
for n in range(2, N+1):
    k=(n+1)//2
    d=b(n,k)-b(n,k-1)
    if d<0: neg.append(n)
    elif d==0: out.append("d=0 at n=%d"%n)
out.append("d_{n,k_n}<0 for n in: %s"%neg)
# 2<=n<=15: k_n<=j<=n-2 nonincreasing?
for n in range(2,16):
    k=(n+1)//2
    ok=all(b(n,j)>=b(n,j+1) for j in range(k,n-1))
    if not ok: out.append("P_C small-n check FAILS n=%d"%n)
out.append("P_C small n check done")
# b_{n,k_n} < b_{n,k_n+1}
fail=[n for n in range(6,N+1) if not (b(n,(n+1)//2) < b(n,(n+1)//2+1))]
out.append("b_{n,k_n}<b_{n,k_n+1} fails for n in [6,%d]: %s"%(N,fail))
# 단봉성 n<=N 및 증인 >= ceil(n/2) 부터
nonuni=[]; wit_small=[]
for n in range(1,N+1):
    row=[b(n,l) for l in range(n)]
    mx=max(row); i=row.index(mx)
    uni = all(row[j]<=row[j+1] for j in range(i)) and all(row[j]>=row[j+1] for j in range(i,n-1))
    if not uni: nonuni.append(n)
    if i < (n+1)//2: wit_small.append(n)
out.append("non-unimodal n<=%d: %s"%(N,nonuni))
out.append("witness < ceil(n/2) for n: %s"%wit_small)
open(sys.argv[2] if len(sys.argv)>2 else "/dev/stdout","w").write("\n".join(out)+"\n")
