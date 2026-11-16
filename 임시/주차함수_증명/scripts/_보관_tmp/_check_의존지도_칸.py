# -*- coding: utf-8 -*-
"""재생성한 의존지도 1절 표의 칸 수(10)와 1.1 표의 칸 수(3)를 확인한다. 읽기만 한다."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = io.open(os.path.join(ROOT, "의존지도_v2.md"), encoding="utf-8").read()
SPLIT = re.compile(r"(?<!\\)\|")
i = s.find("\n## 1. ")
j = s.find("\n### 1.1")
rows = [l for l in s[i:j].split("\n") if l.startswith("| `{{")]
bad = [l[:70] for l in rows if len(SPLIT.split(l.strip()[1:-1])) != 10]
print("1절 행", len(rows), "칸 수 이상", len(bad), bad[:3])
k = s.find("\n### 1.1")
m = s.find("\n## 2.")
r2 = [l for l in s[k:m].split("\n") if l.startswith("| ") and not l.startswith("| 라벨")]
bad2 = [l[:70] for l in r2 if len(SPLIT.split(l.strip()[1:-1])) != 3]
print("1.1 행", len(r2), "칸 수 이상", len(bad2), bad2[:3])
print("백슬래시 든 칸 예:", [l[:50] for l in rows if "\\|" in l][:2])
