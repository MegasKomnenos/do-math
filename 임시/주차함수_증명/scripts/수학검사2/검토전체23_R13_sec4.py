# -*- coding: utf-8 -*-
# 장부 4절의 행을 장 파일 머리·대응표와 맞댄다.
import re, json, os
base = r"C:\math\임시\주차함수_증명"
heads = json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_heads.json"),encoding="utf-8"))
hd = {h["label"]:h for h in heads}
L = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s = next(i for i,l in enumerate(L) if l.startswith("## 4. "))
e = next(i for i,l in enumerate(L) if l.startswith("## 5. "))
rows=[]
for i in range(s,e):
    l=L[i]
    if l.startswith("| ") and not l.startswith("| 첫 판") and not l.startswith("|---"):
        cells=[c.strip() for c in l.strip()[1:-1].split(" | ")]
        if len(cells)!=6:
            cells=[c.strip() for c in l.strip()[1:-1].split("|")]
        rows.append((i+1,cells))
print("rows",len(rows))
live=[];dead=[]
for ln,c in rows:
    if len(c)!=6: print("칸수",ln,len(c),c[:3]); continue
    lab=c[5]
    if lab.startswith("{{"):
        live.append(lab)
        h=hd.get(lab)
        if not h: print("머리 없음",ln,c); continue
        if h["kind"]!=c[1]: print("종류 다름",ln,lab,c[1],h["kind"])
        nm=h["name"] or ""
        exp = c[2] + ("; "+c[3] if c[3] and c[2] else c[3])
        if nm!=exp: print("이름 다름",ln,lab,"\n   표:",exp,"\n   머리:",nm)
        if h["sec3"]!=c[4]: print("절 다름",ln,lab,c[4],h["sec3"])
    else:
        dead.append((ln,lab,c))
        if c[4] not in ("뺌",) and "뺌" not in c[4] and "옮김" not in c[4]: print("죽은 라벨인데 절",ln,c[4],lab)
print("live",len(live),"dead",len(dead), "dup live", len(live)-len(set(live)))
for h in heads:
    if h["label"] not in live: print("4절에 없음",h["label"],h["num"],h["name"])
# 순서
print("순서 같음", live==[h["label"] for h in heads])
# 대응표 뺌 행과 비교
M = open(os.path.join(base,"대조v2","라벨_번호_대응표_1114.md"),encoding="utf-8").read().split("\n")
mdead={}
for i,l in enumerate(M,1):
    if l.startswith("| `("):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        mdead[c[0].strip("`")]=(i,c)
ld={lab:(ln,c) for ln,lab,c in dead}
print("대응표 뺌",len(mdead),"장부 뺌",len(ld), "장부 뺌 중복", len(dead)-len(ld))
for k in mdead:
    if k not in ld: print("대응표에만:",k,mdead[k][1][1:4])
for k in ld:
    if k not in mdead: print("장부에만:",ld[k][0],k,ld[k][1][:5])
for k in mdead:
    if k in ld:
        a=mdead[k][1]; b=ld[k][1]
        if a[1]!=b[1]: print("뺌 종류 다름",k,a[1],b[1])
json.dump({"dead":dead,"mdead":mdead},open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_dead.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=0)
