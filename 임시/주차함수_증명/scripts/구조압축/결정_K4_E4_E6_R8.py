# -*- coding: utf-8 -*-
"""결정 K4 검산 2: E4(세 셀 Abel 합의 값과 k-균일 하계), E6(닫힌 꼴 DDL^natural 의 k>=3131 유효성), R8(9.8·9.43 ⊂ 8.6(라)).

E4: 9.23 (1) 의 착지 비 하계를 적분 대신 유한 셀의 Abel 합으로 센다.
    land_m >= sum_{E} omega(E+1)[s_{E-1}(Y)-s_E(Y)]  (omega(t)=(k/t)^{5/2} 비증가, SM 으로 차 >= 0)
    분할 Y=E_0<E_1<...<E_r, omega_i := omega(E_i+1), sbar_i >= s_{E_i}(Y):
      >= omega_1 - sum_{i<r}(omega_i-omega_{i+1}) sbar_i - omega_r sbar_r.
    생존 상계는 10.21: s_{E}(Y) = frak s_{d}(Y), d=E-Y+1, <= min(1, 1.15 (Y+d)/d^{3/2}) (Y>=6666).
    (A) k=6668 에서의 값 (X7 재현), (B) 모든 k>=6668 에 유효한 균일 하계:
       omega_1 은 k 에 증가 -> k=6668 값이 하계; (omega_i-omega_{i+1}) 는 k 에 감소(a k^{-1/3}<2/5 에서) -> 6668 값이 상계;
       sbar_i 는 k 에 감소 -> 6668 값이 상계; omega_r <= 1.
E6: R(k) = 14(log 3k - 1)/(5 sqrt(pi k)) + [7(3-log3)+42/sqrt3]/(5 sqrt(pi) k).
    1단계 상수의 k-의존을 명시해 k>=3131 (과 k>=2001) 에서 F4/A10 의 두 캡이 서는지 확인.
R8: Psi^low_(d) (8.6(라)) >= 0.7978 sqrt d - 0.8848 (9.8) 와 >= 0.3989(2 sqrt d - 1.678) (9.43), d<=10^6 전수 + 해석.
"""
from mpmath import mp, mpf, sqrt, log, pi, e, zeta
mp.dps = 30

def omega(k, E):
    return (mpf(k) / (E + 1)) ** mpf('2.5')

def sbar_1021(Y, E):
    d = E - Y + 1
    return min(mpf(1), mpf('1.15') * (Y + d) / mpf(d) ** mpf('1.5'))

def three_cell(k, Y, cells=(2, 4, 6), uniform=False, k0=None):
    """레벨 Y in {k, k-1}; 셀 경계 E_i = Y + a_i Y^{2/3} (실수; sbar 는 비정수 결손에서도 단조라 유효한 상계)."""
    Es = [Y + a * mpf(Y) ** (mpf(2) / 3) for a in cells]
    om = [omega(k, E) for E in Es]
    sb = [sbar_1021(Y, E) for E in Es]
    r = len(Es)
    val = om[0]
    for i in range(r - 1):
        val -= (om[i] - om[i + 1]) * sb[i]
    val -= (mpf(1) if uniform else om[r - 1]) * sb[r - 1]
    return val

