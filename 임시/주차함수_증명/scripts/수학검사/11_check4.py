# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11txt = open(R+"장v2/장11.md", encoding="utf-8").read()
ch11 = ch11txt.split("\n")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|관찰|주의|가정|표기)\s+\{\{(\d+:[^}]+)\}\}(.*?)\*\*")
blocks = {}; heads = {}; kinds = {}
for f in sorted(glob.glob(R+"장v2/장*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    cur = None
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            cur = m.group(2); kinds[cur] = m.group(1); heads[cur] = m.group(3); blocks[cur] = ""
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l)
        if ms: cur = None
        if cur: blocks[cur] += l + "\n"
# header-declared computation grades
print("===== 진술 머리의 계산 등급 vs 11.3 등급 열 =====")
hg = {}
for lab, h in heads.items():
    m = re.search(r"계산 (?:보조|증거)\(([^)]*)\)", h)
    if m: hg[lab] = m.group(1)
    elif "계산 보조" in h or "계산 증거" in h: hg[lab] = "<등급 괄호 없음> " + h[:150]
in113 = False; g113 = {}
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력"): continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if cells[1] == "없음": continue
    for grp in cells[1].split("; "):
        stm, grade = grp.rsplit(": ", 1)
        for s in re.findall(r"\{\{(\d+:[^}]+)\}\}", stm): g113[s] = (ln, grade)
for s, (ln, g) in g113.items():
    h = hg.get(s, "<머리에 계산 표지 없음>")
    print(f"  행{ln} {s}: 11.3 '{g}' / 머리 '{h}'", "" if g == h else "  <<<")
print("\n머리에 계산 표지가 있으나 11.3 등급 열에 없는 진술:")
for s, h in hg.items():
    if s not in g113: print("  ", kinds[s], s, ":", h[:120])
# transitive closure from 의존지도 (plus header-declared dependencies)
dep = {}
for l in open(R+"의존지도_v2.md", encoding="utf-8"):
    m = re.match(r"\| `\{\{([^}]+)\}\}` \| ([^|]*) \| [^|]* \| [^|]* \| [^|]* \| ([^|]*) \|", l)
    if m: dep[m.group(1)] = set(re.findall(r"\{\{([^}]+)\}\}", m.group(3)))
# also use body citations (labels appearing in the statement block)
body = {lab: set(re.findall(r"\{\{(\d+:[^}]+)\}\}", b)) - {lab} for lab, b in blocks.items()}
def closure(start, use):
    seen = set(); st = [start]
    while st:
        x = st.pop()
        for y in use.get(x, set()):
            if y not in seen: seen.add(y); st.append(y)
    return seen
for name, use in (("의존지도", dep), ("본문 인용", body)):
    c1 = closure("9:old-7-46", use); c2 = closure("10:old-8-37", use)
    print(f"\n===== 닫힘({name}): 첫째 {len(c1)}, 둘째 {len(c2)}, 공유 {len(c1&c2)} =====")
    comp = set(re.findall(r"\| 부록 D\.\{\{D:[^}]+\}\} \| ([^|]*) \|", ch11txt))
    compstm = set()
    for c in comp: compstm |= set(re.findall(r"\{\{(\d+:[^}]+)\}\}", c))
    print("  11.2 계산 진술 중 첫째 닫힘에만:", sorted(compstm & c1 - c2))
    print("  11.2 계산 진술 중 둘째 닫힘에만:", sorted(compstm & c2 - c1))
    print("  11.2 계산 진술 중 공유:", sorted(compstm & c1 & c2))
    print("  11.2 계산 진술 중 어느 닫힘에도 없음:", sorted(compstm - c1 - c2))
    # 11.3 input rows classification
    in113 = False; table = 0
    for ln, line in enumerate(ch11, 1):
        if line.startswith("**공유 입력.**"): table = 1
        if line.startswith("**첫째 증명의 고유 입력.**"): table = 2
        if line.startswith("**둘째 증명의 고유 입력.**"): table = 3
        if line.startswith("### 11.4"): break
        if not line.startswith("| ") or line.startswith("| 입력"): continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        for x in re.findall(r"\{\{(\d+:[^}]+)\}\}", cells[0]):
            cls = "공유" if (x in c1 and x in c2) else "첫째만" if x in c1 else "둘째만" if x in c2 else "없음"
            exp = {1:"공유",2:"첫째만",3:"둘째만"}[table]
            if cls != exp: print(f"  행{ln} 표{table}({exp}) 입력 {x}: 닫힘 판정 {cls}")
    # 11.4 shared check
    print("  --- 11.4: 쓰인 자리 라벨의 닫힘 소속")
    in114 = False
    for ln, line in enumerate(ch11, 1):
        if line.startswith("### 11.4"): in114 = True
        if not in114 or not line.startswith("| ") or line.startswith("| 문헌"): continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        labs = re.findall(r"\{\{(\d+:[^}]+)\}\}", cells[2])
        sh = [x for x in labs if x in c1 and x in c2]
        print(f"   행{ln} {cells[0][:30]}: 라벨 {len(labs)}개, 공유 닫힘 안 {len(sh)}개, 첫째만 {len([x for x in labs if x in c1 and x not in c2])}, 둘째만 {len([x for x in labs if x in c2 and x not in c1])}, 밖 {len([x for x in labs if x not in c1 and x not in c2])}")
