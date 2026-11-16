import re,json,sys
root=r"C:\math\임시\주차함수_증명"
D={}
for f in ["부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]:
    txt=open(root+"\장v2\\"+f+".md",encoding="utf-8").read()
    for m in re.finditer(r"### D\.\{\{D:([^}]+)\}\}(.*?)(?=\n### D\.|\Z)",txt,re.S):
        name=m.group(1); body=m.group(2)
        head=re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$", body.split("\n")[0].strip())
        ir=re.search(r"\*\*독립 재계산\.\*\*\s*(.*?)\n",body)
        ar=re.search(r"\*\*산술 등급\.\*\*\s*(.*?)\n",body)
        D[name]=dict(head=body.split("\n")[0].strip(), indep=ir.group(1).strip() if ir else None, arith=ar.group(1).strip() if ar else None)
t=open(root+"\장v2\장11.md",encoding="utf-8").read()
rows=[l for l in t.split("\n") if l.startswith("| 부록 D.{{D:")]
for l in rows:
    cells=[c.strip() for c in l.strip().strip("|").split(" | ")]
    name=re.search(r"\{\{D:([^}]+)\}\}",cells[0]).group(1)
    if name not in D: continue
    stmt,grade,where,recalc,indep=cells[1],cells[2],cells[3],cells[4],cells[5]
    d=D[name]
    # compare recalc bracket + indep text
    m=re.match(r"(〔.*?〕)\s*(.*)",d["indep"],re.S)
    br,rest=m.group(1),m.group(2)
    print("==",name)
    print("  stmt(table):",stmt)
    print("  head(D):",d["head"][:200])
    print("  grade(table):",grade," | D arith:",d["arith"][:120])
    if br!=recalc: print("  BRACKET DIFF:\n   T:",recalc,"\n   D:",br)
    if rest!=indep:
        # find first diff
        i=0
        while i<min(len(rest),len(indep)) and rest[i]==indep[i]: i+=1
        print("  INDEP DIFF at",i,":\n   T:",indep[max(0,i-60):i+120],"\n   D:",rest[max(0,i-60):i+120])
