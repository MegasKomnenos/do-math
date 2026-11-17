# -*- coding: utf-8 -*-
# R11 검산: D.critical-window-rig — 이 글의 재실행 인증서(critical_window_rerun/cert/*.json)가
# 기록 [ra4c01fc] §8.2의 표본(상자 여섯, 같은 c 값)에서 참값(양의 재귀, binary64)을 담는지.
# 기록의 exact_en_B.recursions 를 읽기 전용으로 불러 쓴다(기록의 contain_check.py 와 같은 모형 식).
import json, math, sys, glob, os, time
REC = glob.glob(r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/ra4c01fc*/evidence/peer")[0]
sys.path.insert(0, REC)
from exact_en_B import recursions
CERT = r"C:/math/임시/주차함수_증명/원고_자료/세션_재계산/critical_window_rerun/cert"
boxes = {"A00": [10001, 10500, 11036], "A01": [11037, 12220], "A05": [16970, 19093], "A10": [32257, 37356], "A15": [73119, 88801], "A20": [226116, 301430]}
only = sys.argv[1:] or list(boxes)
def lam(n): return math.exp(math.lgamma(n + 1) + (n + 1) - (n - 1) * math.log(n + 1))
def tau(c): return math.exp(-c + (c - 1) * math.log(c) - math.lgamma(c + 1))
tot = 0; totfail = 0; gworst = 1e9; minratio = 1e9
for bx in only:
    D = json.load(open(os.path.join(CERT, bx + ".json"), encoding="utf-8"))
    recs = D["records"]; xlo = float(D["x_lo"]); xhi = float(D["x_hi"])
    ulo, uhi = D["u"][0], D["u"][1]
    npts = 0; nfail = 0; worst = 1e9; t0 = time.time()
    for c in boxes[bx]:
        u = c ** (-1.0 / 3)
        assert ulo - 1e-15 <= u <= uhi + 1e-15, (bx, c, u, ulo, uhi)
        Ymax = int(10 * c ** (2.0 / 3)) + 2
        nmax = min(2 * c, c + Ymax)
        r, a, d, e, j = recursions(c, nmax=nmax)
        tc = tau(c)
        for n in range(c + 1, nmax + 1):
            Y = n - c; xh = (Y + 1) * u * u
            if xh < xlo or xh > xhi: continue
            conv = math.pi / (lam(n) * tc * u ** 4)
            Ehat = e[n] / r[n] * conv; Bhat = j[n] / r[n] * conv
            cell = None
            for rc in recs:
                if rc["xa"] - 1e-12 <= xh <= rc["xb"] + 1e-12: cell = rc; break
            if cell is None: continue
            xm = (cell["xa"] + cell["xb"]) / 2; dx = xh - xm
            def model(F0, F1, L2, tail):
                lo = F0[0] + min(dx * F1[0], dx * F1[1]) - dx * dx / 2 * L2 - tail
                hi = F0[1] + max(dx * F1[0], dx * F1[1]) + dx * dx / 2 * L2 + tail
                return lo, hi
            Elo, Ehi = model(cell["E0"], cell["E1"], cell["L2e"], cell["tailE"])
            Blo, Bhi = model(cell["B0"], cell["B1"], cell["L2B"], cell["tailB"])
            ok = (Elo <= Ehat <= Ehi) and (Blo <= Bhat <= Bhi)
            npts += 1; nfail += (not ok)
            worst = min(worst, Ehat - Elo, Ehi - Ehat, Bhat - Blo, Bhi - Bhat)
            minratio = min(minratio, e[n] / j[n])
    print(bx, "c =", boxes[bx], "points", npts, "failures", nfail, "worst slack %.3e" % worst, "(%.0fs)" % (time.time() - t0), flush=True)
    tot += npts; totfail += nfail; gworst = min(gworst, worst)
print("TOTAL points", tot, "failures", totfail, "worst slack %.3e" % gworst, "min e/B %.4f" % minratio)
