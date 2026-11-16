# O2 검산: 3장 수치 (행 n<=10 증인, n=80 로그오목, n=780 누적 로그오목 일부, 정리 3.6 유리수, 멜린 꼬리 상수)
from fractions import Fraction
from math import comb, gamma, sqrt, pi
import sys

def A_table(nmax, lmax):
    # A[n][l] for 0<=n<=nmax, 0<=l<=lmax via last-car recursion
    A = [[0]*(lmax+1) for _ in range(nmax+1)]
    for l in range(lmax+1):
        A[0][l] = 1
    for n in range(1, nmax+1):
        for l in range(lmax+1):
            if l >= n-1:
                A[n][l] = (n+1)**(n-1)
            else:
                s = 0
                for j in range(n):
                    s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
                A[n][l] = s
    return A

# 1) rows n<=10, witnesses
A = A_table(10, 10)
for n in range(1, 11):
    row = [A[n][l] - (A[n][l-1] if l>=1 else 0) for l in range(n)]
    assert sum(row) == (n+1)**(n-1)
    mx = max(row)
    wit = [l for l in range(n) if row[l]==mx]
    # peak position vs ceil(n/2)
    kn = -(-n//2)
    print(n, row, "witnesses", wit, "ceil(n/2)=", kn, "all < kn:", all(w<kn for w in wit))

# 2) n=80 log-concavity: need A[n][l] for n<=80, l<=79
A = A_table(80, 79)
first = None
for n in range(1, 81):
    row = [A[n][l] - (A[n][l-1] if l>=1 else 0) for l in range(n)]
    assert sum(row) == (n+1)**(n-1)
    assert all(x>0 for x in row)
    for l in range(1, n-1):
        if row[l]**2 < row[l-1]*row[l+1]:
            if first is None:
                first = (n, l)
            print("LC fail", n, l)
print("first LC failure", first)
row80 = [A[80][l] - (A[80][l-1] if l>=1 else 0) for l in range(80)]
print("b80,39<b80,40<b80,41:", row80[39] < row80[40] < row80[41])
print("ratios", row80[40]/row80[39], row80[41]/row80[40])
print("b80,39 =", row80[39])

# 3) Theorem 3.6 rational
lam = Fraction(751, 1000)
J = 8
val = lam**J + Fraction(1,31)*sum(i*lam**(i-1) for i in range(1, J+1)) + Fraction(1,1000)*sum((i-1)*lam**(i-1) for i in range(1, J+1))
print("3.6 value", val, float(val), val == Fraction(7309649993107890414228499, 15500000000000000000000000))
# E_n omega_n for n<=5
def Eomega(n):
    p = lambda m: (m+1)**(m-1) if m>=0 else 0
    return sum(Fraction(comb(n,j)*j**j*p(n-j), p(n)) for j in range(1, n//2+1))
print("Eomega", [Eomega(n) for n in range(1,6)])
# quadratic
print("9n^2-48n-32 at 6:", 9*36-48*6-32)
# ceil(3n/4)<=n-1 for n>=4
print("ceil(3n/4)<=n-1 check n=4..20:", all(-(-3*n//4) <= n-1 for n in range(4,21)))

# 4) Mellin tail constant: E X^s = (3/2)^{s/3} G(1+2s/3) G(5/6-s/3)/G(5/6) * G(1/2-s/3)G(2/3)/(G(1/2)G(2/3-s/3))
def mellin(s):
    return (1.5)**(s/3)*gamma(1+2*s/3)*gamma(5/6-s/3)/gamma(5/6)*gamma(0.5-s/3)*gamma(2/3)/(gamma(0.5)*gamma(2/3-s/3))
# near s=3/2: E X^s ~ (3/2) C /(3/2 - s) if P(X>x)~C x^{-3/2}
for d in [1e-3, 1e-5]:
    s = 1.5-d
    print("C estimate", mellin(s)*d/1.5, "expected sqrt(2/pi)=", sqrt(2/pi))
# Legendre duplication check
print("G(1/3)G(5/6) vs 2^{1/3}sqrt(pi)G(2/3):", gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
# normalization
print("mellin(0)=", mellin(0))
# density near 0: pole at s=-3/2 => f(x) ~ c x^{1/2}
