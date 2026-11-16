import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
base="C:/math/임시/주차함수_증명/장v2/"
items={}
for f in ["7A","7B","8","9","10"]:
    txt=open(base+f"부록D_장{f}.md",encoding="utf-8").read()
    for blk in re.split(r"(?m)^### ",txt)[1:]:
        m=re.match(r"D\.\{\{D:([^}]+)\}\}",blk)
        lab=m.group(1)
        head=blk.split("\n",1)[0]
        stmts=re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}",head)
        ir=re.search(r"\*\*독립 재계산\.\*\*\s*(.*)",blk)
        ar=re.search(r"\*\*산술 등급\.\*\*\s*(.*)",blk)
        items[lab]=dict(file=f,head=head,stmts=stmts,ir=ir.group(1).strip() if ir else None,ar=ar.group(1).strip() if ar else None)
t11=open(base+"장11.md",encoding="utf-8").read().split("\n")
rows={}
for line in t11:
    m=re.match(r"\| 부록 D\.\{\{D:([^}]+)\}\} \|(.*)",line)
    if m:
        cells=[c.strip() for c in m.group(2).split(" | ")]
        rows[m.group(1)]=cells
for lab,it in items.items():
    print("=====",lab,it['file'])
    if lab not in rows: print("  NO ROW"); continue
    c=rows[lab]
    print("  D head stmts:",it['stmts'])
    print("  11.2 stmt cell:",c[0])
    print("  11.2 grade:",c[1]," | D grade line:",it['ar'][:150])
    print("  11.2 place:",c[2])
    ir=it['ir']
    m=re.match(r"〔(.*?)〕\s*(.*)",ir,re.S)
    br,rest=m.group(1),m.group(2)
    print("  bracket equal:", ("〔"+br+"〕")==c[3])
    if ("〔"+br+"〕")!=c[3]:
        print("   D :",br); print("   11:",c[3])
    last=c[4].rstrip("|").strip()
    if rest.strip()!=last:
        import difflib
        print("  REST DIFFERS:")
        for d in difflib.ndiff([rest.strip()],[last]):
            pass
        sm=difflib.SequenceMatcher(None,rest.strip(),last)
        for op,a1,a2,b1,b2 in sm.get_opcodes():
            if op!='equal': print("   ",op,"D:",repr(rest.strip()[max(0,a1-20):a2+20]),"11:",repr(last[max(0,b1-20):b2+20]))
    else: print("  rest equal")
