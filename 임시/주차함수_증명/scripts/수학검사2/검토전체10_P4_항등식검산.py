# P4 검산: 5.5절 항등식·부등식의 소규모 정확 검산 (python -I)
from fractions import Fraction as Fr
from math import comb, factorial, exp, sqrt, pi, log, floor, ceil
import sys
N = 44
# A[l][n]: 최대 변위 <= l 인 길이 n 주차함수 수 (정리 2-10/2-11 가중 숲 분해)
def A_table(L, N):
    A = {}
    for l in range(0, L+1):
        a = [Fr(0)]*(N+1); a[0] = Fr(1)
        for n in range(1, N+1):
            s = Fr(0)
            for t in range(1, n+1):
                s += comb(n-1, t-1)*min(t, l+1)*a[t-1]*a[n-t]
            a[n] = s
        A[l] = a
    return A
L = N
A = A_table(L, N)
p = [(n+1)**(n-1) if n >= 1 else 1 for n in range(N+2)]
def Aget(n, l):
    if l < 0: return Fr(0)
    if n == 0: return Fr(1)
    return A[min(l, L)][n]
def s(m, y):  # 생존 확률
    if y <= 0: return Fr(0)
    return Aget(m, y-1)/p[m]
def c(m, Y): return s(m, Y+1)-s(m, Y)
def b(m, Y): return c(m, Y)*p[m]
def sT(t, Y): # 나무 생존 확률
    if t <= Y: return Fr(1)
    return Fr(Y, t)*s(t-1, Y)
def x(t, y): return sT(t, y+1)-2*sT(t, y)+sT(t, y-1)
def pi_n(n, t): return Fr(comb(n, t)*t**(t-1)*p[n-t], p[n])
# 쪼개짐 확률: 모든 나무 크기 <= y 인 숲 수
def forests_le(n, y):
    f = [0]*(n+1); f[0] = 1
    for m in range(1, n+1):
        f[m] = sum(comb(m-1, t-1)*t**(t-1)*f[m-t] for t in range(1, min(m, y)+1))
    return f
def pi0(n, y): return Fr(forests_le(n, y)[n], p[n])
# 1) 정수성 및 p_n 일치
for n in range(1, 12):
    assert Aget(n, n) == p[n], n
    for l in range(n): assert Aget(n, l).denominator == 1
print("A 정수·p_n 일치 OK")
# 2) 5.5.1 x_t(y) 식: t>=y+1 에서 x_t = [(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)]/t ; x_y(y) = -1/y
for y in range(2, 15):
    assert x(y, y) == Fr(-1, y)
    for t in range(y+1, 2*y+2):
        assert x(t, y) == ((y+1)*c(t-1, y)-(y-1)*c(t-1, y-1))/t, (t, y)
