# 검토전체21 R3: 작은 n에서 행 b_{n,l}을 정확 정수로 계산해
#  (1) 단봉성, (2) 첫째 조각 사슬 b_{n,0}<...<b_{n,k_n-1}이 깨지는 n,
#  (3) 명제 witness-position-bound 의 값  n+1-l* - 0.59963(n+1)^{2/3} - 1.24847(n+1)^{1/3}
# 를 확인한다. 재귀: 정리 2.old-2-6  A_{n,l} = sum_j C(n-1,j) min(j+1,l+1) A_{j,l} A_{n-1-j,l}
import sys, math
from math import comb
N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
# A[l][n]
A = {}
for l in range(0, N):
    row = [1]  # A_{0,l}=1
    for n in range(1, N+1):
        s = 0
        for j in range(0, n):
            s += comb(n-1, j) * min(j+1, l+1) * row[j] * row[n-1-j]
        row.append(s)
    A[l] = row
def b(n, l):
    if l < 0: return 0
    if l >= n: return 0
    prev = A[l-1][n] if l-1 >= 0 else 0
    return A[l][n] - prev
broken = []
nonunimodal = []
vals = []
for n in range(1, N+1):
    row = [b(n, l) for l in range(n)]
    # unimodal check & smallest witness
    # find first decrease
    lstar = None
    for i in range(n-1):
        if row[i] > row[i+1]:
            lstar = i; break
    if lstar is None: lstar = n-1
    uni = all(row[i] >= row[i+1] for i in range(lstar, n-1))
    if not uni: nonunimodal.append(n)
    kn = math.ceil(n/2)
    chain = all(row[i] < row[i+1] for i in range(0, kn-1))
    if not chain and n >= 3: broken.append(n)
    if n >= 50:
        v = n+1-lstar - 0.59963*(n+1)**(2/3) - 1.24847*(n+1)**(1/3)
        vals.append((n, lstar, v))
    if n <= 15:
        print(n, 'l*=', lstar, 'unimodal', uni, 'chain', chain)
print('nonunimodal n:', nonunimodal)
print('chain broken n (n>=3):', broken)
if vals:
    print('witness values: min', min(v for _,_,v in vals), 'max', max(v for _,_,v in vals))
    print('first few:', vals[:5])
    print('last few:', vals[-3:])
