# -*- coding: utf-8 -*-
"""검토전체6 L1: 2장의 항등식·부등식을 작은 n,k에서 정확 정수로 재계산한다.
- 정리 old-2-5: n<=6 모든 섬유 행 단봉 (무차별)
- 보조정리 old-2-14 부호식 (무차별, n<=7)
- 정리 old-2-28 동률–막힘 항등식 d=2E-B (무차별, n<=7)
- 보조정리 old-2-30: B_{n,k-1} = J_n(k-1) - Xi (n<=2k) (무차별, n<=8)
- 보조정리 J-egf (가) 재귀로 J_n(z) 재현 (n<=2k, 다항식 비교)
- 정리 old-2-13 사슬 공식, 정리 old-2-40 다섯 몫 분해, 보조정리 b-top, 명제 old-2-41
- 정리 old-2-31 (SM)(DM0), 보조정리 old-2-34, 따름정리 ratio-e (표에서)
- 정리 moving-tail (가)(나)(마)(사)(아) 수치 확인, (라)의 합 <= 1/2 (m<=3000)
- 보조정리 old-2-37(라) Psi 상계, 정리 old-2-38 (ii)(iii)(iv)
python -I 로 돌린다."""
from fractions import Fraction as Fr
from math import comb, factorial, exp, log, sqrt, cosh, pi, lgamma
import itertools, sys

def A_table(N):
    A = [[0]*(N+2) for _ in range(N+1)]
    for l in range(N+2): A[0][l] = 1
    for n in range(1, N+1):
        for l in range(N+2):
            A[n][l] = sum(comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A
def Aval(A, n, l):
    if l < 0: return 0
    return A[n][min(l, len(A[n])-1)]
def b(A, n, l):
    return Aval(A, n, l) - Aval(A, n, l-1)
def p(n): return 1 if n == 0 else (n+1)**(n-1)

def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        z = max([j for j in range(1, i) if sigma[j-1] > sigma[i-1]] + [0])
        h.append(i - z)
    return h

def park(a):
    n = len(a); occ = [False]*(n+2); pos = [0]*n
    for i in range(n):
        q = a[i]
        while q <= n and occ[q]: q += 1
        if q > n: return None
        occ[q] = True; pos[i] = q
    return pos

print("== 정리 old-2-5: n<=6 섬유 행 단봉 ==")
for n in range(1, 7):
    bad = 0
    for sg in itertools.permutations(range(1, n+1)):
        h = caps(sg)
        Arow = [1]
        for l in range(n):
            Arow.append(1)
        Al = [eval('*'.join(str(min(hi, l+1)) for hi in h)) for l in range(n)]
        row = [Al[0]] + [Al[l]-Al[l-1] for l in range(1, n)]
        # 단봉 검사
        i = 0
        while i+1 < n and row[i] <= row[i+1]: i += 1
        while i+1 < n and row[i] >= row[i+1]: i += 1
        if i+1 < n: bad += 1
    print(n, "비단봉 섬유 수 =", bad)
# n=7 보기
sg = (1,2,3,5,4,6,7); h = caps(sg); print("n=7 sigma h =", h, [eval('*'.join(str(min(hi,l+1)) for hi in h)) for l in range(7)])

print("== old-2-14, old-2-28, old-2-30 (무차별 n<=7) ==")
A = A_table(40)
for n in range(1, 8):
    # 모든 주차함수 열거: 결과 순열, 변위 벡터
    data = []  # (sigma, d-vector by position)
    for a in itertools.product(range(1, n+1), repeat=n):
        pos = park(a)
        if pos is None: continue
        sigma = [0]*n
        for i in range(n): sigma[pos[i]-1] = i+1
        dpos = [pos[i]-a[i] for i in range(n)]  # 차 i의 변위
        data.append((tuple(sigma), tuple(dpos)))
    ok28 = ok14 = ok30 = True
    for k in range(1, n+1):
        E = sum(1 for s, d in data if max(d) == k and sum(1 for x in d if x == k) % 2 == 0 and sum(1 for x in d if x == k) > 0)
        E2 = sum(1 for s, d in data if max(d) == k and sum(1 for x in d if x == k) == 2)
        # B_{n,k-1}: M=k-1 이고 최댓값 차마다 h_i = k
        B = 0
        for s, d in data:
            if max(d) != k-1: continue
            h = caps(s)
            pos_of_car = {s[i]: i+1 for i in range(n)}
            if all(h[pos_of_car[i+1]-1] == k for i in range(n) if d[i] == k-1): B += 1
        dnk = b(A, n, k) - b(A, n, k-1)
        if dnk != 2*E - B: ok28 = False; print("  2-28 어긋남", n, k, dnk, E, B)
        if not (2*E2 - B <= dnk): ok29 = False; print("  2-29 어긋남", n, k)
        # 2-30: 첫 식과 J
        B1 = 0; J = 0; H2 = 0
        for sg in itertools.permutations(range(1, n+1)):
            h = caps(sg); Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            small = 1
            for x in h:
                if x < k: small *= x
            B1 += small*(k-1)**Z*(k**H - (k-1)**H)
            J += H*k**(H-1)*(k-1)**Z*small if H >= 1 else 0
        if B1 != B: ok30 = False; print("  2-30 첫식 어긋남", n, k, B1, B)
        if n <= 2*k:
            Xi = comb(2*k-1, k-1)*p(k-1)**2 if n == 2*k else 0
            if B != J - Xi: ok30 = False; print("  2-30 Xi 어긋남", n, k, B, J, Xi)
        # 2-14 섬유 부호식
        for sg in set(s for s, d in data):
            h = caps(sg); Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            Al = lambda l: 0 if l < 0 else eval('*'.join(str(min(hi, l+1)) for hi in h))
            lhs = Fr(Al(k) - 2*Al(k-1) + Al(k-2))
            v = (1+Fr(1,k))**Z + (1-Fr(1,k))**(Z+H) - 2
            if lhs != Al(k-1)*v: ok14 = False; print("  2-14 어긋남", n, k, sg)
    print(n, "2-28", ok28, "2-14", ok14, "2-30", ok30)

print("== J-egf (가) 재귀 vs 정의 (n<=2k, k<=4, 다항식) ==")
# 다항식을 계수 리스트로 (z의 거듭제곱)
def padd(a, b):
    r = [0]*max(len(a), len(b))
    for i, x in enumerate(a): r[i] += x
    for i, x in enumerate(b): r[i] += x
    return r
def pmul(a, b):
    r = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i+j] += x*y
    return r