print("나무 곡률 식 OK")
# 3) 보조정리 old-5-19 열 재귀
for n in range(3, 30):
    for y in range((n+1+1)//2, n):
        if 2*y < n+1: continue
        lhs = c(n, y)-c(n, y-1)
        rhs = sum(pi_n(n, t)*x(t, y) for t in range(y, n+1))
        assert lhs == rhs, (n, y)
print("열 재귀 OK")
# 4) 보조정리 old-5-20 핵 비
def g(x_): return (x_-1)*log(1+1/x_)
for n in range(5, 25):
    for t in range(ceil((n+1)/2), n):
        r = float(pi_n(n, t+1)/pi_n(n, t))
        assert abs(r-exp(g(t)-g(n-t))) < 1e-12 and r > 1
print("핵 비 OK")
# 5) 보조정리 old-5-27 기저 항등식 ; 따름정리 cor-L
for n in range(3, 30):
    for y in range(ceil((n+1)/2), n):
        P = sum(x(t, y) for t in range(y, n+1))
        rhs = Fr(-1, y)+sum(((y+1)*c(m, y)-(y-1)*c(m, y-1))/(m+1) for m in range(y, n))
        assert P == rhs
        top = Fr(y*(y-1), n)*c(n-1, y-1)
        assert y*P >= -1-top, (n, y, float(y*P), float(-1-top))
print("기저 항등식·cor-L OK")
# 6) 정리 old-5-28 크기 방향 하계
for m in range(2, 30):
    for d in range(1, m//2+1):
        w = m-d
        z = exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
        assert float(c(m+1, w+1)) >= (1-z)*float(c(m, w))-1e-15, (m, d)
print("크기 방향 하계 OK")
# 7) 정리 diag-first-layer 부등식 (6.31) 소규모
for m in range(2, 30):
    for d in range(1, (m+1)//2+1):
        w = m-d
        if m < max(2, 2*d-1): continue
        assert (w+2)*(m+1)*c(m+1, w+1) > w*(m+2)*c(m, w), (m, d)
print("(6.31) OK")
# 8) 이음 행 t_0, Abel 환원 (★′) 실제 자료로 IH 판정
def t0(y):
    t = y+2
    while not (y <= (t-1)-floor(0.75*(t-1)**(2/3))): t += 1
    return t
cnt = 0
for n in range(3, N+1):
    for y in range(ceil((n+1)/2), n):
        T0 = t0(y)
        if T0 > n: continue
        if not all(b(m, y) >= b(m, y-1) for m in range(T0-1, n)): continue
        cnt += 1
        P = sum(x(t, y) for t in range(y, n+1))
        WIN = sum((pi_n(n, t)-pi_n(n, y))*max(-x(t, y), 0) for t in range(y+1, T0))
        POS = sum((pi_n(n, m+1)-pi_n(n, T0-1))*(c(m, y)+c(m, y-1))/(m+1) for m in range(T0-1, n))
        assert c(n, y)-c(n, y-1) >= pi_n(n, y)*P-WIN+POS, (n, y)
print("Abel 환원 (★′) OK, 검사 쌍", cnt)
# 9) 보조정리 old-5-24 방문 확률: 사슬 전이로 정확 계산
def visit(t, s_):
    # 크기 t 나무에서 사슬이 s_ 를 방문할 확률 (s_>t/2)
    from functools import lru_cache
    @lru_cache(None)
    def v(cur):
        if cur == s_: return Fr(1)
        if cur < s_: return Fr(0)
        tot = Fr(0)
        for nxt in range(s_, cur):
            if 2*nxt > cur-1:
                tot += pi_n(cur-1, nxt)*v(nxt)
        return tot
    return v(t)
def Bor_ratio(t, s_):  # Ren(t-s)Bor(s)/Bor(t) 유리수
    d = t-s_
    return Fr(d**d, factorial(d))*Fr(s_**(s_-1), factorial(s_))*Fr(factorial(t), t**(t-1))
for t in range(3, 26):
    for s_ in range(t//2+1, t):
        assert visit(t, s_) == Bor_ratio(t, s_), (t, s_)
print("방문 확률 OK")
# 10) 보조정리 old-5-25 항별 상계 (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t))
for y in range(2, 20):
    for t in range(y+1, 2*y):
        assert max(-x(t, y), 0) <= Bor_ratio(t, y)/y
print("창 항 항별 상계 OK")
# 11) 정리 old-5-31 Lc(Y,q) <= c_{Y+q}(Y) (부동소수)
def Bor(m): return exp(-m)*m**(m-1)/factorial(m)
def BorT(z, D): return (z/D)*exp(-D)*D**(D-z)/factorial(D-z) if D >= z else 0.0
for Y in range(1, 16):
    for q in range(1, Y+2):
        Lc = 0.0
        for z in range(1, q+1):
            for D in range(z, q+1):
                Lc += z*BorT(z, D)*Bor(Y+q+1-D)/Bor(Y+q+1)*float(pi0(Y+q-D, Y))*exp(-(z*(q+1)-D*(z+1)/2)/Y)
        Lc /= Y
        assert float(c(Y+q, Y)) >= Lc-1e-13, (Y, q, float(c(Y+q, Y)), Lc)
print("Lc 하계 OK")
# 12) stop-lower 상계 pi0_{Y+j}(Y) <= Pr(beta>j)
for Y in range(1, 15):
    for j in range(0, 12):
        tail = 1-sum(Bor(i) for i in range(1, j+1))
        assert float(pi0(Y+j, Y)) <= tail+1e-13
print("쪼개짐 상계 OK")
# 13) bt-tail (가)
for z in range(1, 8):
    for D in range(z+1, 40):
        W = D-z
        assert BorT(z, D) <= z/sqrt(2*pi)/D/sqrt(W)*exp(-z*z/(2*W)+z**3/(3*W*W))+1e-15
print("BT 꼬리 (가) OK")
# 14) Abel 환원 (★′): IH가 성립하는 최소 t_0 를 자료로 잡아 검사 (기록 r58b4caa 의 방식)
cnt = 0
for n in range(3, N+1):
    for y in range(ceil((n+1)/2), n):
        T0 = None
        for t in range(y+2, n+1):
            if all(b(m, y) >= b(m, y-1) for m in range(t-1, n)): T0 = t; break
        if T0 is None: continue
        cnt += 1
        P = sum(x(t, y) for t in range(y, n+1))
        WIN = sum((pi_n(n, t)-pi_n(n, y))*max(-x(t, y), 0) for t in range(y+1, T0))
        POS = sum((pi_n(n, m+1)-pi_n(n, T0-1))*(c(m, y)+c(m, y-1))/(m+1) for m in range(T0-1, n))
        assert c(n, y)-c(n, y-1) >= pi_n(n, y)*P-WIN+POS, (n, y)
print("Abel 환원 (★′) 자료 t_0 OK, 검사 쌍", cnt)
