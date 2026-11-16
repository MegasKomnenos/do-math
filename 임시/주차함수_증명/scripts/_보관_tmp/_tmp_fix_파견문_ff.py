# -*- coding: utf-8 -*-
"""수학검사 파견문에서 heredoc 처리로 생긴 폼피드 글자(\\f → \x0c)를 \\frac으로 되돌린다. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "파견", "수학검사_파견문.md")
s = io.open(P, encoding="utf-8").read()
n = s.count("\x0crac")
s = s.replace("\x0crac", "\\frac")
bad = sum(1 for ch in s if ord(ch) < 32 and ch not in "\n\t")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("고침", n, "남은 제어 문자", bad)
