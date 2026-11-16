import re,io
ids=["column-certification-k500","seed-certificates-k120","self-consistent-constants","xcert-partAB","polar-blocks-488","band102-integer","moment-certification","column-certificates-841-2000","Q-fin-1130","window-mass-env","bprime-boxes","band-boxes","stored-table-check","m1-column-reading","H-star-plus-interval","AR-integrals","band-LP","pair-one-variable","M-natural-integrals","four-families"]
D={}
for f in ["부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]:
    txt=open(f"장v2/{f}.md",encoding="utf-8").read()
    parts=re.split(r"(?m)^### D\.\{\{D:([^}]+)\}\}",txt)
    for i in range(1,len(parts),2):
        D[parts[i]]=parts[i+1]
T=open("장v2/장11.md",encoding="utf-8").read()
rows={}
for line in T.splitlines():
    m=re.match(r"\| 부록 D\.\{\{D:([^}]+)\}\} \|",line)
    if m:
        cols=[c.strip() for c in line.strip().strip("|").split(" | ")]
        rows[m.group(1)]=cols
import difflib
for k in ids:
    body=D[k]
    m=re.search(r"\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n\n\*\*자료",body,re.S)
    br,desc=m.group(1),m.group(2).strip()
    cols=rows[k]
    tb,td=cols[4],cols[5]
    # grade
    gm=re.search(r"\*\*산술 등급\.\*\*\s*(.*?)\n",body)
    print("==",k,"| 11.2 grade:",cols[2],"| D grade line:",gm.group(1)[:90])
    if br!=tb: print("  BRACKET DIFF\n   D :",br,"\n   T :",tb)
    if desc!=td:
        sm=difflib.SequenceMatcher(None,desc,td)
        for op,a1,a2,b1,b2 in sm.get_opcodes():
            if op!="equal": print("  ",op,"D:",repr(desc[max(0,a1-15):a2+15]),"T:",repr(td[max(0,b1-15):b2+15]))
