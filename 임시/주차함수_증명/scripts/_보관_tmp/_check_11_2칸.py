# -*- coding: utf-8 -*-
"""11.2 표의 행 수와 칸 수(6)를 확인하고, 6열이 부록 D 항목의 「독립 재계산」 문단(꺾쇠 뺀 것)과 같은지 센다. 읽기만 한다."""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPLIT = re.compile(r"(?<!\\)\|")
s = io.open(os.path.join(ROOT, "장v2", "장11.md"), encoding="utf-8").read()
rows = [l for l in s.split("\n") if l.startswith("| 부록 D.{{D:")]
bad = [l[:70] for l in rows if len(SPLIT.split(l.strip()[1:-1])) != 6]
print("11.2 행", len(rows), "칸 수 이상", len(bad), bad[:3])
# D 항목의 독립 재계산 문단
ind = {}
for p in glob.glob(os.path.join(ROOT, "장v2", "부록D_*.md")):
    cur = None
    for l in io.open(p, encoding="utf-8").read().split("\n"):
        m = re.match(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}", l)
        if m:
            cur = m.group(1)
        elif cur and l.startswith("**독립 재계산.**"):
            body = re.sub(r"^\*\*독립 재계산\.\*\*\s*〔[^〕]*〕\s*", "", l).strip()
            ind[cur] = body.replace("|", "\\vert ")
same = diff = 0
for l in rows:
    cells = [c.strip() for c in SPLIT.split(l.strip()[1:-1])]
    lab = re.search(r"\{\{D:([^}]+)\}\}", cells[0]).group(1)
    if lab in ind and cells[5] == ind[lab].strip():
        same += 1
    else:
        diff += 1
        print("  다름:", lab, "|", cells[5][:60], "||", ind.get(lab, "")[:60])
print("6열 = D 문단", same, "다름", diff)
