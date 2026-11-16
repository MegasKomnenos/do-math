# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|관찰|주의|가정|표기)\s+\{\{(\d+:[^}]+)\}\}")
blocks = {}   # label -> (file, startline, text)
kinds = {}
sections = {} # "7.2" -> text
for f in sorted(glob.glob(R+"장v2/장*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    cur = None; sec = None
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            cur = m.group(2); kinds[cur] = m.group(1); blocks[cur] = [f.split("/")[-1], i, ""]
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l)
        if ms:
            sec = ms.group(1); sections.setdefault(sec, ""); cur = None
        if cur: blocks[cur][2] += l + "\n"
        if sec: sections[sec] += l + "\n"
# 의존지도
dep = {}
for l in open(R+"의존지도_v2.md", encoding="utf-8"):
    m = re.match(r"\| `\{\{([^}]+)\}\}` \| ([^|]*) \| [^|]* \| [^|]* \| [^|]* \| ([^|]*) \|", l)
    if m:
        dep[m.group(1)] = (m.group(2).strip(), set(re.findall(r"\{\{([^}]+)\}\}", m.group(3))))
print("blocks:", len(blocks), "dep rows:", len(dep))
# 1. all labels in ch11 exist
labs = re.findall(r"\{\{(\d+:[^}]+)\}\}", "\n".join(ch11))
missing = sorted(set(l for l in labs if l not in blocks))
print("장11 라벨 수(연)", len(labs), "종류", len(set(labs)), "존재하지 않음:", missing)
# kind check: "정리 {{x}}" vs header kind
for ln, line in enumerate(ch11, 1):
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}", line):
        k, lab = m.group(1), m.group(2)
        if lab in kinds and kinds[lab] != k:
            print(f"  종류 불일치 행{ln}: 장11 '{k} {lab}' vs 머리 '{kinds[lab]}'")
    # also "·{{x}}" continuation inherits kind of preceding — check chains
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}((?:·\{\{\d+:[^}]+\}\})+)", line):
        k = m.group(1)
        for lab in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(3)):
            if lab in kinds and kinds[lab] != k:
                print(f"  종류 불일치(연쇄) 행{ln}: 장11 '{k} ·{lab}' vs 머리 '{kinds[lab]}'")
# 2. 11.3 tables
print("\n===== 11.3 표 의존 검사 =====")
in113 = False
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력") : continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    inputs = re.findall(r"\{\{(\d+:[^}]+)\}\}", cells[0])
    print(f"\n--- 행{ln}: {cells[0][:70]}")
    print("   입력:", inputs)
    for ci, cell in enumerate(cells[2:], 3):
        users = [u for u in re.findall(r"\{\{(\d+:[^}]+)\}\}", cell) if u not in inputs]
        for u in dict.fromkeys(users):
            via_dep = [x for x in inputs if x in dep.get(u, ("", set()))[1]]
            via_txt = [x for x in inputs if u in blocks and ("{{"+x+"}}") in blocks[u][2]]
            flag = "" if (via_dep or via_txt) else "  <<< 인용 못 찾음"
            print(f"   열{ci} 사용자 {kinds.get(u,'?')} {u}: 의존지도={via_dep} 본문={via_txt}{flag}")
# 3. grade cross-check: 11.3 col2 statements vs 11.2 grades
print("\n===== 산술 등급 대조 =====")
g112 = {}
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \|", line)
    if m:
        for s in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(2)):
            g112.setdefault(s, []).append((m.group(1), m.group(3)))
in113 = False
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력"): continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    col2 = cells[1]
    if col2 == "없음": continue
    # split by ';' groups: "stmts: grade"
    for grp in col2.split("; "):
        if ":" not in grp: print(f"  행{ln} 형식?: {grp}"); continue
        stm, grade = grp.rsplit(": ", 1)
        for s in re.findall(r"\{\{(\d+:[^}]+)\}\}", stm):
            got = g112.get(s)
            if not got:
                print(f"  행{ln} {s}: 11.2 표에 없음 (등급 '{grade}')")
                continue
            gset = set()
            for d, g in got:
                for x in g.split(", "): gset.add(x)
            claimed = set(grade.split(", "))
            ok = "OK" if gset == claimed else "<<< 다름"
            print(f"  행{ln} {s}: 11.3 '{grade}' vs 11.2 {[(d,g) for d,g in got]} {ok}")
# statements in 11.2 not in any 11.3 col2
all113 = set()
in113 = False
for line in ch11:
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if in113 and line.startswith("| ") and not line.startswith("| 입력"):
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        all113 |= set(re.findall(r"\{\{(\d+:[^}]+)\}\}", cells[1]))
print("\n11.2 진술 중 11.3 등급 열에 없는 것:", sorted(set(g112) - all113))
print("11.3 등급 열 진술 중 11.2에 없는 것:", sorted(all113 - set(g112)))
# who uses 3:old-3-5
print("\n{{3:old-3-5}}를 입력으로 둔 진술:", [u for u,(s,d) in dep.items() if "3:old-3-5" in d])
print("{{7:theorem-G-prime}} 의존지도:", dep.get("7:theorem-G-prime"))
print("{{7:theorem-C-moment}} 의존지도:", dep.get("7:theorem-C-moment"))