def pscale(a, c): return [c*x for x in a]
for k in range(1, 5):
    Jdef = {}
    for n in range(0, 2*k+1):
        poly = [0]
        for sg in itertools.permutations(range(1, n+1)):
            h = caps(sg); Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
            small = 1
            for x in h:
                if x < k: small *= x
            if H >= 1:
                term = [0]*(Z+1); term[Z] = H*k**(H-1)*small
                poly = padd(poly, term)
        Jdef[n] = poly
    Jrec = {0: [0]}
    for n in range(0, 2*k):
        s = [0]
        for i in range(0, n+1):
            s = padd(s, pscale(pmul([i+1, 1], Jrec[n-i]), comb(n, i)*p(i)))
        if n >= k-1:
            s = padd(s, [comb(n, k-1)*p(k-1)*p(n-k+1)])
        Jrec[n+1] = s
    ok = all(padd(Jdef[n], pscale(Jrec[n], -1)) == [0]*len(padd(Jdef[n], pscale(Jrec[n], -1))) or all(x == 0 for x in padd(Jdef[n], pscale(Jrec[n], -1))) for n in range(0, 2*k+1))
    print("k =", k, "J 재귀 일치(n<=2k):", ok, " n=2k+1에서 일치?", all(x == 0 for x in padd(Jdef.get(2*k+1, [0]) if 2*k+1 <= 8 else [0], [0])) if False else "생략")

