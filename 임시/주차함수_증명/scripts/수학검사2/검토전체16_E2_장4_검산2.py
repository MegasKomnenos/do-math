# 검토전체16 E2: 4장 4.3절 해석 상수 검산
# (1) 보조정리 gauss-contraction: 잔차 R(iota) 의 x^0..x^3 계수 소멸(수치), C_i 값, 수축 상수
# (2) g(kappa) Taylor 계수 (수치 미분으로 2차 계수 확인), (4.9) 와 M4/M0 공식 (정확 유리수, 작은 k)
# (3) 보조정리 gauss-coeff (가)(나)(다) 를 k=10000, 30000 에서 정확 유리수 Hermite 수로 직접 확인
# (4) 따름정리 gauss-coeff-numeric 의 상수와 유리수
from fractions import Fraction as Fr
from math import comb, sqrt, exp, log, gamma, pi
import mpmath as mp
mp.mp.dps = 50

# ---- (1) 잔차 계수 ----
def ups0(i): return (1 + mp.sqrt(1 - 4 * i)) / 2
def C1(i):
    u = ups0(i); g = 2 * u - 1
    return (1 - u) / g**2
def C2(i):
    u = ups0(i); g = 2 * u - 1
    return -(1 - u) * (2 + u) / g**5
def C3(i):
    u = ups0(i); g = 2 * u - 1
    return 5 * (1 - u) * (6 + g - g**2) / (2 * g**8)
def uhat(i, x): return ups0(i) + x * C1(i) + x**2 * C2(i) + x**3 * C3(i)
def R(i, x): return (uhat(i, x) - 1) * uhat(i - x, x) + i
# x 의 거듭제곱 전개: 작은 x 에서 R ~ c4 x^4 이어야 함
for i in [mp.mpf('0.05'), mp.mpf('0.15'), mp.mpf('0.2')]:
    for x in [mp.mpf('1e-3'), mp.mpf('1e-4'), mp.mpf('1e-5')]:
        print(f"iota={float(i)} x={float(x)}: R/x^4 = {mp.nstr(R(i,x)/x**4, 8)}")
