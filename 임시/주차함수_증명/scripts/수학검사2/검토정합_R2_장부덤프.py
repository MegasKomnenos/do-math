# -*- coding: utf-8 -*-
"""R2: 장부 1.3·3·7절 표를 열 단위로 쪼개 읽기 좋게 덤프한다(읽기 전용)."""
import io, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
L = io.open(ROOT + r"\장부_v2.md", encoding="utf-8").read().split("\n")
def rows(a, b):
    out = []
    for i in range(a-1, b):
        ln = L[i]
        if ln.startswith("|") and not ln.startswith("|---"):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            out.append((i+1, cells))
    return out
mode = sys.argv[1]
buf = io.StringIO()
if mode == "13":
    for n, c in rows(341, 416):
        buf.write(f"[{n}] 글자: {c[0]}\n    뜻: {c[1] if len(c)>1 else ''}\n    자리: {c[2] if len(c)>2 else ''}\n")
elif mode == "3":
    for n, c in rows(503, 706):
        buf.write(f"[{n}] " + " | ".join(c) + "\n")
elif mode == "7":
    for n, c in rows(1200, 1412):
        buf.write(f"[{n}] " + " | ".join(c) + "\n")
elif mode == "11":
    for n, c in rows(20, 43):
        buf.write(f"[{n}] " + " | ".join(c) + "\n")
sys.stdout.buffer.write(buf.getvalue().encode("utf-8"))
