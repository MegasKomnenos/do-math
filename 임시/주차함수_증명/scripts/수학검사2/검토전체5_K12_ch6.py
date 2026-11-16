# K12: D.theorem-D-base extreme ratios, D.prop-W-thirteen values, D.tilt-sum-small-k sums and B_2
import sys, io, time
from fractions import Fraction
from math import comb, factorial
import mpmath as mp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mp.mp.dps = 40
# --- theorem-D-base: q(m,d) = m b_{m,m-d} / (p_m Psi(d)) at (4,1), (3,1), (689,39) via complement recursion
p = [(n+1)**(n-1) if n > 0 else 1 for n in range(0, 800)]
def Ac_col(l, N):
    Ac = [0]*(N+1)
    for n in range(l+2, N+1):
        s = sum(comb(n-1, j)*(j-l)*p[j]*p[n-1-j] for j in range(l+1, n))
        s += sum(Ac[i]*comb(n-1, i)*p[n-1-i]*((l+1)+min(n-i, l+1)) for i in range(l+2, n))
        Ac[n] = s
    return Ac
def Psi(d): return mp.fsum(mp.mpf(j)**j*mp.e**(-j)/mp.factorial(j) for j in range(1, d+1))
def q_of(m, d):
    l = m-d
    A1 = Ac_col(l-1, m) if l-1 >= 0 else None
    A2 = Ac_col(l, m)
    b = (A1[m] if A1 is not None else p[m]) - A2[m]
    return mp.mpf(m)*b/(mp.mpf(p[m])*Psi(d)), b
t = time.time()
for (m, d) in ((3, 1), (4, 1), (689, 39)):
    q, b = q_of(m, d)
    print(f"q({m},{d}) = {mp.nstr(q, 14)}  (b_{{m,m-d}} digits {len(str(b))})")
print("time", round(time.time()-t, 1))
# --- prop-W-thirteen
def eRen(r1): return mp.mpf(r1)**(r1-1)/(mp.e**(r1-1)*mp.factorial(r1-1))  # e*Ren(r1) = r1^{r1-1}/(e^{r1-1}(r1-1)!)
k = 3131
for d in range(1, 15):
    L = (k-1)*(eRen(d+1) - mp.mpf(60)*(d+1)/(k+d))
    R = 2*(1 + mp.fsum(eRen(r+1) + mp.mpf(60)*(r+1)/(k+d) for r in range(1, d)))
    print(f"d={d}: L={mp.nstr(L,6)}, R={mp.nstr(R,4)}, L>R: {L > R}")
# --- tilt-sum-small-k
def S(k):
    return sum(Fraction(n**(n-1), factorial(n))*Fraction(k, k+1)**((k-1)*n) for n in range(2, k+2))
def B2(k): return (1-1/mp.e) + (mp.e**(mp.mpf(3)/2+mp.mpf(1)/k)-1)*2*(mp.sqrt(k+1)-1)/(mp.sqrt(2*mp.pi)*(k+1))
mx = max((S(k), k) for k in range(2, 61))
print("tilt-sum: all <1 for 2<=k<=60:", all(S(k) < 1 for k in range(2, 61)), "max", mx[0], "at k=", mx[1])
for k in (3, 10, 20, 42, 43): print(f"  k={k}: sum={mp.nstr(mp.mpf(S(k).numerator)/S(k).denominator, 7)}")
print("B2(42)=", mp.nstr(B2(42), 7), " B2(43)=", mp.nstr(B2(43), 7), " B2(2000)=", mp.nstr(B2(2000), 5))
