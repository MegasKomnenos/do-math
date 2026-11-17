# R2 검산: e_n > J_n(k-1) (n in {2k-1,2k}), 정확 정수, 작은 범위
from math import comb
from fractions import Fraction as Fr
NMAX = 420
binom = [[comb(n, j) for j in range(n+1)] for n in range(NMAX+1)]
p = [1] + [(n+1)**(n-1) for n in range(1, NMAX+1)]
def e_and_J(k, N):
    # K_n mod (y-k)^3
    K = [(1, 0, 0)]
    for n in range(1, N+1):
        a0 = a1 = a2 = 0
        bn = binom[n-1]
        for j in range(n):
            x0, x1, x2 = K[j]; y0, y1, y2 = K[n-1-j]
            c0 = x0*y0; c1 = x0*y1 + x1*y0; c2 = x0*y2 + x1*y1 + x2*y0
            if j+1 <= k:
                w = (j+1)*bn[j]
                a0 += w*c0; a1 += w*c1; a2 += w*c2
            else:
                w = bn[j]
                a0 += w*k*c0; a1 += w*(k*c1 + c0); a2 += w*(k*c2 + c1)
        K.append((a0, a1, a2))
    yv = k-1
    J = [0]*(N+1)
    for n in range(k, N+1):
        s = 0
        for i in range(n):
            if n-1-i >= k:
                s += binom[n-1][i]*(yv+i+1)*p[i]*J[n-1-i]
        s += binom[n-1][k-1]*p[k-1]*p[n-k]
        J[n] = s
    return K, J
minratio = None
for k in range(1, 201):
    K, J = e_and_J(k, 2*k)
    for n in (2*k-1, 2*k):
        if n < 2: continue
        e = 2*K[n][2]
        gt = e > J[n]
        if (n >= 16 and not gt) or (n < 16 and gt):
            print("unexpected", n, k, gt)
        if n >= 16:
            r = Fr(e, J[n])
            if minratio is None or r < minratio[0]: minratio = (r, n)
        if n in (15, 16, 17, 400):
            print(n, k, "e>J:", gt, "ratio", float(Fr(e, J[n])))
print("min ratio over 16<=n<=400:", float(minratio[0]), "at n=", minratio[1])
