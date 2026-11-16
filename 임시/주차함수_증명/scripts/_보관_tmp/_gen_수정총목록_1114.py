# -*- coding: utf-8 -*-
"""2026-11-14 13:3x–15:5x 구간(외부 지적 D.21, 둘째 수학 검사 열넷, 결정 95 용어 통일)의 수정 전부를 한 파일로 모은다.
원문 발췌만 하고 새로 쓰지 않는다: (1) 장부 항목 원문, (2) 보고 열넷의 「2. 오류 목록」, (3) 보고_용어의 2·3·6.1·6.2절."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "대조v2", "수학검사2", "수정_총목록_1114.md")
TAGS = ["1", "2", "3", "4", "5A", "5B", "6", "7A", "7B", "8", "9", "10", "11", "ABC"]

def section(text, head_start, next_level="## "):
    lines = text.split("\n")
    out, on = [], False
    for l in lines:
        if l.startswith(head_start):
            on = True; out.append(l); continue
        if on and l.startswith(next_level):
            break
        if on:
            out.append(l)
    return "\n".join(out).rstrip()

parts = []
parts.append("# 2026-11-14 수정 총목록(외부 지적 D.21 · 둘째 수학 검사 열넷 · 결정 95 용어 통일)\n")
parts.append("이 파일은 13:3x–15:5x 구간에 원고 조각·부록·장부·설계 파일에 가해진 수정을 한 곳에 모은 **원문 발췌**다. 새로 쓴 문장은 없다. 출처는 셋: 작업 장부의 해당 항목, 둘째 수학 검사 보고 열넷의 「2. 오류 목록」, 용어 통일 보고의 치환 목록. 「확인 요」(사용자 판정 잔여)는 각 보고의 4절과 장부 15:4x–15:5x 항목 끝을 본다.\n")

# (1) 장부 항목
ledger = io.open(os.path.join(ROOT, "작업_장부.md"), encoding="utf-8").read()
items = [l for l in ledger.split("\n") if re.match(r"- 2026-11-14 1[345]:[0-9x]", l)]
parts.append("## 1. 작업 장부 항목 원문(13:3x–15:5x)\n")
parts.append("\n\n".join(items) + "\n")

# (2) 보고 열넷의 오류 목록
parts.append("## 2. 둘째 수학 검사 보고 열넷의 「2. 오류 목록」\n")
for t in TAGS:
    p = os.path.join(ROOT, "대조v2", "수학검사2", "보고_%s.md" % t)
    txt = io.open(p, encoding="utf-8").read()
    sec = section(txt, "## 2.")
    sec = re.sub(r"^## 2\.", "### 보고_%s —" % t, sec, count=1)
    parts.append(sec + "\n")

# (3) 용어 보고
p = os.path.join(ROOT, "대조v2", "수학검사2", "보고_용어.md")
txt = io.open(p, encoding="utf-8").read()
parts.append("## 3. 용어 통일 보고(결정 95)의 치환 목록\n")
for head in ("## 2. 규칙별 치환 목록", "## 3. 정의 문장을 손본 자리"):
    sec = section(txt, head)
    sec = re.sub(r"^## ", "### 보고_용어 — ", sec, count=1)
    sec = re.sub(r"(?m)^### (\d\.\d)", r"#### \1", sec)
    parts.append(sec + "\n")
for head in ("### 6.1", "### 6.2"):
    sec = section(txt, head, next_level="### ")
    sec = re.sub(r"^### ", "### 보고_용어 — ", sec, count=1)
    parts.append(sec + "\n")

body = "\n".join(parts)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(body)
print(OUT, len(body.split("\n")), "행", len(body.encode("utf-8")), "바이트; 장부 항목", len(items))
