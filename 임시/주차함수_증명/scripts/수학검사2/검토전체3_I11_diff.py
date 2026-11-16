# -*- coding: utf-8 -*-
"""11.2절 표의 행과 부록 D 항목의 독립 재계산 줄·꺾쇠·등급·절을 비교해 다른 곳만 적는다(자리 찾기용)."""
import re, os, sys, io, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from 검토전체3_I11_index import ditems, labels, CH
txt = open(os.path.join(CH, "장11.md"), encoding="utf-8").read()
rows = [L for L in txt.splitlines() if L.startswith("| 부록 D.{{D:")]
seen=set()
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
    lab = re.search(r"\{\{D:([^}]+)\}\}", cells[0]).group(1); seen.add(lab)
    d = ditems[lab]
    m = re.match(r"(〔[^〕]*〕)\s*(.*)$", d["indep"])
    dbr, dtext = m.group(1), m.group(2)
    print("="*90); print("행:", lab)
    if dbr != cells[4]:
        print("  꺾쇠 다름:\n    표:", cells[4], "\n    D :", dbr)
    if dtext != cells[5]:
        sm = difflib.SequenceMatcher(None, dtext, cells[5])
        for op, a0,a1,b0,b1 in sm.get_opcodes():
            if op!="equal":
                print(f"  본문 다름[{op}] D:«{dtext[max(0,a0-25):a1+25]}»\n                 표:«{cells[5][max(0,b0-25):b1+25]}»")
    # 진술 목록 비교: D 제목 괄호 안 라벨 vs 표 진술 라벨
    dl = re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", d["title"]); tl = re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", cells[1])
    if dl != tl: print("  진술 라벨 다름: D", dl, "표", tl)
    # 절 비교
    secs=set()
    for ch, sl in re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", cells[1]):
        for k,v in labels.items():
            if k[1]==sl: secs.add(v["sec"])
    print("  표 쓰인곳:", cells[3], "| 진술의 절:", sorted(secs))
    print("  표 등급:", cells[2], "| D 등급:", d["grade"][:160])
missing = set(ditems)-seen
print("표에 없는 D 항목:", missing)
# D 항목 순서 vs 표 순서
print("D 순서:", list(ditems))
print("표 순서:", [re.search(r"\{\{D:([^}]+)\}\}", r).group(1) for r in rows])
