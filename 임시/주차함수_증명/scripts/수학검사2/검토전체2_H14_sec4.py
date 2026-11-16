# -*- coding: utf-8 -*-
"""H14: 장부_v2.md 4절(이름 사전)의 종류·이름·기록 이름·둘째 판 절·라벨을 장 파일 머리와 비교한다."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CHAPTER_RE = re.compile(r"^## (\d+)\."); SEC_RE = re.compile(r"^### (\d+\.\d+)")
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(rf"{re.escape(prefix)}{i}[A-Z]\.md",n)))
    return out
heads={}; order=[]; chapter=0; sec=""
for name in chapter_files("장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=CHAPTER_RE.match(ln)
        if m: chapter=int(m.group(1)); sec=f"{chapter}.0"; continue
        s=SEC_RE.match(ln)
        if s: sec=s.group(1); continue
        h=HEAD_RE.match(ln)
        if h:
            key=f"{h.group(2)}:{h.group(3)}"; r=ln[h.end():].lstrip(); nm=""
            if r.startswith("("):
                dep=0
                for j,ch in enumerate(r):
                    if ch=="(": dep+=1
                    elif ch==")":
                        dep-=1
                        if dep==0: nm=r[1:j]; break
            heads[key]=dict(kind=h.group(1),name=nm.strip(),sec=sec,loc=f"{name}:{ln_no}"); order.append(key)
lines=io.open(os.path.join(ROOT,"장부_v2.md"),encoding="utf-8").read().split("\n")
probs=[]; seen=set(); n=0
in4=False
for i,ln in enumerate(lines,1):
    if ln.startswith("## 4."): in4=True; continue
    if ln.startswith("## 5."): break
    if not in4 or not ln.startswith("| ") or ln.startswith("| 첫 판") or ln.startswith("|---"): continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells)<6: probs.append(f"행{i}: 열 수 {len(cells)}"); continue
    first,kind,nm,rec,sec,lab=cells
    n+=1
    if lab.startswith("{{"):
        key=lab[2:-2]; seen.add(key)
        if key not in heads: probs.append(f"행{i} {lab}: 머리 없음"); continue
        h=heads[key]
        if kind!=h["kind"]: probs.append(f"행{i} {key}: 종류 {kind} / 본문 {h['kind']} ({h['loc']})")
        if sec!=h["sec"]: probs.append(f"행{i} {key}: 절 {sec} / 본문 {h['sec']} ({h['loc']})")
        exp = nm + (("; "+rec) if rec else "")
        if exp.replace("\*","*")!=h["name"].replace("\*","*"): probs.append(f"행{i} {key}: 이름 [{exp}] / 본문 [{h['name']}] ({h['loc']})")
    else:
        # 뺌 row: label in parens or —; check no head exists
        key=lab.strip("()")
        if key in heads: probs.append(f"행{i} 뺌 {lab}: 본문에 머리 있음 ({heads[key]['loc']})")
        if sec!="뺌": probs.append(f"행{i} {lab}: 절 열 {sec} (뺌 아님)")
for k in order:
    if k not in seen: probs.append(f"본문 머리 {k} ({heads[k]['loc']}) 4절에 없음")
print(n,"rows;",len(probs),"problems")
for p in probs: print(p)
