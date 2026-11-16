# -*- coding: utf-8 -*-
"""H14: 장v2 조각에서 진술 머리를 모아 조립 규칙대로 번호를 매기고, 라벨·번호·종류·이름·지위·파일:행을 표로 낸다. 원고.md는 쓰지 않는다."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CHAPTER_RE = re.compile(r"^## (\d+)\.")
D_HEAD_RE = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        parts=sorted(n for n in os.listdir(base) if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md",n))
        out.extend(parts)
    return out
rows=[]; counters={}; chapter=0
for name in chapter_files("장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=CHAPTER_RE.match(ln)
        if m: chapter=int(m.group(1)); counters.setdefault(chapter,0); continue
        h=HEAD_RE.match(ln)
        if h:
            counters[chapter]+=1
            num=f"{chapter}.{counters[chapter]}"
            rest=ln[h.end():]
            # name in parens, status in brackets
            mm=re.match(r"\s*(\((.*?)\))?\s*(\[(.*?)\])?",rest)
            nm=mm.group(2) or ""; st=mm.group(4) or ""
            rows.append((f"{h.group(2)}:{h.group(3)}",num,h.group(1),nm,st,f"{name}:{ln_no}"))
out=io.open(os.path.join(ROOT,"대조v2","수학검사2","_H14_heads.tsv"),"w",encoding="utf-8",newline="\n")
for r in rows: out.write("\t".join(r)+"\n")
out.close()
print(len(rows),"heads")
d=[]; dc=0
for name in chapter_files("부록D_장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=D_HEAD_RE.match(ln)
        if m: dc+=1; d.append((m.group(1),str(dc),f"{name}:{ln_no}",ln))
out=io.open(os.path.join(ROOT,"대조v2","수학검사2","_H14_dheads.tsv"),"w",encoding="utf-8",newline="\n")
for r in d: out.write("\t".join(r)+"\n")
out.close()
print(dc,"D items")
