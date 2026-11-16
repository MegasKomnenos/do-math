# -*- coding: utf-8 -*-
"""E14: 장 파일의 진술 머리를 뽑아 TSV로 적는다. 열: 파일, 행, 절, 종류, 장번호, 라벨, 괄호(이름; 기록), 지위대괄호"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|관찰|주장|추측)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
rows = []
for f in files:
    path = f"{ROOT}/장v2/{f}.md"
    sec = ""
    with open(path, encoding='utf-8') as fh:
        for ln, line in enumerate(fh, 1):
            m = re.match(r'^(#+)\s*(\d+(?:\.\d+)*)[\s.]', line)
            if m:
                sec = m.group(2)
            m = head_re.match(line)
            if m:
                kind, ch, lab, rest = m.groups()
                rest = rest.strip().rstrip('.').strip()
                paren = ""; status = ""
                if rest.startswith('('):
                    depth = 0
                    for i,c in enumerate(rest):
                        if c == '(': depth += 1
                        elif c == ')':
                            depth -= 1
                            if depth == 0:
                                paren = rest[1:i]; status = rest[i+1:].strip(); break
                else:
                    status = rest
                rows.append((f, ln, sec, kind, ch, lab, paren, status))
out = f"{ROOT}/scripts/수학검사2/_E14_heads.tsv"
with open(out, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write("\t".join(str(x) for x in r) + "\n")
print(len(rows), "heads ->", out)
# 라벨 중복 검사
from collections import Counter
c = Counter((r[4], r[5]) for r in rows)
for k,v in c.items():
    if v>1: print("DUP", k, v)
# 장 번호와 파일 불일치
for r in rows:
    fch = re.sub(r'[AB]$','',r[0][1:])
    if fch != r[4]: print("CHAPTER MISMATCH", r[:6])
