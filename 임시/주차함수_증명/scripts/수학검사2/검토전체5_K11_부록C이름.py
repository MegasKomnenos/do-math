# -*- coding: utf-8 -*-
"""부록 C 「기록이 결과에 붙인 이름」 표를 진술 머리 괄호의 「기록 [rX]의 Y」와 맞춘다."""
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
C = open(root+"부록C.md", encoding="utf-8").read()
sec = C.split("### 기록이 결과에 붙인 이름")[1].split("### 기록의 글자")[0]
crows = {}
for l in sec.split("\n"):
    if not l.startswith("| 기록"): continue
    c=[x.strip() for x in l.strip().strip("|").split(" | ")]
    mm = re.search(r"\{\{([^}]+)\}\}", c[1])
    if not mm: print("라벨 없는 행:", l[:200]); continue
    lab = mm.group(1)
    crows[lab]=(c[0], c[1], c[2])
heads={}
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\} (\((.*?)\) )?\[")
for f in sorted(glob.glob(root+"장*.md")):
    for l in open(f,encoding="utf-8"):
        m=HEAD.match(l)
        if m: heads[m.group(2)]=(m.group(1), (m.group(4) or "").strip())
n=0
for lab,(typ,par) in heads.items():
    if "기록 [" in par:
        name_part = par.split(";")[-1].strip() if ";" in par else par
        own = par.split(";")[0].strip() if ";" in par else ""
        if lab not in crows:
            print("!! 부록 C에 없음:", lab, "|", par); continue
        c0,c1,c2 = crows[lab]
        probs=[]
        if c0.replace(" ","")!=name_part.replace(" ",""): probs.append(f"기록이름: C「{c0}」 vs 머리「{name_part}」")
        if own and c2.replace(" ","")!=own.replace(" ",""): probs.append(f"이 글 이름: C「{c2}」 vs 머리「{own}」")
        if not c1.startswith(typ): probs.append(f"유형: C「{c1}」 vs 머리「{typ}」")
        if probs: n+=1; print(lab, "::", " ; ".join(probs))
for lab in crows:
    if lab not in heads: print("!! 부록 C 라벨이 본문에 없음:", lab)
    elif "기록 [" not in heads[lab][1]: print("!! 머리에 기록 이름이 없는데 C에 있음:", lab, "|", heads[lab][1], "| C:", crows[lab][0])
print("불일치 수", n, "/ C 행 수", len(crows))
