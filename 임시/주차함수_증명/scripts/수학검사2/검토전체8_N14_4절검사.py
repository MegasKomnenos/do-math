# -*- coding: utf-8 -*-
"""장부 4절(첫 판 번호↔라벨) 표를 장 파일 머리·대응표와 견준다."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CH_RE = re.compile(r"^## (\d+)\."); SEC_RE = re.compile(r"^#{3,4} (\d+\.\d+(?:\.\d+)?)")
cur={}; chapter=None; sec=None
for name in order:
    for line in open(os.path.join(root,"장v2",name+".md"),encoding='utf-8'):
        m=CH_RE.match(line)
        if m: chapter=int(m.group(1)); sec=None
        m=SEC_RE.match(line)
        if m: sec=m.group(1)
        m=HEAD_RE.match(line)
        if m:
            key=f"{m.group(2)}:{m.group(3)}"; rest=line[m.end():]; nm=""
            if rest.startswith(" ("):
                depth=0
                for idx,ch in enumerate(rest[1:],1):
                    if ch=="(": depth+=1
                    elif ch==")":
                        depth-=1
                        if depth==0: nm=rest[2:idx].strip(); break
            cur[key]=dict(kind=m.group(1),sec=sec,name=nm)
rows=[]; insec=False; nolabel=[]
for ln,line in enumerate(open(os.path.join(root,"장부_v2.md"),encoding='utf-8'),1):
    if line.startswith("## 4."): insec=True; continue
    if line.startswith("## 5."): break
    if insec and line.startswith("| ") and not line.startswith("| 첫 판") and not line.startswith("|---"):
        cells=[c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells)>=6:
            rows.append((ln,cells))
print("4절 행", len(rows))
seen=set()
for ln,c in rows:
    old,kind,name,recname,sec,lab=c[:6]
    m=re.search(r"\{\{(\d+):([^}]+)\}\}",lab)
    if not m:
        nolabel.append((ln,old,kind,name,sec,lab)); continue
    key=f"{m.group(1)}:{m.group(2)}"
    if key in seen: print("중복 라벨 행",ln,key)
    seen.add(key)
    if key not in cur:
        print(f"행{ln}: 장 파일에 없는 라벨 {key} | {old} {kind} {name} | {lab[:60]}"); continue
    h=cur[key]
    if h['kind']!=kind: print(f"행{ln} 종류 다름 {key}: 장부 {kind} / 장 {h['kind']}")
    if not (h['sec']==sec or (h['sec'] or '').startswith(sec+'.')): print(f"행{ln} 절 다름 {key}: 장부 {sec} / 장 {h['sec']}")
    full = name + ("; "+recname if recname else "")
    if h['name']!=full: print(f"행{ln} 이름 다름 {key}: 장부 「{full}」 / 장 「{h['name']}」")
for k in cur:
    if k not in seen: print("4절에 없는 머리:",k,cur[k]['kind'],cur[k]['name'])
print("라벨 없는 행(뺌 등):",len(nolabel))
for x in nolabel: print("  ",x[0],x[1],x[2],x[3],"|",x[4],"|",x[5][:80])
