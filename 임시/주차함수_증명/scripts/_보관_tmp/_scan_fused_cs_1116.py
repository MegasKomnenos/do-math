# -*- coding: utf-8 -*-
"""수식 안에서 제어열이 뒤따르는 대문자와 붙어 깨진 자리(예: \\geR) 전수 탐색. 2026-11-16."""
import io, re, glob
pat = re.compile(r"\\(ge|le|ne|lt|gt|in|to|mid|cdot|times|pm|ll|gg|sim|succ|prec|sub|sup|cup|cap|land|lor|not)([A-Z])")
hits = 0
for p in sorted(glob.glob(r"C:\math\임시\주차함수_증명\장v2\*.md")):
    for i, ln in enumerate(io.open(p, encoding="utf-8"), 1):
        for m in pat.finditer(ln):
            hits += 1
            print(p.split("\\")[-1], i, ln[max(0, m.start() - 40):m.end() + 30].strip())
print("hits", hits)