g13 = mp.mpf(1) / 3
print("C at gamma=1/3:", mp.nstr(C1((1-g13**2)/4), 10), mp.nstr(C2((1-g13**2)/4), 10), mp.nstr(C3((1-g13**2)/4), 10))
print("합 11328660 =", 120*3**7//24 + (192*3**8 + 60*3**7)//6 + (175*3**9 + 96*3**8 + 15*3**7)//2 + 5*(48*3**10 + 35*3**9 + 12*3**8 + 5*3**7)//2)
x = mp.mpf('1.12e-5')
tot = 468018 + (216*60750 + 34020*378) * x + 34020 * 60750 * x**2 + (mp.mpf(1)/3 + 4e-5) * 11328660
print("|R|/x^4 총합 <= ", mp.nstr(tot, 10))

# ---- (2) g(kappa) Taylor 계수 ----
def gfun(kap, nu, th):
    Nt = 3 + (nu + 1 - th) * kap
    x = (1 - th * kap) * kap / Nt**2
    xn = (2 + (nu - 1) * kap) * (1 - th * kap) / Nt**2
    return (Nt * uhat(xn, x) - 2 - nu * kap) / kap
for nu in [0, -1]:
    for th in [mp.mpf(0), mp.mpf('0.5'), mp.mpf(1)]:
        # Taylor 계수 추정: g(k) 를 kappa 의 다항식으로 보고 mpmath taylor
        coeffs = mp.taylor(lambda kk: gfun(kk, nu, th), mp.mpf('1e-30'), 5)
        c2_claim = 506 + 97*nu + 5*nu**2 + (168 + 16*nu)*th + 12*th**2
        print(f"nu={nu} th={float(th)}: g0={mp.nstr(coeffs[0],8)} g1={mp.nstr(coeffs[1],8)} (claim {-(26+4*nu+8*th)}) g2={mp.nstr(coeffs[2],8)} (claim {c2_claim}) g3={mp.nstr(coeffs[3],8)} g4={mp.nstr(coeffs[4],8)}")

# ---- (2b) (4.9), M4/M0 공식: 정확 Hermite 수 (y=k 정수) ----
def hermite(N_, y, n):
    He = [Fr(1), Fr(N_)]
    for j in range(2, n + 1):
        He.append(N_ * He[j-1] - (j - 1) * y * He[j-2])
    return He
def M_ratio(r, k, n, y):
    # M_r^{(y,n)} / M_0^{(y,n)} = [Y^n](1-Y)^{r+1} B(Y) / [Y^n](1-Y) B(Y), B = exp(N Y - y Y^2/2), [Y^j]B = He_j/j!
    N_ = n + y + 1
    He = hermite(N_, y, n)
    from math import factorial
    def coef(rr):
        return sum((-1)**i * comb(rr + 1, i) * He[n - i] / factorial(n - i) for i in range(rr + 2) if n - i >= 0)
    return coef(r) / coef(0)
for k in [5, 7, 10, 23]:
    for n in [2*k - 1, 2*k]:
        y = k; N_ = n + y + 1
        He = hermite(N_, y, n)
        theta = He[n] / He[n-1] - n
        r2 = M_ratio(2, k, n, y)
        claim2 = (theta * ((n - y)**2 + n) - n*(n+1)) / (y**2 * theta)
        r4 = M_ratio(4, k, n, y)
        kk = Fr(k)
        if n == 2*k:
            claim4 = 1 + 16/kk + 18/kk**2 + 2/kk**3 - (4 + 38/kk + 22/kk**2 + 2/kk**3) / theta
        else:
            claim4 = 1 + 12/kk - 6/kk**2 - (4 + 26/kk - 14/kk**2) / theta
        print(f"k={k} n={n}: (4.9) {r2 == claim2}, M4/M0 식 {r4 == claim4}")

# ---- (3) gauss-coeff 직접 확인 (y=k, 정확 유리수) ----
for k in [10000, 30000]:
    for n in [2*k - 1, 2*k]:
        N_ = n + k + 1
        He = hermite(N_, k, n)
        theta = He[n] / He[n-1] - n
        r2 = M_ratio(2, k, n, k); r4 = M_ratio(4, k, n, k)
        # M0 = e^{-k/2} He_{n-1} theta / p_n  -> 로그로
        logM0 = -k/2 + float(mp.log(mp.mpf(He[n-1].numerator)) - mp.log(mp.mpf(He[n-1].denominator))) + log(float(theta)) - (n - 1) * log(n + 1)
        M0 = exp(logM0)
        gk = 2 - k * float(r2)
        print(f"k={k} n={n}: theta={float(theta):.8f}  M0={M0:.6f} (>=5.642? {M0>=5.642}; 4sqrt2(1-26/k)={4*sqrt(2)*(1-26/k):.6f})  k*M2/M0={float(k*r2):.6f}  k^2*M4/M0={float(k*k*r4):.5f}  g_k={gk:.5f}")

# ---- (4) 따름정리 ----
a0 = mp.quad(lambda w: mp.e**(-w**3/3), [0, mp.inf]); a1 = mp.quad(lambda w: w*mp.e**(-w**3/3), [0, mp.inf])
print("a0 =", mp.nstr(a0, 12), " a1 =", mp.nstr(a1, 12), " 3^{-2/3}Gamma(1/3) =", mp.nstr(mp.mpf(3)**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3), 12))
w = Fr(699, 100)
val = w - Fr(7, 2) - (4*w + Fr(1,2)) * Fr(3,2) / 31 - Fr(13,2) * w * 1 / 961 - 12 * w / 30000
print("(나) 유리수:", val, "==", Fr(495594511, 240250000), val == Fr(495594511, 240250000), float(val))
w = Fr(698, 100)
val2 = w - Fr(7,2) - (4*w + Fr(1,2)) * Fr(12879, 10000) * Fr(464159, 10**7) - Fr(13,2) * w * Fr(939, 1000) * Fr(464159, 10**7)**2 - 12 * w / 10000
print("(다):", float(val2), ">=1.6809:", val2 >= Fr(16809, 10000))
# (라) of gauss-contraction: 11/2 x + 350 n x^2 < 10/k at k=10000
for nu in [-1, 0, 5]:
    for th in [0, 1]:
        k = 10000; n = 2*k + nu; y = k - th; N_ = n + y + 1; x = Fr(y, N_**2)
        print(f"nu={nu} th={th}: q={float(Fr(n)*x):.6f} <2/9, x={float(x):.3e}<=1.12e-5: {x <= Fr(112,10**7)}, 11/2x+350nx^2={float(Fr(11,2)*x + 350*n*x*x):.6e} < 10/k={1e-3}: {Fr(11,2)*x + 350*n*x*x < Fr(10,k)}")
