# 독립 재계산: A_{n,l} = 모든 변위가 l 이하인 길이 n 주차함수 수. 점유 집합 DP (차 순서대로 선호 자리 선택).
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)
def A(n, l):
    if l < 0: return 0
    full = (1<<n)-1
    @lru_cache(None)
    def f(S):
        if S == full: return 1
        tot = 0
        for a in range(n):
            p = a
            while p < n and (S>>p)&1: p += 1
            if p < n and p - a <= l:
                tot += f(S | (1<<p))
        return tot
    return f(0)
for n in range(1, 17):
    As = [A(n,l) for l in range(-1, n)]
    b = [As[i+1]-As[i] for i in range(n)]
    pk = max(range(n), key=lambda i: b[i])
    # 단봉 확인 & 가장 작은 증인
    lstar = None
    for w in range(n):
        if all(b[i]<=b[i+1] for i in range(w)) and all(b[i]>=b[i+1] for i in range(w, n-1)):
            lstar = w; break
    kn = (n+1)//2
    d = b[kn]-b[kn-1] if kn <= n-1 else None
    print(n, b, 'sum', sum(b), (n+1)**(n-1), 'l*', lstar, 'd_{n,k_n}', d)
