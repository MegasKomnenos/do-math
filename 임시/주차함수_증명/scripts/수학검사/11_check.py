# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
# parse 11.2 table rows
rows = {}
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔.*?〕) \| (.*) \|$", line)
    if m:
        rows[m.group(1)] = dict(ln=ln, stmts=m.group(2), grade=m.group(3), where=m.group(4), rec=m.group(5), indep=m.group(6))
print("11.2 rows:", len(rows))
# parse appendix D items
items = {}
order = []
for f in sorted(glob.glob(R+"장v2/부록D_장*.md")):
    txt = open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^### D\.\{\{(D:[^}]+)\}\}", txt)
    # parts: [pre, label1, body1, label2, body2...]
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i+1]
        head = body.split("\n",1)[0]
        hp = re.findall(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", head.strip())
        grade = re.search(r"\*\*산술 등급\.\*\*\s*(.*)", body)
        indep = re.search(r"\*\*독립 재계산\.\*\*\s*(.*)", body)
        items[lab] = dict(file=f.split("/")[-1], head=head.strip(), headpar=hp[0] if hp else "", grade=grade.group(1) if grade else "", indep=indep.group(1) if indep else "")
        order.append(lab)
print("D items:", len(items))
print("missing in table:", [l for l in order if l not in rows])
print("extra in table:", [l for l in rows if l not in items])
print("order same:", order == list(rows.keys()))
for lab in order:
    if lab not in rows: continue
    r, it = rows[lab], items[lab]
    print("="*100)
    print(f"[{lab}] 표 행 {r['ln']} / {it['file']}")
    print("  표 진술 :", r['stmts'])
    print("  D 머리  :", it['headpar'])
    print("  표 등급 :", r['grade'])
    print("  D 등급  :", it['grade'][:300])
    # recompute bracket
    m = re.match(r"(〔.*?〕)\s*(.*)", it['indep'])
    dbr, dtxt = (m.group(1), m.group(2)) if m else ("", it['indep'])
    print("  괄호 같음:", dbr == r['rec'])
    if dbr != r['rec']:
        print("   표:", r['rec']); print("   D :", dbr)
    # compare indep text: check whether table text is a prefix (modulo "이 글을 쓰며" vs "이 글의 재계산에서는")
    tt = r['indep']
    norm = lambda s: s.replace("이 글을 쓰며 ", "").replace("이 글의 재계산에서는 ", "").replace("이 글의 재계산에서 ", "")
    nd, nt = norm(dtxt), norm(tt)
    if nd.startswith(nt):
        print("  서술: 표는 D의 앞부분(또는 전부)과 같음", "(전부)" if nd==nt else f"(D 나머지 {len(nd)-len(nt)}자)")
    else:
        # find first differing position
        k = 0
        while k < min(len(nd), len(nt)) and nd[k]==nt[k]: k+=1
        print("  서술 다름 @", k)
        print("   표:", tt[max(0,k-60):k+200])
        print("   D :", dtxt[max(0,k-60):k+200])
