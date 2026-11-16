# -*- coding: utf-8 -*-
"""H14: 장부 1.2 전역 기호의 「정의 절」을 본문에서의 첫 등장 절과 비교한다(공백 제거 뒤 문자열 포함 검색; 참고용)."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
CHAPTER_RE = re.compile(r"^## (\d+)\."); SEC_RE = re.compile(r"^### (\d+\.\d+)")
BS = chr(92)
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(re.escape(prefix)+str(i)+r"[A-Z]\.md",n)))
    return out
body=[]; sec="0.0"
for name in chapter_files("장"):
    for ln_no, ln in enumerate(io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"),1):
        m=CHAPTER_RE.match(ln)
        if m: sec=f"{m.group(1)}.0"
        s=SEC_RE.match(ln)
        if s: sec=s.group(1)
        body.append((sec,name,ln_no,re.sub(r"\s+","",ln)))
def norm(s): return re.sub(r"\s+","",s)
lines=io.open(os.path.join(ROOT,"장부_v2.md"),encoding="utf-8").read().split("\n")
in12=False; out=[]
SPLIT=re.compile(",\\s*(?=[A-Za-z(]|" + BS + BS + ")")
for i,ln in enumerate(lines,1):
    if ln.startswith("### 1.2"): in12=True; continue
    if ln.startswith("### 1.3"): break
    if not in12 or not ln.startswith("| $"): continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    glyphs=cells[0]; defsec=cells[3]; chapters=cells[4]
    alts=re.findall(r"\$(.+?)\$",glyphs)
    cands=[]
    for a in alts:
        for part in SPLIT.split(a):
            cands.append(norm(part))
    found=None
    for c in cands:
        tries=[c]
        b=re.sub(r"\([^()]*\)$","",c)
        if b!=c: tries.append(b)
        for t in tries:
            if len(t)<2: continue
            for sec_,name,ln_no,txt in body:
                if t in txt:
                    found=(t,sec_,name,ln_no); break
            if found: break
        if found: break
    out.append((i,glyphs,defsec,chapters,found))
def secnum(s):
    m=re.match(r"(\d+)\.(\d+)",s); return (int(m.group(1)),int(m.group(2))) if m else None
for i,g,d,ch,f in out:
    if f is None: print(f"행{i} {g}: 본문에서 못 찾음(정의 절 {d})"); continue
    t,s,name,ln=f
    ds=[x.strip() for x in re.split(r"[,;]",re.sub(r"\(.*?\)","",d))]
    ok=any(secnum(x) and secnum(x)==secnum(s) for x in ds)
    if not ok:
        earlier=any(secnum(x) and secnum(s)<secnum(x) for x in ds)
        tag="앞선 사용" if earlier else "뒤"
        print(f"행{i} {g}: 정의 절 {d} / 첫 등장 {s} ({name}:{ln}) [{t}] {tag}")
