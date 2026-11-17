# 검토전체24 R7a: 7.4절 수치 재계산 (tail-half, 접합점 상수, 손실 대괄호, 비교 수, pair-loss-bound)
from mpmath import mp, mpf, sqrt, pi
import itertools, random
mp.dps = 40

print("== tail-half 상수")
r = (1 + mpf(100)/10001)**mpf(1.5)
print("(1+100/10001)^1.5 =", r, "<1.0151:", r < mpf('1.0151'))
c = mpf('1.0151')/sqrt(2*pi)
print("1.0151*(2pi)^-1/2 =", c, "<0.405:", c < mpf('0.405'))
def lhs(q):
    q = mpf(q)
    return mpf('0.04')*q**1.5 - mpf('0.405')*(q + sqrt(q) - mpf(2)/3 - 2/(3*sqrt(q)))
print("좌변(2) =", lhs(2), " 좌변(101) =", lhs(101))
print("max 좌변 on integers 2..101:", max(lhs(q) for q in range(2,102)))
# 직접: 원래 부등식 k(1-s) <= 0.405*[...] <= q^1.5/2 를 정수 q에서 직접
def br(q):
    q = mpf(q)
    return mpf(4)/3*(q-1)**1.5 + sqrt(q-1) - q + mpf(2)/3
worst = max(mpf('0.405')*br(q) - mpf(q)**1.5/2 for q in range(2,102))
print("max(0.405*대괄호 - q^1.5/2) =", worst)
# k=10000에서 prefactor 그대로
k = 10000
worst2 = max(((mpf(k+q)/(k+1))**1.5 * mpf(k)/(k+1) / sqrt(2*pi))*br(q) - mpf(q)**1.5/2 for q in range(2,102))
print("k=10000 정확 prefactor: max diff =", worst2)
print("대괄호 최소(q=2..101) =", min(br(q) for q in range(2,102)))

print("== 접합점 kappa_{K,L}")
J = [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]
claimed = ['0.5113','0.5116','0.5167','0.5216','0.5210']
for (K,L),cl in zip(J,claimed):
    kap = (1 + mpf(L-1)/K)/(2*(1 - mpf(L-1)**1.5/(2*K)))
    print(K,L, kap, "<=",cl, kap <= mpf(cl), " <21/40:", kap < mpf(21)/40, " nhat<1:", mpf(L-1)**1.5/(2*K))
print("== 손실 대괄호")
claimed2 = [2712,3844,7975,13629,14633]
for (K,L),cl in zip(J,claimed2):
    v = mpf(L)**2/3 + mpf(8)/25*sqrt(mpf(2)/5)*mpf(21)/40*mpf(L)**2.5
    print(K,L, v, "<=",cl, v<=cl, " <K:", cl<K)
print("(2/5)(3/5)^1.5 =", mpf(2)/5*(mpf(3)/5)**1.5, " (8/25)sqrt(2/5) =", mpf(8)/25*sqrt(mpf(2)/5))

print("== pair-loss-bound 전수(작은 L) 검사")
def LHS(q,qp,j,kap):
    return j*(q+qp+kap*(q**1.5+qp**1.5)) + ((q+kap*q**1.5)*(qp-1)+(qp+kap*qp**1.5)*(q-1))/2
bad = 0; worst_ratio = 0
for L in list(range(2,121)):
    for kap in [0.0, 0.3, 0.525, 1.0, 5.0, 100.0]:
        rhs = L*L/3 + 8*kap/25*(0.4**0.5)*L**2.5
        for q in range(1,L):
            for qp in range(q,L-q+1):
                j = L-q-qp
                v = LHS(q,qp,j,kap)
                if v > rhs*(1+1e-12): bad += 1
                worst_ratio = max(worst_ratio, v/rhs)
print("위반 수:", bad, " 최대 좌/우 비:", worst_ratio)
# 실제 쓰이는 범위에서 직접 최대 손실 분자 (kappa=21/40) 대 K
for (K,L) in J:
    m = 0
    for q in range(1,L):
        for qp in range(q,L-q+1):
            j = L-q-qp
            m = max(m, LHS(q,qp,j,0.525))
    print("접합점",K,L,"직접 최대 손실 분자 =", m, "<K:", m<K)

print("== integer-strips 비교 수")
a = sum(1 for k in range(9981,11100) for n in range(max(20001,2*k+1), 2*k+41))
b = sum(1 for k in range(9950,12000) for n in range(max(2*k+41,20001), 2*k+103))
c3 = 1000*(102-59+1) + 1000*(102-80+1) + 1000*(102-96+1)
print("(가) =", a, " (나) =", b, " (다) =", c3, " (나)+(다) =", b+c3)

print("== 정리 7:old-6-13 덮개 전수 검사 (k 9950..16000, nu 1..102, n>=20001)")
def pair_ok(k,nu):
    return any(k>=K and nu<=L for K,L in J)
def ana_ok(k,nu):
    if k>=10000 and 1<=nu<=19: return True
    if k>=11100 and 20<=nu<=40: return True
    for K1,nm in [(12000,58),(13000,79),(14000,99),(15000,102)]:
        if k>=K1 and 41<=nu<=nm: return True
    return False
def strip_ok(k,nu):
    n = 2*k+nu
    if 9981<=k<=11099 and max(20001,2*k+1)<=n<=2*k+40: return True
    if 9950<=k<=11999 and max(2*k+41,20001)<=n<=2*k+102: return True
    if 12000<=k<=12999 and 59<=nu<=102: return True
    if 13000<=k<=13999 and 80<=nu<=102: return True
    if 14000<=k<=14999 and 96<=nu<=102: return True
    return False
unc = [(k,nu) for k in range(9940,16001) for nu in range(1,103) if 2*k+nu>=20001 and not ((pair_ok(k,nu) and ana_ok(k,nu)) or strip_ok(k,nu))]
print("덮이지 않은 위치 수:", len(unc), unc[:5])
# 증명 본문의 경우 나눔 그대로
def proof_case(k,nu):
    if nu<=40:
        if k>=11100: return pair_ok(k,nu) and ana_ok(k,nu)
        if 10000<=k<=11099:
            return (pair_ok(k,nu) and ana_ok(k,nu)) if nu<=19 else strip_ok(k,nu)
        return strip_ok(k,nu)
    else:
        if k>=15000: return (k>=15000 and nu<=102) and ana_ok(k,nu)
        if k>=14000: return ((nu<=99) and ana_ok(k,nu)) or (96<=nu<=102 and strip_ok(k,nu))
        if k>=13000: return ((nu<=79) and ana_ok(k,nu)) or (80<=nu and strip_ok(k,nu))
        if k>=12000: return ((nu<=58) and ana_ok(k,nu)) or (59<=nu and strip_ok(k,nu))
        return strip_ok(k,nu)
unc2 = [(k,nu) for k in range(9940,16001) for nu in range(1,103) if 2*k+nu>=20001 and not proof_case(k,nu)]
print("증명의 경우 나눔으로 덮이지 않은 위치 수:", len(unc2), unc2[:5])
print("행 진술: n=20001..20010의 k_n-51:", [ -(-n//2)-51 for n in range(20001,20004)])
