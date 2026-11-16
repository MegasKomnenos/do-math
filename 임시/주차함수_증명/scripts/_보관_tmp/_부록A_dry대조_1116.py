# -*- coding: utf-8 -*-
"""RL 인계 2: 부록_v2.py가 만드는 부록 A(건조)와 현행 장v2/부록A.md를 표 행 단위로 대조한다. 2026-11-16."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
mod = importlib.import_module("부록_v2")
ledger = io.open(mod.LEDGER, encoding="utf-8").read()
texts = mod.chapter_texts()
body = "\n".join(texts.values())
A_gen, missing = mod.build_A(ledger, body, prune=False)
A_cur = io.open(os.path.join(ROOT, "장v2", "부록A.md"), encoding="utf-8").read()


def rows(text):
    out = {}
    hdr = None
    for ln in text.split("\n"):
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        if hdr is None and "기록의 글자" in ln:
            hdr = cells
            continue
        if set(ln.replace("|", "").strip()) <= set("-: "):
            continue
        if hdr is None:
            continue
        key = cells[0]
        out.setdefault(key, []).append(cells)
    return hdr, out


h1, g = rows(A_gen)
h2, c = rows(A_cur)
print("생성 머리:", h1)
print("현행 머리:", h2)
print("생성 행", sum(len(v) for v in g.values()), "현행 행", sum(len(v) for v in c.values()))
only_g = [k for k in g if k not in c]
only_c = [k for k in c if k not in g]
print("생성에만 있는 키", len(only_g), only_g[:20])
print("현행에만 있는 키", len(only_c), only_c[:20])
# 기록의 글자 열 비교
try:
    ig = h1.index("기록의 글자"); ic = h2.index("기록의 글자")
except Exception as e:
    print("열 찾기 실패", e); raise SystemExit
diff = []
for k in g:
    if k in c:
        for rg, rc in zip(g[k], c[k]):
            if len(rg) > ig and len(rc) > ic and rg[ig] != rc[ic]:
                diff.append((k, rg[ig], rc[ic]))
print("기록의 글자 열이 다른 행", len(diff))
for k, a, b in diff[:80]:
    print(" -", k[:40], "| 생성:", a[:90], "| 현행:", b[:90])
# 다른 열(뜻·절)의 차이 수만
odiff = 0
for k in g:
    if k in c:
        for rg, rc in zip(g[k], c[k]):
            for j, (x, y) in enumerate(zip(rg, rc)):
                if j != ig and x != y:
                    odiff += 1
print("기록의 글자 밖 칸 차이 수", odiff)
