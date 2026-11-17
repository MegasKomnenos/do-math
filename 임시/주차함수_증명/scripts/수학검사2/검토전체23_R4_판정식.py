# 검토전체23 R4: (5.3) 을 W-sharp 위치에서 정의대로(이음 행은 정의, 핵은 lgamma) 직접 계산해
# 명제 5:band-inequality, 보조정리 5:right-part 의 결론(Psi >= 1.474 lam - 0.532, Psi_R > 0.163)과 견준다.
# hov 는 보조정리 5:hover-tail 의 하계로, 착지 질량은 w0=4/5 로 둔다(배정밀도; 여유가 0.1 규모라 충분).
import sys
from math import exp, floor, lgamma, log, pi, sqrt


def m_cells_table(nmax):
    out = [0] * (nmax + 1)
    m = 170
    for n in range(1, nmax + 1):
        while True:
            c = m + 1
            rest = n - 9 * c
            if c >= 171 and rest >= 0 and c ** 3 <= rest * rest:
                m = c
            else:
                break
        out[n] = m
    return out


def lbor(i):  # log Bor(i)
    return -i + (i - 1) * log(i) - lgamma(i + 1)


def check(n, mf, step):
    lb1 = lbor(n + 1)

    def pik(t):
        return exp(lbor(n + 1 - t) + lbor(t) - lb1)

    # Bor 부분합
    cum = [0.0]
    for i in range(1, n + 1):
        cum.append(cum[-1] + exp(lbor(i)))
    worstB = 1e9
    worstR = 1e9
    cnt = 0
    for y in range((n + 2) // 2, n, step):
        if not ((n - y + 1) ** 3 > 1000 * y * y):
            continue
        cnt += 1
        r = n - y
        lam = y / n
        m = y + 1
        while not (m - y >= mf[m] + 1):
            m += 1
        t0 = m + 1
        wid = t0 - 1 - y
        qmax = floor(6 * y ** (2 / 3) + 1e-9)
        if 3 * y <= 2 * n:
            chi = floor(0.3 * r)
        else:
            chi = min(floor(0.3 * r), (r - qmax) // 2 - 6)
        chi2 = chi
        # 따름정리 old-5-34 의 조건
        assert chi >= 4 and chi2 >= 1 and chi + chi2 + qmax <= r - 1 and chi2 <= r - wid, (n, y)
        rho0 = (y - 1) / n
        hv = chi ** -0.5 * (2 / sqrt(pi) * (1 + 1 / chi) + 1 / sqrt(pi))
        hov = 1 / (1 - rho0) * (1 - hv / (1 - rho0))
        Vst = (2 * pi) ** -0.5 * (n / (y * (n - y))) ** 1.5 * exp(
            -1 / (12 * (n - chi2 - chi - y - qmax + 1)) - 1 / (12 * y))
        K = Vst * y / (n * pik(y))
        topp = (y - 1) * pik(y)
        br = 2 * cum[chi2] - 2 * chi2 * pik(t0 - 1) - topp
        c1 = 1.5 * (2 * y + 2 * wid - n) / (y * (n - y - wid))
        e0 = 1.5 * wid * (2 * y + 2 * wid - 2 - n) / ((y + wid - 1) * (n - y - wid + 1))
        win = (2 * pi) ** -0.5 * (2 / 3) * (wid + 1) ** 1.5 * c1 * (1 + wid / y) ** 1.5 * exp(e0 + 1 / (12 * y))
        lhs = hov * 0.8 * K * br - win
        psi = (r + 1) / n * (lhs - 1)
        if 3 * y <= 2 * n:
            worstB = min(worstB, psi - (1.474 * lam - 0.532))
        else:
            worstR = min(worstR, psi - 0.163)
        assert lhs >= 1, (n, y, lhs)
    print('n=%d: W-sharp 위치 %d곳에서 (5.3) 성립; min[Psi-(1.474lam-0.532)]=%.4f (조립 범위), min[Psi_R-0.163]=%.4f (오른쪽 범위)'
          % (n, cnt, worstB, worstR))


NS = [50001, 50002, 60000, 100000, 200000]
mf = m_cells_table(2 * max(NS))
for n in NS:
    check(n, mf, 1 if n < 60000 else 7)
