# -*- coding: utf-8 -*-
"""심사 X2 — S1(망원곱 W_0 상계), S2(합산 손실 1/2), S4(6.48 vs 9.7), S5(Jensen 지수), S6(5.50 손실률 vs 6.21)의 정확 산술·수치 검산.
실행: python -I 심사_X2_S1S2S4S5_algebra.py > 심사_X2_S1S2S4S5_algebra_out.txt
"""
from fractions import Fraction as Fr
import math

out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

# ---------- 공통: Bor, Ren, Psi (고정밀 부동소수; 상대오차 1e-15 수준) ----------
def logBor(n):
    return -n + (n-1)*math.log(n) - math.lgamma(n+1)
def Bor(n): return math.exp(logBor(n))
def Ren(n): return n*Bor(n)
PSI = [0.0]
for j in range(1, 200001):
    PSI.append(PSI[-1] + Ren(j))
def Psi(d): return PSI[d]

# ================= S1: 정규화 H_d(m) 단조성 ⇔ 6.21, 망원곱 U_d^sharp, 최댓값 d=1 =================
P("## S1 정규화와 망원곱")
# (a) 6.21: (w+2)(m+1)c_{m+1}(w+1) >= w(m+2)c_m(w), w=m-d  ⇔  H_d(m+1) >= H_d(m), H_d(m)=(m-d)(m-d+1)/(m+1) c_m(m-d)
# 기호 검산: H_d(m+1)/H_d(m) = [(w+1)(w+2)/(m+2)] / [w(w+1)/(m+1)] * c_{m+1}(w+1)/c_m(w) = (w+2)(m+1)/(w(m+2)) * ratio >= 1  ⇔ 6.21. (손 검산; 자명)
# (b) 망원곱 U_d^sharp = prod_{m=k-1+d}^{2k-2} [H-정규화 비] = (k+d)(2k-1-d)(2k-d)/(2k^2(k-1))
def Ud_exact(k, d):
    # c_{m_d}(m_d-d) <= c_M(M-d) * [ (M-d)(M-d+1)/(M+1) ] * [ (m_d+1)/((m_d-d)(m_d-d+1)) ],  m_d=k-1+d, M=2k-1
    md, M = k-1+d, 2*k-1
    return Fr((M-d)*(M-d+1), M+1) * Fr(md+1, (md-d)*(md-d+1))
bad = 0
for k in range(2, 60):
    for d in range(1, k+1):
        lhs = Ud_exact(k, d)
        rhs = Fr((k+d)*(2*k-1-d)*(2*k-d), 2*k*k*(k-1))
        if lhs != rhs: bad += 1
P("U_d^sharp 닫힌 꼴 불일치 수 (k<60, 1<=d<=k):", bad)
# (c) 1 - U_{d+1}/U_d = (3d+2)/((2k-d)(k+d))
bad = 0
for k in range(2, 60):
    for d in range(1, k):
        U1 = Fr((k+d)*(2*k-1-d)*(2*k-d), 2*k*k*(k-1)); U2 = Fr((k+d+1)*(2*k-2-d)*(2*k-d-1), 2*k*k*(k-1))
        if 1 - U2/U1 != Fr(3*d+2, (2*k-d)*(k+d)): bad += 1
P("비 항등식 1-U_{d+1}/U_d=(3d+2)/((2k-d)(k+d)) 불일치 수:", bad)
# (d) 6.21 적용 조건 m>=2d-1 for m in [k-1+d, 2k-2]  ⇔ d<=k ; m>=2 for k>=2 (d=k: 빈 곱)
P("조건: m_d=k-1+d>=2d-1 ⇔ d<=k (자명); d=k에서 U_k=", Fr((2*k)*(k-1)*k, 2*k*k*(k-1)) if True else None, "(k 임의) → 1")
# (e) d=1 값과 Stirling: W_0 <= Bor(k+1)(k+1)(2k-1)/k^2 <= (2pi)^{-1/2} (2k-1)/(k^2 sqrt(k+1)) < 2 (2pi)^{-1/2} k^{-3/2}
for k in [2, 3, 10, 100, 3131, 10**6]:
    U1 = Fr((k+1)*(2*k-1), k*k)
    b = Bor(k+1)*float(U1)
    st = (2*k-1)/(k*k*math.sqrt(k+1))/math.sqrt(2*math.pi)
    P(f"k={k}: Bor(k+1)U_1={b:.6e}, Stirling 상계={st:.6e}, 2/sqrt(2pi) k^-3/2={2/math.sqrt(2*math.pi)*k**-1.5:.6e}, 현행 gamma_W s_B k^-3/2={2*math.exp(0.0031)/math.sqrt(2*math.pi)*k**-1.5:.6e}")
