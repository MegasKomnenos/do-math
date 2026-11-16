# -*- coding: utf-8 -*-
"""E2: 장2·장5A의 「= 소수」 자리와 그 둘레 산술 사슬을 50자리로 확인. python -I 로 돌린다."""
from fractions import Fraction as Fr
from mpmath import mp, mpf, e, pi, sqrt, exp, log, quad, nstr, inf, floor, cos, sin, cot
mp.dps = 50
chk = []
def C(desc, cond, *vals):
    chk.append((desc, bool(cond))); print(("OK   " if cond else "FAIL ") + desc, *[nstr(v, 15) for v in vals])

print("=== 장2 623 (보조정리 old-2-37 (라)) ===")
v = 2/sqrt(2*pi)
C("2(2π)^{-1/2} = 0.79788... (앞 다섯 자리)", floor(v*10**5) == 79788, v)
C("2(2π)^{-1/2} ≤ 0.7979 (진술 (라)·따름정리 (d))", v <= mpf('0.7979'), v)
C("(2π)^{-1/2}(2√q-1) ≤ 2(2π)^{-1/2}√q  (q=1에서 등호 아님, 자명)", True)

print("=== 장5A 202 (보조정리 cayley-ratio, 1≤k≤9) ===")
listed = ['2.75','2.75','2.7407','2.7343','2.7302','2.7274','2.7255','2.7241','2.7231']
allok = True
for k in range(1, 10):
    cr = Fr(k+1, k)**(k-2)                      # (1+1/k)^{k-2}, 유리수
    val = cr*(1+Fr(5, 2*k)+Fr(2, k*k))
    fl = Fr(int(val*10**4), 10**4)             # 소수 다섯째 자리에서 내림(넷째 자리까지)
    ok = (Fr(listed[k-1]) == fl or (Fr(listed[k-1]) == val)) and Fr(listed[k-1]) <= val and val > Fr(87, 32)
    allok &= ok
    print(("OK   " if ok else "FAIL "), "k=%d 참값 %s = %s ; 적힌 값 %s ; 내림 %s ; >87/32: %s" % (k, val, nstr(mpf(val.numerator)/val.denominator, 12), listed[k-1], fl, val > Fr(87, 32)))
C("아홉 값 모두 적힌 대로(내림) 이상이고 87/32보다 큼", allok)
C("87/32 = 2.71875 (정확)", Fr(87, 32) == Fr('2.71875'))
C("e < 65/24 + 1/100", e < mpf(65)/24 + mpf(1)/100, e, mpf(65)/24 + mpf(1)/100)
C("65/24 + 1/100 < 87/32", Fr(65, 24)+Fr(1, 100) < Fr(87, 32))
C("5/12 - 7/20 = 1/15", Fr(5, 12)-Fr(7, 20) == Fr(1, 15))

print("=== 장5A 441·443·445 (정리 old-5-5 증명, r ≥ 10^4) ===")
def M(i): return quad(lambda y: y**i*exp(-y-y*y/2), [0, inf])
M0, M1, M2, M3, M4, M5 = [M(i) for i in range(6)]
M26 = quad(lambda y: y**2*exp(-y-y*y/2), [0, 6])
def Mstar(i):
    ys = (-1+sqrt(1+4*i))/2
    return ys**i*exp(-ys-ys*ys/2)
Ms2, Ms3, Ms4, Ms5 = [Mstar(i) for i in (2, 3, 4, 5)]
C1 = 2*Ms2 + M3/2 + M5/3; C2 = Ms3/2 + Ms5/3 + M4/2; C3 = Ms4/2 + M3/6; C4 = Ms3/6
print("  M0..M5 =", [nstr(x, 8) for x in (M0, M1, M2, M3, M4, M5)], " M2^(6) =", nstr(M26, 10), " C1..C4 =", [nstr(x, 8) for x in (C1, C2, C3, C4)])
C("M1 = 1 - M0 (재귀 검산)", abs(M1-(1-M0)) < mpf(10)**-40, M1, 1-M0)
def L(r):
    s = sqrt(mpf(r))
    return (M26 - C1/s - C2/s**2 - C3/s**3 - C4/s**4)/(M1 + (M0+exp(-mpf(1)/2))/s + 1/s**2)
