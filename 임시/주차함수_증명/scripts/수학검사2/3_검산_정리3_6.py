# -*- coding: utf-8 -*-
"""3_검산_정리3_6.py -- 3.3절 반례 수치와 3.4절 정리 3.6 증명의 수치 사슬을 정확 정수·유리수·mpmath로 다시 계산한다.

(A) n=80 반례: 열 39·40·41 의 A_{n,l} 을 마지막 차 재귀로 n≤80 까지 새로 계산해 b_{80,39..41}, 교차곱, 분리자, 두 비
(B) E_n ω_n = Σ_{j≤n/2} C(n,j) j^j p_{n-j}/p_n 의 정확 유리수 (n=1..5) 와 √n 비교; n≤300 에서 E_n ω_n ≤ √n 과 상계 √(2/π)√((n+1)(n+2)/n)
(C) 각 항의 재배열 C(n,j) j^j p_{n-j}/p_n = (n+1)/(n+1-j) C(n+1,j) (j/(n+1))^j (1-j/(n+1))^{n+1-j} (정확 유리수)
(D) Robbins 결합 1/(12(n+1)) - 1/(12j+1) < 0, 항 < η(j/(n+1))/√(2π(n+1)) (수치)
(E) 적분 상계 2√((⌊n/2⌋+1)/(n-⌊n/2⌋)) ≤ 2√((n+2)/n); 9n^2-48n-32 at n=6; 2(n+1)(n+2) ≤ π n^2 ⇔ 우변 ≤ √n
(F) λ = ⌈3n/4⌉/n ≤ 3/4+3/(4n) ≤ 751/1000, n^{-1/2} ≤ 1/31, n^{-1} ≤ 1/1000 (n≥1000); J=8 유리수; 0.4716 비교
(G) 둘째 문장: k=⌈3n/4⌉ ≤ n-1 (n≥4), 2k ≥ n+ℓ* (ℓ* ≤ ⌈n/2⌉-1)
"""
from fractions import Fraction as Fr
from math import comb, factorial, isqrt, ceil, floor, sqrt, pi
from mpmath import mp, mpf, quad, sqrt as msqrt, pi as mpi, exp as mexp, log as mlog

mp.dps = 30

print("(A) n=80 반례")
N = 80
cols = {}
for l in (39, 40, 41):
    col = [1]
    for n in range(1, N+1):
        col.append(sum(comb(n-1, j)*min(j+1, l+1)*col[j]*col[n-1-j] for j in range(n)))
    cols[l] = col
b = {l: cols[l][80]-cols[l-1][80] if l-1 in cols else None for l in (40, 41)}
# b_{80,39} 는 열 38 도 필요
col38 = [1]
for n in range(1, N+1):
    col38.append(sum(comb(n-1, j)*min(j+1, 39)*col38[j]*col38[n-1-j] for j in range(n)))
b[39] = cols[39][80]-col38[80]
for l in (39, 40, 41):
    print(f"  b_80,{l} = {b[l]}")
print("  b39*b41 - b40^2 =", b[39]*b[41]-b[40]**2 > 0, "(양수)")
print("  증가:", b[39] < b[40] < b[41])
print("  25000 b40 < 25928 b39:", 25000*b[40] < 25928*b[39], "; 25928 b40 < 25000 b41:", 25928*b[40] < 25000*b[41])
mp.dps = 50
print("  b40/b39 =", mpf(b[40])/mpf(b[39]), " b41/b40 =", mpf(b[41])/mpf(b[40]), " 25928/25000 =", 25928/25000)
mp.dps = 30

def p(n):
    return (n+1)**(n-1) if n >= 1 else 1

