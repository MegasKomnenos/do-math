# 11.2절 표의 각 행을 부록 D 항목과 대조한다. 판단은 사람이 한다; 이 스크립트는 자리와 문자열 차이를 찾는 데만 쓴다.
import re, glob, os, difflib, sys
root = r"C:\math\임시\주차함수_증명"
D = {}
for f in sorted(glob.glob(os.path.join(root, "장v2", "부록D_*.md"))):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"^(?=### D\.\{\{D:)", txt, flags=re.M)
    for p in parts:
        m = re.match(r"### D\.\{\{D:([a-zA-Z0-9-]+)\}\}\s*(.*?)\s*\((.*)\)\s*$", p.split("\n")[0])
        if not m: continue
        lab = m.group(1)
        d = {"file": os.path.basename(f), "title": m.group(2), "stmt_hdr": m.group(3)}
        for key in ["확인하는 진술", "산술 등급", "독립 재계산", "범위", "결과"]:
            mm = re.search(r"^\*\*" + key + r"\.\*\*\s*(.*)$", p, flags=re.M)
            d[key] = mm.group(1).strip() if mm else None
        D[lab] = d
ch11 = open(os.path.join(root, "장v2", "장11.md"), encoding="utf-8").read()
rows = {}
for line in ch11.split("\n"):
    if line.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        lab = re.match(r"부록 D\.\{\{D:([a-zA-Z0-9-]+)\}\}", cells[0]).group(1)
        rows[lab] = dict(stmt=cells[1], grade=cells[2], place=cells[3], brk=cells[4], text=cells[5])
print("D 항목 수", len(D), "표 행 수", len(rows))
print("D에만:", sorted(set(D) - set(rows)))
print("표에만:", sorted(set(rows) - set(D)))
# 순서 비교
print("D 순서:", list(D))
print("표 순서:", list(rows))
# 진술 라벨 비교(머리 괄호의 진술 vs 표 열)
def labels(s): return re.findall(r"(정리|명제|보조정리|따름정리)\s*\{\{(\d+[AB]?:[a-zA-Z0-9-]+)\}\}(\([가-힣]+\))?", s)
for lab, r in rows.items():
    d = D[lab]
    a, b = labels(d["stmt_hdr"]), labels(r["stmt"])
    if a != b: print("\n[진술 불일치]", lab, "\n  D머리:", d["stmt_hdr"], "\n  표  :", r["stmt"])
    # 산술 등급: D 줄의 첫 등급
    g = d["산술 등급"]
    first = re.split(r"[\(（;。.]", g)[0].strip() if g else None
    if first is None or not r["grade"].startswith(first.split("·")[0][:4]):
        print("\n[등급 확인]", lab, "\n  D:", g, "\n  표:", r["grade"])
    else:
        # 표 등급과 D 등급 문자열이 다르면 표시
        if r["grade"] not in g: print("\n[등급 문자열 다름]", lab, "\n  D:", g[:200], "\n  표:", r["grade"])
    # 꺾쇠 괄호와 본문
    t = d["독립 재계산"] or ""
    m = re.match(r"(〔.*?〕)\s*(.*)$", t, flags=re.S)
    if not m: print("\n[꺾쇠 없음]", lab, t[:100]); continue
    brk, body = m.group(1), m.group(2)
    if brk != r["brk"]: print("\n[꺾쇠 다름]", lab, "\n  D:", brk, "\n  표:", r["brk"])
    body2 = body.replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호")
    if body2 != r["text"]:
        print("\n[본문 다름]", lab)
        for op in difflib.SequenceMatcher(None, body2, r["text"]).get_opcodes():
            if op[0] != "equal":
                print("   ", op[0], "D:", repr(body2[op[1]:op[2]][:200]), "표:", repr(r["text"][op[3]:op[4]][:200]))