P("상수: 2/e =", 2/math.e, " 현행 2e^{.0031}/e =", 2*math.exp(0.0031)/math.e)
# (f) 모든 k>=2: (2-1/k) sqrt(k/(k+1)) < 2 자명.

# ================= S2: Ren(n+1)/Ren(n) >= 1-1/(2n)  ⇔  (1+1/n)^n/e >= 1-1/(2n) =================
P("\n## S2 합산 손실")
worst = 1e9
for n in list(range(1, 20001)) + [10**5, 10**6, 10**7]:
    lhs = n*math.log1p(1/n) - 1   # log((1+1/n)^n/e)
    rhs = math.log1p(-1/(2*n))
    worst = min(worst, lhs - rhs)
P("min_n [log((1+1/n)^n/e) - log(1-1/(2n))] over n<=20000 ∪ {1e5,1e6,1e7} =", worst, "(>0이어야 함)")
# 해석: n log(1+1/n) = 1 - 1/(2n) + 1/(3n^2) - ... > 1 - 1/(2n) + 1/(3n^2) - 1/(4n^3); log(1-x) <= -x. 따라서 차 >= 1/(3n^2)-1/(4n^3) >0 (n>=1).
# 따라서 D_{n,k} >= (k-1)Bor(n)c_{n-1}(k-1)[ (n+1)Bor(n+1)/(n Bor(n)) - 1 ] >= -(k-1)/(2n) Bor(n) c_{n-1}(k-1) >= -(1/2) Bor(n) c_{n-1}(k-1)  (n>=k+1>k-1).
# 새 손실 상수 d(k) = (1/2)(2/e) + u(k)/(e 2^{3/2})
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
for k in [3131, 10001]:
    newd = 0.5*(2/math.e) + u(k)/(math.e*2**1.5)
    oldd = (2*math.exp(0.0031)/math.e)*(0.5+2.5/k+0.25/k**2) + u(k)/(math.e*2**1.5)
    P(f"k={k}: 새 d(k)={newd:.6f}  현행 d(k)={oldd:.6f}  본문 상계 {'0.420987' if k==3131 else '0.397933'}")
# 임계 창 앞쪽 (prop-W(다)) 쿠션 0.4345 대 새 손실 (1/2)(2/e)=1/e
P("prop-W(다): 쿠션 하계 0.4345 - 새 손실 1/e =", 0.4345 - 1/math.e, " (현행 0.4345-0.3697=0.0648)")

