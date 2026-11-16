# 검토전체 G3: 장v2/장5A.md의 수치·항등식 검산. python -I 로 돌린다.
import math
from fractions import Fraction
import sympy as sp
from mpmath import mp, mpf, loggamma, log

out = []
def rec(name, ok, detail=""):
    out.append(f"[{'OK' if ok else 'FAIL'}] {name} {detail}")

# 1. 정리 old-5-1 둘째 조각의 비교 수 (74,995,000)와 넷째 조각의 위치 수 (99,970,002), 정리 old-5-2의 위치 수 (524,955,000)
c_km1 = sum(math.ceil(n/2)-1 for n in range(10001, 20001))
c_k = sum(math.ceil(n/2) for n in range(10001, 20001))
rec("둘째 조각: Σ(k_n-1)=74,995,000 (본문 수)", c_km1 == 74_995_000, f"Σ(k_n-1)={c_km1}, Σk_n={c_k}")
def cnt(a, b):
    s = 0
    for n in range(a, b+1):
        lo = math.ceil((n-1)/2); hi = n-3
        if hi >= lo: s += hi-lo+1
    return s
rec("넷째 조각 위치 수 99,970,002", cnt(5, 20000) == 99_970_002, str(cnt(5, 20000)))
rec("C50 위치 수 524,955,000", cnt(20001, 50000) == 524_955_000, str(cnt(20001, 50000)))
rec("Newton 다항식 수 14,365", sum(r-1 for r in range(2, 171)) == 14365)

# 2. 보조정리 cayley-ratio의 아홉 값과 87/32
vals = [(1+1/k)**(k-2)*(1+5/(2*k)+2/k**2) for k in range(1, 10)]
rec("Cayley 아홉 값 > 87/32", all(v > 87/32 for v in vals), str([round(v, 4) for v in vals]))
rec("e < 65/24+1/100 < 87/32", math.e < 65/24+0.01 < 87/32)

# 3. third-group (다): 1 <= e(1-1/r)^(r-3) <= 1+6/r
mx = max(math.e*(1-1/r)**(r-3)-1-6/r for r in range(3, 200000))
mn = min(math.e*(1-1/r)**(r-3)-1 for r in range(3, 200000))
rec("nf 비 상하계 (3<=r<2e5)", mx < 0 and mn > 0, f"max(ratio-1-6/r)={mx:.3e}, min(ratio-1)={mn:.3e}")

# 4. m(n) 보기값
def mm(n):
    m = 170
    t = 171
    while t**1.5+9*t <= n: m = t; t += 1
    return m
rec("m(20001)=597, m(50001)=1160", mm(20001) == 597 and mm(50001) == 1160)

# 5. 정리 old-5-5 증명 (B) 산술
s = 100
br = 1/(3*s)+8/(3*s*s)+2.507/s**2+(1+2.1709*s)/s**3
rec("(B) 대괄호<0.0041 at s=100, 주계수 0.019604", br < 0.0041 and abs(0.5+2*0.845204-math.sqrt(3*math.pi/2)-0.019604) < 1e-6, f"bracket={br:.6f}")
rec("sqrt(3pi/2)<=2.1709, sqrt(pi/2)<=1.2534", math.sqrt(3*math.pi/2) <= 2.1709 and math.sqrt(math.pi/2) <= 1.2534)

# 6. sign-sandwich (마) 상수
rec("e^{2/23}+21/80 e^{1/23} < 11/8", math.exp(2/23)+21/80*math.exp(1/23) < 11/8)
rec("o e^{1/23} < 3/4", math.exp(1/23)/math.sqrt(2) < 0.75)
# kernel-bounds 상수
rec("2sqrt2/e > 181/174 > 26/25", 2*math.sqrt(2)/math.e > 181/174 > 26/25)
rec("21/(40sqrt2) > 147/396 > 720/1957 > 1/e", 21/(40*math.sqrt(2)) > 147/396 > 720/1957 > 1/math.e)
# kernel-C-bound 증명 (24m-12 vs 22m): 진술 첫 줄의 상계로는 m<=5에서 1+1/(22m)이 나오지 않음
bad = [m for m in range(1, 10) if 1/(12*(2*m-1)) > 1/(22*m)]
rec("진술 첫 줄 1+1/(12(2m-1)) <= 1+1/(22m) 가 깨지는 m", len(bad) == 0, f"깨지는 m={bad} (증명의 중간 상계 1+1/(24m-2)로는 모든 m>=1에서 성립)")

# 7. omitted-tail (라)
rec("log10(1.15*598^3)<8.4, 598 log10 24>825", math.log10(1.15*598**3) < 8.4 and 598*math.log10(24) > 825)
rec("(r+1)/n < 1/10 at r=598, x^{3/2}=12/5", 12/5*(1+1/598)/math.sqrt(598) < 0.1)
rec("12/(110e) < 1/24", 12/(110*math.e) < 1/24)

