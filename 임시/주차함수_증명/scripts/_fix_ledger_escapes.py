# -*- coding: utf-8 -*-
"""작업_장부.md에서 히어독 작성 때 제어 문자로 바뀐 \\v·\\f를 복원한다."""
import io
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
s = io.open(P, encoding="utf-8", newline="").read()
for i, ln in enumerate(s.split("\n"), 1):
    if "\x0b" in ln or "\x0c" in ln:
        j = min([k for k in (ln.find("\x0b"), ln.find("\x0c")) if k >= 0])
        print(i, repr(ln[max(0, j - 30): j + 20]))
s2 = s.replace("\x0b", "\\v").replace("\x0c", "\\f")
io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
bad = sorted({c for c in s2 if ord(c) < 32 and c not in "\n\t"})
print("remaining:", bad)