# ================= S6: 5.50 손실률 z_m(d) 대 6.21 손실률 (m+d+2)/((w+2)(m+1)) =================
P("\n## S6 5.50 vs 6.21 손실률 (6.21이 지배하는가)")
viol = []
for m in range(2, 2001):
    for d in range(1, m//2 + 1):
        w = m - d
        z = math.exp((d-1)/w)/(w+1) + 1.5*d/((w+1)*(m+1))
        l621 = (m+d+2)/((w+2)*(m+1))
        if l621 > z + 1e-15: viol.append((m, d, z, l621))
P("m<=2000, 1<=d<=m/2 에서 6.21 손실률 > 5.50 손실률인 쌍:", len(viol), viol[:5])

# ================= S4: 6.48(나) Psi(d)/(2m) <= c <= 3Psi(d)/(2m)  대  9.7 상하계 =================
P("\n## S4 6.48(나) 대 9.7 (계산 없는 명시 상하계)")
def lo97(m, d):
    w = m - d
    g = ((m+1)/(m-d+1))**1.5*math.exp(1/(12*(m-d+1)))
    num = g*(2*math.pi)**-0.5*(4/3*d**1.5 + 2*math.sqrt(d)) + g*g*(0.625*d*d + d)
    return Psi(d)/w*math.exp(-num/(w*Psi(d)))
def up97(m, d):
    return Psi(d)*(m+1)**1.5*math.exp(1/(12*(m+1)))/(m-d+1)**2.5
first_lo_ok = None; first_up_ok = None
lo_fail_m = []; up_fail_m = []
for m in range(4, 5001):
    dmax = int(math.floor(m**(2/3)/2))
    ok_lo = all(lo97(m, d) >= Psi(d)/(2*m) for d in range(1, dmax+1))
    ok_up = all(up97(m, d) <= 3*Psi(d)/(2*m) for d in range(1, dmax+1))
    if not ok_lo: lo_fail_m.append(m)
    if not ok_up: up_fail_m.append(m)
P("9.7 하계가 6.48 하계보다 약한 m (m<=5000):", len(lo_fail_m), "최대 m =", max(lo_fail_m) if lo_fail_m else None)
P("9.7 상계가 6.48 상계보다 약한 m (m<=5000):", len(up_fail_m), "최대 m =", max(up_fail_m) if up_fail_m else None)
# 소비처 범위: prop-W(다)는 m>=k+14>=3145, 14<=d<=m^{2/3}/2 에서 하계만 씀
mn = min(lo97(m, d)/(Psi(d)/(2*m)) for m in range(3145, 3146+2000, 7) for d in range(14, int(m**(2/3)/2)+1))
P("소비처 범위(m>=3145, 14<=d<=m^{2/3}/2, m 표본)에서 min 9.7하계/(Psi/2m) =", mn)

# ================= S5: F3 §3.1 Jensen 지수  δ/(1-δ)·(μ2-μ1)/μ1  with μ1>=Psi(d), μ2-μ1 <= d(1-δ)^{-3/2}e^{1/(12(m+1))} =================
P("\n## S5 6.52(lemma-H)형 하계의 지수 손실 (m>=2001, 14<=d<=m^{2/3}/2)")
def expo(m, d):
    dl = d/m
    return dl/(1-dl)*d*(1-dl)**-1.5*math.exp(1/(12*(m+1)))/Psi(d)
mx = 0; arg = None
for m in list(range(2001, 20001)) + [int(2001*1.01**i) for i in range(1, 800) if 2001*1.01**i < 2e5]:
    dmax = int(math.floor(m**(2/3)/2))
    for d in range(14, dmax+1):
        e = expo(m, d)
        if e > mx: mx, arg = e, (m, d)
P("max 지수 =", mx, "at (m,d)=", arg, "; log2 =", math.log(2), "; F3 주장 .663774")
# 9.8의 Psi 하계(0.7978 sqrt d - 0.8848)를 쓰면:
def expo_lb(m, d):
    dl = d/m; ps = 0.7978*math.sqrt(d) - 0.8848
    return dl/(1-dl)*d*(1-dl)**-1.5*math.exp(1/(12*(m+1)))/ps
mx2 = 0; arg2 = None
for m in list(range(2001, 20001, 3)):
    dmax = int(math.floor(m**(2/3)/2))
    for d in range(14, dmax+1):
        e = expo_lb(m, d)
        if e > mx2: mx2, arg2 = e, (m, d)
P("Psi 하계(9.8) 사용 시 max 지수 =", mx2, "at", arg2)
# 소비처(prop-W(다)) 범위는 m>=3145 이므로 더 여유 있음:
mx3 = max(expo(m, d) for m in range(3145, 30000, 5) for d in range(14, int(m**(2/3)/2)+1))
P("소비처 범위 m>=3145 에서 max 지수 =", mx3)
# 6.53의 Low(k,rho) 꼴과 같은 입력임을 적어 둔다.

with open(__file__.replace(".py", "_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
