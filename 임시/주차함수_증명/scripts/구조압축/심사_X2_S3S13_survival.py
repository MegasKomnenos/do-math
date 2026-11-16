# -*- coding: utf-8 -*-
"""심사 X2 — S3(10.21을 y>=4000으로; 6.1 따름), S13(생존 상계 비 표·수준 질량 하계 비 표 재계산), C3(Abel 합 7/10), 8.10(가) vs 6.1.
생존 확률 s_m(y)는 (6.1)의 마지막 차 재귀를 배정밀도로 풀어 얻는다(numpy 벡터화).
실행: python -I 심사_X2_S3S13_survival.py > 심사_X2_S3S13_survival_out.txt
"""
import math, sys, time
import numpy as np
from math import lgamma, log, exp, sqrt, pi

out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s, flush=True)

def logBor(n): return -n + (n-1)*log(n) - lgamma(n+1)
def Bor(n): return exp(logBor(n))
def Ren(n): return n*Bor(n)

# ---------------- 생존 확률 s_m(y) 재귀 (6.1) ----------------
def survival(y, M):
    """s[m]=Pr_m(M<=y-1), m=0..M. s_m=1 for m<=y-1."""
    s = np.ones(M+1)
    lg = np.array([lgamma(i+1) for i in range(M+2)])          # lgamma(i+1)=log(i!)
    def logp(n):  # p_n=(n+1)^(n-1)
        return (n-1)*np.log(n+1)
    for m in range(y, M+1):
        j = np.arange(1, m+1)
        # P_m(j) = j C(m-1,j-1) p_{j-1} p_{m-j} / p_m
        lP = np.log(j) + (lg[m-1] - lg[j-1] - lg[m-j]) + logp(j-1) + logp(m-j) - logp(m)
        Pm = np.exp(lP)
        fac = np.minimum(j, y)/j
        s[m] = np.sum(Pm*fac*s[j-1]*s[m-j])
    return s

# ---------------- S3: 10.21의 7단계 계수 재유도 (q>=277) ----------------
P("## S3 10.21 증명 7단계의 계수와 네 경우 (q>=277)")
c0 = 2*(2*pi)**-0.5
def Fcal(u): return c0*(1+2*u*u)*sqrt(1-u*u)
def Ecoef(u, q):  # E(q,rho) <= c0[ (1/4)(1-1/(2q))^{-3/2} + (1+u+u^2)(1-u)^{-1/2}(1+u)^{-3/2} ]/q  → 계수
    return c0*(0.25*(1-1/(2*q))**-1.5 + (1+u+u*u)*(1-u)**-0.5*(1+u)**-1.5)
for q in [277, 389]:
    P(f"q={q}: max_u<=0.9 계수 = {max(Ecoef(u,q) for u in np.linspace(0,0.9,9001)):.4f} (본문 2.82); "
      f"max_(0.9,0.99] = {max(Ecoef(u,q) for u in np.linspace(0.9,0.99,9001)):.4f} (9.3); "
      f"max_(0.99,0.9999] = {max(Ecoef(u,q) for u in np.linspace(0.99,0.9999,90001)):.4f} (85)")
P("F 최댓값 2/sqrt(pi) =", 2/sqrt(pi), "; u in (0.9,0.99]: F<=", Fcal(0.9), "; u in (0.99,0.9999]: F<=", Fcal(0.99))
for q in [277, 389]:
    P(f"q={q}: 1.1284+2.82/q={1.1284+2.82/q:.6f}; 1.044+9.3/q={1.044+9.3/q:.6f}; 0.34+85/q={0.34+85/q:.6f}; 직접 셈 0.182+7.3e-4*... <0.19")
# 넷째 경우의 두 수치: q/50-1/2 >= 0.77 q/50 ⇔ q>=109 ; 𝔳(θ)<=1.6θ for θ<=1/50
P("q/50-1/2 >= 0.77q/50 ⇔ q >=", 0.5/(0.23/50)); P("𝔳(0.02)=", (1-0.02)**-1.5-1, "<= 1.6*0.02 =", 0.032)
# 문턱: y>=4000 ⇒ q > (1.15y)^{2/3} >= 4600^{2/3}
P("(1.15*4000)^{2/3} =", (1.15*4000)**(2/3), "→ q>=277")
# 6.1 따름: 1.15(k+q+1)/(q+1)^{3/2} <= 3k/q^{3/2} for 1<=q<=k ⇔ 1.15(k+q+1) q^{3/2} <= 3k (q+1)^{3/2}; 충분조건 1.15(k+q+1)<=3k
P("1.15(2k+1)<3k ⇔ k>", 1.15/(3-2.3))

