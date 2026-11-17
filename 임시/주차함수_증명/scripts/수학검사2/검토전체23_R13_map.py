# -*- coding: utf-8 -*-
# 대응표의 행을 장 파일 머리와 맞댄다.
import re, json, os
base = r"C:\math\임시\주차함수_증명"
heads = json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_heads.json"),encoding="utf-8"))
hd = {h["label"]:h for h in heads}
rows=[]
for ln,line in enumerate(open(os.path.join(base,"대조v2","라벨_번호_대응표_1114.md"),encoding="utf-8").read().split("\n"),1):
    if line.startswith("| `{{"):
        cells=[c.strip() for c in line.strip().strip("|").split(" | ")]
        rows.append((ln,cells))
print("rows",len(rows))
seen=set()
order=[]
for ln,c in rows:
    lab=c[0].strip("`")
    if c[3] in ("뺌","—") or "뺌" in c[3]:
        if lab in hd: print("뺌인데 머리 있음",ln,lab)
        continue
    order.append(lab)
    if lab in seen: print("중복",ln,lab)
    seen.add(lab)
    h=hd.get(lab)
    if not h: print("머리 없음",ln,c); continue
    if h["kind"]!=c[1]: print("종류 다름",ln,lab,c[1],h["kind"])
    if h["num"]!=c[3]: print("번호 다름",ln,lab,c[3],h["num"])
    nm = h["name"] if h["name"] else "—"
    if nm!=c[2]: print("이름 다름",ln,lab,"| 표:",c[2],"| 머리:",nm)
    if h["sec3"]!=c[5]: print("절 다름",ln,lab,c[5],h["sec3"],h["sec"])
for h in heads:
    if h["label"] not in seen: print("표에 없음",h["label"],h["num"])
print("순서 같음", order==[h["label"] for h in heads])
