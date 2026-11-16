# -*- coding: utf-8 -*-
"""H14: 대응표의 라벨·종류·이름·현재 번호·둘째 판 절을 장 파일의 머리와 비교한다."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CHAPTER_RE = re.compile(r"^## (\d+)\.")
SEC_RE = re.compile(r"^### (\d+\.\d+)")
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md",n)))
    return out
heads={}; order=[]; counters={}; chapter=0; sec=""
for name in chapter_files("장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=CHAPTER_RE.match(ln)
        if m: chapter=int(m.group(1)); counters.setdefault(chapter,0); sec=f"{chapter}.0"; continue
        s=SEC_RE.match(ln)
        if s: sec=s.group(1); continue
        h=HEAD_RE.match(ln)
        if h:
            counters[chapter]+=1
            key=f"{h.group(2)}:{h.group(3)}"
            rest=ln[h.end():]
            nm=""; st=""; r=rest.lstrip()
            if r.startswith("("):
                dep=0
                for j,ch in enumerate(r):
                    if ch=="(": dep+=1
                    elif ch==")":
                        dep-=1
                        if dep==0: nm=r[1:j]; r=r[j+1:].lstrip(); break
            if r.startswith("["):
                st=r[1:r.index("]")]
            heads[key]=dict(num=f"{chapter}.{counters[chapter]}",kind=h.group(1),name=nm.strip(),status=st,sec=sec,loc=f"{name}:{ln_no}",line=ln)
            order.append(key)
tab=io.open(os.path.join(ROOT,"대조v2","라벨_번호_대응표_1114.md"),encoding="utf-8").read().split("\n")
seen=set(); probs=[]
for i,ln in enumerate(tab,1):
    if not ln.startswith("| `"): continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    lab=cells[0].strip("`")
    if lab.startswith("("): continue
    lab=lab[2:-2]
    seen.add(lab)
    if lab not in heads: probs.append(f"행{i}: 라벨 {lab} 머리 없음"); continue
    h=heads[lab]
    if cells[1]!=h["kind"]: probs.append(f"행{i} {lab}: 종류 표 {cells[1]} / 본문 {h['kind']} ({h['loc']})")
    if cells[3]!=h["num"]: probs.append(f"행{i} {lab}: 번호 표 {cells[3]} / 본문 {h['num']} ({h['loc']})")
    if cells[5]!=h["sec"]: probs.append(f"행{i} {lab}: 절 표 {cells[5]} / 본문 {h['sec']} ({h['loc']})")
    nm=cells[2].replace("\*","*")
    hn=h["name"]
    if nm=="—": nm=""
    if nm!=hn: probs.append(f"행{i} {lab}: 이름 표 [{cells[2]}] / 본문 [{hn}] ({h['loc']})")
for k in order:
    if k not in seen: probs.append(f"본문 머리 {k} ({heads[k]['loc']}) 표에 없음")
print(len(probs),"differences")
for p in probs: print(p)
