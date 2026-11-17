# 검토전체23 R4: 정의 5:old-5-21 의 이음 행 t_0(y) 와 보조정리 5:joining-width 를 정의대로 다시 센다.
from math import isqrt


def m_cells_table(nmax):
    """mfrak(n) = max({170} ∪ {m>=171 : m^{3/2}+9m <= n}), 정수 산술로."""
    out = [0] * (nmax + 1)
    m = 170
    for n in range(1, nmax + 1):
        # (m+1)^{3/2} + 9(m+1) <= n  <=>  (m+1)^3 <= (n-9(m+1))^2, n-9(m+1) >= 0
        while True:
            c = m + 1
            rest = n - 9 * c
            if c >= 171 and rest >= 0 and c ** 3 <= rest * rest:
                m = c
            else:
                break
        out[n] = m
    return out


NMAX = 400000
mf = m_cells_table(NMAX)
assert mf[20001] == 597 and mf[50001] == 1160, (mf[20001], mf[50001])
print('mfrak(20001)=597, mfrak(50001)=1160: OK')


def icbrt_sq_ceil(y):
    """ceil(y^{2/3}) 정수로: 최소 c with c^3 >= y^2."""
    c = int(round(y ** (2 / 3)))
    while c ** 3 < y * y:
        c += 1
    while (c - 1) ** 3 >= y * y:
        c -= 1
    return c


worst = 0
cnt = 0
for y in range(20001, 300000, 7):
    m = y + 1
    while not (m - y >= mf[m] + 1):
        m += 1
    t0 = m + 1
    cnt += 1
    assert t0 >= y + 2
    bound = y + icbrt_sq_ceil(y) + 2
    assert t0 <= bound, (y, t0, bound)
    wid = t0 - 1 - y
    worst = max(worst, wid / y ** (2 / 3))
    # (가): 그 위의 행들에서도 조건이 성립 (표의 끝까지 몇 행만 표본)
    for mm in (m, m + 1, m + 17, m + 1000, 2 * y - 2):
        if mm <= NMAX and mm >= m:
            assert mm - y >= mf[mm] + 1, (y, mm)
print('t_0(y) <= y+ceil(y^(2/3))+2 와 (가): y=20001..300000(간격 7) %d건 OK; max wid/y^(2/3)=%.4f' % (cnt, worst))

# W-sharp 위치에서 t_0(y) <= n : n=50001, 60001, 100001 의 모든 위치
for n in (50001, 60001, 100001):
    c = 0
    for y in range((n + 2) // 2, n):
        # n-y+1 > 10 y^{2/3}  <=>  (n-y+1)^3 > 1000 y^2
        if (n - y + 1) ** 3 > 1000 * y * y:
            m = y + 1
            while not (m - y >= mf[m] + 1):
                m += 1
            assert m + 1 <= n, (n, y)
            c += 1
    print('n=%d: W-sharp 위치 %d곳 모두 t_0(y)<=n' % (n, c))
