# K12: position/pair counts of D.exact-n20000 and D.c50; margin at (13,6); EGF formula of D.exact-n20000 (ㄱ) for small k
import math
from fractions import Fraction
from math import comb, factorial, ceil
def kn(n): return (n+1)//2
# (ㄹ) positions 5<=n<=20000: (n-1)/2 <= l <= n-3
pos = lambda n: max(0, (n-3) - ceil((n-1)/2) + 1)
pairs = lambda n: max(0, (n-2) - ceil((n-1)/2) + 1)
print("C20 positions", sum(pos(n) for n in range(5, 20001)), "pairs", sum(pairs(n) for n in range(5, 20001)), "rows", 20000-5+1)
print("C50 positions", sum(pos(n) for n in range(20001, 50001)), "pairs", sum(pairs(n) for n in range(20001, 50001)))
print("n<=2000 positions", sum(pos(n) for n in range(5, 2001)))
# (ㄱ) counts
c1 = sum(10000-12+1 for k in range(2, 6)) + sum(10000-2*k for k in range(6, 121))
print("(ㄱ) k=2..120 comparisons", c1, "; k<=5 each", 10000-12+1)
print("(ㄱ) row cert 501..4999", sum(10000-2*k for k in range(501, 5000)))
print("(ㄴ) comparisons", sum(kn(n)-1 for n in range(10001, 20001)))
print("(ㅂ) rows", 20000-50+1)
# exact rows n<=16 via last-car recursion; margin at (n,k)=(13,6)
p = [(n+1)**(n-1) if n > 0 else 1 for n in range(0, 40)]
def colA(l, N):
    A = [1]
    for n in range(1, N+1):
        if l >= n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1, j)*min(j+1, l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
A = {l: colA(l, 30) for l in range(0, 30)}
def Aof(n, l): return A[l][n] if l >= 0 else 0
n, k = 13, 6
d = Aof(n, k) - 2*Aof(n, k-1) + Aof(n, k-2)
den = Aof(n, k) + 2*Aof(n, k-1) + Aof(n, k-2)
print("margin (13,6) = d/(A_k+2A_{k-1}+A_{k-2}) =", "%.4e" % (d/den))
# EGF formula check: T_k, G_k=e^{T_k}, Q_k=sum_{j<k} p_j x^j/j!, H' = k Q H + k (G - Q), E = G/(1-H); compare e_n with A_{n,k-1}/n! (rc=1)
N = 22
def mul(a, b):
    c = [Fraction(0)]*(N+1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(0, N+1-i): c[i+j] += ai*b[j]
    return c
def expo(a):  # a[0]=0
    e = [Fraction(0)]*(N+1); e[0] = Fraction(1)
    # e' = a' e
    da = [(i+1)*a[i+1] for i in range(N)] + [Fraction(0)]
    for n in range(1, N+1):
        e[n] = sum(da[i]*e[n-1-i] for i in range(n)) / n
    return e
for k in (2, 3, 5):
    T = [Fraction(0)]*(N+1)
    for j in range(1, k+1): T[j] = Fraction(j**(j-1), factorial(j))
    G = expo(T)
    Q = [Fraction(0)]*(N+1)
    for j in range(0, k): Q[j] = Fraction(p[j], factorial(j))
    GmQ = [G[i]-Q[i] for i in range(N+1)]
    H = [Fraction(0)]*(N+1)
    for n in range(1, N+1):  # H_n = (1/n) [x^{n-1}] (k Q H + k (G-Q))
        s = k*sum(Q[i]*H[n-1-i] for i in range(n)) + k*GmQ[n-1]
        H[n] = s / n
    # E = G/(1-H): E = G + H E
    E = [Fraction(0)]*(N+1)
    for n in range(0, N+1):
        E[n] = G[n] + sum(H[i]*E[n-i] for i in range(1, n+1))
    ok = all(E[n] == Fraction(A[k-1][n], factorial(n)) for n in range(0, N+1))
    print(f"k={k}: E_n == A_(n,k-1)/n! for n<={N}:", ok, "" if ok else [(n, E[n], Fraction(A[k-1][n], factorial(n))) for n in range(N+1) if E[n] != Fraction(A[k-1][n], factorial(n))][:3])
