# -*- coding: utf-8 -*-
"""README의 한 문단에서 `\\natural`의 `\\n`이 줄바꿈으로 읽혀 `^` 뒤에 줄이 바뀌고 `atural`이 남은 것을 되돌린다. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "원고_자료", "README.md")
s = io.open(P, encoding="utf-8").read()
old = "$\\mathrm{DDL}^\natural(k)$"  # 실제 줄바꿈 문자가 든 꼴
new = "$\\mathrm{DDL}^\\natural(k)$"
n = s.count(old)
if n:
    s = s.replace(old, new)
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("고침", n, "/ 남은 'atural' 줄머리:", sum(1 for l in s.split("\n") if l.startswith("atural")))
