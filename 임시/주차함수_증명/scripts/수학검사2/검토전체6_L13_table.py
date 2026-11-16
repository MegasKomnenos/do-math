# L13: 11.2절 표의 재계산·독립 재계산 열과 부록 D 독립 재계산 줄 대조
import re
BASE=r"C:/math/임시/주차함수_증명"
D={}
for f in ["부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]:
    txt=open(f"{BASE}/장v2/{f}.md",encoding="utf-8").read()
    for sec in re.split(r"\n(?=### D\.)",txt):
        m=re.match(r"### D\.\{\{D:([^}]+)\}\}",sec)
        if not m: continue
        name=m.group(1)
        mm=re.search(r"\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)(?=\n\s*\n|\Z)",sec,re.S)
        D[name]=(mm.group(1).strip(),mm.group(2).strip()) if mm else None
tbl=open(f"{BASE}/장v2/장11.md",encoding="utf-8").read()
for line in tbl.splitlines():
    if not line.startswith("| 부록 D.{{D:"): continue
    cells=[c.strip() for c in line.strip().strip("|").split(" | ")]
    name=re.match(r"부록 D\.\{\{D:([^}]+)\}\}",cells[0]).group(1)
    if name not in D: continue
    br,txt=D[name]
    print("==",name)
    if cells[4]!=br: print("  재계산 괄호 다름:\n   D:",br,"\n   T:",cells[4])
    t=cells[5]
    if t!=txt:
        # 차이 위치
        i=0
        while i<min(len(t),len(txt)) and t[i]==txt[i]: i+=1
        print("  독립재계산 본문 다름 at",i,":\n   D:",txt[max(0,i-60):i+120],"\n   T:",t[max(0,i-60):i+120])
    else: print("  같음")
