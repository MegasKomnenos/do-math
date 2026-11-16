# -*- coding: utf-8 -*-
import io
ROOT = r"C:\math\임시\주차함수_증명"
s = io.open(ROOT + r"\장v2\장5B.md", encoding="utf-8").read()
for key in ("mathfrak C_{\\mathrm I}", "Q_0"):
    i = s.find(key); n = 0
    while i >= 0 and n < 4:
        line = s.count("\n", 0, i) + 1
        print(f"장5B {line}행 [{key}]:", s[max(0, i - 300):i + 420].replace("\n", "⏎"))
        print("----")
        i = s.find(key, i + 1); n += 1
d = io.open(ROOT + r"\장v2\부록D_장5B.md", encoding="utf-8").read().split("\n")
print("==== 부록D_장5B 137–152행")
for k in range(136, 152):
    if d[k].strip():
        print(f"[{k+1}]", d[k][:1600])
        print()
