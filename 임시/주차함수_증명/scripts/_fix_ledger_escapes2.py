# -*- coding: utf-8 -*-
"""작업_장부.md의 남은 제어 문자(\\b, \\r)를 복원한다."""
import io, re
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
s = io.open(P, encoding="utf-8", newline="").read()
for i, ln in enumerate(s.split("\n"), 1):
    for ch in ("\x08", "\r"):
        if ch in ln:
            j = ln.find(ch)
            print(i, repr(ch), repr(ln[max(0, j - 30): j + 20]))
s2 = s.replace("\x08", "\\b")
s2 = re.sub(r"\r(?!\n)", "\\\\r", s2)
io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
bad = sorted({c for c in s2 if ord(c) < 32 and c not in "\n\t"})
print("remaining:", bad)
