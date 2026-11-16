# -*- coding: utf-8 -*-
# 10차 수리 R2: P2 「보충」이 끝내지 못한 두 수치 점검의 짧은 판(mpmath만 씀; scipy 없음).
# (E)  중앙 상쇄 항등식 ∫F0=0, ∫F1=46√2-12, J 선도 적분 3√(2π)  (4.3절 보조정리 two-corrections 넷째·여섯째 단계)
# (E2) (4.14)·(4.11)의 수직선 위 수치 점검 (k=30000, G=1/16; k=10000, G=1/8) — β 몇 점
# 주의: Bor^sum_k(φ) = Z(1-Bor^tail_k(Z)). 첫 실행은 1-Z·Bor^tail로 잘못 적어 (4.11) 검사가 β/√k만큼 어긋났다
#       (P2 스크립트 검토전체10_P2_장4.py (E2)의 같은 실수); 고친 뒤의 결과가 *_E2_out.txt다.
# 실행: python -I 수리_전체10_R2_검산.py [--e2only]
import time, sys
import mpmath as mp
mp.mp.dps = 15
E2ONLY = '--e2only' in sys.argv
t0 = time.time()
SQ2PI = mp.sqrt(2 * mp.pi)
ninf = 2 / mp.sqrt(mp.pi)

def Dawson_half(b):
    # D(b) = e^{-b^2/2} ∫_0^b e^{v^2/2} dv = √2 · dawsn(b/√2),  dawsn(x) = (√π/2) e^{-x^2} erfi(x)
    x = b / mp.sqrt(2)
    return mp.sqrt(2) * mp.sqrt(mp.pi) / 2 * mp.e ** (-x * x) * mp.erfi(x)

def BorldR(b):
    # Bor^ld_R(b) e^{-b^2/2} = 2 - 2 b D(b)
    return mp.e ** (b * b / 2) * (2 - 2 * b * Dawson_half(b))

def Pq(z, r):
    mu = 1 - r * r
    return mu * z * z + mu * mu * z ** 4 / 4

def F0(z):
    inner = mp.quad(lambda r: r * r * mp.e ** ((1 - r * r) * z * z / 2) * Pq(z, r) * BorldR(r * z) / SQ2PI, [0, 1])
    return -ninf * z ** 4 * mp.e ** (-z * z) * inner

def F1(z):
    inner = mp.quad(lambda r: r * r * mp.e ** ((1 - r * r) * z * z / 2) * Pq(z, r) * (mp.mpf(4) / 3 * r * r * z * z - mp.mpf(2) / 3 * r * z ** 4), [0, 1])
    return -ninf * z ** 4 * mp.e ** (-z * z) * inner

if not E2ONLY:
    print("=== (E) 중앙 상쇄 항등식 ===")
    I0 = mp.quad(F0, [0, 1, 2, 4, 8, 14])
    I1 = mp.quad(F1, [0, 1, 2, 4, 8, 14])
    print("int_R F0 =", 2 * I0, "(기대 0)")
    print("int_R F1 =", 2 * I1, " 46sqrt2-12 =", 46 * mp.sqrt(2) - 12)
    J = mp.quad(lambda z: z ** 3 * mp.e ** (-z * z / 2) * ((mp.mpf(4) / 15) * z ** 3 - z / 3), [-mp.inf, mp.inf])
    print("J 선도 적분 =", J, " 3sqrt(2pi) =", 3 * SQ2PI)
    print("max beta*D(beta) on grid =", max(b * Dawson_half(b) for b in [mp.mpf(i) / 20 for i in range(1, 401)]))
    print("time %.1fs" % (time.time() - t0))

print("=== (E2) (4.14)·(4.11) 수직선 위 수치 점검 ===")
mp.mp.dps = 25

def bortail(k, Z):
    # Bor^tail_k(Z) = 1 - Z^{-1} Σ_{j≤k} Bor(j) (Z e^{1-Z})^j ; Bor(j+1)/Bor(j) = e^{-1}(1+1/j)^{j-1}
    q = Z * mp.e ** (1 - Z)
    s = mp.mpf(0)
    bj = mp.e ** (-1)  # Bor(1)
    pw = q
    for j in range(1, k + 1):
        s += bj * pw
        bj = bj * mp.e ** (-1) * (1 + mp.mpf(1) / j) ** (j - 1)
        pw *= q
    return 1 - s / Z

def Borld(phi):
    return 2 + mp.quad(lambda w: w ** mp.mpf(-1.5) * (1 - mp.e ** (-phi * w)), [0, 1])

cases = (
    (30000, mp.mpf(1) / 16,
     lambda b: mp.mpf(3) / 5 + mp.mpf(12) / 5 * b ** 2 + mp.mpf(3) / 2 * b ** 4 + b ** 6 / 25,
     lambda b: mp.mpf(1) / 100 + mp.mpf(201) / 100 * b + mp.mpf(7) / 10 * b ** 3 + b ** 4 / 500 + b ** 5 / 50000 + b ** 7 / 500000),
    (10000, mp.mpf(1) / 8,
     lambda b: mp.mpf(3) / 5 + mp.mpf(12) / 5 * b ** 2 + mp.mpf(8) / 5 * b ** 4 + b ** 6 / 25,
     lambda b: mp.mpf(1) / 100 + mp.mpf(201) / 100 * b + mp.mpf(3) / 4 * b ** 3 + b ** 4 / 250 + b ** 5 / 10 ** 4 + b ** 7 / 10 ** 5),
)
allok = True
for k, G, TR, TI in cases:
    eps = 1 / mp.sqrt(k)
    print("k=%d, G=%s" % (k, G))
    for beta in (mp.mpf('0.3'), mp.mpf(1), mp.mpf('2.5'), mp.mpf(5), mp.mpf(8), G * mp.sqrt(k)):
        Z = 1 + 1j * beta * eps
        bt = bortail(k, Z)
        val = mp.sqrt(k) * bt
        BR = BorldR(beta)
        reerr = abs(mp.re(val) - BR / mp.sqrt(2 * mp.pi) - mp.mpf(4) / 3 * beta ** 2 * eps)
        imerr = abs(mp.im(val) - beta)
        reb = eps ** 2 * mp.e ** (beta ** 2 / 2) * TR(beta) / mp.sqrt(2 * mp.pi)
        imb = eps * mp.e ** (beta ** 2 / 2) * TI(beta) / mp.sqrt(2 * mp.pi)
        phi = -k * (mp.log(Z) + 1 - Z)
        borsum = Z * (1 - bt)
        lhs = abs(borsum - 1 + Borld(phi) / mp.sqrt(2 * mp.pi * k) - mp.mpf(2) / 3 * phi / k)
        rhs = (2 * mp.pi) ** mp.mpf(-0.5) * mp.mpf(k) ** mp.mpf(-1.5) * mp.e ** (-mp.re(phi)) * (mp.mpf(5) / 9 + mp.mpf(2) / 3 * abs(phi) + mp.mpf(13) / 12 * abs(phi) ** 2)
        ok = (reerr <= reb) and (imerr <= imb) and (lhs <= rhs)
        allok = allok and ok
        print("  beta=%7.3f | (4.14) re_err=%.3e <= %.3e | im_err=%.3e <= %.3e | (4.11) err=%.3e <= %.3e | |phi|/b^2=%.4f | ok=%s"
              % (float(beta), float(reerr), float(reb), float(imerr), float(imb), float(lhs), float(rhs), float(abs(phi) / beta ** 2), ok))
print("(E2) 모두 성립:", allok)
print("time %.1fs" % (time.time() - t0))
