# 검토전체8 N11: 11.2절 표와 부록 D 항목을 대조한다.
import re, glob, os, difflib
root = r"C:\math\임시\주차함수_증명\장v2"
# 부록 D 항목 파싱
items = {}
for f in sorted(glob.glob(os.path.join(root, "부록D_*.md"))):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"^(?=### D\.\{\{D:)", txt, flags=re.M)
    for p in parts:
        m = re.match(r"### D\.\{\{D:([^}]+)\}\}\s*(.*)", p)
        if not m: continue
        key = m.group(1)
        head = m.group(2)
        def line(name):
            mm = re.search(r"^\*\*" + name + r"\.\*\*\s*(.*)$", p, flags=re.M)
            return mm.group(1).strip() if mm else None
        items[key] = dict(file=os.path.basename(f), head=head, grade=line("산술 등급"), recalc=line("독립 재계산"), stmt=line("확인하는 진술"))
# 11.2 표 파싱
ch11 = open(os.path.join(root, "장11.md"), encoding="utf-8").read().split("\n")
rows = []
for ln in ch11:
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        rows.append(cells)
print("표 행 수", len(rows), "부록 D 항목 수", len(items))
seen = set()
for cells in rows:
    key = re.match(r"부록 D\.\{\{D:([^}]+)\}\}", cells[0]).group(1)
    seen.add(key)
    it = items.get(key)
    if not it:
        print("!! 표에만 있음:", key); continue
    # 확인하는 진술: 머리 괄호의 라벨과 비교
    head_labels = re.findall(r"(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}", it["head"])
    tbl_labels = re.findall(r"(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}", cells[1])
    if head_labels != tbl_labels:
        print(f"[{key}] 진술 다름: 표={tbl_labels} D머리={head_labels}")
    # 산술 등급
    g = it["grade"]
    print(f"[{key}] 표 등급={cells[2]!r} | D 등급 줄={g[:160]!r}")
    # 재계산 괄호
    rc = it["recalc"] or ""
    mb = re.match(r"〔([^〕]*)〕\s*(.*)", rc, flags=re.S)
    if not mb:
        print(f"[{key}] !! D 독립 재계산 줄에 꺾쇠 없음: {rc[:100]}")
        continue
    if mb.group(1).strip() != cells[4].strip("〔〕").strip():
        print(f"[{key}] 꺾쇠 다름:\n   표: {cells[4]}\n   D : 〔{mb.group(1)}〕")
    body = mb.group(2).strip()
    tb = cells[5].strip()
    if body != tb:
        sm = difflib.SequenceMatcher(None, body, tb)
        print(f"[{key}] 서술 다름 (ratio {sm.ratio():.3f}):")
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                print(f"     {tag}: D='{body[i1:i2][:200]}' | 표='{tb[j1:j2][:200]}'")
for k in items:
    if k not in seen:
        print("!! 부록 D에만 있음:", k)