print("== 정리 old-2-13 사슬 공식 (l<=5, n<=2l+3) ==")
def pi0(n, y):
    # 쪼개짐 확률: 크기 y 이하의 나무만 있는 숲 수 / p_n ; 지수 공식 계수로
    # 숲 수 = n! [x^n] exp(sum_{t<=y} t^{t-1} x^t/t!)
    from fractions import Fraction
    coef = [Fraction(0)]*(n+1); coef[0] = Fraction(1)
    T = [Fraction(0)]*(n+1)
    for t in range(1, min(y, n)+1): T[t] = Fraction(t**(t-1), factorial(t))
    # exp(T) via recurrence: F' = T' F
    F = [Fraction(0)]*(n+1); F[0] = Fraction(1)
    for m in range(1, n+1):
        F[m] = sum(Fraction(t, m)*T[t]*F[m-t] for t in range(1, m+1))
    return F[n]*factorial(n)/p(n)
ok = True
for l in range(0, 6):
    for n in range(1, 2*l+4):
        rhs = p(n)*pi0(n, l+1) + sum(comb(n, m)*(l+1)*Aval(A, m-1, l)*p(n-m) for m in range(l+2, n+1))
        if rhs != Aval(A, n, l): ok = False; print("  2-13 어긋남", l, n, rhs, Aval(A, n, l))
print("2-13 일치:", ok)

print("== 보조정리 b-top, 정리 old-2-40, 명제 old-2-41 ==")
print("b-top:", all(b(A, k, k-1) == k**(k-2) for k in range(2, 30)))
def bT(t, l):
    # 크기 t, 최대 변위 정확히 l 인 나무 수
    N = lambda t, l: 0 if l < 0 else min(t, l+1)*Aval(A, t-1, l)
    return N(t, l) - N(t, l-1)
ok = True
for k in range(2, 9):
    for n in range(2*k+1, 3*k):
        Theta = comb(n, k)*k**(k-2)*Aval(A, n-k, k-1)
        FL = sum(comb(n, t)*(bT(t, k)-bT(t, k-1))*Aval(A, n-t, k-1) for t in range(k+1, 2*k+2))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(A, m, k)+b(A, m, k-1)) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*(b(A, m, k)-b(A, m, k-1)) for m in range(2*k+1, n))
        PAIR2 = 0
        for t1 in range(1, n+1):
            for t2 in range(1, n-t1+1):
                PAIR2 += factorial(n)//(factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1, k)*bT(t2, k)+bT(t1, k-1)*bT(t2, k-1))*p(n-t1-t2)
        PAIR = Fr(PAIR2, 2)
        d = b(A, n, k) - b(A, n, k-1)
        if d != -Theta + FL + BV + KD + PAIR: ok = False; print("  2-40 어긋남", k, n, d, -Theta+FL+BV+KD+PAIR)
        # PAIR via 생성함수 계수 비교: A_{k-1}(x)*(B_k^2+B_{k-1}^2)/2 의 x^n/n! 계수
        # 직접: sum over t1,t2 with A_{n-t1-t2,k-1} (정의) — 2-41은 n<=3k-1에서 p 로 바꿈
        PAIRdef = 0
        for t1 in range(1, n+1):
            for t2 in range(1, n-t1+1):
                PAIRdef += factorial(n)//(factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1, k)*bT(t2, k)+bT(t1, k-1)*bT(t2, k-1))*Aval(A, n-t1-t2, k-1)
        if Fr(PAIRdef, 2) != PAIR: ok = False; print("  2-41 어긋남", k, n)
print("2-40·2-41 일치 (k<=8):", ok)

