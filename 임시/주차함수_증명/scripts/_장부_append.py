# -*- coding: utf-8 -*-
"""장부 「기록」 끝(「## 재개 기록」 앞)에 텍스트 파일의 내용을 항목으로 붙인다. 첫 줄의 굵은 제목이 이미 있으면 붙이지 않는다(멱등).
사용: python -I scripts/_장부_append.py <항목 텍스트 파일>"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(ROOT, "작업_장부.md")
src = sys.argv[1]
entry = io.open(src, encoding="utf-8").read().strip("\n")
m = re.search(r"\*\*(.+?)\*\*", entry)
key = m.group(1) if m else entry[:60]
t = io.open(L, encoding="utf-8").read()
if key in t:
    print("이미 있음:", key[:40]); sys.exit(0)
mark = "\n## 재개 기록"
i = t.find(mark)
t = t[:i].rstrip("\n") + "\n\n" + entry + "\n" + t[i:]
io.open(L, "w", encoding="utf-8", newline="\n").write(t)
print("추가:", key[:60])