L4 = L(10**4)
C("𝔏(10^4) ≥ 0.845204 (본문 441행·D (B))", L4 >= mpf('0.845204'), L4)
C("2·0.845204 = 1.690408 (정확)", Fr('0.845204')*2 == Fr('1.690408'))
s3 = sqrt(3*pi/2)
C("√(3π/2) < 2.170804 (445행의 숨은 단계; 위로 반올림 방향)", s3 < mpf('2.170804'), s3)
C("√(3π/2) ≤ 2.1709 (441행)", s3 <= mpf('2.1709'))
C("1/2 + 1.690408 - 2.170804 = 0.019604 (정확 소수 산술)", Fr(1, 2)+Fr('1.690408')-Fr('2.170804') == Fr('0.019604'))
C("따라서 1/2 + 2·0.845204 - √(3π/2) > 0.019604", mpf(1)/2 + 2*mpf('0.845204') - s3 > mpf('0.019604'), mpf(1)/2 + 2*mpf('0.845204') - s3)
C("√(π/2) ≤ 1.2534 (441행)", sqrt(pi/2) <= mpf('1.2534'), sqrt(pi/2))
C("2·1.2534 ≤ 2.507 (441행: 2eb/k ≤ 2.507/s²)", Fr('1.2534')*2 <= Fr('2.507'))
br = lambda s: 1/(3*s) + 8/(3*s*s) + mpf('2.507')/(s*s) + (1+mpf('2.1709')*s)/s**3
C("대괄호(s=100) < 0.0041 (s에 감소)", br(mpf(100)) < mpf('0.0041'), br(mpf(100)))
C("s ≥ 25에서 0.019604 s - 0.0041 ≥ 0.0196 s - 0.004  ⇔ 0.000004 s ≥ 0.0001", Fr('0.000004')*25 >= Fr('0.0001'))
C("끝: s(0.019604)+1/2-0.0041 ≥ 0.0196 s + 0.496 (s=100 대입)", mpf('0.019604')*100 + mpf(1)/2 - mpf('0.0041') >= mpf('0.0196')*100 + mpf('0.496'))
C("여유: 0.0196·100+0.496 = 2.456 > 0", mpf('0.0196')*100 + mpf('0.496') > 0, mpf('0.0196')*100 + mpf('0.496'))
# k_r ≥ s^3+8s^2 에서 첫 항
C("(s³+8s²)(1/(2s²)-1/(3s⁴)) = s/2+4-1/(3s)-8/(3s²) (항등식, s=100 수치)", abs((mpf(100)**3+8*mpf(100)**2)*(1/(2*mpf(100)**2)-1/(3*mpf(100)**4)) - (mpf(50)+4-mpf(1)/300-mpf(8)/30000)) < mpf(10)**-40)

print("=== 장5A 576 (정리 old-5-7: -0.02965 < -1/40) ===")
C("-0.02965 < -1/40", Fr('-0.02965') < Fr(-1, 40))

print("=== 장5A 716 (정리 old-5-12: 부록 D.band-A-certification 결과 대 본문) ===")
first = mpf(-20763942788699649828208058950993518)/mpf(2)**120
C("첫 인증 최악 상계 = -0.01562... < -0.0156 (본문 '-0.0156')", first < mpf('-0.0156'), first)
C("독립 재인증 최악 -0.04599 < -0.0459", mpf('-0.04599') < mpf('-0.0459'))
for d, b in ((-0.1821, -0.182), (-0.1468, -0.146), (-0.01555, -0.0155), (-0.01743, -0.0174)):
    C("(A⁺) D %s < 본문 %s" % (d, b), mpf(str(d)) < mpf(str(b)))
C("모두 -1/100 미만", mpf('-0.0155') < mpf(-1)/100)

print("=== 장5A 796·842·844 (임계 창) ===")
phi = mpf(1)/2
let = log(phi/sin(phi)) + (1 - phi*cot(phi))
C("log et(1/2) = 0.126775... > 0.1267", let > mpf('0.1267'), let)
C("ag ≤ 1에서 (1-cos ag)/ag² ≥ 0.458 (최솟값은 ag=1)", (1-cos(mpf(1))) >= mpf('0.458'), 1-cos(mpf(1)))
C("0.0015/1.25^12 = 1.0307...×10^{-4}", floor(mpf('0.0015')/mpf('1.25')**12*10**8) == 10307, mpf('0.0015')/mpf('1.25')**12)
C("최소 여유 0.001827 > 0.0018 (본문 844행을 부등식으로)", mpf('0.001827') > mpf('0.0018'))

print("=== 장2 283 (명제 old-2-20; D.old-2-20 결과의 위 끝 대 본문 상계) ===")
for dv, bv in (('0.7395086877', '0.740'), ('0.3168484270', '0.317'), ('0.06573317522', '0.0658'), ('0.01142155148', '0.0115')):
    C("D %s ≤ 본문 %s" % (dv, bv), mpf(dv) <= mpf(bv))

print("FAIL 수:", sum(1 for d, c in chk if not c), "/", len(chk))

print("=== 장5A 576 보충: 기록 인증서의 정확 최대 Bernstein 계수 (원고_자료/r690be93/entry-slope-certificate.json) ===")
import json
try:
    d = json.load(open(r'원고_자료/r690be93/entry-slope-certificate.json', encoding='utf-8'))
    mxe = max((Fr(e['max_exact']) for e in d))
    C("정확 최대 계수 = -0.0296507... < -0.02965 (본문을 '보다 작아'로)", mxe < Fr('-0.02965'), mpf(mxe.numerator)/mxe.denominator)
    C("모든 35칸 ok, 최대 계수 < -1/40", all(e['ok'] for e in d) and mxe < Fr(-1, 40))
except Exception as ex:
    print("건너뜀:", ex)
print("FAIL 수(전체):", sum(1 for d_, c in chk if not c), "/", len(chk))
