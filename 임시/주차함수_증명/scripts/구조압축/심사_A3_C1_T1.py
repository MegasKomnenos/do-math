# 심사 A3 — C1·C2 검산: 기울인 생일 법칙의 정확 항등식, 모멘트 상계, 평균 하계 (6/7)sqrt r,
# 5:suff-cond(마)의 Pc(k) 하계, 그리고 eb=0일 때 r<=170, n>=20001에서 Pc>0.
# 정확 산술(Fraction) + 필요 자리에서는 Decimal(50자리)로 sqrt/pi 상하계.
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
import math, sys
getcontext().prec = 60

def birthday_law(r, rho):
    # bd_{r-1,rho}(j) ∝ rho^j (j+1) (r-1)_j / r^j, 0<=j<=r-1   (장5A 237행; F4 §3의 (j+1)a_j)
    w = []
    a = Fr(1)
    for j in range(r):
        w.append((j+1)*a)
        a = a*rho*Fr(r-1-j, r)
    Z = sum(w)
    return [x/Z for x in w]

def moments(p):
    mu = sum(j*pj for j,pj in enumerate(p))
    m2 = sum(j*j*pj for j,pj in enumerate(p))
    return mu, m2

print("== (1) 정확 항등식 E[J^2]+(3+r^2/k)mu+2 = 2r  및 (2) E[J(J-1)] <= 3mu^2/2 (정확 분수)")
for r in [2,3,5,10,37,64,100,171,300]:
    for k in [r+1, 3*r, math.ceil(r**1.5+8*r), 10*r*r]:
        rho = Fr(k, k+r)
        p = birthday_law(r, rho)
        mu, m2 = moments(p)
        lhs = m2 + (3 + Fr(r*r, k))*mu + 2
        assert lhs == 2*r, (r,k,lhs)
        assert m2 - mu <= Fr(3,2)*mu*mu, (r,k)
print("   모든 표본 (r,k)에서 항등식 정확 성립, 모멘트 상계 성립")

print("== (3) tm_{r-1}(k/n) > (6/7) sqrt r  at k = ceil(r^1.5+8r), 64<=r<=400 (정확 분수), 이어 Decimal 표본")
worst = None
fails = []
for r in range(2, 401):
    k = math.ceil(r**1.5 + 8*r)
    p = birthday_law(r, Fr(k, k+r))
    mu, _ = moments(p)
    ok = mu*mu > Fr(36*r, 49)
    if r >= 64 and not ok: fails.append(r)
    if r < 64 and not ok: pass
    ratio = mu*mu/Fr(r)  # (mu/sqrt r)^2
    if r >= 64 and (worst is None or ratio < worst[1]): worst = (r, ratio)
print("   r>=64 실패:", fails, " 최소 (mu/sqrt r)^2 at r>=64:", worst[0], float(worst[1]), " (36/49 =", 36/49, ")")
small = [r for r in range(2,64) if moments(birthday_law(r, Fr(math.ceil(r**1.5+8*r), math.ceil(r**1.5+8*r)+r)))[0]**2 <= Fr(36*r,49)]
print("   r<64에서 (6/7)sqrt r 하계가 깨지는 r:", small)

print("== (4) 해석적 하계: Pc(k) >= sqrt r/70 + 7/20 for all r>=64, k>=r^1.5+8r (eb=(6/7)sqrt r)")
# Pc(k) = k(1/(2r)-1/(3r^2)) - 5/2 + 2 eb (1-1/k) - k/(k-1) (1+sqrt(3 pi (r-1)/2))
# k에 대해 비감소(lemma-L(가)의 논증: 첫 항 증가, 2eb(1-1/k) 비감소, -k/(k-1) 증가)이므로 k=k_r에서 보면 된다.
D = Decimal
SQ3PI2_UP = (D(3)*D("3.14159265358979323846264338327950288419716939937511")/D(2)).sqrt()*(1+D("1e-30"))
def Pc_lower(r):
    k = math.ceil(r**1.5 + 8*r)
    s = D(r).sqrt()
    eb = D(6)/D(7)*s*(1-D("1e-40"))  # 하계로 약간 낮춤
    t1 = D(k)*(D(1)/(2*D(r)) - D(1)/(3*D(r)*D(r)))
    t3 = 2*eb*(1-D(1)/D(k))
    t4 = D(k)/D(k-1)*(1+SQ3PI2_UP*D(r-1).sqrt())
    return t1 - D(5)/2 + t3 - t4, s/70 + D(7)/20
minmargin = None
for r in list(range(64, 5000)) + [10**4, 10**5, 10**6, 10**8, 10**10]:
    pc, target = Pc_lower(r)
    m = pc - target
    if minmargin is None or m < minmargin[1]: minmargin = (r, m)
    assert pc > target, (r, pc, target)
print("   모든 표본 r에서 Pc(k_r) > sqrt r/70 + 7/20; 최소 여유 r=%d, %.6f" % (minmargin[0], float(minmargin[1])))
# 점근: Pc/sqrt r -> 1/2 + 12/7 - sqrt(3pi/2)
print("   점근 계수 1/2+12/7-sqrt(3pi/2) =", float(D(1)/2 + D(12)/7 - SQ3PI2_UP), " (> 1/70 =", 1/70, ")")

print("== (5) C2: eb=0에서 Pc(k)>0,  2<=r<=170,  k = 20001-r (n=20001) 및 k=49831")
def Pc0(r, k):
    t1 = D(k)*(D(1)/(2*D(r)) - D(1)/(3*D(r)*D(r)))
    t4 = D(k)/D(k-1)*(1+SQ3PI2_UP*D(r-1).sqrt())
    return t1 - D(5)/2 - t4
mn = None
for r in range(2, 171):
    v = Pc0(r, 20001-r)
    if mn is None or v < mn[1]: mn = (r, v)
    assert v > 0, (r, v)
print("   n=20001: 모든 2<=r<=170에서 Pc>0, 최솟값 r=%d, Pc=%.3f" % (mn[0], float(mn[1])))
mn = None
for r in range(2, 171):
    v = Pc0(r, 49831)
    if mn is None or v < mn[1]: mn = (r, v)
print("   k=49831: 최솟값 r=%d, Pc=%.3f (F4의 57/2=28.5와 비교)" % (mn[0], float(mn[1])))
# eb=0 경로가 r<=R까지 미치는 최대 R (n=20001):
R = 170
while Pc0(R+1, 20001-(R+1)) > 0: R += 1
print("   eb=0, n=20001에서 Pc>0이 유지되는 최대 꼬리 좌표 R =", R)
print("== (6) 기존 T1 (lemma-L(나))의 상수 L(1e4)=0.845204 와 새 하계 6/7=0.857143 비교:", 6/7)

print("== (3b) 큰 r 표본 (Decimal 60자리): tm_{r-1}(k/n)/sqrt r at k=ceil(r^1.5+8r)")
def tm_dec(r, k):
    rho = D(k)/D(k+r); w = D(1); S0 = D(0); S1 = D(0)
    for j in range(r):
        S0 += (j+1)*w; S1 += j*(j+1)*w
        w = w*rho*D(r-1-j)/D(r)
    return S1/S0
for r in [500, 1000, 1500, 3000, 10000, 20000]:
    k = math.ceil(r**1.5+8*r)
    v = tm_dec(r, k)/D(r).sqrt()
    print("   r=%6d  tm/sqrt r = %.6f   (6/7 = 0.857143; 기존 L(r) 하계 r=1e4: 0.845204)" % (r, float(v)))
