# K12: compare the 11.2 table rows (columns 5,6) with the D items' 독립 재계산 lines for the 23 items of K12
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r"C:/math/임시/주차함수_증명/장v2/"
items = {}
for f in ("부록D_장2.md", "부록D_장3.md", "부록D_장4.md", "부록D_장5A.md", "부록D_장5B.md", "부록D_장6.md"):
    txt = open(base+f, encoding="utf-8").read()
    for m in re.finditer(r"### D\.\{\{D:([^}]+)\}\}(.*?)(?=\n### D\.|\Z)", txt, re.S):
        body = m.group(2)
        r = re.search(r"\*\*독립 재계산\.\*\*\s*(.*?)\n", body)
        items[m.group(1)] = (f, r.group(1).strip() if r else None)
t11 = open(base+"장11.md", encoding="utf-8").read()
rows = {}
for line in t11.splitlines():
    m = re.match(r"\| 부록 D\.\{\{D:([^}]+)\}\} \|(.*)\|\s*$", line)
    if m:
        cols = [c.strip() for c in m.group(2).split(" | ")]
        rows[m.group(1)] = cols
for key, (f, line) in items.items():
    if key not in rows:
        print("NO 11.2 ROW:", key); continue
    cols = rows[key]
    if len(cols) < 5:
        print("ROW TOO SHORT:", key, len(cols)); continue
    brk, rest = cols[3], cols[4]
    m = re.match(r"(〔[^〕]*〕)\s*(.*)", line)
    dbrk, drest = m.group(1), m.group(2)
    ok1 = (brk == dbrk)
    norm = lambda s: s.replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호")
    ok2 = (norm(drest) == rest)
    print(f"{key:32s} {f:14s} bracket {'OK' if ok1 else 'DIFF'}  text {'OK' if ok2 else 'DIFF'}")
    if not ok1: print("   D :", dbrk); print("   11:", brk)
    if not ok2:
        a, b = norm(drest), rest
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
        print("   first diff at", i); print("   D :", a[max(0, i-60):i+100]); print("   11:", b[max(0, i-60):i+100])
