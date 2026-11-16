# -*- coding: utf-8 -*-
"""M11: 11.3 입력 표의 공유/고유 분류를 인용 폐포로 검사하고, 표가 빠뜨린 인용 자리의 문맥을 뽑는다."""
import re, glob, os, json, sys
from collections import deque, defaultdict
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()
HEAD0 = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}\s*(.*?)\.\*\*(.*)$")
index = {}; blocks = {}; order = []
for f in sorted(glob.glob(os.path.join(ROOT, "장*.md"))):
    ch = os.path.basename(f)[1:-3]
    lines = rd(f).splitlines(); sec = ""; cur = None; buf = []; cursec = ""; curline = 0
    def flush():
        if cur is not None: blocks[cur] = dict(text="\n".join(buf), sec=cursec, ch=ch, line=curline, file=os.path.basename(f))
    for i, ln in enumerate(lines, 1):
        ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
        if ms: flush(); cur = None; buf = []; sec = ms.group(2); continue
        m = HEAD0.match(ln)
        if m:
            flush(); typ, chp, lab, mid, rest = m.groups()
            mt = re.search(r"\[([^\[\]]*)\]\s*$", mid); tag = mt.group(1) if mt else ""
            key = f"{chp}:{lab}"; index[key] = dict(type=typ, tag=tag, file=os.path.basename(f), line=i, sec=sec)
            order.append(key); cur = key; cursec = sec; curline = i; buf = [ln]
        elif cur is not None: buf.append(ln)
    flush()
def cites(key):
    return [l for l in re.findall(r"\{\{(\w+:[^}]+)\}\}", blocks[key]["text"]) if l != key and not l.startswith("D:")]
def closure(start):
    seen = set(); st = [start]; parent = {start: None}
    while st:
        k = st.pop()
        if k in seen or k not in blocks: continue
        seen.add(k)
        for c in cites(k):
            if c not in seen and c not in parent: parent[c] = k; st.append(c)
    return seen
def path(start, goal):
    # BFS 최단 경로
    prev = {start: None}; dq = deque([start])
    while dq:
        k = dq.popleft()
        if k == goal: break
        if k not in blocks: continue
        for c in cites(k):
            if c not in prev: prev[c] = k; dq.append(c)
    if goal not in prev: return None
    p = []; k = goal
    while k is not None: p.append(k); k = prev[k]
    return p[::-1]
def ctx(key, lab, width=160):
    t = blocks[key]["text"]; out = []
    for m in re.finditer(r"\{\{" + re.escape(lab) + r"\}\}", t):
        s = max(0, m.start() - width); e = min(len(t), m.end() + width)
        out.append("…" + t[s:e].replace("\n", " ") + "…")
    return out

c1 = closure("9:old-7-46"); c2 = closure("10:old-8-37")
print("##### (a) 첫째 증명 고유라 적힌 앞 장 진술에 둘째 증명 폐포가 닿는 최단 경로")
for lab in ["7:old-6-22", "7:old-6-21", "2:old-2-34", "2:b-top", "2:old-2-41", "2:old-2-38", "2:old-2-35", "2:old-2-36", "2:old-2-39", "6:increment-bounds", "6:D-bound", "9:old-7-16", "9:H-star-plus", "8:old-6-29", "9:pair-one-variable", "9:old-7-26"]:
    p = path("10:old-8-37", lab)
    print(f"  {lab}: ", " -> ".join(p) if p else "닿지 않음")
print("\n##### (a') 둘째 증명 고유라 적힌 진술에 첫째 폐포가 닿는지")
for lab in ["10:old-8-23", "10:check-na", "10:check-ga", "10:old-8-36", "2:old-2-46", "2:old-2-44", "6:old-8-13", "6:same-kernel", "6:stay-margin-identity", "6:lemma-omega", "6:lemma-phi", "6:old-8-12", "6:DD-lower-bound", "7:old-6-14"]:
    p = path("9:old-7-46", lab)
    print(f"  {lab}: ", " -> ".join(p) if p else "닿지 않음")

