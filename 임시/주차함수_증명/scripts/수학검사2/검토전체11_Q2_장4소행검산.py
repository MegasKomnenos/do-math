# Q2: 4장 작은 n 검산 — 정리 4.5의 2<=n<=15 부호와 P_C, 4.8(나)의 b_{n,k_n}<b_{n,k_n+1} (n<=NMAX), 4.9의 Q_L(n) (3<=n<=15)
from math import comb
NMAX = 200
A = [[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1): A[0][l] = 1
for n in range(1, NMAX+1):
    pn = (n+1)**(n-1)
    for l in range(NMAX+1):
        if l >= n-1: A[n][l] = pn
        else:
            s = 0
            for j in range(n):
                s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
            A[n][l] = s
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
def kn(n): return -(-n//2)
bad=[]
for n in range(2, NMAX+1):
    k=kn(n); d=b(n,k)-b(n,k-1)
    if n<=15:
        if not d<0: bad.append(("d<0 fails",n))
        if not all(b(n,j)>=b(n,j+1) for j in range(k, n-1)): bad.append(("PC fails",n))
    else:
        if not d>0: bad.append(("d>0 fails",n))
    if n>=20:
        if not (b(n,k)<b(n,k+1) and k+1<=n-2): bad.append(("4.8(나) fails",n))
    if 3<=n<=15:
        # Q_L(n): for 2l<=n-2: b_l>b_{l+1} => b_{l+1}^2>=b_l b_{l+2}
        for l in range(0, n-2):
            if 2*l<=n-2 and b(n,l)>b(n,l+1) and not b(n,l+1)**2>=b(n,l)*b(n,l+2): bad.append(("QL fails",n,l))
print("failures:", bad)
# check n=16..19: is b_{n,k_n}<b_{n,k_n+1}? (the text starts at n>=20)
for n in range(14, 22):
    k=kn(n); print(n, k, "d_{n,k_n}=", b(n,k)-b(n,k-1), " b_k<b_{k+1}:", b(n,k)<b(n,k+1), " witness:", [l for l in range(n) if b(n,l)==max(b(n,l2) for l2 in range(n))])
