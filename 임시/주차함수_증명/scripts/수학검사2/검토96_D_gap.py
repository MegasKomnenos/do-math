# -*- coding: utf-8 -*-
"""검토 D: _d15_gap_check.py의 격자 계산을 v1_floatgrid/cert(옛 인증서)로 다시 돌려 틈 수·폭·양 끝 값을 확인한다(가벼움)."""
import glob, json, os
from fractions import Fraction as Fr
HERE = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\critical_window_rerun\v1_floatgrid"
certs = sorted(glob.glob(os.path.join(HERE, "cert", "?[0-9][0-9].json")))
print("옛 인증서", len(certs))
x_lo = 1.4; m = 43
hh = (10.0 - x_lo) / m
print("hh =", Fr(hh), "=", repr(hh))
xa = [x_lo + k * hh for k in range(m)]; xb = [a + hh for a in xa]; xm = [(a + b) / 2 for a, b in zip(xa, xb)]
r = Fr(hh) / 2
regions = [(Fr(c) - r, Fr(c) + r) for c in xm]
gaps = [(k, regions[k + 1][0] - regions[k][1]) for k in range(m - 1) if regions[k + 1][0] > regions[k][1]]
print("Taylor 틈 수", len(gaps), "최소 폭 %.3e 최대 폭 %.3e" % (float(min(g for _, g in gaps)), float(max(g for _, g in gaps))))
print("최대 폭 > 1e-15 ?", max(g for _, g in gaps) > Fr(1, 10**15))
box_gaps = [(k, Fr(xa[k + 1]) - Fr(xb[k])) for k in range(m - 1) if Fr(xa[k + 1]) > Fr(xb[k])]
print("저장 셀 틈 수", len(box_gaps), "최대 폭 %.3e" % float(max(g for _, g in box_gaps)))
print("아래 끝 미덮음 %.3e, 위 끝 미덮음 %.3e" % (float(regions[0][0] - Fr(7, 5)), float(10 - regions[-1][1])))
over = max(max(Fr(xa[k]) - regions[k][0], regions[k][1] - Fr(xb[k])) for k in range(m))
print("보장 구간이 셀 밖으로 나가는 최대 폭 %.3e" % float(over))
same = True
for p in certs:
    D = json.load(open(p)); recs = D["records"]
    if [q["xa"] for q in recs] != xa or [q["xb"] for q in recs] != xb:
        same = False; print("격자 다름", os.path.basename(p))
print("44개 옛 인증서가 같은 격자:", same)
print("k=125j^3>=10001, j<=200 인 j 수:", sum(1 for j in range(1, 201) if 125 * j ** 3 >= 10001))
