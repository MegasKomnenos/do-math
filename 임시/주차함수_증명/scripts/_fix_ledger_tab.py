# -*- coding: utf-8 -*-
"""작업_장부.md에 남은 리터럴 탭(깨진 `\\tau` 예시)을 `\\tau` 글자로 되돌린다."""
import io
P = r"C:\math\임시\주차함수_증명\작업_장부.md"
s = io.open(P, encoding="utf-8", newline="").read()
for i, ln in enumerate(s.split("\n"), 1):
    if "\t" in ln:
        j = ln.find("\t")
        print(i, repr(ln[max(0, j - 40): j + 20]))
s2 = s.replace("`\tau`", "`\\tau`").replace("\t", " ")
io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
bad = sorted({c for c in s2 if ord(c) < 32 and c not in "\n"})
print("remaining:", bad)
