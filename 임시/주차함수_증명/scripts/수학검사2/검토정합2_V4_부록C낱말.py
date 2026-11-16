# -*- coding: utf-8 -*-
"""V4: 부록 C 낱말 표의 각 행을 장부 3절의 같은 낱말 행과 대조한다(절 열·기록의 용어 열). 읽기 전용."""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
led = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read()
s3 = led[led.index("## 3. 낱말 사전"):led.index("\n## 4.")]
rows3 = {}
for l in s3.split("\n"):
    if l.startswith("| ") and not l.startswith("| 낱말"):
        c = [x.strip() for x in l.strip().strip("|").split(" | ")]
        if len(c) >= 4:
            rows3[c[0]] = c
C = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read()
sC = C[C.index("### 낱말"):C.index("### 기록이 결과에")]
n = 0
for l in sC.split("\n"):
    if not l.startswith("| ") or l.startswith("| 이 글의 용어"):
        continue
    c = [x.strip() for x in l.strip().strip("|").split(" | ")]
    if len(c) < 3:
        continue
    w = re.sub(r"\([A-Za-z][^)]*\)$", "", c[0]).strip()
    r = rows3.get(w)
    if r is None:
        print("3절에 없음:", c[0], "|", c[1], "|", c[2]); n += 1; continue
    if r[2] != c[2]:
        print(f"절 다름: {w} | C={c[2]} | 장부={r[2]}"); n += 1
print("차이", n)
