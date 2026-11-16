# O4: 5.5.1-5.5.4 의 항등식·부등식을 작은 n 에서 정확 유리수로 검산
from fractions import Fraction as Fr
from math import comb, factorial
from itertools import product
import sys
sys.setrecursionlimit(10000)

NMAX = 40
# A[n][l] : 최대 변위 <= l 인 길이 n 주차함수 수 (l>=-1), 라벨 1 의 나무로 분해하는 재귀
A = [[0]*(NMAX+3) for _ in range(NMAX+2)]
for n in range(NMAX+2):
    for l in range(-1, NMAX+2):
        if l < 0: A[n][l+1 if False else l] = 0  # placeholder
def Aget(n,l):
    if l < 0: return 0
    if n == 0: return 1
    return A[n][l]
for n in range(1, NMAX+2):
    for l in range(0, NMAX+2):
        s = 0
        for m in range(1, n+1):
            N = min(m, l+1)*Aget(m-1, l)   # 크기 m 나무 중 M<=l 인 것의 수 (정리 2-10)
            s += comb(n-1, m-1)*N*Aget(n-m, l)
        A[n][l] = s
# 브루트포스 대조 n<=6
def brute(n):
    cnt = {}
    for pref in product(range(1,n+1), repeat=n):
        spots = [False]*(n+1); md = 0; ok=True
        for p in pref:
            q = p
            while q <= n and spots[q]: q += 1
            if q > n: ok=False; break
            spots[q]=True; md = max(md, q-p)
        if ok: cnt[md] = cnt.get(md,0)+1
    return cnt
for n in range(1,7):
    c = brute(n)
    for l in range(0,n):
        assert Aget(n,l) == sum(v for k,v in c.items() if k<=l), (n,l)
print("A 재귀 = 브루트포스 (n<=6) OK; p_n 검사:", all(Aget(n,n-1)==(n+1)**(n-1) for n in range(1,30)))