def check_E4():
    print("E4 (A) 세 셀 [2,4,6]Y^{2/3}, 생존 상계 10.21:")
    for k in (6668, 10 ** 4, 2 * 10 ** 4, 10 ** 5, 10 ** 6):
        v = three_cell(k, k) + three_cell(k, k - 1)
        vu = three_cell(k, k, uniform=True) + three_cell(k, k - 1, uniform=True)
        print("  k=%7d: land >= %.4f  (omega_r<=1 로 둔 균일판 %.4f)" % (k, v, vu))
    print("  요구값(k=6668): 띠 1.0845, 벌크 1.0787 ; 현행 적분값 L_*(6668)=1.206")
    # (B) 균일 하계의 단조 근거: 세 인자 방향 확인(표본)
    ks = [6668, 7000, 8000, 10 ** 4, 10 ** 5, 10 ** 6]
    for a, b in ((2, 4), (4, 6)):
        diffs = [omega(k, k + a * mpf(k) ** (mpf(2) / 3)) - omega(k, k + b * mpf(k) ** (mpf(2) / 3)) for k in ks]
        print("  omega(a=%d)-omega(a=%d) 가 k 에 감소: " % (a, b), all(diffs[i] > diffs[i + 1] for i in range(len(ks) - 1)))
    for a in (2, 4, 6):
        sbs = [sbar_1021(k, k + a * mpf(k) ** (mpf(2) / 3)) for k in ks]
        print("  sbar(a=%d) 가 k 에 감소: " % a, all(sbs[i] > sbs[i + 1] for i in range(len(ks) - 1)), [float(x) for x in sbs[:2]])
    om1 = [omega(k, k + 2 * mpf(k) ** (mpf(2) / 3)) for k in ks]
    print("  omega_1 가 k 에 증가: ", all(om1[i] < om1[i + 1] for i in range(len(ks) - 1)))
    # 레벨 k-1 에서 10.21 의 조건: y=k-1>=6666 (k>=6667), d<=y+2 — 셀 끝 d=6(k-1)^{2/3}+1 <= k+1 (k>=6667) 확인
    print("  d_max=6(k-1)^{2/3}+1 <= (k-1)+2 at k=6668:", 6 * mpf(6667) ** (mpf(2) / 3) + 1 <= 6669)

def R_closed(k):
    k = mpf(k)
    return 14 * (log(3 * k) - 1) / (5 * sqrt(pi * k)) + (7 * (3 - log(3)) + 42 / sqrt(3)) / (5 * sqrt(pi) * k)

def check_E6():
    print("E6 닫힌 꼴 R(k):")
    for k in (2001, 3131, 6667, 6668, 8065, 9551, 9705, 20000, 10 ** 6):
        print("  k=%7d: R(k)=%.5f  R(k)/2=%.5f   (현행 6.38: 50.62/sqrt(k-1)=%.4f)" % (k, R_closed(k), R_closed(k) / 2, 50.62 / sqrt(mpf(k) - 1)))
    # 1단계 상수의 k-의존: 10.20 증명 1단계는 k>=6667 에서 A^crit <= 1.00057 q_d, c_d = 0.16696 q_d^2 를 둔다.
    # 일반 k: 1-e^{-x} >= x(1-x/2) 에 inc^+ <= 3/(2k) ; (k-1)(k+1+q)/(k-1+q)^2 <= 1+1/k ; (k+1+d)/(k-1+d) <= 1+2/k.
    # A^crit = (k-1) kappa / (2(1-e^{-inc^+})) 의 상계 인자 ~ (1+1/k)(1+2/k)/(1-3/(4k)) =: g(k); n_q <= g q_d (k+1+q)/q ;
    # 둘째 캡 상수 c_d(k) = (g q_d)^2 (1+2/k)^2 /6 ; 필요: c_d(k) <= 1/3 (F4 의 둘째 캡), 앞인자 2.3274/k <= 21/(5 sqrt pi k)=2.3696/k (k 무관).
    qd_max = 1 + mpf('0.7501') / 2
    for k in (501, 2001, 3131, 6667):
        k = mpf(k)
        g = (1 + 1 / k) * (1 + 2 / k) / (1 - 3 / (4 * k))
        cd = (g * qd_max) ** 2 * (1 + 2 / k) ** 2 / 6
        print("  k=%5d: g=%.6f, c_d(k) <= %.5f (<=1/3: %s); k>=6667 원고 상수 1.00057·q_d, 0.16696·q_d^2=%.5f" % (k, g, cd, cd <= mpf(1) / 3, mpf('0.16696') * qd_max ** 2))
    # 합-적분 비교 상수: sum_{j<=k}(1+log 3j)/sqrt j <= 2 sqrt k (log 3k - 1) + 3 - log 3 (피적분 x>e/3 감소; j=1 항은 1+log3)
    for k in (501, 2001, 3131, 6667):
        s = sum((1 + log(3 * j)) / sqrt(mpf(j)) for j in range(1, int(k) + 1))
        ub = 2 * sqrt(mpf(k)) * (log(3 * mpf(k)) - 1) + 3 - log(3)
        print("  k=%5d: sum=%.4f <= %.4f : %s" % (k, s, ub, s <= ub))
    # 네 가족 (나) 여유의 선형 이동(부록 D 구간값): old margin - (R(k0) - DDL^nat_old(k0))
    old = {'벌크': (6668, mpf('0.5893564'), mpf('0.132366')), '2': (8065, mpf('0.5045530'), mpf('0.122330')),
           '1b': (9551, mpf('0.4673235'), mpf('0.114039')), '1a': (9705, mpf('0.2047101'), mpf('0.113284'))}
    for F, (k0, mg, dold) in old.items():
        print("  가족 %s k0=%d: 새 (나) 여유 ~ %.4f (R=%.5f, 옛 DDL^nat=%.6f);  F4의 1/4 이면 %.4f" % (F, k0, mg - (R_closed(k0) - dold), R_closed(k0), dold, mg - (mpf('0.25') - dold)))
    print("  1a (가)(a) q0=2 여유 0.2354722 -> %.4f ; (가)(b) m0>N 0.3947510 -> %.4f" % (mpf('0.2354722') - (R_closed(9705) - mpf('0.113284')), mpf('0.394751') - (R_closed(9705) - mpf('0.113284'))))

