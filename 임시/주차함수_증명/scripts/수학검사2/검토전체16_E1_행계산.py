# E1 검산: A_{n,l} = sum over outcome permutations of prod min(cap_j, l+1)
# f_l(m) = sum_p C(m-1,p-1) f_l(p-1) f_l(m-p) min(p, l+1), f_l(0)=1  (max element at position p; wall to the left)
from math import comb, ceil
import sys
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20
def A_row(n):
    # returns A_{n,l} for l=0..n-1
    out = []
    for l in range(n):
        f = [1] + [0]*n
        for m in range(1, n+1):
            s = 0
            for p in range(1, m+1):
                s += comb(m-1, p-1) * f[p-1] * f[m-p] * min(p, l+1)
            f[m] = s
        out.append(f[n])
    return out
rows = {}
for n in range(1, NMAX+1):
    A = A_row(n)
    b = [A[0]] + [A[l]-A[l-1] for l in range(1, n)]
    rows[n] = b
    assert sum(b) == (n+1)**(n-1), n
    kn = ceil(n/2)
    d = b[kn] - b[kn-1] if kn <= n-1 else None
    # unimodal? smallest witness
    peaks = [i for i in range(n) if all(b[j] <= b[j+1] for j in range(i)) and all(b[j] >= b[j+1] for j in range(i, n-1))]
    lc_fail = [l for l in range(1, n-1) if b[l]**2 < b[l-1]*b[l+1]]
    Alc_fail = [l for l in range(1, n-1) if A[l]**2 < A[l-1]*A[l+1]]
    if n <= 10:
        print(n, b, sum(b))
    print(f"n={n} k_n={kn} d(n,k_n)={d} smallest_witness={peaks[0] if peaks else None} unimodal={bool(peaks)} b_logconcave_fail={lc_fail} A_lc_fail={Alc_fail}")
