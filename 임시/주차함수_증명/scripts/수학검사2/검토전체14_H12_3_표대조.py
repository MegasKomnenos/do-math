# H12 검산 3: 11.2절 표의 행과 부록 D 항목(2~6장) 대조
import re, glob, os
root=r"C:\math\임시\주차함수_증명\장v2"
items={}
for f in ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]:
    txt=open(os.path.join(root,f),encoding="utf-8").read()
    parts=re.split(r"^### D\.\{\{D:([^}]+)\}\}",txt,flags=re.M)
    for i in range(1,len(parts),2):
        lab=parts[i]; body=parts[i+1]
        title=body.split("\n",1)[0].strip()
        m=re.search(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$",title)
        stmt=m.group(1) if m else "?"
        g=re.search(r"\*\*산술 등급\.\*\*\s*(.*)",body); grade=g.group(1).strip() if g else "?"
        r=re.search(r"\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*)",body)
        items[lab]=dict(file=f,stmt=stmt,grade=grade,br=r.group(1) if r else "?",txt=r.group(2).strip() if r else "?")
ch11=open(os.path.join(root,"장11.md"),encoding="utf-8").read().split("\n")
rows={}
for line in ch11:
    m=re.match(r"\|\s*부록 D\.\{\{D:([^}]+)\}\}\s*\|(.*)\|\s*$",line)
    if m:
        cells=[c.strip() for c in m.group(2).split(" | ")]
        if len(cells)!=5: cells=[c.strip() for c in m.group(2).split("|")]
        rows[m.group(1)]=cells
# section lookup
chap={}
for f in glob.glob(os.path.join(root,"장*.md")):
    sec=None
    for line in open(f,encoding="utf-8"):
        h=re.match(r"^### (\d+\.\d+)",line)
        if h: sec=h.group(1)
        for lab in re.findall(r"\*\*(?:정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}",line):
            chap[lab]=sec
for lab,it in items.items():
    print("=====",lab,"(",it["file"],")")
    if lab not in rows: print("  !! 11.2 표에 행 없음"); continue
    c=rows[lab]
    print("  진술  D:",it["stmt"]); print("        T:",c[0], "  SAME" if it["stmt"].replace(" ","")==c[0].replace(" ","") else "  <<DIFF")
    print("  등급  D:",it["grade"][:120]); print("        T:",c[1])
    labs=re.findall(r"\{\{(\d+:[^}]+)\}\}",c[0]); secs=sorted({chap.get(l,"?") for l in labs})
    print("  절    T:",c[2]," 실제:",secs, "" if c[2] in secs or len(secs)==0 else "  <<DIFF")
    print("  괄호  ", "SAME" if it["br"]==c[3] else "<<DIFF\n     D:"+it["br"]+"\n     T:"+c[3])
    dt=it["txt"].replace("이 문단 머리의 꺾쇠 괄호","「재계산」 열의 꺾쇠 괄호")
    if dt==c[4]: print("  본문   SAME")
    else:
        # find first difference
        i=0
        while i<min(len(dt),len(c[4])) and dt[i]==c[4][i]: i+=1
        print("  본문   <<DIFF at",i,"\n     D:",dt[max(0,i-60):i+100],"\n     T:",c[4][max(0,i-60):i+100])
print("표에만 있는 항목(내 범위 밖 포함):",[k for k in rows if k not in items])
