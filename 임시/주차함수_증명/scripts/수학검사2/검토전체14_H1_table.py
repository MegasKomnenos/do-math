# 1.3절 표(n<=10의 행 b_{n,l})와 1.2절 n=3 보기, 증인 위치를 DP로 다시 센다.
from collections import defaultdict
def rows(n):
    # 상태: (점유 비트마스크, 현재 최대 변위) -> 개수
    st = defaultdict(int); st[(0,0)] = 1
    for car in range(n):
        nst = defaultdict(int)
        for (occ,mx),c in st.items():
            for a in range(1,n+1):
                p=a
                while p<=n and (occ>>(p-1))&1: p+=1
                if p>n: continue
                nst[(occ|(1<<(p-1)), max(mx,p-a))]+=c
        st=nst
    b=[0]*n
    for (occ,mx),c in st.items(): b[mx]+=c
    return b
for n in range(1,11):
    b=rows(n); s=sum(b)
    peak=min(i for i in range(n) if b[i]==max(b))
    uni = all(b[i]<=b[i+1] for i in range(peak)) and all(b[i]>=b[i+1] for i in range(peak,n-1))
    print(n, b, s, (n+1)**(n-1), "unimodal" if uni else "NOT", "minwitness", peak)
