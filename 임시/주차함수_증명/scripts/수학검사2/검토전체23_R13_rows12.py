# -*- coding: utf-8 -*-
# 장부 1.2의 행을 칸으로 쪼개 JSON으로(칸 구분은 ' | ' — 뒤에 원문 행을 열어 확인).
import re, json, os
base = r"C:\math\임시\주차함수_증명"
L = open(os.path.join(base,"장부_v2.md"),encoding="utf-8").read().split("\n")
s = next(i for i,l in enumerate(L) if l.startswith("### 1.2 "))
e = next(i for i,l in enumerate(L) if l.startswith("### 1.3 "))
rows=[]
for i in range(s,e):
    l=L[i]
    if l.startswith("| $") or l.startswith("| ("):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        rows.append(dict(line=i+1,n=len(c),sym=c[0],base=c[1],mean=c[2],sec=c[3],chs=c[4],rest=c[5:]))
json.dump(rows,open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_rows12.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=0)
print(len(rows))
for r in rows:
    flag="" if r["n"]==7 else " <<<칸수 %d"%r["n"]
    print(r["line"],"|",r["sym"],"|",r["sec"],"|",r["chs"],flag)
