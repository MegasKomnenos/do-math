import re, difflib
files=["장v2/부록D_장7A.md","장v2/부록D_장7B.md","장v2/부록D_장8.md","장v2/부록D_장9.md","장v2/부록D_장10.md"]
rows={}
for line in open("장v2/장11.md",encoding="utf-8"):
    m=re.match(r"\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*) \|\s*$", line)
    if m: rows[m.group(1)]=m.groups()[1:]
for f in files:
    txt=open(f,encoding="utf-8").read()
    items=re.split(r"\n(?=### D\.)", "\n"+txt)
    for it in items:
        m=re.match(r"\n?### D\.\{\{D:([^}]+)\}\} (.*)", it)
        if not m: continue
        lab=m.group(1); title=m.group(2)
        if lab not in rows: print(f, lab, "NO ROW IN 11.2"); continue
        stmt, grade, where, brk, text = rows[lab]
        m2=re.search(r"\*\*독립 재계산\.\*\* (〔[^〕]*〕) ?(.*)", it)
        dbrk, dtext = m2.group(1), m2.group(2).strip()
        m3=re.search(r"\*\*산술 등급\.\*\* (.*)", it); dgrade=m3.group(1).strip() if m3 else "?"
        print("==", f.split('/')[-1], lab)
        print("  title-stmts:", re.findall(r"\(([^()]*\{\{[^}]+\}\}[^()]*)\)\s*$", title), "| row stmt:", stmt)
        print("  row grade:", grade, "| D grade line:", dgrade[:160])
        if dbrk!=brk: print("  BRACKET DIFF:\n   D:", dbrk, "\n   R:", brk)
        if dtext!=text:
            print("  TEXT DIFF:")
            for d in difflib.ndiff([dtext],[text]):
                if d[0] in "?": print("   ", d[:400])
            sm=difflib.SequenceMatcher(None,dtext,text)
            for op,a1,a2,b1,b2 in sm.get_opcodes():
                if op!='equal': print("   ",op,"D[",dtext[max(0,a1-20):a2+20],"] R[",text[max(0,b1-20):b2+20],"]")
