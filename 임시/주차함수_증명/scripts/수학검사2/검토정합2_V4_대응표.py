# -*- coding: utf-8 -*-
"""V4: 라벨_번호_대응표의 「15:52 조립본 번호」 열이 결정 101의 삭제(2.23, 5.16·5.17·5.23–5.25·5.39–5.41)를 반영하지 않은 행을 센다. 읽기 전용."""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = [l for l in io.open(os.path.join(ROOT, "대조v2", "라벨_번호_대응표_1114.md"), encoding="utf-8").read().split("\n") if l.startswith("| `{{")]
aff2 = []; aff5 = []
for l in rows:
    c = [x.strip() for x in l.strip().strip("|").split(" | ")]
    lab, cur, old = c[0], c[3], c[4]
    ch, n = cur.split(".")
    if ch == "2" and int(n) >= 23:
        aff2.append((lab, cur, old))
    if ch == "5" and int(n) >= 42 - 2 + 0:  # 둘째 판 5장: 5.16·5.17(5.4절 끝)은 현재 5.41(W♯⇔W) 뒤·5.42 앞에 있었다
        aff5.append((lab, cur, old))
print("2장: 현재 2.23 이상(15:52에는 2.23이 명제였으므로 +1이어야 함)", len(aff2), "행; 표본", aff2[:3])
print("5장: 현재 5.42 이상(15:52에는 5.16·5.17이 앞에 있어 +2 이상이어야 함)", len(aff5), "행; 표본", aff5[:3], aff5[-1])
same = sum(1 for _, c, o in aff2 + aff5 if c == o)
print("그중 두 열이 같은 행", same)
