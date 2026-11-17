# -*- coding: utf-8 -*-
# 검토 24차 R4: 이음 행의 폭(보조정리 joining-width)과, W# 의 표본 위치에서
# 창 항의 닫힌 꼴 상계(보조정리 5:old-5-26)·판정식 (5.3)의 각 재료를 배정밀도로 직접 세어 본문 상수와 견준다.
import math


def build_mfrak(nmax):
    # m(n) = max({170} ∪ {m>=171 : m^{3/2}+9m <= n})
    tab = [170] * (nmax + 1)
    m = 171
    thr = m ** 1.5 + 9 * m
    cur = 170
    for n in range(1, nmax + 1):
        while thr <= n:
            cur = m
            m += 1
            thr = m ** 1.5 + 9 * m
        tab[n] = cur
    return tab


NMAX = 400000
MF = build_mfrak(NMAX)
assert MF[20001] == 597 and MF[50001] == 1160


def t0(y):
    m = y + 1
    while m - y < MF[m] + 1:
        m += 1
    return m + 1


# (1) t0(y) <= y + ceil(y^{2/3}) + 2,  y >= 20001
worst = -10 ** 9
for y in range(20001, 300000, 7):
    t = t0(y)
    bound = y + math.ceil(y ** (2 / 3)) + 2
    worst = max(worst, t - bound)
    assert t <= bound, y
    # (가): m >= t0-1 에서 조건 유지
    for m in (t - 1, t, t + 5, t + 100):
        assert m - y >= MF[m] + 1
print("(1) 이음 행의 폭: 표본 y 에서 t0 - (y+ceil(y^(2/3))+2) 의 최댓값 =", worst)


def lbor(m):
    return -m + (m - 1) * math.log(m) - math.lgamma(m + 1)


def lpi(n, t):
    return lbor(t) + lbor(n + 1 - t) - lbor(n + 1)


def g(x):
    return (x - 1) * math.log1p(1 / x)


def hv(chi):
    return chi ** -0.5 * (2 / math.sqrt(math.pi) * (1 + 1 / chi) + 1 / math.sqrt(math.pi))


def check(n, y):
    r = n - y
    lam = y / n
    assert 2 * y >= n + 1 and r + 1 > 10 * y ** (2 / 3)
    T0 = t0(y)
    assert T0 <= n
    wid = T0 - 1 - y
    # 창 항: WIN^V_0 * y / pi_n(y) 를 직접 센다
    s = 0.0
    lp = 0.0  # log(pi_n(t)/pi_n(y))
    for t in range(y + 1, T0):
        lp += g(t - 1) - g(n - (t - 1))
        q = t - y
        theta = math.exp(math.log(q) + lbor(q) + lbor(y) - lbor(t))
        s += math.expm1(lp) * theta
    c1 = 1.5 * (2 * y + 2 * wid - n) / (y * (n - y - wid))
    e0 = 1.5 * wid * (2 * y + 2 * wid - 2 - n) / ((y + wid - 1) * (n - y - wid + 1))
    win = (2 * math.pi) ** -0.5 * (2 / 3) * (wid + 1) ** 1.5 * c1 * (1 + wid / y) ** 1.5 * math.exp(e0 + 1 / (12 * y))
    assert s <= win, (n, y, s, win)
    # 매개변수
    qmax = math.floor(6 * y ** (2 / 3))
    if 3 * y <= 2 * n:
        chi = math.floor(0.3 * r)
    else:
        chi = min(math.floor(0.3 * r), (r - qmax) // 2 - 6)
    assert chi >= 4 and 2 * chi + qmax <= r - 1 and chi <= r - wid
    rho0 = (y - 1) / n
    hovlow = 1 / (1 - rho0) * (1 - hv(chi) / (1 - rho0))
    Vst = (2 * math.pi) ** -0.5 * (n / (y * (n - y))) ** 1.5 * math.exp(-1 / (12 * (n - 2 * chi - y - qmax + 1)) - 1 / (12 * y))
    Kt = Vst * y / (n * math.exp(lpi(n, y)))
    c2 = 1 / (12 * (n - 2 * chi - y - qmax + 1)) + 1 / (12 * y) + 1 / (12 * (n + 1))
    assert Kt >= lam * math.exp(-c2) * (1 - 1e-12)
    sb = sum(math.exp(lbor(i)) for i in range(1, chi + 1))
    pit = math.exp(lpi(n, T0 - 1))
    toppi = (y - 1) * math.exp(lpi(n, y))
    brack = 2 * sb - 2 * chi * pit - toppi
    lhs = hovlow * 0.8 * Kt * brack - win
    psi = (r + 1) / n * (lhs - 1)
    return wid, chi, s, win, toppi, pit, hv(chi) * n / (r + 1), sb - chi * pit, psi


print("(2) 표본 위치의 판정식 (5.3):  n, y, wid, chi, WIN^V*y/pi, win, top_pi, pi(t0-1), eps_hov, 무게합, Psi")
for n in (50001, 50002, 80000, 200000, 399999):
    ys = []
    y = (n + 2) // 2
    ys.append(y)
    ys.append((y + (2 * n) // 3) // 2)
    ys.append((2 * n) // 3)
    ys.append((2 * n) // 3 + 1)
    # 오른쪽 끝: r+1 > 10 y^{2/3} 을 만족하는 가장 큰 y
    yy = n - 1
    while not (n - yy + 1 > 10 * yy ** (2 / 3)):
        yy -= 1
    ys.append((ys[-1] + yy) // 2)
    ys.append(yy)
    for y in ys:
        wid, chi, s, win, toppi, pit, eh, ws, psi = check(n, y)
        lam = y / n
        if 3 * y <= 2 * n:
            ref = 1.474 * lam - 0.532
            okc = eh <= 0.0719 and ws >= 0.9843 and toppi <= 0.0132 and (n - y + 1) / n * win <= 0.4885 * (2 * lam - 1) + 0.0203
        else:
            ref = 0.7457 * lam - (1 - lam) - 2.5e-5
            okc = eh <= 0.1573 and ws >= 0.9798 and toppi <= 0.0232 and (n - y + 1) / y * win <= 0.5513
        print("  %7d %7d wid=%5d chi=%6d WINV=%.5f win=%.5f top_pi=%.5f pi=%.2e eps=%.4f w=%.5f Psi=%.4f (본문 하계 %.4f) 상수 %s"
              % (n, y, wid, chi, s, win, toppi, pit, eh, ws, psi, ref, "OK" if okc and psi >= ref else "FAIL"))
