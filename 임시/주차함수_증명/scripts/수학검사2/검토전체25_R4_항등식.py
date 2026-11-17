# 검토전체25 R4: 장5B의 항등식·부등식을 작은 n에서 정확 유리수로 대조
# (1) b_{n,l}을 n<=7에서 무차별 대입으로 세고, (2) 곱 공식 재귀(정리 2:old-2-10 꼴)와 맞춘 뒤
# (3) 재귀로 n<=NMAX까지 넓혀 보조정리 5:old-5-19, 명제 5:old-5-22, 따름정리 6:cor-L, 정리 2:old-2-38,
#     정리 5:old-5-33(창 폭 R 임의)의 꼴을 확인한다.
from fractions import Fraction as F
from itertools import product
from math import comb, factorial, exp
import sys

def brute(n):
    cnt = [0]*n
    for pref in product(range(n), repeat=n):
        occ = [False]*n; ok = True; M = 0
        for a in pref:
            j = a
            while j < n and occ[j]: j += 1
            if j == n: ok = False; break
            occ[j] = True
            if j-a > M: M = j-a
        if ok: cnt[M] += 1
    return cnt

NMAX = 46
# A[n][l] : 최대 변위 <= l 인 길이 n 주차함수 수. 재귀: 마지막 차 분해(가중 분배)
# A_{n,l} = sum_{j=1}^n C(n-1,j-1) * min(j,l+1) * A_{j-1,l} * A_{n-j,l}
def Acol(l, nmax):
    A = [1]
    for n in range(1, nmax+1):
        A.append(sum(comb(n-1, j-1)*min(j, l+1)*A[j-1]*A[n-j] for j in range(1, n+1)))
    return A
A = {l: Acol(l, NMAX) for l in range(-1, NMAX+2)}
A[-1] = [1]+[0]*NMAX
def p(n): return 1 if n == 0 else (n+1)**(n-1)
def b(n, l):
    if l < 0: return 0
    return A[l][n]-A[l-1][n]
bad = 0
for n in range(1, 8):
    br = brute(n)
    rec = [b(n, l) for l in range(n)]
    if br != rec: bad += 1; print("MISMATCH n", n, br, rec)
    assert A[n][n] == p(n)
print("brute vs recursion n<=7 mismatches:", bad)

def s(m, y):
    if y <= 0: return F(0)
    return F(A[y-1][m], p(m))
def c(m, Y): return F(b(m, Y), p(m))
def pi(n, t): return F(comb(n, t)*t**(t-1)*p(n-t), p(n))
def sT(t, Y): return F(min(t, Y), t)*s(t-1, Y)
def x(t, y): return sT(t, y+1)-2*sT(t, y)+sT(t, y-1)
def Bor(m): return F(m**(m-1), factorial(m))  # e^{-m} 생략(비에서 소거되도록 쓸 것)

