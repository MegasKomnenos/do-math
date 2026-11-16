# -*- coding: utf-8 -*-
"""H14: 의존지도_v2.md 1절의 절·요지·지위·입력(머리/본문 인용)·부록 D 계산 열을 장 파일에서 독립 재계산해 비교한다.
간선 규칙은 파견문대로(머리 줄 인용; 머리 다음부터 다음 머리(진술 머리 또는 「…의 증명.」 머리) 전까지의 본문 인용; 뒤로 미룬 증명 단락 인용)."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
BS = chr(92)
LABEL_RE = re.compile(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DEFER_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*")
SEC_RE = re.compile(r"^### (\d+\.\d+)"); CH_RE = re.compile(r"^## (\d+)\.")
RID = re.compile(r"\br[0-9a-f]{7}\b")
CELL_SPLIT = re.compile("(?<!" + BS + BS + ")" + BS + "|")
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(re.escape(prefix)+str(i)+r"[A-Z]\.md",n)))
    return out
st={}; order=[]; defers=[]
for name in chapter_files("장"):
    lines=io.open(os.path.join(base,name),encoding="utf-8").read().split("\n")
    marks=[]; sec=""
    for i,ln in enumerate(lines):
        m=CH_RE.match(ln)
        if m: sec=m.group(1)
        s=SEC_RE.match(ln)
        if s: sec=s.group(1); continue
        d=DEFER_RE.match(ln)
        if d: marks.append((i,"defer",f"{d.group(2)}:{d.group(3)}",sec)); continue
        h=HEAD_RE.match(ln)
        if h: marks.append((i,"head",f"{h.group(2)}:{h.group(3)}",sec))
    for j,(i,kind,key,sec) in enumerate(marks):
        end=marks[j+1][0] if j+1<len(marks) else len(lines)
        head=lines[i]; body=lines[i+1:end]
        if kind=="head":
            r=head[HEAD_RE.match(head).end():].lstrip(); nm=""; stt=""
            if r.startswith("("):
                dep=0
                for t,ch in enumerate(r):
                    if ch=="(": dep+=1
                    elif ch==")":
                        dep-=1
                        if dep==0: nm=r[1:t]; r=r[t+1:].lstrip(); break
            if r.startswith("["):
                stt=r[1:r.index("]")]
            st[key]=dict(sec=sec,name=nm.strip(),bracket=stt,loc=f"{name}:{i+1}",
                         hl=set(LABEL_RE.findall(head))-{key}, bl=set(), kind=HEAD_RE.match(head).group(1))
            for ln in body: st[key]["bl"].update(LABEL_RE.findall(ln))
            order.append(key)
        else:
            defers.append((key,[head]+body,f"{name}:{i+1}"))
for key,bl,loc in defers:
    if key not in st: print("[경고] 미룬 증명의 진술 없음",key,loc); continue
    for ln in bl: st[key]["bl"].update(LABEL_RE.findall(ln))
    st[key]["defer"]=loc
for k in st: st[k]["bl"]-= (st[k]["hl"]|{k})
def status(b):
    if not b: return "정의"
    if ";" in b:
        return b.split(";",1)[0].strip()
    if RID.findall(b) and not RID.sub("",b).strip(" ,"): return "정의"
    return b.strip()
appd={}
for ln in io.open(os.path.join(base,"장11.md"),encoding="utf-8").read().split("\n"):
    if ln.startswith("| 부록 D.{{D:"):
        c=[x.strip() for x in ln.strip().strip("|").split("|")]
        dm=re.search(r"\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}",c[0])
        for k in LABEL_RE.findall(c[1]): appd.setdefault(k,[]).append((dm.group(1),c[2]))
tab=io.open(os.path.join(ROOT,"의존지도_v2.md"),encoding="utf-8").read().split("\n")
probs=[]; seen=set(); n=0
for i,ln in enumerate(tab,1):
    if ln.startswith("## 2."): break
    if not ln.startswith("| `{{"): continue
    c=[x.strip() for x in CELL_SPLIT.split(ln.strip()[1:-1])]
    if len(c)!=10: probs.append(f"행{i}: 칸 수 {len(c)}"); continue
    key=c[0].strip("`{}"); n+=1; seen.add(key)
    if key not in st: probs.append(f"행{i} {key}: 머리 없음"); continue
    s=st[key]
    if c[1]!=s["sec"]: probs.append(f"행{i} {key}: 절 {c[1]} / 본문 {s['sec']}")
    gist=c[3].replace("／","|")
    if s["name"] and gist!=s["name"]: probs.append(f"행{i} {key}: 요지 [{c[3]}] / 머리 [{s['name']}]")
    stt=status(s["bracket"])
    if c[4]!=stt: probs.append(f"행{i} {key}: 지위 [{c[4]}] / 머리 [{stt}]")
    inp=c[5]
    if inp=="—": hl=set(); bl=set()
    else:
        parts=inp.split("본문 인용:")
        hl=set(LABEL_RE.findall(parts[0])); bl=set(LABEL_RE.findall(parts[1])) if len(parts)>1 else set()
    if hl!=s["hl"]: probs.append(f"행{i} {key}: 머리 인용 표 {sorted(hl)} / 본문 {sorted(s['hl'])}")
    if bl!=s["bl"]: probs.append(f"행{i} {key}: 본문 인용 표에만 {sorted(bl-s['bl'])} / 본문에만 {sorted(s['bl']-bl)}")
    a=c[8]; exp=appd.get(key,[])
    tn=set(re.findall(r"\{\{D:([A-Za-z0-9\-]+)\}\}",a)); en=set(d for d,_ in exp)
    if tn!=en: probs.append(f"행{i} {key}: 부록 D 열 {sorted(tn)} / 11.2 표 {sorted(en)}")
    else:
        for dn,grade in exp:
            m=re.search(r"\{\{D:"+re.escape(dn)+r"\}\}\(([^)]*)\)",a)
            if not m or m.group(1)!=grade: probs.append(f"행{i} {key}: 부록 D 산술 등급 [{a}] / 11.2 [{dn}({grade})]")
for k in order:
    if k not in seen: probs.append(f"본문 머리 {k} 표에 없음")
print(n,"rows;",len(probs),"differences")
for p in probs: print(p)
