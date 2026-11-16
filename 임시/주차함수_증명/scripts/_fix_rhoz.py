# -*- coding: utf-8 -*-
"""7B의 글자 치환(\\varrho→\\rho)이 만든 붙은 명령 `\\rhoz` → `\\rho z`."""
import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in glob.glob(os.path.join(ROOT, "장v2", "*.md")):
    s = io.open(p, encoding="utf-8").read()
    n = s.count("\\rhoz")
    if n:
        s = s.replace("\\rhoz", "\\rho z")
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
        print(os.path.basename(p), "고침", n)
print("done")
