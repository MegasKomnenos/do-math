# R7a: 7.4절의 상수 재계산 (보조정리 tail-half, pair-loss-bound, 정리 old-6-13, 명제 integer-strips의 비교 수)
from mpmath import mp, mpf, sqrt, pi
mp.dps = 40
# (1) tail-half
c = (1 + mpf(100)/10001)**mpf(1.5)
print("((k+q)/(k+1))^{3/2} sup =", c, " <1.0151:", c < mpf('1.0151'))
print("1.0151*(2pi)^-1/2 =", mpf('1.0151')/sqrt(2*pi), " <0.405:", mpf('1.0151')/sqrt(2*pi) < mpf('0.405'))
def f(q):
    q = mpf(q)
    return mpf('0.04')*q**mpf(1.5) - mpf('0.405')*(q + sqrt(q) - mpf(2)/3 - 2/(3*sqrt(q)))
print("f(2) =", f(2), " f(101) =", f(101))
print("max f on integers 2..101:", max(f(q) for q in range(2, 102)))
# 직접: 0.405[4/3 (q-1)^{3/2}+sqrt(q-1)-q+2/3] <= q^{3/2}/2
worst = max(mpf('0.405')*(mpf(4)/3*mpf(q-1)**mpf(1.5)+sqrt(q-1)-q+mpf(2)/3) - mpf(q)**mpf(1.5)/2 for q in range(2, 102))
print("direct worst (should be <0):", worst)
# 대괄호가 양수인지(계수를 올려 쓰는 단계)
print("min bracket:", min(mpf(4)/3*mpf(q-1)**mpf(1.5)+sqrt(q-1)-q+mpf(2)/3 for q in range(2,102)))
# (2) kappa_{K,L}
J = [(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]
claimed_k = ['0.5113','0.5116','0.5167','0.5216','0.5210']
claimed_b = [2712,3844,7975,13629,14633]
for (K,L),ck,cb in zip(J,claimed_k,claimed_b):
    kap = (1+mpf(L-1)/K)/(2*(1-mpf(L-1)**mpf(1.5)/(2*K)))
    br = mpf(L)**2/3 + mpf(8)/25*sqrt(mpf(2)/5)*mpf(21)/40*mpf(L)**mpf(2.5)
    print(K, L, "kappa=", kap, "<=", ck, kap <= mpf(ck), "| bracket=", br, "<=", cb, br <= cb, "<K:", cb < K)
print("21/40 =", mpf(21)/40)
# (3) pair-loss-bound 상수
print("(2/5)(3/5)^{3/2} =", mpf(2)/5*(mpf(3)/5)**mpf(1.5), " (8/25)sqrt(2/5) =", mpf(8)/25*sqrt(mpf(2)/5),
      " (1/sqrt2)(2/5)(4/5)^{3/2} =", mpf(2)/5*(mpf(4)/5)**mpf(1.5)/sqrt(2))
# (7.9)를 격자에서 직접 검사: kappa=21/40, L=2..102 정수, 모든 (q,q',j)
kap = mpf(21)/40
bad = 0; tight = None
for L in range(2, 103):
    rhs = mpf(L)**2/3 + mpf(8)/25*sqrt(mpf(2)/5)*kap*mpf(L)**mpf(2.5)
    for q in range(1, L):
        for q2 in range(q, L-q+1):
            j = L-q-q2
            eq = q + kap*mpf(q)**mpf(1.5); eq2 = q2 + kap*mpf(q2)**mpf(1.5)
            lhs = j*(eq+eq2) + (eq*(q2-1)+eq2*(q-1))/2
            if lhs > rhs: bad += 1
            r = lhs/rhs
            if tight is None or r > tight[0]: tight = (r, L, q, q2, j)
print("(7.9) violations:", bad, " tightest ratio:", tight)
# (4) 명제 integer-strips의 비교 수
a = sum(2*k+40 - max(20001, 2*k+1) + 1 for k in range(9981, 11100))
b = sum(max(0, 2*k+102 - max(2*k+41, 20001) + 1) for k in range(9950, 12000))
cc = 1000*(102-59+1) + 1000*(102-80+1) + 1000*(102-96+1)
print("(가) =", a, " (나) =", b, " (다) =", cc, " (나)+(다) =", b+cc)
# (5) 정리 old-6-13의 덮개: 모든 (k,nu), k>=9950.., 1<=nu<=102, n>=20001 이 어느 경우로 닫히는지
table = {12000:58,13000:79,14000:99,15000:102,20000:115,30000:132,50000:164,100000:228,200000:298,500000:435,1000000:590}
def pair_ok(k,nu):
    return any(k>=K and nu<=L for K,L in J)
def ana_ok(k,nu):
    if k>=10000 and 1<=nu<=19: return True
    if k>=11100 and 20<=nu<=40: return True
    return any(k>=K1 and 41<=nu<=vm for K1,vm in table.items())
def strip_ok(k,nu):
    n = 2*k+nu
    if 9981<=k<=11099 and max(20001,2*k+1)<=n<=2*k+40: return True
    if 9950<=k<=11999 and max(2*k+41,20001)<=n<=2*k+102: return True
    if 12000<=k<=12999 and 59<=nu<=102: return True
    if 13000<=k<=13999 and 80<=nu<=102: return True
    if 14000<=k<=14999 and 96<=nu<=102: return True
    return False
unc = 0
for k in range(2001, 40001):
    for nu in range(1, 103):
        if 2*k+nu < 20001: continue
        if not ((pair_ok(k,nu) and ana_ok(k,nu)) or strip_ok(k,nu)): unc += 1
print("uncovered positions for 2001<=k<=40000:", unc)
