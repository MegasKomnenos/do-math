# 24차 수리 Z9 검산: 명제 9:old-8-33 (i) 증명의 Abel 꼬리 대목에 채운 걸음의 수치 대조(엄밀 구간 아님).
# python -I -X utf8 로 실행. 읽기 전용(파일을 쓰지 않는다).
import mpmath as mp
mp.mp.dps = 30
mS = mp.mpf('1.15')

def check(k, y, nubar):
    k = int(k); y = int(y); nubar = mp.mpf(nubar)
    wt = lambda d: min(mp.mpf(2), 2 - (d - nubar - 2) / k)           # \tilde\omega
    ysh = lambda d: wt(d) * (d - 1) / (y + 2 - d)                    # \mathfrak y^\sharp
    sup = lambda d: min(mp.mpf(1), mS * (y + d) / mp.mpf(d) ** 1.5)  # \mathfrak s^{up}_d(y)
    W = lambda t: min(mp.mpf(2), 2 - (t - 3 - nubar) / k)
    e = lambda t: (y + t) * mp.mpf(t) ** (-1.5) * (y + 2 - t) ** (-2)
    # 근 a_y 와 a^sharp_y
    ay = mp.findroot(lambda t: t ** 1.5 - mS * (y + t), (mS * y) ** (mp.mpf(2) / 3))
    ash = max(d for d in range(1, int(ay) + 3) if mS * (y + d) >= mp.mpf(d) ** 1.5)
    assert ash == int(mp.floor(ay)), (ash, ay)
    assert ash > ay - 1 >= (mS * y) ** (mp.mpf(2) / 3) - 1
    dstar = (6 * y) // 10
    assert mp.mpf(6) / 10 < mp.mpf(dstar + 1) / y <= mp.mpf(6) / 10 + mp.mpf(1) / y
    # (1) 항별 상계
    worst = mp.mpf(0); S = mp.mpf(0); T = mp.mpf(0)
    for d in range(ash + 1, dstar + 1):
        term = (ysh(d) - ysh(d - 1)) * sup(d)
        bound = (y + 1) * mS * W(d) * e(d)
        assert W(d) == wt(d - 1)
        assert term <= bound * (1 + mp.mpf(10) ** -25), (d, term, bound)
        S += term; T += W(d) * e(d)
    # (2) 합과 적분
    I = mp.quad(lambda t: W(t - 1) * e(t), mp.linspace(ash, dstar + 1, 60))
    assert T <= I, (T, I)
    # (3) 닫힌 꼴 Ab
    z = mp.mpf(6) / 10 + mp.mpf(1) / y
    cAb = lambda r: 2 * mp.sqrt(r) / (1 - r) + 2 * mp.log((1 + mp.sqrt(r)) / (1 - mp.sqrt(r)))
    xi = (nubar + 4) / (k - 1)
    Sub = mp.mpf(0) if xi >= mp.mpf(6) / 10 else mp.mpf(k - 1) / k * mp.quad(
        lambda r: (r - xi) * (1 + r) * r ** (-1.5) * (1 - r) ** (-2), [xi, mp.mpf(6) / 10])
    Ab = mS * (1 + mp.mpf(1) / y) * (4 * ((mS * y) ** (mp.mpf(2) / 3) - 1) ** (-0.5)
                                    + mp.mpf(y) ** (-0.5) * (2 * cAb(z) - 4 * z ** (-0.5) - Sub))
    assert (y + 1) * mS * I <= Ab, ((y + 1) * mS * I, Ab)
    rho0 = mp.mpf(ash) / y
    return float(S), float((y + 1) * mS * I), float(Ab), ash, float(xi), float(rho0)

for k in (6667, 8065, 9551, 9705, 20000, 100000):
    for y in (k - 1, k):
        for nb in (0, 1.3 * k ** (2 / 3), 2 * k ** (2 / 3), 0.48 * k):
            r = check(k, y, nb)
            print(k, y, round(float(nb), 1), 'sum=%.6f  (y+1)mS*int=%.6f  Ab=%.6f  a#=%d  xiSub=%.4f rho0=%.4f' % r)
print('모두 통과')