def E_omega(n):
    return sum(Fr(comb(n, j)*j**j*p(n-j), p(n)) for j in range(1, n//2+1))

print("(B) E_n ω_n")
for n in range(1, 6):
    e = E_omega(n)
    print(f"  n={n}: E ω = {e} ≈ {float(e):.5f}, √n = {sqrt(n):.5f}, ≤ : {e*e <= n}")
bad = []
for n in range(1, 301):
    e = E_omega(n)
    ub = Fr(2)*(n+1)*(n+2)/n  # 우변^2 = (2/π)(n+1)(n+2)/n ; 비교는 π 로 부동소수
    if not (e*e <= n):
        bad.append(('sqrt', n))
    if n >= 1 and not (float(e) <= sqrt(2/pi*(n+1)*(n+2)/n) + 1e-12):
        bad.append(('ub', n))
print("  n≤300 에서 E ω ≤ √n 과 E ω ≤ √(2/π)√((n+1)(n+2)/n) 위반:", bad)
print("  n=6: √(2/π)√(7·8/6) =", sqrt(2/pi*56/6), " √6 =", sqrt(6), "; 9·36-48·6-32 =", 9*36-48*6-32)
print("  n=5: √(2/π)√(6·7/5) =", sqrt(2/pi*42/5), " √5 =", sqrt(5), " (n=5 에서는 상계가 √n 을 넘으므로 직접 값이 필요)")
print("  π > 25/8 :", pi > 25/8, "; 16(n+1)(n+2) ≤ 25n^2 ⇔ 9n^2-48n-32 ≥ 0 :", all(16*(n+1)*(n+2) <= 25*n*n for n in range(6, 2000)), " n=5:", 16*6*7 <= 25*25)

print("(C) 항 재배열 (정확 유리수, n=37, 모든 j)")
n = 37
ok = True
for j in range(1, n//2+1):
    lhs = Fr(comb(n, j)*j**j*p(n-j), p(n))
    rhs = Fr(n+1, n+1-j)*comb(n+1, j)*Fr(j, n+1)**j*Fr(n+1-j, n+1)**(n+1-j)
    ok &= (lhs == rhs)
print("  일치:", ok)

print("(D) Robbins 결합과 η 상계 (n=37, 1000)")
def rb(m):
    return mlog(factorial(m)) - (m+mpf(1)/2)*mlog(m) + m - mlog(2*mpi)/2
for n in (37, 1000):
    worst = None
    for j in range(1, n//2+1):
        d = rb(n+1)-rb(j)-rb(n+1-j)
        assert d < 0 and d < 1/mpf(12*(n+1)) - 1/mpf(12*j+1)
        term = mpf(comb(n, j)*j**j*p(n-j))/mpf(p(n))
        phi = mpf(j)/(n+1)
        eta = phi**(-mpf(1)/2)*(1-phi)**(-mpf(3)/2)
        ratio = term/(eta/msqrt(2*mpi*(n+1)))
        worst = ratio if worst is None else max(worst, ratio)
    print(f"  n={n}: rb 결합 모두 음수·상계 성립; max 항/(η/√(2π(n+1))) = {worst} (<1)")
    print(f"     Robbins 구간 확인 rb_{n}: 1/(12n+1)={1/mpf(12*n+1)}, rb={rb(n)}, 1/(12n)={1/mpf(12*n)}")

print("(E) 적분 상계")
for n in (6, 7, 1000, 1001):
    lhs = 2*sqrt((n//2+1)/(n-n//2)); rhs = 2*sqrt((n+2)/n)
    print(f"  n={n}: 2√((⌊n/2⌋+1)/(n-⌊n/2⌋)) = {lhs:.6f} ≤ 2√((n+2)/n) = {rhs:.6f}: {lhs <= rhs + 1e-15}")
# 합을 적분으로 감싸는 부등식 직접 확인 (n=1000)
n = 1000
S = sum((mpf(j)/(n+1))**(-mpf(1)/2)*(1-mpf(j)/(n+1))**(-mpf(3)/2) for j in range(1, n//2+1))/(n+1)
I = 2*msqrt(mpf(n//2+1)/(n-n//2))
print(f"  n=1000: (1/(n+1))Σ η = {S} ≤ ∫_0^((⌊n/2⌋+1)/(n+1)) η = {I}: {S <= I}")
print(f"  E_1000 ω = {float(E_omega(1000)):.6f}, 상계 √(2/π)√(1001·1002/1000) = {sqrt(2/pi*1001*1002/1000):.6f}, √1000 = {sqrt(1000):.6f}")

print("(F) 수치 사슬")
lam_max = max(Fr(ceil(Fr(3*n, 4)), n) for n in range(1000, 5001))
print("  max_{1000≤n≤5000} ⌈3n/4⌉/n =", lam_max, "≈", float(lam_max), " 3/4+3/4000 =", float(Fr(3, 4)+Fr(3, 4000)), " ≤ 751/1000:", Fr(3, 4)+Fr(3, 4000) <= Fr(751, 1000))
print("  ⌈3n/4⌉ ≤ 3n/4 + 3/4 (n≤5000):", all(ceil(Fr(3*n, 4)) <= Fr(3*n, 4)+Fr(3, 4) for n in range(1, 5001)))
print("  31^2 =", 31**2, "< 1000:", 31**2 < 1000, " ⇒ n^{-1/2} ≤ 1/31 for n ≥ 1000:", Fr(1, 1000) <= Fr(1, 961))
lam = Fr(751, 1000); J = 8
val = lam**J + Fr(1, 31)*sum(i*lam**(i-1) for i in range(1, J+1)) + Fr(1, 1000)*sum((i-1)*lam**(i-1) for i in range(1, J+1))
print("  J=8 유리수 =", val)
print("  본문 =", Fr(7309649993107890414228499, 15500000000000000000000000), " 일치:", val == Fr(7309649993107890414228499, 15500000000000000000000000))
mp.dps = 30
print("  소수 =", mpf(val.numerator)/val.denominator, " < 0.4716:", val < Fr(4716, 10000), " < 1/2:", val < Fr(1, 2))
# 우변이 λ, n^{-1/2}, n^{-1} 에 대해 증가함은 자명(모든 계수 양수). J 를 바꾸면?
for JJ in (6, 7, 8, 9, 10, 12):
    v = lam**JJ + Fr(1, 31)*sum(i*lam**(i-1) for i in range(1, JJ+1)) + Fr(1, 1000)*sum((i-1)*lam**(i-1) for i in range(1, JJ+1))
    print(f"    J={JJ}: {float(v):.6f}")
# 실제 n=1000 (λ=3/4, n^{-1/2}=1/√1000) 에서의 값 (참고)
lam0 = mpf(3)/4
v0 = lam0**8 + sum(i*lam0**(i-1) for i in range(1, 9))/msqrt(1000) + sum((i-1)*lam0**(i-1) for i in range(1, 9))/1000
print("  참고: n=1000 의 실제 세 값으로 J=8 우변 =", v0)

print("(G) 둘째 문장")
print("  ⌈3n/4⌉ ≤ n-1 for 4≤n≤5000:", all(ceil(Fr(3*n, 4)) <= n-1 for n in range(4, 5001)), "; n=3:", ceil(Fr(9, 4)) <= 2)
print("  ℓ* ≤ ⌈n/2⌉-1 ⇒ 2⌈3n/4⌉ ≥ n+ℓ* (n≤5000):", all(2*ceil(Fr(3*n, 4)) >= n + (ceil(Fr(n, 2))-1) for n in range(1, 5001)))
print("  (k-ℓ*)/(n-ℓ*) ≥ 1/2 (n≤5000, ℓ*=⌈n/2⌉-1):", all(Fr(ceil(Fr(3*n, 4))-(ceil(Fr(n, 2))-1), n-(ceil(Fr(n, 2))-1)) >= Fr(1, 2) for n in range(2, 5001)))
