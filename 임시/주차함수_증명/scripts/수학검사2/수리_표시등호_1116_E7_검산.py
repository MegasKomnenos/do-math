"""E7 검산(읽기 전용): 장7B 정리 polar-PD 증명(526행)·정리 theorem-W (나) 증명(630행)·명제 pair-check-10000 증명(209행),
장7A 따름정리 cor-S-prime 증명(555행)의 표시값을 60자리(mpmath) 또는 정확 유리수(fractions)로 다시 세고,
고친 부등식이 참인지 확인한다.  사용: python -I 이_파일.py
"""
from fractions import Fraction as F

from mpmath import ceil, exp, mp, mpf, sqrt

mp.dps = 60
ok = True


def chk(name, cond, val):
    global ok
    ok &= bool(cond)
    print(f"{'OK ' if cond else 'FAIL'} {name}: {val}")


print("== 장7B 526행 (정리 polar-PD 증명)")
v = 2 * exp(-mpf('5.3146') * mpf('0.6996'))
chk("2e^{-5.3146*0.6996} < 0.0486 (왼쪽 상계)", v < mpf('0.0486'), v)
chk("0.7*2001/2002 >= 0.6996", mpf(7) / 10 * 2001 / 2002 >= mpf('0.6996'), mpf(7) / 10 * 2001 / 2002)
chk("0.3^{3/2}/2 > 0.0821", mpf('0.3') ** mpf(1.5) / 2 > mpf('0.0821'), mpf('0.3') ** mpf(1.5) / 2)
r = mpf('0.0821') * exp(-mpf(3) / 25233)
chk("0.0821 e^{-3/25233} > 0.0820 (오른쪽 하계)", r > mpf('0.0820'), r)
chk("ceil(2002^{4/3}) = 25233", ceil(mpf(2002) ** (mpf(4) / 3)) == 25233, mpf(2002) ** (mpf(4) / 3))
chk("사슬 닫힘: 0.0486 < 0.0820", mpf('0.0486') < mpf('0.0820'), "여유 0.0334")
v2 = 2 * exp(-mpf('4.57') * mpf('0.6996'))
chk("ς>4.57이면 충분: 2e^{-4.57*0.6996} < 0.0820", v2 < mpf('0.0820'), v2)

print("== 장7B 630행 (정리 theorem-W (나) 증명)")
k = mpf(3131)
chk("0.14*2.38*0.9999 >= 0.33316", mpf('0.14') * mpf('2.38') * mpf('0.9999') >= mpf('0.33316'),
    mpf('0.14') * mpf('2.38') * mpf('0.9999'))
chk("0.14*301 = 42.14", mpf('0.14') * 301 == mpf('42.14'), mpf('0.14') * 301)
chk("0.33316/4 = 0.08329", mpf('0.33316') / 4 == mpf('0.08329'), mpf('0.33316') / 4)
d2 = mpf('0.08329') * sqrt(k) - 2 - mpf('42.14') / k
chk("D_k(2) at k=3131 > 2.647", d2 > mpf('2.647'), d2)
u = k ** (mpf(1) / 6)
chk("3131^{1/6} >= 3.8248", u >= mpf('3.8248'), u)
chk("(1+1/3131)^{4/3} <= 1.0005", (1 + 1 / k) ** (mpf(4) / 3) <= mpf('1.0005'), (1 + 1 / k) ** (mpf(4) / 3))
chk("1.001 + 42.14/3131 <= 1.0145", mpf('1.001') + mpf('42.14') / k <= mpf('1.0145'), mpf('1.001') + mpf('42.14') / k)
right = mpf('0.33316') * (sqrt(k) - 2 * u + 1 / u) - mpf('1.0005') * k ** (mpf(1) / 3) - mpf('1.0145')
chk("오른쪽 끝 하계식 at k=3131 > 0.529", right > mpf('0.529'), right)
der = mpf('0.33316') * (3 * u ** 2 - 2 - 1 / u ** 2) - mpf('2.001') * u
chk("k^{1/6}에 대한 도함수 at k=3131 > 0", der > 0, der)

print("== 장7B 209행 (명제 pair-check-10000 증명; (7.11) 우변의 정확 유리수 최솟값, k=10000, q+q'+j<=50)")
K = 10000


def pish(q):
    return F(q * (q - 1), 2 * (K + 1))


def exb(q):
    p = pish(q)
    return q + (K + q) * p / (1 - p)


best = None
cnt = 0
for q in range(1, 51):
    for qp in range(1, 51 - q):
        for j in range(0, 51 - q - qp):
            val = 1 - F(j, K) * (exb(q) + exb(qp)) - (exb(q) * (qp - 1) + exb(qp) * (q - 1)) / (2 * K)
            if q <= qp:
                cnt += 1
            if best is None or val < best[0]:
                best = (val, q, qp, j)
chk("경우의 수(q<=q') = 10725", cnt == 10725, cnt)
chk("최솟값 자리 = (1,33,16)", best[1:] == (1, 33, 16), best[1:])
chk("최솟값 > 0.0492", best[0] > F(492, 10000), float(best[0]))
chk("최솟값 < 0.04926 (옛 등호는 올림 표시였음)", best[0] < F(4926, 100000), float(best[0]))

print("== 장7A 555행 (따름정리 cor-S-prime 증명; 표의 올림값 A0·B0를 넣은 정확 유리수 평가)")
for name, xi_den, y, A0, B0, lo, disp in [
    ("범위 1", 501, F(13, 100), F('1.4708'), F('0.098505'), F('3.24e-4'), F('3.247e-4')),
    ("범위 2", 1855, F(2, 25), F('2.5335'), F('0.060259'), F('7.80e-5'), F('7.801e-5')),
    ("범위 3", 6098, F(11, 200), F('2.7354'), F('0.0422'), F('2.27e-4'), F('2.275e-4')),
]:
    xi = F(1, xi_den)
    val = (y - xi) * (y - 2 * xi - xi * xi) - (1 + xi) ** 2 * (A0 * xi + B0 * y)
    vert = (3 * xi + xi * xi) / 2 + (1 + xi) ** 2 * B0 / 2
    chk(f"{name}: 올림값 평가 > {float(disp):.3e} (본문 괄호) 그리고 > {float(lo):.2e} (본문 본값)",
        val > disp and val > lo, float(val))
    chk(f"{name}: 꼭짓점 조건 (3ξ+ξ²)/2+(1+ξ)²B0/2 <= y", vert <= y, f"{float(vert):.5f} <= {float(y)}")

print("ALL OK" if ok else "SOME FAIL")