print("== 정리 old-2-31 (SM)(DM0), 보조정리 old-2-34, ratio-e (m<=35) ==")
def s(m, y): return Fr(Aval(A, m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(A, m, Y), p(m))
okSM = all(s(m+1, y) <= s(m, y) for m in range(0, 35) for y in range(1, 40))
okDM = all(s(m, y) <= s(m+1, y+1) for m in range(0, 35) for y in range(1, 40))
ok34 = all(sum(c(m, Y) for m in range(Y+1, K+1)) >= 1 - s(K, Y) for Y in range(1, 15) for K in range(Y+1, 36))
okre = all(Fr(Aval(A, m+1, y-1), factorial(m+1)) <= Fr(Aval(A, m, y-1), factorial(m))*Fr(2718281829, 10**9) for m in range(0, 35) for y in range(1, 40))
print("SM", okSM, "DM0", okDM, "2-34", ok34, "ratio-e(e<2.7182818290)", okre)

print("== moving-tail: (가) 상하계, (나), (마), (사), (아) 수치 (n<=40) ==")
def Ren(j): return 1.0 if j == 0 else exp(j*log(j)-j-lgamma(j+1))
def Wn2(n, g1, g2):
    t1 = n+1-g1; t2 = t1-g2
    return Fr(factorial(n), factorial(g1-1)*factorial(g2)*factorial(t2))*t2**(t2-1)*g1**(g1-1)*g2**g2
ok_ga = ok_ma = ok_sa = ok_a = True
for n in range(3, 41):
    for r in range(1, (n-1)//2+1):
        Q1 = comb(n, r)*(n-r)**(n-r-2)*(r+1)**r
        Q2 = Fr(0)
        for g1 in range(1, r+1):
            for g2 in range(1, r+2-g1):
                t1 = n+1-g1; t2 = t1-g2
                w = Wn2(n, g1, g2)/(t1*t2)
                if g1+g2 <= r: Q2 += 2*w
                elif g1+g2 == r+1: Q2 += (g2+1)*w
        lhs = b(A, n, n-r-1) - b(A, n, n-r)
        if not (Q1 - Q2 <= lhs <= Q1): ok_ga = False; print("  (가) 어긋남", n, r)
        nf = exp(r)*factorial(n)/factorial(n-r)*(n-r)**(n-r-2)/n**(n-2)
        mid = nf*exp(1)*Ren(r+1) + float(-lhs)/n**(n-2)
        if not (-1e-9 <= mid <= exp(1)*(5*r-1)/(4*n*(1-r/n)**4)+1e-9): ok_ma = False; print("  (마) 어긋남", n, r, mid)
        if abs(float(lhs)/n**(n-2) - exp(1)*Ren(r+1)) > 60*(r+1)/n: ok_sa = False; print("  (사) 어긋남", n, r)
    for D in range(2, 6):
        if n >= 20*D**1.5:
            if not all(b(A, n, n-rr-1) > b(A, n, n-rr) for rr in range(1, D)): ok_a = False; print("  (아) 어긋남", n, D)
print("(가)", ok_ga, "(마)", ok_ma, "(사)", ok_sa, "(아)", ok_a)
mx = 0
for m in range(2, 3001):
    sm = sum(Ren(g)*Ren(m-g) for g in range(1, m))
    mx = max(mx, sm)
print("(라) max_m sum Ren*Ren (m<=3000) =", mx, "<= 1/2 ?", mx <= 0.5)
print("(바) e*Ren(r+1) in [e^{-1/2} r^{-1/2}, 1] r<=2000:", all(exp(-0.5)*r**-0.5 <= exp(1)*Ren(r+1) <= 1+1e-12 for r in range(1, 2001)))

print("== old-2-37(라), old-2-38 (ii)(iii)(iv) ==")
Psi = 0.0; ok37 = True
for q in range(1, 5001):
    Psi += Ren(q)
    if not (Psi <= 0.7979*sqrt(q)): ok37 = False
print("Psi(q) <= 0.7979 sqrt q (q<=5000):", ok37)
def theta(t, k): return comb(t, k)*k**(k-1)*(t-k)**(t-k)/t**(t-1) if t > k else 1.0
def xt(t, k):
    N = lambda t, l: 0 if l < 0 else min(t, l+1)*Aval(A, t-1, l)
    return Fr(N(t, k) - 2*N(t, k-1) + N(t, k-2), t**(t-1))
ok38 = True
for k in range(2, 20):
    for t in range(k, min(2*k, 40)+1):
        q = t-k
        v = float(k*xt(t, k))
        if v < -theta(t, k) - 1e-12: ok38 = False; print("  (ii) 어긋남", k, t)
        if v > -theta(t, k) + (2*q*q+q)*cosh(q/k)/k + 1e-12: ok38 = False; print("  (iii) 어긋남", k, t)
        if not (Ren(q) - 1e-12 <= theta(t, k) <= Ren(q)*(1+q/k)**1.5 + 1e-12): ok38 = False; print("  (iv) 어긋남", k, t)
print("2-38 (ii)(iii)(iv) (k<20, t<=2k):", ok38)
print("x_y(y) = -1/y:", all(xt(y, y) == Fr(-1, y) for y in range(2, 30)))
print("끝")