# 8. 정리 old-5-11 (가) 진입 지표 수치
rec("27.14^3<20001, 0.75*736.5>=552", 27.14**3 < 20001 and 0.75*736.5 >= 552)
rec("(149/200)^3>(16/25)^2, (3/4)^3<(13/20)^2", (149/200)**3 > (16/25)**2 and (3/4)**3 < (13/20)**2)
# cover-edge
rec("1/(1+9/sqrt598)>0.73, 832^{1.5}<1.2*20001<833^{1.5}", 1/(1+9/math.sqrt(598)) > 0.73 and 832**1.5 < 1.2*20001 < 833**1.5)

# 9. kernel-bounds 증명의 두 유리 항등식 (P_Theta, Q_Theta)
P = sp.symbols('Psi'); th = 2*P/(1-P)
L = 2*sum(P**(2*i+1)/(2*i+1) for i in range(4)); U = L+2*P**9/(9*(1-P**2))
um = 1+th/2-th**2/24; up = 1+th/2-th**2/44
numP = sp.simplify(th**2*sp.diff(up, P)/sp.diff(th, P)-(th-L)*up)
numQ = sp.simplify(th**2*sp.diff(um, P)/sp.diff(th, P)-(th-U)*um)
PT = 175-665*P+581*P**2-427*P**3+375*P**4-309*P**5+150*P**6+15*P**7
QT = 945+42*P-252*P**2+66*P**3-108*P**4+42*P**5-60*P**6-10*P**7
rec("P_Theta 항등식", sp.simplify(numP-2*P**3*PT/(1155*(1-P)**3)) == 0)
rec("Q_Theta 항등식", sp.simplify(numQ+P**4*QT/(945*(1-P)**3*(1+P))) == 0)

# 10. weight-envelope (가): log nf 의 1/n 전개 계수 lc_i
mp.dps = 60
def lognf(n, d): return d+loggamma(n+1)-loggamma(n-d+1)+(n-d-2)*log(n-d)-(n-2)*log(n)
def lc(i, d): return Fraction(1, i)*(Fraction(d**(i+1), i+1)+2*d**i-sum(r**i for r in range(d)))
ok = True
for n, d in [(10**6, 7), (1000, 7), (500, 40)]:
    approx = sum(mpf(lc(i, d).numerator)/lc(i, d).denominator*mpf(n)**(-i) for i in range(1, 60))
    ok &= abs(lognf(n, d)-approx) < mpf(10)**-50
rec("lc_i 전개 (세 점, 60자리)", ok)
rec("lc_1=5d/2, lc_2=5d^2/4-d/12 (d=5)", lc(1, 5) == Fraction(25, 2) and lc(2, 5) == Fraction(5, 4)*25-Fraction(5, 12))

# 11. 동질 타일 합 hb_d 의 계수와 hb_d(1)
rho = sp.symbols('rho')
def hb(dd):
    tw = {1: 1}
    for j in range(2, dd+1): tw[j] = sp.Rational((j-1)**(j-1), math.factorial(j))
    V = [sp.Integer(1)]
    for m in range(1, dd+1):
        V.append(sp.expand((1+rho)*V[m-1]+sum(tw[j]*V[m-j] for j in range(2, m+1))))
    return V[dd]
ok = True
for dd in [3, 5, 8]:
    h = sp.Poly(hb(dd), rho)
    ok &= all(h.coeff_monomial(rho**j) == sp.Rational((j+1)*(dd+1)**(dd-j-1), math.factorial(dd-j)) for j in range(dd+1))
    ok &= h.eval(1) == sp.Rational((dd+1)**dd, math.factorial(dd))
rec("[rho^j]hb_d, hb_d(1) 닫힌 꼴 (d=3,5,8)", ok)

# 12. third-group (가): 셋째 후진 차분 공식
import random
random.seed(1)
ws = [0]+[random.random() for _ in range(60)]
def iota(v): return v*sum(ws[g]*max(v-g, 0) for g in range(1, 60)) if v >= 0 else 0
ok = abs(iota(2)-3*iota(1)+3*iota(0)-iota(-1)-2*ws[1]) < 1e-12
for v in [3, 4, 7, 12]:
    d3 = iota(v)-3*iota(v-1)+3*iota(v-2)-iota(v-3)
    ok &= abs(d3-(v*ws[v-1]-(v-3)*ws[v-2])) < 1e-9
rec("∇^3 ι_ws 공식", ok)

# 13. 중앙 이항계수 상하계 (sign-sandwich (다), kernel-sandwich (나))
def cb(m): return math.comb(2*m, m)/4**m
ok = all((1-2/13**2)/math.sqrt(math.pi) <= cb(r+3)*math.sqrt(r) <= 1/math.sqrt(math.pi) for r in range(169, 3000))
ok &= all(1/(math.sqrt(math.pi)*(1+1.25/r)) <= math.sqrt(r)*cb(r+2) <= 1/math.sqrt(math.pi) for r in range(1, 3000))
rec("cb 상하계 (r<3000 표본)", ok)

print("\n".join(out))
