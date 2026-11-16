# -*- coding: utf-8 -*-
# 검토전체3 I7b: 장7B 7.6-7.8절의 수치 상수와 항등식 재계산.
# 정확 부분은 Fraction, 상수 부분은 float(여유가 충분히 큼).
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, pi, floor, ceil
import sys

out = []
def rep(name, ok, detail=""):
    out.append(("OK " if ok else "FAIL") + " | " + name + (" | " + detail if detail else ""))

# ---------- 정확 계산: A_{n,l}, p_n, s_m(y), P_n(j) ----------
MAXN = 36
p = [Fr((n+1)**(n-1)) if n >= 1 else Fr(1) for n in range(MAXN+2)]
A = [[Fr(0)]*(MAXN+2) for _ in range(MAXN+2)]
for l in range(MAXN+2):
    A[0][l] = Fr(1)
for n in range(1, MAXN+2):
    for l in range(MAXN+2):
        A[n][l] = sum(Fr(comb(n-1, j))*min(j+1, l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
def Aget(n, l):
    if l < 0: return Fr(0)
    return A[n][l]
def s(m, y):  # s_m(y)=A_{m,y-1}/p_m
    return Aget(m, y-1)/p[m]
def c(m, Y):  # c_m(Y)=b_{m,Y}/p_m
    return (Aget(m, Y)-Aget(m, Y-1))/p[m]
def b(m, l):
    return Aget(m, l)-Aget(m, l-1)
def d(n, k):
    return b(n, k)-b(n, k-1)
def P(n, j):  # 마지막 차 자리 법칙
    return Fr(j*comb(n-1, j-1))*p[j-1]*p[n-j]/p[n]
def F(n, chi):
    return sum(P(n, j) for j in range(1, chi+1))
def Pk(n, j, k):  # 뿌리 자리 법칙
    return Fr(min(j, k))*comb(n-1, j-1)*Aget(j-1, k-1)*Aget(n-j, k-1)/Aget(n, k-1)
def clp(m, k): return c(m, k)/s(m, k)
def clm(m, k): return c(m, k-1)/s(m, k)
def mu(m, k): return clp(m, k)-clm(m, k)
def chi(m, j, k):
    h = 1 if j > k else 0
    t = 1 if j == k else 0
    lin = Fr(1, k)*(-t*(1-clm(m-k, k)) + h*(clp(j-1, k)+clm(j-1, k)+clp(m-j, k)+clm(m-j, k)))
    quad = (1+Fr(h, k))*clp(j-1, k)*clp(m-j, k) + (1-Fr(h, k))*clm(j-1, k)*clm(m-j, k)
    return lin, quad
def src(m, k):
    return sum(Pk(m, j, k)*sum(chi(m, j, k)) for j in range(1, m+1))
def inh(m, k):
    tot = Fr(0)
    for j in range(1, m+1):
        L, R = j-1, m-j
        tot += Pk(m, j, k)*((mu(L, k) if k <= L <= 2*k else 0) + (mu(R, k) if k <= R <= 2*k else 0))
    return tot
def hz(N, k): return 1 - s(N+1, k)/s(N, k)

# (1) 보조정리 root-symmetry: V(nu)=1, V(q+1)/V(q)=e^{g(k+1+q)-g(k+nu-1-q)} (정확: e^{g(x)}=(1+1/x)^{x-1})
def eg(x): return (Fr(x+1, x))**(x-1)
ok = True
for k in (2, 3, 5):
    for nu in (1, 2, 4):
        n = 2*k+nu
        if n > MAXN: continue
        V = lambda q: Fr(k, k+1+q)*P(n, k+1+q)/P(n, k)
        ok &= (V(nu) == 1)
        for q in range(0, k+nu-1):
            ok &= (V(q+1)/V(q) == eg(k+1+q)/eg(k+nu-1-q))
        ok &= all(V(q) >= 1 for q in range(nu, k+nu))
rep("root-symmetry (가)(나) 정확", ok)

# (2) (7.23): 이차 몫을 뺀 원천의 k s_n 배가 우변과 같음(정확)
ok = True
for k in (2, 3, 4):
    for nu in (1, 2, 3):
        n = 2*k+nu
        lhs = k*s(n, k)*sum(Pk(n, j, k)*chi(n, j, k)[0] for j in range(1, n+1))
        rhs = sum(Fr(k, j)*P(n, j)*((c(j-1, k-1)+c(j-1, k))*s(n-j, k) + s(j-1, k)*(c(n-j, k-1)+c(n-j, k))) for j in range(k+1, n+1)) - P(n, k)*s(n-k, k-1)
        ok &= (lhs == rhs)
rep("(7.23) 선형 몫 항등식(정확)", ok)

# (3) (7.24) 두 부등식(정확)
ok = True
for k in (2, 3, 4, 5):
    for nu in (1, 2, 3):
        n = 2*k+nu
        if n+1 > MAXN: continue
        V = lambda q: Fr(k, k+1+q)*P(n, k+1+q)/P(n, k)
        lhs = k*s(n, k)*src(n, k)
        mid = P(n, k)*(sum(V(q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1))
        last = P(n, k)*(c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1))
        ok &= (lhs >= mid >= last)
rep("(7.24) 정확 부등식", ok)

# (4) (7.25)/(7.26) 위험률 항등식(정확)
ok = True
for k in (2, 3, 5):
    for N in range(1, 22):
        f = {}
        for j in range(1, N+1):
            f[j] = (F(N, j)-F(N+1, j))/P(N, j)
            ok &= (0 <= f[j] <= 1)
        def sh(j):
            if j <= k-1: return Fr(0)
            return hz(j-1, k)*Fr(j, j+1) + Fr(1, j+1)
        rhs = sum(Pk(N, j, k)*(f[j]*sh(j) + (1-f[j])*hz(N-j, k)) for j in range(1, N+1))
        ok &= (hz(N, k) == rhs)
rep("(7.26) 위험률 항등식(정확)", ok)

# (5) hazard-floor (가): s_N-s_{N+1} >= P_{N+1}(N+1) k s_N/(N(N+1)); P_{N+1}(N+1)=((N+1)/(N+2))^N
ok = True
for k in (2, 3, 5):
    for N in range(k, 25):
        ok &= (P(N+1, N+1) == Fr(N+1, N+2)**N)
        ok &= (s(N, k)-s(N+1, k) >= P(N+1, N+1)*k*s(N, k)/(N*(N+1)))
        ok &= (Fr(N+1, N+2)**N >= Fr(1, 3))  # 1/e > 1/3 대충 확인
rep("hazard-floor (가) 정확 부등식", ok)

# (6) hazard-floor (나) 첫 부등식(정확 좌변, 정확 우변의 합 부분)과 확률 식 검사
ok = True
for k in (3, 5, 8):
    for N in range(k, 26):
        for U1 in range(0, min(k-1, N-k)+1):
            # 확률 식: F_N(N-U)-F_{N+1}(N-U) = P_N(N-U) - sum_{U'<=U} P_N(N-U')(1-rt_{U'})
            for U in range(0, U1+1):
                rt = lambda Up: P(N+1, N+1-Up)/P(N, N-Up)
                lhs = F(N, N-U)-F(N+1, N-U)
                rhs = P(N, N-U) - sum(P(N, N-Up)*(1-rt(Up)) for Up in range(0, U+1))
                ok &= (lhs == rhs)
            bound = Fr(k)*s(N, k)/(N*(N+1))*(sum(P(N, N-U) for U in range(U1+1)) - (U1+1)*(Fr(1, 2*(N-U1))+Fr(4, N*N)))
            ok &= (s(N, k)-s(N+1, k) >= bound)
rep("hazard-floor (나) 확률 식·첫 부등식(정확)", ok)

# (7) 상수들
c0 = (2*pi)**-0.5
rep("(가) 0.367 <= (2pi)^-1/2 e^-1/12", c0*exp(-1/12) >= 0.367, f"{c0*exp(-1/12):.6f}")
rep("(가) 2(2pi)^-1/2 <= 0.8", 2*c0 <= 0.8, f"{2*c0:.6f}")
rep("(2pi)^-1/2 <= 0.398943", c0 <= 0.398943, f"{c0:.7f}")
def im(m): return m*log(m/(m+1))+1
rep("i_N 상계식", all(0 <= im(m) <= 1/(2*(m+1))+1/(6*m*(m+1)) for m in range(1, 5000)))
N = 1000
rep("(라) e^{i_N+2.1/(N+1)} <= e^0.0027 at N=1000", im(N)+2.1/(N+1) <= 0.0027, f"{im(N)+2.1/(N+1):.6f}")
rep("(라) 0.8/0.367 <= 2.18, 2.18e^0.0027 <= 2.2", 0.8/0.367 <= 2.18 and 2.18*exp(0.0027) <= 2.2, f"{0.8/0.367:.4f} {2.18*exp(0.0027):.4f}")
rep("(마) e^{i_N}0.4/0.367<=1.1, e^{i_N}5.4/0.367<=15", exp(im(N))*0.4/0.367 <= 1.1 and exp(im(N))*5.4/0.367 <= 15, f"{exp(im(N))*0.4/0.367:.4f} {exp(im(N))*5.4/0.367:.3f}")
rep("(다) e^{-2.1/(N+1)} 인자는 여분(증명은 Ren/(N+1-j) 자체를 줌)", True)

# (8) 정리 H* 기저
k = 2000
def fl(m, U1): return 1-0.8/sqrt(U1+1)-(U1+1)*(1/(2*(m-U1))+4/m**2)
v1 = (0.2-1/(2*k)-4/k**2)*k/(k+1)
rep("H* 기저 (ㄱ) >= 0.1996", v1 >= 0.1996, f"{v1:.5f}")
a = (0.8*k)**(2/3)
fl2 = 1-0.8/sqrt(2)-(a+1)*(1/(2*k)+4/k**2); r2 = 1/(1+(a+1)/k)
rep("H* 기저 (ㄴ) fl>=0.399, ratio>=0.935, prod>=0.373", fl2 >= 0.399 and r2 >= 0.935 and fl2*r2 >= 0.373, f"{fl2:.4f} {r2:.4f} {fl2*r2:.4f}")
def fl3(m): return 1-0.8*(0.2*m)**(-1/3)-((0.2*m)**(2/3)+1)*(1/(2*m*(1-0.342*m**(-1/3)))+4/m**2)
mono = all(fl3(m+1) >= fl3(m) for m in range(2000, 200000))
rep("H* 기저 (ㄷ) fl3(2000)>=0.877, m에 증가, /4.0005>=0.219", fl3(2000) >= 0.877 and mono and fl3(2000)/4.0005 >= 0.219, f"{fl3(2000):.4f} mono={mono}")
rep("(0.2)^(2/3) <= 0.342", 0.2**(2/3) <= 0.342, f"{0.2**(2/3):.4f}")
# 직접: k=2000,3131,10000에서 모든 k<=m<=4k에 fl(m)k/(m+1)>=0.14
ok = True
for k in (2000, 3131, 10000):
    for m in range(k, 4*k+1):
        U1 = min(m-k, floor((0.2*m)**(2/3)))
        if not (U1 <= k-1): ok = False
        if fl(m, U1)*k/(m+1) < 0.14: ok = False; break
rep("H* 기저: 세 k에서 모든 m in [k,4k]에 fl(m)k/(m+1)>=0.14 직접", ok)

# (9) 정리 H* 귀납 수치
rep("0.8/sqrt(2000)=0.01789", abs(0.8/sqrt(2000)-0.01789) < 1e-5, f"{0.8/sqrt(2000):.6f}")
rep("15*1.000125/sqrt(2000) <= 0.3355", 15*1.000125/sqrt(2000) <= 0.3355, f"{15*1.000125/sqrt(2000):.5f}")
def L(w): return 0.98211*((1-1.1/(w-1)**2-0.3355/(w*(w-1)))*0.999875/0.14-1)
def Rr(w): return 2.2*w/(w-1)*(1+1.5/(w-1)+0.000125)
ws = [4+i*0.01 for i in range(0, 100000)]
rep("H* 귀납: L(4)=4.978, R(4)=4.400, L 증가 R 감소, L>R", abs(L(4)-4.978) < 1e-3 and abs(Rr(4)-4.400) < 1e-3 and all(L(ws[i+1]) >= L(ws[i]) and Rr(ws[i+1]) <= Rr(ws[i]) for i in range(len(ws)-1)) and all(L(w) > Rr(w) for w in ws), f"{L(4):.4f} {Rr(4):.4f}")
# gain_N -1 >0 at w=4
rep("gain-1>0 at w=4", (1-1.1/9-0.3355/12)*0.999875/0.14-1 > 0)

# (10) 정리 W
rep("1-0.8/sqrt(301) >= 0.9538", 1-0.8/sqrt(301) >= 0.9538, f"{1-0.8/sqrt(301):.5f}")
rep("0.9538/0.398943 >= 2.38", 0.9538/0.398943 >= 2.38, f"{0.9538/0.398943:.4f}")
n = 6263
rep("(나) e^{-i_n} >= 0.9999 at n=6263", exp(-im(n)) >= 0.9999, f"{exp(-im(n)):.6f}")
rep("0.14*2.38*0.9999 >= 0.33316", 0.14*2.38*0.9999 >= 0.33316, f"{0.14*2.38*0.9999:.6f}")
def D(k, w): return 0.33316*sqrt(k)*(1-1/w)**2 - w - 42.14/k
k = 3131
rep("D_3131(2) = 2.647", abs(D(k, 2)-2.647) < 2e-3, f"{D(k,2):.4f}")
wmax_bound = k**(1/3)*(1+1/k)**(4/3)+1+2/k
rep("w_max <= 1.0005k^{1/3}+1.001", wmax_bound <= 1.0005*k**(1/3)+1.001, f"{(1+1/k)**(4/3):.6f} {2/k:.6f}")
t = k**(1/6)
rep("k^{1/6}>=3.8249 at 3131", t >= 3.8249, f"{t:.5f}")
val = 0.33316*(k**0.5-2*k**(1/6)+k**(-1/6))-1.0005*k**(1/3)-1.0145
rep("D_k(w_max) 하계 = 0.529 at 3131", abs(val-0.529) < 2e-3, f"{val:.4f}")
der = 0.33316*(3*k**(1/3)-2-k**(-1/3))-2.001*k**(1/6)
rep("도함수 양수 at 3131", der > 0, f"{der:.3f}")
rep("1.001+42.14/3131 <= 1.0145", 1.001+42.14/3131 <= 1.0145, f"{1.001+42.14/3131:.5f}")
# 직접: 여러 k에서 D_k(w)>0 on [2, n_PD/k]
ok = True
for k in (3131, 4000, 6667, 10**4, 10**5, 10**6):
    nPD = ceil((k+1)**(4/3))+k+1
    wm = nPD/k
    ok &= (nPD >= 3*k+2)
    for i in range(0, 20001):
        w = 2+(wm-2)*i/20000
        if D(k, w) <= 0: ok = False; break
rep("D_k(w)>0 on [2,w_max] 직접(여섯 k), n_PD>=3k+2", ok)
# G_k(n)>1 직접(정의대로), k=3131, 모든 2k+1<=n<=n_PD-1
k = 3131
ok = True
nPD = ceil((k+1)**(4/3))+k+1
for n in range(2*k+1, nPD):
    G = 0.14/n*(2.38*k**1.5*(n-k+1)**2/(exp(im(n))*n*(n+1))-301)
    if G <= 1: ok = False; break
rep("G_3131(n)>1 for all 2k+1<=n<n_PD 직접", ok, f"n_PD={nPD}")

# (11) 보조정리 threshold-unit-ratio
k = 6667
j0 = floor(0.3*k)
v = -(0.3*k-1)*(0.3*k)/(2*(1.3*k+1))
rep("-(0.3k-1)(0.3k)/(2(1.3k+1)) = -230.6 at 6667", abs(v+230.6) < 0.1, f"{v:.2f}")
v2 = 1+1.5*log(k)+v
rep("1+1.5log k + ... = -216.4", abs(v2+216.4) < 0.1, f"{v2:.2f}")
rep("e^0.3 <= 1.34986", exp(0.3) <= 1.34986, f"{exp(0.3):.6f}")
rep("e^{3/(2k)} <= 1.00023", exp(1.5/k) <= 1.00023, f"{exp(1.5/k):.7f}")
rep("1.00023*1.34986 < 1.3502", 1.00023*1.34986 < 1.3502, f"{1.00023*1.34986:.6f}")
rep("2*0.7654-1.3502 >= 0.18", 2*0.7654-1.3502 >= 0.18, f"{2*0.7654-1.3502:.4f}")
rep("실제 j0 하계 식: j0(j0+1)/(2(k+1+j0)) >= 230.6", j0*(j0+1)/(2*(k+1+j0)) >= 230.6, f"{j0*(j0+1)/(2*(k+1+j0)):.2f}")
rep("「1.35배 미만」 주장: 증명된 상계 1.3502 > 1.35", 1.00023*1.34986 > 1.35, f"{1.00023*1.34986:.6f}")
# 분모 하계: C(2k-1,k)k^{k-1}(k-1)^{k-2}/(2k)^{2k-2} >= e^{-1}k^{-3/2} (정확 비교, 작은 k와 중간 k)
ok = True
for k in (3, 5, 10, 50, 200):
    lhs = Fr(comb(2*k-1, k)*k**(k-1)*(k-1)**(k-2), (2*k)**(2*k-2))
    ok &= (float(lhs) >= exp(-1)*k**-1.5)
rep("s_N(k) 분모 하계 e^{-1}k^{-3/2} 수치", ok)
# 망원 꼴 정확 검사: u_{3k}/w_k = e^{g(2k)-g(k)} r^thr, e^{g(2k)-g(k)} = (1+1/(2k))^{2k-1}/(1+1/k)^{k-1}
ok = True
for k in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
    n = 3*k
    if n > MAXN: continue
    w = lambda m: Fr(comb(n-1, m))*p[m]*Aget(n-1-m, k-1)/Aget(n, k-1)
    u3k = w(2*k)*s(2*k, k+1)
    rthr = s(2*k, k+1)/s(2*k-1, k)
    ok &= (u3k/w(k) == eg(2*k)/eg(k)*rthr)
    # 분할 무게 비감소 (k-1<=m<=2k)
    ws_ = [Fr(0)]+[w(m) for m in range(k, 2*k+1)]
    ok &= all(ws_[i+1] >= ws_[i] for i in range(len(ws_)-1))
rep("threshold-unit-ratio 첫 등식·분할 무게 비감소(정확, n=3k)", ok)

# (12) (7.28),(7.29),(7.30) 정확 검사
ok28 = ok29 = ok30 = True
for k in (2, 3, 4, 5, 6, 7):
    for n in range(2*k+1, min(3*k, MAXN)+1):
        KD = sum(Fr(k+n-m)*comb(n-1, m)*p[n-1-m]*d(m, k) for m in range(2*k+1, n))
        ok29 &= (Aget(n, k-1)*(src(n, k)+inh(n, k)) == d(n, k)-KD)
    n = 3*k
    if n <= MAXN:
        w = lambda m: Fr(comb(n-1, m))*p[m]*Aget(n-1-m, k-1)/Aget(n, k-1)
        pm = lambda m: ((k+1)*b(m, k)-(k-1)*b(m, k-1))/p[m]
        Left = sum(w(m)*pm(m) for m in range(k, 2*k+1))
        u3k = w(2*k)*s(2*k, k+1)
        Quad = sum(Pk(n, j, k)*chi(n, j, k)[1] for j in range(k+1, n+1))
        Stem = Fr(1, k)*sum(Pk(n, j, k)*((clp(j-1, k)+clm(j-1, k))*(1 if j-1 > 2*k else 0)+(clp(n-j, k)+clm(n-j, k))*(1 if n-j > 2*k else 0)) for j in range(k+1, n+1))
        ok30 &= (src(n, k)+inh(n, k) == 2*Left-u3k+Quad+Stem)
    for n in range(3*k+1, min(3*k+4, MAXN)+1):
        w = lambda m: Fr(comb(n-1, m))*p[m]*Aget(n-1-m, k-1)/Aget(n, k-1)
        pm = lambda m: ((k+1)*b(m, k)-(k-1)*b(m, k-1))/p[m]
        Left = sum(w(m)*pm(m) for m in range(k, 2*k+1))
        inhlin = Fr(1, k)*sum(Pk(n, j, k)*((clp(j-1, k)+clm(j-1, k))*(1 if k <= j-1 <= 2*k else 0)+(clp(n-j, k)+clm(n-j, k))*(1 if k <= n-j <= 2*k else 0)) for j in range(1, n+1))
        ok28 &= (inhlin+inh(n, k) == 2*Left)
rep("(7.29) 정확", ok29); rep("(7.30) 정확", ok30); rep("(7.28) 정확", ok28)

# (13) 정리 old-6-22: x_k n > 368 at k=501, n=1003; n^flat>3k 추정의 수치
k = 501
xk = (k/(k+1))**(k-1)
rep("x_k n > 368 (k=501,n=1003)", xk*1003 > 368, f"{xk*1003:.2f}")
rep("x_k >= 1/e", xk >= exp(-1))
# 16.5 상계: m#<2, x n/k<=3
rep("(m#)^2+(m#+3)^2/2 < 16.5", 4+12.5 <= 16.5)

# (14) 6.2절 old-7-24와 비교: 0.307/(N+1) >= 0.14/N for N>=1
rep("0.307/(N+1) >= 0.14/N (N>=1)", all(0.307/(N+1) >= 0.14/N for N in range(1, 100000)))

print("\n".join(out))
