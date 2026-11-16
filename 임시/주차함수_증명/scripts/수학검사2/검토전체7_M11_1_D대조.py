# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 대조한다 (M11 검토용).
비교: 항목 순서, 확인하는 진술, 산술 등급(첫 등급), 재계산 꺾쇠 괄호, 독립 재계산 본문."""
import re, glob, os, sys, difflib
ROOT = r"C:\math\임시\주차함수_증명\장v2"
def rd(p): return open(p, encoding="utf-8").read()

# 부록 D 항목 파싱
D = {}
Dorder = []
for f in sorted(glob.glob(os.path.join(ROOT, "부록D_장*.md"))):
    txt = rd(f)
    parts = re.split(r"(?m)^### D\.\{\{D:([^}]+)\}\} ", txt)
    for i in range(1, len(parts), 2):
        lab = parts[i]; body = parts[i+1]
        title = body.split("\n", 1)[0]
        m = re.search(r"\(([^()]*(?:\{\{[^}]+\}\}[^()]*)*)\)\s*$", title)
        stmts = m.group(1) if m else "?"
        def line(name):
            mm = re.search(r"(?m)^\*\*" + name + r"\.\*\*\s*(.*)$", body)
            return mm.group(1).strip() if mm else None
        D[lab] = dict(file=os.path.basename(f), title=title, stmts=stmts,
                      grade=line("산술 등급"), recalc=line("독립 재계산"),
                      confirm=line("확인하는 진술"))
        Dorder.append(lab)

# 11.2 표 파싱
t11 = rd(os.path.join(ROOT, "장11.md"))
rows = []
for ln in t11.splitlines():
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        if len(cells) != 6:
            print("열 수 이상:", len(cells), ln[:80]); continue
        lab = re.match(r"부록 D\.\{\{D:([^}]+)\}\}", cells[0]).group(1)
        rows.append(dict(lab=lab, stmts=cells[1], grade=cells[2], where=cells[3], br=cells[4], text=cells[5]))

print("부록 D 항목 수:", len(Dorder), " 표 행 수:", len(rows))
Torder = [r["lab"] for r in rows]
print("표에 없는 D 항목:", [l for l in Dorder if l not in Torder])
print("D에 없는 표 행:", [l for l in Torder if l not in D])
print("순서 일치:", Dorder == Torder)
if Dorder != Torder:
    for a, b in zip(Dorder, Torder):
        if a != b: print("  D:", a, " 표:", b)

def norm(s):
    s = s.replace("이 문단 머리의 꺾쇠 괄호", "「재계산」 열의 꺾쇠 괄호")
    s = re.sub(r"\s+", " ", s).strip()
    return s

for r in rows:
    d = D.get(r["lab"])
    if not d: continue
    print("\n=====", r["lab"], "(", d["file"], ")")
    # 확인하는 진술
    if norm(r["stmts"]) != norm(d["stmts"]):
        print(" [진술 불일치]\n   표:", r["stmts"], "\n   D :", d["stmts"])
    # 산술 등급
    g = d["grade"] or ""
    g1 = re.split(r"[(（.;]", g)[0].strip()
    if r["grade"] != g1:
        print(" [등급 차이] 표:", r["grade"], " | D 첫 등급:", g1, " | D 줄:", g[:160])
    # 재계산 꺾쇠 괄호와 본문
    rc = d["recalc"] or ""
    m = re.match(r"〔([^〕]*)〕\s*(.*)$", rc, re.S)
    if not m:
        print(" [D 독립 재계산 줄에 꺾쇠 괄호 없음]", rc[:100]); continue
    dbr, dtext = "〔" + m.group(1) + "〕", m.group(2)
    if norm(r["br"]) != norm(dbr):
        print(" [꺾쇠 불일치]\n   표:", r["br"], "\n   D :", dbr)
    if norm(r["text"]) != norm(dtext):
        print(" [본문 차이]")
        a, b = norm(dtext), norm(r["text"])
        sm = difflib.SequenceMatcher(None, a, b)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                print(f"   {op}: D『{a[max(0,i1-25):i2+25]}』 → 표『{b[max(0,j1-25):j2+25]}』")