fail = {k: 0 for k in ('5-19', 'x-formula', '5-20', '2-38', 'cor-L', 'abel', 'pi-borel')}
cnt = {k: 0 for k in fail}
for n in range(3, NMAX+1):
    for y in range(2, n):
        # 따름정리 6:cor-L : y>=2, y+1<=n<=2y+1
        if y+1 <= n <= 2*y+1:
            P = sum(x(t, y) for t in range(y, n+1))
            cnt['cor-L'] += 1
            if not (y*P >= -1 - F(y*(y-1), n)*c(n-1, y-1)): fail['cor-L'] += 1
        if 2*y >= n+1:
            lhs = c(n, y)-c(n, y-1)
            rhs = sum(pi(n, t)*x(t, y) for t in range(y, n+1))
            cnt['5-19'] += 1
            if lhs != rhs: fail['5-19'] += 1
            for t in range(y+1, n+1):
                cnt['x-formula'] += 1
                if x(t, y) != F(1, t)*((y+1)*c(t-1, y)-(y-1)*c(t-1, y-1)): fail['x-formula'] += 1
            cnt['x-formula'] += 1
            if x(y, y) != F(-1, y): fail['x-formula'] += 1
            # Abel 재배열 항등식
            P = sum(x(t, y) for t in range(y, n+1))
            tail = lambda s_: sum(x(t, y) for t in range(s_+1, n+1))
            ab = pi(n, y)*P + sum((pi(n, s_+1)-pi(n, s_))*tail(s_) for s_ in range(y, n))
            cnt['abel'] += 1
            if ab != lhs: fail['abel'] += 1
            # 명제 5-22: 모든 t0 in [y+2,n] 가운데 IH가 성립하는 것에서 부등식
            for t0 in range(y+2, n+1):
                if all(b(m, y) >= b(m, y-1) for m in range(t0-1, n)):
                    r = pi(n, y)*P - sum((pi(n, t)-pi(n, y))*max(-x(t, y), 0) for t in range(y+1, t0)) \
                        + sum((pi(n, m+1)-pi(n, t0-1))*(c(m, y)+c(m, y-1))/(m+1) for m in range(t0-1, n))
                    cnt.setdefault('5-22', 0); fail.setdefault('5-22', 0)
                    cnt['5-22'] += 1
                    if not lhs >= r: fail['5-22'] += 1
        # 2-38: y x_t(y) >= -theta_t(y), t>=y ; theta = C(t,y) y^{y-1}(t-y)^{t-y}/t^{t-1}
        t = n
        if t >= y:
            th = F(comb(t, y)*y**(y-1)*((t-y)**(t-y) if t > y else 1), t**(t-1))
            cnt['2-38'] += 1
            if not (y*x(t, y) >= -th): fail['2-38'] += 1
    for t in range(1, n+1):
        cnt['pi-borel'] += 1
        if pi(n, t) != Bor(t)*Bor(n+1-t)/Bor(n+1): fail['pi-borel'] += 1
    for t in range((n+2)//2, n):
        cnt['5-20'] += 1
        if not pi(n, t+1) > pi(n, t): fail['5-20'] += 1
print("checks:", cnt); print("fails :", fail)

# 정리 5:old-5-33의 꼴: Y>=1, 창 폭 R>=1, chi>=2, Y+R+chi+1<=m<=2Y+1
# c_m(Y) >= hov(Y/(m+1),chi) * V(m,Y,chi,R) * Lam(Y,R)
from math import pi as PI, sqrt
def bor(m): return m**(m-1)*exp(-m)/factorial(m)
def bt(z, D):  # Pr(R_z = D)
    if z == 0: return 1.0 if D == 0 else 0.0
    if D < z: return 0.0
    return z/D*exp(-D)*D**(D-z)/factorial(D-z)
def hov(rho, chi, zmax=400):
    return sum(rho**z*sum(bt(z, D) for D in range(0, chi)) for z in range(0, zmax))
worst = None; n33 = 0; f33 = 0
for Y in range(3, 22):
    for R in range(1, Y):
        for chi in range(2, Y):
            for m in range(Y+R+chi+1, 2*Y+2):
                if m > NMAX-1: continue
                lam = sum(Y/(Y+q+1)*float(c(Y+q, Y)) for q in range(1, R+1))
                V = (2*PI)**-0.5*((m+1)/((Y+1)*(m-Y)))**1.5*exp(-1/(12*(m-chi-Y-R+1))-1/(12*(Y+1)))
                rhs = hov(Y/(m+1), chi)*V*lam
                lhs = float(c(m, Y))
                n33 += 1
                ratio = lhs/rhs
                if worst is None or ratio < worst[0]: worst = (ratio, Y, R, chi, m)
                if lhs < rhs: f33 += 1
print("5-33 form: cases", n33, "fails", f33, "min ratio lhs/rhs", worst)
# 생산자 식(정정 전)과 비교용: [m/((Y+1)(m-Y-1))] 꼴이면 실패가 나는지
f_old = 0
for Y in range(3, 22):
    for R in range(1, Y):
        for chi in range(2, Y):
            for m in range(Y+R+chi+1, 2*Y+2):
                if m > NMAX-1 or m-chi-Y-R <= 0: continue
                lam = sum(Y/(Y+q+1)*float(c(Y+q, Y)) for q in range(1, R+1))
                V = (2*PI)**-0.5*(m/((Y+1)*(m-Y-1)))**1.5*exp(-1/(12*(m-chi-Y-R))-1/(12*(Y+1)))
                if float(c(m, Y)) < hov(Y/(m+1), chi)*V*lam: f_old += 1
print("  (참고) 한 칸 어긋난 옛 꼴의 실패 수:", f_old)
