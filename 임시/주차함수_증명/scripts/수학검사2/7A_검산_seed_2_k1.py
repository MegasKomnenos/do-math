"""본문 328행 (라)의 k=1 손 증명: b_{n,1} >= (n-1) n!/2 를 n<=7 전수 열거로 확인한다.
구성한 수열(선호 j 두 번, j+1 없음, 나머지 한 번)이 주차함수이고 M=1 이며 j마다 n!/2 개, j가 다르면 서로소인지 확인한다."""
import itertools
from math import factorial


def park(pref, n):
    occ = [False] * n; md = 0
    for a in pref:
        p = a
        while p < n and occ[p]: p += 1
        if p == n: return None
        occ[p] = True; md = max(md, p - a)
    return md


def main():
    for n in range(2, 8):
        cnt = {}
        for pref in itertools.product(range(n), repeat=n):
            md = park(pref, n)
            if md is not None: cnt[md] = cnt.get(md, 0) + 1
        b0, b1 = cnt.get(0, 0), cnt.get(1, 0)
        constructed = set(); per_j = []
        for j in range(1, n):  # 선호 j (1-based) -> index j-1 ; j+1 -> index j
            vals = [j - 1, j - 1] + [v for v in range(n) if v not in (j - 1, j)]
            S = set(itertools.permutations(vals))
            assert len(S) == factorial(n) // 2
            assert all(park(p, n) == 1 for p in S)
            per_j.append(len(S)); assert constructed.isdisjoint(S); constructed |= S
        lb = (n - 1) * factorial(n) // 2
        print(f"n={n}: b_(n,0)={b0}=n!:{b0==factorial(n)}, b_(n,1)={b1}, constructed {len(constructed)} = (n-1)n!/2={lb}: {len(constructed)==lb}, b1>=lb: {b1>=lb}, b1>b0: {b1>b0} (needs n>=4: {(n-1)/2>1})")


if __name__ == '__main__':
    main()
