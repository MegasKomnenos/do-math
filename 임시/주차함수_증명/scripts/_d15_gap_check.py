# -*- coding: utf-8 -*-
"""D.15(정리 5.39) 인증서의 x̂ 덮개를 정확 유리수로 검사한다(외부 지적 「D.15의 구간 덮개」 검증).
저장된 셀 끝점 xa, xb(binary64)과 코드가 쓴 중점 xm=fl((xa+xb)/2), 반지름 hh/2(hh=fl((10-1.4)/43))로
Taylor 모형의 보장 구간 [xm-hh/2, xm+hh/2]를 정확히 계산해 (1) 인접 셀 사이의 틈, (2) 양 끝의 덮개, (3) 상자(u) 쪽
c_lo·c_hi의 연속성을 보고한다. 또 틈에 실제로 드는 정수 입력 (k, r)의 예를 든다."""
import glob
import json
import math
import os
from fractions import Fraction as Fr

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "원고_자료", "세션_재계산", "critical_window_rerun")
certs = sorted(glob.glob(os.path.join(HERE, "v1_floatgrid", "cert", "?[0-9][0-9].json")))   # binary64 격자 판(기록 코드와 같은 격자)의 인증서
print("인증서", len(certs))

x_lo = 1.4
m = 43
hh = (10.0 - x_lo) / m
print("hh(float) =", repr(hh), "=", Fr(hh), "; 정확 1/5과의 차 =", float(Fr(hh) - Fr(1, 5)))
# 코드가 만드는 격자(상자와 무관)
xa = [x_lo + k * hh for k in range(m)]
xb = [a + hh for a in xa]
xm = [(a + b) / 2 for a, b in zip(xa, xb)]
r = Fr(hh) / 2
regions = [(Fr(c) - r, Fr(c) + r) for c in xm]
gaps = []
for k in range(m - 1):
    g = regions[k + 1][0] - regions[k][1]
    if g > 0:
        gaps.append((k, g, regions[k][1], regions[k + 1][0]))
print("Taylor 보장 구간 사이의 양의 틈:", len(gaps))
for k, g, a, b in gaps:
    print("  셀 %d|%d 사이: 틈 폭 %.3e, 명목 경계 %.1f, 구간 (%s, %s)" % (k, k + 1, float(g), x_lo + (k + 1) * 0.2, float(a), float(b)))
box_gaps = [(k, Fr(xa[k + 1]) - Fr(xb[k])) for k in range(m - 1) if Fr(xa[k + 1]) > Fr(xb[k])]
print("저장 셀 상자 [xa,xb] 사이의 양의 틈:", len(box_gaps), [(k, float(g)) for k, g in box_gaps])
print("첫 구간 아래 끝 - 1.4 =", float(regions[0][0] - Fr(7, 5)), "(음수여야 덮음)")
print("마지막 구간 위 끝 - 10 =", float(regions[-1][1] - 10), "(양수여야 덮음)")
# 보장 구간이 셀 상자 밖으로 나가는 양(L2·꼬리가 유효한 상자는 [xa,xb])
over = max(max(Fr(xa[k]) - regions[k][0], regions[k][1] - Fr(xb[k])) for k in range(m))
print("보장 구간이 [xa,xb] 밖으로 나가는 최대 폭:", float(over))

# 모든 인증서의 xa/xb가 위 격자와 같은지, c 범위가 연속인지
same = True
cs = []
for p in certs:
    D = json.load(open(p))
    recs = D["records"]
    if [q["xa"] for q in recs] != xa or [q["xb"] for q in recs] != xb:
        same = False
        print("  격자 다름:", os.path.basename(p))
    cs.append((D["box"], D["c_lo"], D["c_hi"]))
print("모든 인증서의 셀 격자가 위와 같음:", same)
cs.sort(key=lambda t: t[1])
print("c 범위:", cs[0], "...", cs[-1])
bad = [(a, b) for a, b in zip(cs, cs[1:]) if a[2] is None or b[1] != a[2] + 1]
print("c 범위 불연속:", bad)

# 틈에 드는 정수 입력: x̂=(r+1)k^{-2/3}가 정확히 1.4+0.2i 이려면 k=c^3, 5 | c.
ex = []
for j in range(1, 200):
    c = 5 * j
    k = c ** 3
    if k < 10001:
        continue
    for kk, g, a, b in gaps:
        i = kk + 1
        num = (7 + i) * c * c
        if num % 5 == 0:
            rr = num // 5 - 1
            ex.append((k, rr, (7 + i) / 5))
    if len(ex) >= 6:
        break
print("틈에 정확히 드는 정수 입력의 예 (k, r, x̂):", ex[:6])
print("그런 k의 수(k=125j^3 >= 10001, j<=200):", sum(1 for j in range(1, 201) if 125 * j ** 3 >= 10001))
