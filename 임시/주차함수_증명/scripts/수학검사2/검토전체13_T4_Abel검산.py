# T4 검산(추가): 명제 5-22의 Abel 재배열 항등식과, IH가 실제로 성립하는 위치에서의 환원 부등식.
from fractions import Fraction as Fr
from math import comb, floor
from mpmath import mp, mpf
mp.dps = 40
def pf(n): return 1 if n == 0 else (n+1)**(n-1)
def pi_n(n, t): return Fr(comb(n, t)*t**(t-1)*pf(n-t), pf(n))
A = {}
def Aval(n, l):
    if l < 0: return 0
    if n <= l+1: return pf(n)
    if (n, l) in A: return A[(n, l)]
    assert n <= 2*l+3
    pi0 = 1 - sum(pi_n(n, m) for m in range(l+2, n+1))
    val = pf(n)*pi0 + sum(comb(n, m)*(l+1)*Aval(m-1, l)*pf(n-m) for m in range(l+2, n+1))
    A[(n, l)] = int(val); return A[(n, l)]
def s(m, y): return Fr(Aval(m, y-1), pf(m)) if y >= 1 else Fr(0)
def c(m, Y): return s(m, Y+1) - s(m, Y)
def sT(t, Y): return Fr(1) if t <= Y else Fr(Y*Aval(t-1, Y-1), t**(t-1))
def x(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)
def t0(y):
    t = y + 2
    while not (y <= (t-1) - floor(0.75*(t-1)**(2/3))): t += 1
    return t
# (1) Abel 항등식 (정확)
bad = 0
for n in range(5, 30):
    for y in range((n+2)//2, n):
        lhs = c(n, y) - c(n, y-1)
        P = sum(x(t, y) for t in range(y, n+1))
        rhs = pi_n(n, y)*P + sum((pi_n(n, s_+1) - pi_n(n, s_))*sum(x(t, y) for t in range(s_+1, n+1)) for s_ in range(y, n))
        if lhs != rhs: bad += 1
print("Abel 재배열 항등식 n<=29: 위반", bad)
# (2) IH가 성립하는 위치에서 5-22의 부등식 (정확)
checked = 0; bad = 0; ex = []
for n in range(30, 110):
    for y in range((n+2)//2, n):
        T0 = t0(y)
        if T0 > n: continue
        if not all(c(m, y) >= c(m, y-1) for m in range(T0-1, n)): continue
        checked += 1
        P = sum(x(t, y) for t in range(y, n+1))
        WIN = sum((pi_n(n, t) - pi_n(n, y))*max(-x(t, y), Fr(0)) for t in range(y+1, T0))
        POS = sum((pi_n(n, m+1) - pi_n(n, T0-1))*(c(m, y) + c(m, y-1))/Fr(m+1) for m in range(T0-1, n))
        if c(n, y) - c(n, y-1) < pi_n(n, y)*P - WIN + POS: bad += 1
        if len(ex) < 3: ex.append((n, y, T0))
print(f"5-22 환원 부등식: IH 성립 위치 {checked}개(n<110) 검사, 위반 {bad}; 예 {ex}")
