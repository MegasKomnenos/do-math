# R11 검산: D.central-gap-integer (ㄴ) — n<=60 행의 한가운데 차분 부호와 오른쪽 절반 비증가
from math import comb
N = 60
A = [[1]*(N+1)]
for n in range(1, N+1):
    A.append([sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n)) for l in range(N+1)])
neg, pos, zero, rightok = [], [], [], []
for n in range(1, N+1):
    b = [A[n][l]-(A[n][l-1] if l else 0) for l in range(n+1)]   # b[n]=0
    kn = (n+1)//2
    if kn > n-1:
        print("n=%d: no position (k_n=%d > n-1)" % (n, kn)); continue
    d = b[kn]-b[kn-1]
    (neg if d < 0 else pos if d > 0 else zero).append(n)
    if d < 0:
        rightok.append(all(b[j] >= b[j+1] for j in range(kn, n-1)))
print("d<0:", neg); print("d=0:", zero); print("d>0:", pos[0], "..", pos[-1], len(pos))
print("right half nonincreasing for d<0 rows:", all(rightok))