p = lambda n: (n+1)**(n-1) if n>0 else 1
def s(m,y): return Fr(Aget(m,y-1), p(m))          # 생존 확률
def c(m,Y): return Fr(Aget(m,Y)-Aget(m,Y-1), p(m)) # 수준 질량
def sT(t,Y): return Fr(1) if t<=Y else Fr(Y*Aget(t-1,Y-1), t**(t-1))
def x(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
def pi(n,t): return Fr(comb(n,t)*t**(t-1)*p(n-t), p(n))
def pi0(n,y): # 가장 큰 나무 <= y 일 확률; y >= n/2 이면 1-sum
    assert 2*y >= n
    return 1 - sum(pi(n,t) for t in range(y+1,n+1))

bad = 0
# 5.5.1: x_t(y) 식 과 x_y(y) = -1/y
for y in range(2, 20):
    assert x(y,y) == Fr(-1,y)
    for t in range(y+1, 2*y+2):
        assert x(t,y) == Fr(1,t)*((y+1)*c(t-1,y)-(y-1)*c(t-1,y-1)), (t,y)
print("5.5.1 x_t(y) 식 OK")
# 보조정리 5-19 열 재귀, 5-27 기저 항등식
for n in range(3, NMAX+1):
    for y in range((n+1)//2 + (n+1)%2, n):   # ceil((n+1)/2) <= y <= n-1
        if 2*y < n+1: continue
        lhs = c(n,y)-c(n,y-1)
        assert lhs == sum(pi(n,t)*x(t,y) for t in range(y,n+1)), ("5-19",n,y)
        P = sum(x(t,y) for t in range(y,n+1))
        assert P == Fr(-1,y)+sum(((y+1)*c(m,y)-(y-1)*c(m,y-1))/Fr(m+1) for m in range(y,n)), ("5-27",n,y)
        # Abel 재배열
        tail = lambda s_: sum(x(t,y) for t in range(s_+1,n+1))
        assert lhs == pi(n,y)*P + sum((pi(n,s_+1)-pi(n,s_))*tail(s_) for s_ in range(y,n)), ("Abel",n,y)
        # 명제 5-22 : 임의 t0 in [y+2,n] 중 IH 가 성립하는 것에 대해
        for t0 in range(y+2, n+1):
            if all(c(m,y) >= c(m,y-1) for m in range(t0-1, n)):
                rhs = pi(n,y)*P - sum((pi(n,t)-pi(n,y))*max(-x(t,y),0) for t in range(y+1,t0)) \
                      + sum((pi(n,m+1)-pi(n,t0-1))*(c(m,y)+c(m,y-1))/Fr(m+1) for m in range(t0-1,n))
                if lhs < rhs: bad += 1; print("5-22 위반", n,y,t0)
        # 따름정리 cor-L (6.36)
        top = Fr(y*(y-1),n)*c(n-1,y-1)
        if y*P < -1-top: bad+=1; print("cor-L 위반", n, y)
print("5-19·5-27·Abel·5-22·cor-L (n<=%d) 위반 수:"%NMAX, bad)
# 보조정리 5-20 핵 비
from math import log, exp
g = lambda x_: (x_-1)*log(1+1/x_)
for n in range(5, 30):
    for t in range((n+2)//2, n):
        r = pi(n,t+1)/pi(n,t)
        assert abs(float(r) - exp(g(t)-g(n-t))) < 1e-9 and r > 1
print("5-20 OK")
# 정리 5-28 : c_{m+1}(w+1) >= (1-z_m(d)) c_m(w)
bad=0
for m in range(2, NMAX):
    for d in range(1, m//2+1):
        w = m-d
        z = exp((d-1)/w)/(w+1) + 3*d/(2*(w+1)*(m+1))
        if float(c(m+1,w+1)) < (1-z)*float(c(m,w)) - 1e-15: bad+=1; print("5-28 위반",m,d)
        # 손실률 비교 (m+d+2)/((w+2)(m+1)) <= z
        assert (m+d+2)/((w+2)*(m+1)) <= z + 1e-15
print("5-28 위반 수:", bad)
# 보조정리 5-23/5-24/5-25 : (x_t(y))_- <= Ren(t-y)Bor(y)/(y Bor(t)) , t/2<y<t
from math import e
Bor = lambda m_: Fr(m_**(m_-1), factorial(m_)) * Fr(1) # e^-m 은 따로
def visit(t,sv): # Ren(t-s)Bor(s)/Bor(t) = theta_t(s) 정확식 (2-37 마)
    return Fr(comb(t,sv)*sv**(sv-1)*(t-sv)**(t-sv), t**(t-1))
bad=0
for t in range(3, NMAX):
    for y in range(t//2+1, t):
        if max(-x(t,y),0) > visit(t,y)/y: bad+=1; print("5-25 위반",t,y)
print("5-25 위반 수:", bad)
# 보조정리 stop-lower 상계 : pi0_{Y+j}(Y) <= Pr(beta>j) (Bor 는 e^-m 포함 float)
import math
BorF = lambda m_: math.exp(-m_)*m_**(m_-1)/math.factorial(m_)
bad=0
for Y in range(1, 25):
    for j in range(0, Y+1):
        lhs = float(pi0(Y+j, Y)); rhs = 1-sum(BorF(i) for i in range(1,j+1))
        if lhs > rhs + 1e-12: bad+=1; print("stop-lower 상계 위반",Y,j,lhs,rhs)
print("stop-lower 상계 위반 수:", bad)
# 정리 5-31 : c_{Y+q}(Y) >= Lc(Y,q) , 1<=q<=Y+1
def BorTanner(z,D): return Fr(z,D)*Fr(D**(D-z), factorial(D-z))  # e^-D 제외
def Lc(Y,q):
    tot = 0.0
    for z in range(1,q+1):
        for D in range(z,q+1):
            bt = float(BorTanner(z,D))*math.exp(-D)
            ratio = BorF(Y+q+1-D)/BorF(Y+q+1)
            tot += z*bt*ratio*float(pi0(Y+q-D,Y))*math.exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
bad=0
for Y in range(1, 18):
    for q in range(1, Y+2):
        if float(c(Y+q,Y)) < Lc(Y,q) - 1e-12: bad+=1; print("5-31 위반",Y,q,float(c(Y+q,Y)),Lc(Y,q))
print("5-31 위반 수:", bad)
