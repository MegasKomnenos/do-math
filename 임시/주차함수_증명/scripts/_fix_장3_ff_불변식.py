# -*- coding: utf-8 -*-
"""장3.md의 제어 문자 U+000C(히어독의 \\f 깨짐)를 \\frac으로 복구하고, 불변식 검사기의 오탐 둘을 고친다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P = os.path.join(ROOT, "장v2", "장3.md")
s = io.open(P, encoding="utf-8").read()
n = s.count("\x0c")
s = s.replace("\x0c" + "rac", "\\" + "frac")
assert "\x0c" not in s, "남은 제어 문자"
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("장3.md form feed fixed:", n, "| \\frac 수:", s.count("\\frac"))

Q = os.path.join(ROOT, "scripts", "불변식_v2.py")
t = io.open(Q, encoding="utf-8").read()
old = (
    "            for w in STATUS_BAD:\n"
    "                if w in status_part:\n"
    "                    failures.append(f\"{i}: 이 글에 쓰이지 않는 지위 「{w}」 [{bracket}]\")\n"
    "            extra = status_part\n"
    "            for w in STATUS_OK + MODIFIERS:\n"
    "                extra = extra.replace(w, \"\")\n"
)
new = (
    "            extra = status_part\n"
    "            for w in STATUS_OK + MODIFIERS:\n"
    "                extra = extra.replace(w, \"\")\n"
    "            for w in STATUS_BAD:\n"
    "                if w in extra:\n"
    "                    failures.append(f\"{i}: 이 글에 쓰이지 않는 지위 「{w}」 [{bracket}]\")\n"
)
if old in t:
    t = t.replace(old, new)
    print("STATUS_BAD check reordered")
else:
    print("STATUS_BAD block already patched or not found")
t2 = t.replace("|항등식|부등식|대응|극한 진술|", "|항등식|부등식|대응|극한 진술|진술|")
if t2 != t:
    t = t2
    print("낯선 낱말: 진술 허용")
io.open(Q, "w", encoding="utf-8", newline="\n").write(t)
