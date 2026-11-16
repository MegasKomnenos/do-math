# -*- coding: utf-8 -*-
"""결정 K4 검산 3: E4 — 9.23 (1)의 적분을 정수 경계의 세 셀 Abel 합으로 바꾼 하계의 정확한 식과 k-균일 값.

수준 Y in {k, k-1}, 무게 omega(t) = (k/t)^{5/2} (비증가), 셀 경계 E_i := floor(Y + a_i Y^{2/3}), a = (2,4,6).
  S_Y := sum_{E=Y+1}^{2k} omega(E+1) c_E(Y) >= sum_E omega(E+1)[s_{E-1}(Y) - s_E(Y)]     (2.34; SM 으로 차 >= 0)
      >= sum_{i=1}^{3} omega(E_i+1) [s_{E_{i-1}}(Y) - s_{E_i}(Y)]   (셀 안에서 omega(E+1) >= omega(E_i+1), 망원; E_3 너머는 버림)
      =  omega_1 - (omega_1-omega_2) s_{E_1}(Y) - (omega_2-omega_3) s_{E_2}(Y) - omega_3 s_{E_3}(Y)
  s_{E_i}(Y) = frak s_{d_i}(Y), d_i = E_i - Y + 1 >= a_i Y^{2/3}  ->  <= sbar_i := 1.15 (1 + a_i Y^{-1/3}) / a_i^{3/2}   (10.21, y=Y>=6666)
  omega_i >= omegabar_i := (k/(Y + a_i Y^{2/3} + 1))^{5/2}.
k-균일 하계: omegabar_1 는 k 에 증가(최솟값 k=6668), (omegabar_i - omegabar_{i+1}) 와 sbar_i 는 k 에 감소(최댓값 k=6668),
  omegabar_3 sbar_3 = 1.15 [ (k/(Y+a_3 Y^{2/3}+1))^{5/3} (1+a_3 Y^{-1/3})/a_3^{3/2} ]^{...} 는 k 에 증가 -> 상한 = 극한 1.15/6^{3/2} (Y=k), 같은 극한 (Y=k-1).
"""
from mpmath import mp, mpf, floor
mp.dps = 30
A = (2, 4, 6)

def pieces(k, Y):
    k = mpf(k); Y = mpf(Y)
    om = [(k / (Y + a * Y ** (mpf(2) / 3) + 1)) ** mpf('2.5') for a in A]
    sb = [mpf('1.15') * (1 + a * Y ** (-mpf(1) / 3)) / mpf(a) ** mpf('1.5') for a in A]
    return om, sb

def bound(k, Y, last='exact'):
    om, sb = pieces(k, Y)
    v = om[0] - (om[0] - om[1]) * sb[0] - (om[1] - om[2]) * sb[1]
    if last == 'exact':
        v -= om[2] * sb[2]
    elif last == 'limit':
        v -= mpf('1.15') / mpf(6) ** mpf('1.5')
    elif last == 'one':
        v -= sb[2]
    return v

if __name__ == "__main__":
    print("E4 세 셀(정수 경계, d_i >= a_i Y^{2/3} 로 둔 sbar):")
    for k in (6668, 7000, 10 ** 4, 2 * 10 ** 4, 10 ** 5, 10 ** 6):
        ex = bound(k, k) + bound(k, k - 1)
        li = bound(k, k, 'limit') + bound(k, k - 1, 'limit')
        on = bound(k, k, 'one') + bound(k, k - 1, 'one')
        print("  k=%7d: 그대로 %.4f | 마지막 항을 극한 1.15/6^{3/2}=%.5f 로 둔 판 %.4f | omega_3<=1 판 %.4f" % (k, ex, mpf('1.15') / 6 ** mpf(1.5), li, on))
    print("  요구값 1.0845(띠)·1.0787(벌크); 현행 1.206")
    # k-균일 하계 L_3 := [omegabar_1 - (omegabar_1-omegabar_2) sbar_1 - (omegabar_2-omegabar_3) sbar_2](k=6668) - 1.15/6^{3/2}, 두 수준 합
    L3 = bound(6668, 6668, 'limit') + bound(6668, 6667, 'limit')
    print("  k-균일 하계 L_3 (k=6668 에서 평가, 마지막 항 극한) = %.4f ; 여유 = %.4f (띠), %.4f (벌크)" % (L3, L3 - mpf('1.0845'), L3 - mpf('1.0787')))
    # 각 인자의 단조 방향(표본 확인; 해석 근거는 본문)
    ks = [6668, 6700, 7000, 8000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8]
    for Y_off in (0, 1):
        oms = [pieces(k, k - Y_off) for k in ks]
        print("  Y=k-%d: omegabar_1 증가 %s; (om1-om2) 감소 %s; (om2-om3) 감소 %s; sbar_1 감소 %s; sbar_2 감소 %s; om3*sb3 증가 %s" % (
            Y_off,
            all(oms[i][0][0] < oms[i + 1][0][0] for i in range(len(ks) - 1)),
            all(oms[i][0][0] - oms[i][0][1] > oms[i + 1][0][0] - oms[i + 1][0][1] for i in range(len(ks) - 1)),
            all(oms[i][0][1] - oms[i][0][2] > oms[i + 1][0][1] - oms[i + 1][0][2] for i in range(len(ks) - 1)),
            all(oms[i][1][0] > oms[i + 1][1][0] for i in range(len(ks) - 1)),
            all(oms[i][1][1] > oms[i + 1][1][1] for i in range(len(ks) - 1)),
            all(oms[i][0][2] * oms[i][1][2] < oms[i + 1][0][2] * oms[i + 1][1][2] for i in range(len(ks) - 1))))
    om, sb = pieces(6668, 6668)
    print("  k=6668, Y=k: omegabar=(%.5f, %.5f, %.5f), sbar=(%.5f, %.5f, %.5f)" % tuple([float(x) for x in om] + [float(x) for x in sb]))
    om, sb = pieces(6668, 6667)
    print("  k=6668, Y=k-1: omegabar=(%.5f, %.5f, %.5f), sbar=(%.5f, %.5f, %.5f)" % tuple([float(x) for x in om] + [float(x) for x in sb]))
