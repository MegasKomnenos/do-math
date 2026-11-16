# -*- coding: utf-8 -*-
"""결정 100: 부록 C(손 편집본)에 장부 3절의 새 낱말 행을 생성기 순서대로 끼워 넣고, 글자 표의 PAIR_n 행을 장부 7절과 맞추며,
장부 1.3절 412행의 「젊은 경로의 걸음 수 상한」을 「젊은 사슬의 걸음 수 상계」로 고친다. 멱등. 부록_v2.py는 돌리지 않는다(C는 손 편집본).
사용: python -I scripts/수학검사2/부록C_동기화_1114.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
gen_mod = importlib.import_module("부록_v2")
DRY = "--dry" in sys.argv

ledger = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read()
gen = gen_mod.build_C(ledger)
P_C = os.path.join(ROOT, "장v2", "부록C.md")
cur = io.open(P_C, encoding="utf-8").read()


def table_rows(text, head):
    i = text.find(head)
    j = text.find("\n### ", i + 5)
    j = j if j > 0 else len(text)
    return [l for l in text[i:j].split("\n") if l.startswith("| ") and not l.startswith("| 이 글의 용어") and not l.startswith("| 이 글의 글자")]


def key(line):
    return line.split("|")[1].strip()


# ---- 1. 낱말 표: 빠진 행을 생성기 순서대로 끼워 넣기 ----
g = table_rows(gen, "### 낱말")
lines = cur.split("\n")
c_rows = table_rows(cur, "### 낱말")
c_keys = [key(l) for l in c_rows]
inserted = []
for idx, row in enumerate(g):
    if key(row) in c_keys:
        continue
    anchor = None
    for p in range(idx - 1, -1, -1):
        if key(g[p]) in c_keys:
            anchor = key(g[p])
            break
    if anchor is None:
        print("[경고] 앵커 없음:", row[:60])
        continue
    # 현재 파일에서 앵커 행 위치(낱말 표 안) 찾고, 이미 끼운 같은 앵커의 행 뒤로
    pos = None
    for n, l in enumerate(lines):
        if l.startswith("| ") and key(l) == anchor:
            pos = n
            break
    if pos is None:
        print("[경고] 앵커 행을 파일에서 못 찾음:", anchor)
        continue
    q = pos + 1
    while q < len(lines) and lines[q].startswith("| ") and key(lines[q]) in [key(r) for r in inserted] and True:
        q += 1
    lines.insert(q, row)
    inserted.append(row)
    c_keys.append(key(row))
    print("끼움:", key(row), "← 앵커", anchor)
cur2 = "\n".join(lines)

# ---- 2. 글자 표: PAIR_n 행을 생성본과 맞춤 ----
g7 = table_rows(gen, "### 기록의 글자")
c7 = table_rows(cur2, "### 기록의 글자")
gmap = {key(l): l for l in g7}
for l in c7:
    k = key(l)
    if k.startswith("$\\mathrm{PAIR}_n$") and k in gmap and gmap[k] != l:
        cur2 = cur2.replace(l, gmap[k])
        print("글자 표 동기화:", k[:40])

if cur2 != cur:
    if not DRY:
        io.open(P_C, "w", encoding="utf-8", newline="\n").write(cur2)
    print("부록C.md", "쓰기 생략(dry)" if DRY else "씀", "행 수", len(cur2.split("\n")))
else:
    print("부록C.md 변경 없음")

# ---- 3. 장부 412행 글귀 ----
P_L = os.path.join(ROOT, "장부_v2.md")
old = "$\\mathfrak n_q$(젊은 경로의 걸음 수 상한)"
new = "$\\mathfrak n_q$(젊은 사슬의 걸음 수 상계)"
s = ledger
if old in s:
    if not DRY:
        io.open(P_L, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("장부 1.3절 글귀 고침", "(dry)" if DRY else "")
elif new in s:
    print("장부 글귀 이미 옳음")
else:
    print("[경고] 장부 글귀 앵커 없음")
