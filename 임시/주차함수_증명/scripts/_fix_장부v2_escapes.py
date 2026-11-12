# -*- coding: utf-8 -*-
"""장부_v2.md에서 히어독 작성 때 제어 문자로 깨진 LaTeX 명령을 복원한다."""
import io
P = r"C:\math\임시\주차함수_증명\장부_v2.md"
s = io.open(P, encoding="utf-8", newline="").read()
fixes = [
    ("\tau_", "\\tau_"),
    ("\rho_", "\\rho_"),
    ("\rceil", "\\rceil"),
    ("\beta_", "\\beta_"),
]
for bad, good in fixes:
    n = s.count(bad)
    s = s.replace(bad, good)
    print(repr(bad), "->", good, n)
# 줄 끝 CR이 남아 있으면 제거(원래 LF 파일)
s = s.replace("\r\n", "\n")
bad_chars = sorted({c for c in s if ord(c) < 32 and c not in "\n"})
print("remaining control chars:", [hex(ord(c)) for c in bad_chars])
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