# ---------------- 수치 표 (k=6668) ----------------
def tables(k):
    t0 = time.time()
    M = 2*k + 2
    LB = np.array([0.0]+[logBor(n) for n in range(1, M+3)])   # LB[n]=log Bor(n)
    LR = LB + np.log(np.maximum(np.arange(M+3),1))             # LR[n]=log Ren(n)
    s_k   = survival(k,   M)
    s_kp1 = survival(k+1, M)
    s_km1 = survival(k-1, M)
    P(f"\n## k={k}: 재귀 완료 {time.time()-t0:.1f}s")
    # 진단: s_{k+q}(k) 단조, c>=0
    c_k = lambda m: s_kp1[m] - s_k[m]          # c_m(k)
    # --- 생존 상계 비 표: 상계 / 참값  for s_{k+q}(k)
    def b61(q):  return min(1, 3*k*q**-1.5)
    def b1021(q): return min(1, 1.15*(k+q+1)/(q+1)**1.5)
    def b1011(q):
        m = k+q
        r = np.arange(0, q)
        return 1 - np.sum(np.exp(LB[r+1])*(q-r)/(m-r))
    def b810(q):
        N = k+q
        ms = np.arange(k+1, N+1)
        lth = LB[ms] + LR[N+1-ms] - LB[N+1]
        B = np.sum(np.exp(lth)*(ms-k)/ms)
        return 1/(1+B)
    def b88(q):  # 8.8 탈출 하계
        N = k+q
        ms = np.arange(k+1, N+1)
        lpi = LB[ms] + LB[N+1-ms] - LB[N+1]
        pim = np.exp(lpi)
        pi0 = 1 - pim.sum(); km = np.sum(pim*k/ms)
        return pi0/(1-km)
    xi_pts = [("xi=1", int(round(k**(2/3)))), ("xi=2", int(round(2*k**(2/3)))), ("xi=4", int(round(4*k**(2/3)))), ("q=k/2", k//2), ("q=k", k)]
    P("생존 s_{k+q}(k): 상계/참값   [6.1, 10.21, 10.11, 8.10(가)] ; 8.8 하계/참값")
    for name, q in xi_pts:
        tr = s_k[k+q]
        P(f"  {name:6s} q={q:5d} 참값={tr:.5e}  6.1={b61(q)/tr:6.2f} 10.21={b1021(q)/tr:6.2f} 10.11={b1011(q)/tr:7.2f} 8.10={b810(q)/tr:6.2f} | 8.8={b88(q)/tr:5.3f}")
    # 8.10(가) <= 6.1 전수 (1<=q<=k)
    worst = -1; wq = None
    for q in range(1, k+1):
        r = b810(q)/b61(q)
        if r > worst: worst, wq = r, q
    P(f"  max_q 8.10(가)/6.1 = {worst:.4f} at q={wq}  (<=1 이면 8.10(가)가 6.1을 지배)")
    # 참값 상수: max_q s_{k+q}(k) q^{3/2}/k
    qs = np.arange(1, k+1)
    P("  참값 max_q s_{k+q}(k) q^{3/2}/k =", float(np.max(s_k[k+qs]*qs**1.5/k)), "(F5: 1.07–1.14)")
    # --- 수준 질량 하계 비 표: k c_{k+q}(k) 참값 대 [6.48(나), 9.7, 6.53, 10.27]
    PSI = np.concatenate([[0.0], np.cumsum([Ren(j) for j in range(1, 2*k+3)])])
    def lo648(q):  # m=k+q, d=q, 범위 d<=m^{2/3}/2
        m = k+q
        return k*PSI[q]/(2*m) if q <= m**(2/3)/2 else None
    def lo97(q):
        m, d = k+q, q; w = k
        g = ((m+1)/(m-d+1))**1.5*exp(1/(12*(m-d+1)))
        num = g*(2*pi)**-0.5*(4/3*d**1.5+2*sqrt(d)) + g*g*(0.625*d*d+d)
        return k*PSI[d]/w*exp(-num/(w*PSI[d]))
    def lo653(q):  # (k+1)c_m(k) >= Low(k,rho) ; q>=2
        rho = q/k**(2/3); eps = k**(-1/3)
        if 2*sqrt(rho) <= 2.218*eps: return None
        Low = (2*pi)**-0.5*k**(1/3)*(2*sqrt(rho)-2.218*eps)/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho*rho*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/((2*pi)**-0.5*(2*sqrt(rho)-2.218*eps)))
        return Low*k/(k+1)
    def lo1027(q0):  # 10.27(i): y=k+1, 𝔰_q(y)=s_{y+q-1}(y)=s_{k+q}(k+1)
        y = k+1
        frakS = lambda q: s_kp1[y+q-1]
        PrBorge = 1 - sum(Bor(j) for j in range(1, q0))
        zR = 0.0
        for q in range(1, q0):
            j = q0-q
            Renst = (2*pi)**-0.5*j**-0.5*exp(-1/(12*j))
            Aup = sqrt(2*pi)/4*exp(1/(12*j))*(q0+q)*sqrt(j)
            zR += Renst*exp(-(q+Aup)/y)*frakS(q)
        return k/(k+1)*(1-q0/(2*k))*(max(zR, frakS(q0)-PrBorge) + Bor(q0))
    pts = [("q=20", 20), ("xi=.5", int(round(0.5*k**(2/3)))), ("xi=1", int(round(k**(2/3)))), ("xi=2", int(round(2*k**(2/3)))), ("xi=4", int(round(4*k**(2/3))))]
    P("수준 질량 k c_{k+q}(k): 하계/참값  [6.48(나), 9.7, 6.53, 10.27]")
    for name, q in pts:
        tr = k*c_k(k+q)
        a = lo648(q); b = lo97(q); c = lo653(q); d = lo1027(q)
        f = lambda v: f"{v/tr:5.3f}" if v is not None else "범위밖"
        P(f"  {name:6s} q={q:5d} 참값={tr:.5e}  6.48={f(a)} 9.7={f(b)} 6.53={f(c)} 10.27={f(d)}")
    # 10.27 at q=k+1 (F6: 참값의 1/260)
    q = k+1; tr = k*c_k(k+q); P(f"  q=k+1 : 10.27/참값 = {lo1027(q)/tr:.5f}")
    # 참값 c_{y+d}(y) ≈ (1.3–1.6)(y+d)/d^{5/2} ?
    for q in [int(2*k**(2/3)), k//2, k]:
        P(f"  c_{{k+q}}(k) d^{{5/2}}/(k+q) at q={q}: {c_k(k+q)*q**2.5/(k+q):.3f}")
    # 판정 V 수치: min_m V_k(m) (m in [k,2k]), 𝔭_m=(k+1)c_m(k)-(k-1)c_m(k-1)
    cm_k = s_kp1 - s_k; cm_km1 = s_k - s_km1
    pm = (k+1)*cm_k - (k-1)*cm_km1
    V = np.cumsum(pm[k:2*k+1][::-1])[::-1]
    P(f"  V_k(k) = {V[0]:.5f} (6.45 하계: 0.082@3131, 0.7654@6667) ; min_m V_k(m) = {V.min():.5e} at m-k={int(np.argmin(V))}")
    return s_k, s_kp1, s_km1

for k in [6668, 4000]:
    tables(k)

# 작은 k 판정 V (S13: 2<=k<=249 성립 주장) — 표본
P("\n## 판정 V 표본 (작은 k)")
for k in [10, 50, 100, 249, 500, 1000, 3130]:
    M = 2*k+1
    sk = survival(k, M); skp = survival(k+1, M); skm = survival(k-1, M)
    pm = (k+1)*(skp-sk) - (k-1)*(sk-skm)
    V = np.cumsum(pm[k:2*k+1][::-1])[::-1]
    P(f"  k={k}: V_k(k)={V[0]:.5f}, min_m V_k(m)={V.min():.3e} at m-k={int(np.argmin(V))}")

# ---------------- C3: Abel 합 하계 Λ̂(Y) > 7/10 (Y>=25000), 6.1만 사용 ----------------
P("\n## C3 Abel 합 (2:old-2-34 + 6.1) 하계 재계산")
def abel_lower(Y):
    Q = int(math.floor(6*Y**(2/3)))
    a = lambda q: Y/(Y+q+1)
    sup = lambda q: min(1.0, 3*Y*q**-1.5) if q >= 1 else 1.0
    # sum a_q (s_{q-1}-s_q) = a_1 s_0 - a_Q s_Q + sum_{q=1}^{Q-1} (a_{q+1}-a_q) s_q ; a 감소, s<=sup
    val = a(1) - a(Q)*sup(Q) + sum((a(q+1)-a(q))*sup(q) for q in range(1, Q))
    return val, Q
for Y in [25000, 30000, 50000, 10**5, 10**6]:
    v, Q = abel_lower(Y)
    P(f"  Y={Y}: Q={Q}, Λ̂ 하계 = {v:.5f}  (>7/10 ?)  ; F4 닫힌 꼴 = {1-2/Y-3*Y/Q**1.5-3**(5/3)*Y**(-1/3)+9/sqrt(Q)+3/Q**1.5:.5f}")
# 6.1 대신 10.21(1.15)로 바꾸면
def abel_lower2(Y):
    Q = int(math.floor(6*Y**(2/3)))
    a = lambda q: Y/(Y+q+1)
    sup = lambda q: min(1.0, 1.15*(Y+q+1)/(q+1)**1.5) if q >= 1 else 1.0
    return a(1) - a(Q)*sup(Q) + sum((a(q+1)-a(q))*sup(q) for q in range(1, Q))
P("  10.21 상계를 쓰면 Y=25000:", abel_lower2(25000))

with open(__file__.replace(".py", "_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
