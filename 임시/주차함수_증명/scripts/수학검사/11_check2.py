# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
rows = {}
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔.*?〕) \| (.*) \|$", line)
    if m: rows[m.group(1)] = dict(ln=ln, indep=m.group(6))
items = {}
for f in sorted(glob.glob(R+"장v2/부록D_장*.md")):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{(D:[^}]+)\}\}", txt)
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i+1]
        indep = re.search(r"\*\*독립 재계산\.\*\*\s*(.*)", body)
        items[lab] = indep.group(1) if indep else ""
def norm(s):
    s = s.replace(r"\vert ", "|").replace(r"\vert", "|").replace("이 글을 쓰며", "이 글의 재계산에서는")
    s = s.replace("「재계산」 열의 꺾쇠 괄호", "이 문단 머리의 꺾쇠 괄호")
    return re.sub(r"\s+", "", s)
for lab, r in rows.items():
    d = norm(items[lab])
    sents = re.split(r"(?<=다\.)\s+|(?<=\)\.)\s+", r['indep'])
    bad = [s for s in sents if norm(s) and norm(s) not in d]
    if bad:
        print(f"[{lab}] 행 {r['ln']}: D에 없는 문장 {len(bad)}개")
        for s in bad: print("   ", s[:400])
print("done")
