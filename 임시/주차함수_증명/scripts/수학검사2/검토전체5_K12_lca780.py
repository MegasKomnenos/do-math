# K12: D.cumulative-logconcavity -- columns 573..580 of A_{n,l} up to n=780, exact integers
import time
from math import comb
N = 780
p = [(n+1)**(n-1) if n > 0 else 1 for n in range(0, N+1)]
C = [[comb(n, j) for j in range(n+1)] for n in range(N)]
def col(l):
    A = [1]
    for n in range(1, N+1):
        if l >= n-1: A.append(p[n]); continue
        s = 0; c = C[n-1]
        for j in range(n):
            s += c[j]*min(j+1, l+1)*A[j]*A[n-1-j]
        A.append(s)
    return A
t = time.time()
A = {l: col(l) for l in range(573, 581)}
print("digits of A_{780,575}:", len(str(A[575][780])))
for n in (779, 780):
    for l in range(574, 580):
        D = A[l][n]**2 - A[l-1][n]*A[l+1][n]
        print(n, l, "sign", (D > 0)-(D < 0), "rel %.4e" % (D/A[l][n]**2))
print("time", round(time.time()-t, 1))