def check_R8():
    z12 = zeta(mpf('0.5')); z32 = zeta(mpf('1.5'))
    cPsi = -z12 + z32 / 12
    c = 1 / sqrt(2 * pi)
    bad98 = bad943 = 0
    # 해석: Psi^low_(d) = c(2 sqrt d - cPsi + 1/(2 sqrt d) - d^{-3/2}/24) >= c(2 sqrt d - cPsi) (d>=1)
    #  9.8:  0.7978 sqrt d - 0.8848 <= c(2 sqrt d - cPsi) <=> (2c-0.7978) sqrt d + 0.8848 - c cPsi >= 0 ; 2c=0.79788>0.7978, c cPsi=0.6694<0.8848 -> 항상 참
    #  9.43: 0.3989(2 sqrt d - 1.678) <= c(2 sqrt d - cPsi) <=> 2(c-0.3989) sqrt d >= c cPsi - 0.3989*1.678 = %.6f
    print("R8: c=%.6f, cPsi=%.6f, c*cPsi=%.6f, 0.3989*1.678=%.6f, 2(c-0.3989)=%.7f" % (c, cPsi, c * cPsi, mpf('0.3989') * mpf('1.678'), 2 * (c - mpf('0.3989'))))
    need = (c * cPsi - mpf('0.3989') * mpf('1.678')) / (2 * (c - mpf('0.3989')))
    print("    9.43 <= 8.6(라)-주항 은 sqrt d >= %.4f, 곧 d >= %.3f 에서 해석적으로 성립; d=1 은 9.43 증명이 따로 다룸(Psi(1)=e^{-1})" % (need, need ** 2))
    for d in range(1, 10 ** 6 + 1):
        dd = mpf(d)
        low = c * (2 * sqrt(dd) - cPsi + 1 / (2 * sqrt(dd)) - dd ** mpf('-1.5') / 24)
        if low < mpf('0.7978') * sqrt(dd) - mpf('0.8848'):
            bad98 += 1
        if low < mpf('0.3989') * (2 * sqrt(dd) - mpf('1.678')):
            bad943 += 1
    print("    d<=10^6 전수: 8.6(라) < 9.8 하계 인 d 수 =", bad98, "; 8.6(라) < 9.43 하계 인 d 수 =", bad943)

if __name__ == "__main__":
    check_E4()
    check_E6()
    check_R8()