print("\n##### (b) 표가 적지 않은 인용 자리의 문맥")
pairs = [("4:old-4-5", "9:head-sum-1"), ("5:old-5-18", "9:head-sum-1"), ("4:old-4-5", "10:old-8-9"), ("5:old-5-1", "10:old-8-9"), ("5:witness-position-bound", "10:old-8-9"),
         ("6:old-6-19", "9:old-7-23"), ("6:old-7-13", "9:old-7-12"), ("6:old-7-13", "10:old-8-23"),
         ("7:threshold-unit-ratio", "10:old-8-3"), ("7:threshold-unit-ratio", "10:old-8-14"), ("8:old-6-23", "9:old-7-11"),
         ("8:old-6-33", "9:old-7-12"), ("8:old-6-33", "9:old-7-18"), ("8:old-6-33", "9:old-7-27"), ("8:old-6-28", "9:old-7-35"), ("8:old-6-28", "9:old-7-37"),
         ("6:old-7-24", "9:old-7-31"), ("6:old-7-21", "9:old-7-18"), ("6:old-7-20", "10:old-8-10"), ("6:old-7-20", "10:old-8-3"),
         ("2:old-2-10", "9:centroid-stop"), ("2:old-2-26", "10:old-8-2"), ("2:old-2-26", "10:old-8-16"), ("2:old-2-37", "10:old-8-19"), ("2:old-2-45", "10:old-8-19"), ("2:old-2-31", "10:old-8-3"),
         ("6:increment-bounds", "9:old-7-23"), ("6:D-bound", "9:old-7-22"), ("8:old-6-29", "9:old-7-18"), ("8:old-6-29", "9:old-7-27"), ("9:H-star-plus", "9:old-7-22"),
         ("6:old-8-13", "10:old-8-25"), ("6:old-8-12", "10:old-8-25"), ("6:DD-lower-bound", "10:old-8-8"), ("6:DD-lower-bound", "10:old-8-17"),
         ("7:old-6-22", "10:old-8-37"), ("7:old-6-21", "10:old-8-9"), ("7:old-6-21", "10:old-8-1"), ("7:old-6-14", "10:old-8-1"), ("7:old-6-14", "10:old-8-2"), ("7:old-6-15", "10:old-8-1"),
         ("5:old-5-11", "10:old-8-37"), ("7:src-plus", "7:old-6-20"), ("7:threshold-unit-ratio", "7:old-6-21"), ("2:old-2-40", "8:old-6-33"), ("7:old-6-14", "7:old-6-15"), ("7:old-6-14", "7:old-6-21")]
for lab, key in pairs:
    print(f"\n[{key} ← {lab}]  ({blocks[key]['file']}:{blocks[key]['line']}, 절 {blocks[key]['sec']})")
    cs = ctx(key, lab)
    if not cs: print("   (인용 없음)")
    for c in cs: print("  ", c)

print("\n##### (c) 폐포 안의 계산 진술(표지에 '계산')과 11.3 표의 계산 진술 열")
t11 = rd(os.path.join(ROOT, "장11.md"))
sec113 = t11.split("### 11.3")[1].split("### 11.4")[0]
tables = sec113.split("**공유 입력.**")[1]
shared_tbl, rest = tables.split("**첫째 증명의 고유 입력.**")
first_tbl, second_tbl = rest.split("**둘째 증명의 고유 입력.**")
def col2(tbl):
    s = set()
    for ln in tbl.splitlines():
        if ln.startswith("| ") and not ln.startswith("| 입력") and not ln.startswith("|---"):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            s |= set(re.findall(r"\{\{(\w+:[^}]+)\}\}", cells[1]))
    return s
S, F1, F2 = col2(shared_tbl), col2(first_tbl), col2(second_tbl)
comp = {k for k in index if "계산" in (index[k]["tag"] or "")}
for k in sorted(comp):
    in1, in2 = k in c1, k in c2
    where = "공유" if (in1 and in2) else "첫째만" if in1 else "둘째만" if in2 else "둘 다 아님"
    listed = "공유표" if k in S else "첫째표" if k in F1 else "둘째표" if k in F2 else "표에 없음"
    flag = ""
    if where == "공유" and listed != "공유표": flag = "  <== 분류 차이"
    if where == "첫째만" and listed != "첫째표": flag = "  <== 분류 차이"
    if where == "둘째만" and listed != "둘째표": flag = "  <== 분류 차이"
    if where == "둘 다 아님" and listed != "표에 없음": flag = "  <== 폐포 밖인데 표에 있음"
    print(f"  {k:32s} 폐포:{where:8s} 표:{listed:8s} 표지:{index[k]['tag'][:70]}{flag}")

print("\n##### (d) 표지에 binary64 / 평가 등급을 단 진술")
for k in order:
    tg = index[k]["tag"] or ""
    if "binary64" in tg or "평가" in tg: print("  ", k, "|", tg)

print("\n##### (e) 6:insertion, 6:log-derivative, 6:trapezoid, 6:cor-L 를 인용하는 블록")
for lab in ["6:insertion", "6:log-derivative", "6:trapezoid", "6:cor-L", "6:pair-rearrange", "6:diag-first-layer"]:
    print("  ", lab, "←", [k for k in order if lab in cites(k)])
print("\n   6:cor-L 블록 본문 인용:", cites("6:cor-L"))
print("   5:old-5-18 블록 인용:", cites("5:old-5-18"))
print("   7:old-6-22 블록 인용:", cites("7:old-6-22"))
print("   10:old-8-37 블록 인용:", cites("10:old-8-37"))
print("   9:old-7-46 블록 인용:", cites("9:old-7-46"))
