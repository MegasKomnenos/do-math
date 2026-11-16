# -*- coding: utf-8 -*-
"""21:09 장부 항목(의존지도 재생성)을 heredoc으로 넣을 때 떨어진 백슬래시를 되살린다. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOOD = "수식은 `\\Theta`·`k-1`·`\\mathrm{LRP}_2`·`(\\star)`로 일관"
BADS = ["수식은 `Theta`·`k-1`·`mathrm{LRP}_2`·`(star)`로 일관"]
for rel in ("작업_장부.md", os.path.join("대조v2", "수학검사2", "_장부_항목_의존지도재생성.txt")):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    if GOOD in s:
        print(rel, "이미 옳음")
        continue
    n = 0
    for b in BADS:
        if b in s:
            s = s.replace(b, GOOD)
            n += 1
    if n:
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
        print(rel, "고침", n)
    else:
        i = s.find("로 일관")
        print(rel, "앵커 없음; 주변:", repr(s[max(0, i - 80):i + 10]))
