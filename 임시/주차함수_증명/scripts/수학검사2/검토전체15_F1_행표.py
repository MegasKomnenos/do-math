# 장1 1.3절 표(n<=10)와 1.4절 "2<=n<=15에서 d_{n,k_n}<0, n>=16에서 >0" 주장을
# 주차 과정의 직접 모사(점유 비트마스크 DP)로 검산한다. 어떤 공식에도 기대지 않는다.
import sys
from collections import defaultdict
def rows(n):
    # 상태: (점유 비트마스크, 지금까지의 최대 변위) -> 가짓수
    full = (1<<n)-1
    cur = {(0,0):1}
    for car in range(n):
        nxt = defaultdict(int)
        for (occ,M),cnt in cur.items():
            for a in range(n):
                p = a
                while p < n and (occ>>p)&1: p += 1
                if p == n: continue
                nxt[(occ|(1<<p), max(M,p-a))] += cnt
        cur = nxt
    b = [0]*n
    for (occ,M),cnt in cur.items():
        assert occ == full
        b[M] += cnt
    return b
N = int(sys.argv[1]) if len(sys.argv)>1 else 16
for n in range(1,N+1):
    b = rows(n)
    kn = (n+1)//2
    peaks = [i for i in range(n) if b[i]==max(b)]
    uni = all(b[i]<=b[i+1] for i in range(peaks[0])) and all(b[i]>=b[i+1] for i in range(peaks[0],n-1))
    d_mid = (b[kn]-b[kn-1]) if kn<=n-1 else None
    print(n, b if n<=10 else "...", "sum",sum(b),"=(n+1)^(n-1)?",sum(b)==(n+1)**(n-1), "unimodal",uni,"minwitness",peaks[0],"d_{n,k_n}",d_mid)
