# -*- coding: utf-8 -*-
"""D.32 블록의 부풀림 인자 토큰·알고리즘 줄의 ulp 문맥·polar-W 머리를 출력한다(읽기 전용)."""
import collections
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = io.open(os.path.join(ROOT, "장v2", "부록D_장7A.md"), encoding="utf-8").read()
i = s.find("### D.{{D:polar-blocks-488}}"); j = s.find("\n### D.", i + 1); blk = s[i:j]
pat = re.compile(r"\(1[+-]10\^\{-1?\d\}\)|\(1\\pm10\^\{-1?\d\}\)")
toks = collections.Counter(m.group() for m in pat.finditer(blk))
print("인자 토큰:", dict(toks))
for m in list(re.finditer(r".{0,80}\(1[+-]10\^\{-1?\d\}\).{0,50}", blk))[:10]:
    print("  …", m.group().replace("\n", " "))
g = re.search(r"\*\*알고리즘\.\*\* ([^\n]*)", blk).group(1)
k = g.find("ulp")
print("[알고리즘 ulp 문맥]", g[max(0, k - 500):k + 260])
h = io.open(os.path.join(ROOT, "장v2", "장7A.md"), encoding="utf-8").read()
for line in h.split("\n"):
    if line.startswith("**명제 {{7:polar-W}}"):
        print("[머리]", line[:line.find(".**") + 3])
        break
