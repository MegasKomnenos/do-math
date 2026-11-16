# -*- coding: utf-8 -*-
"""H14: 장부 1.2 각 행의 「쓰이는 장」을, 글자 열의 첫 LaTeX 꼴(공백 제거)이 글자 그대로 나오는 장의 집합과 비교한다(참고용; 표기 변형은 못 잡는다)."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "장v2")
BS = chr(92)
def chapter_files(prefix):
    out=[]
    for i in range(1,12):
        whole=f"{prefix}{i}.md"
        if os.path.exists(os.path.join(base,whole)): out.append(whole); continue
        out.extend(sorted(n for n in os.listdir(base) if re.fullmatch(re.escape(prefix)+str(i)+r"[A-Z]\.md",n)))
    return out
chap_text={}
for name in chapter_files("장"):
    ch=int(re.match(r"장(\d+)",name).group(1))
    chap_text.setdefault(ch,"")
    chap_text[ch]+=re.sub(r"\s+","",io.open(os.path.join(base,name),encoding="utf-8").read())
SPLIT=re.compile(",\\s*(?=[A-Za-z(]|" + BS + BS + ")")
lines=io.open(os.path.join(ROOT,"장부_v2.md"),encoding="utf-8").read().split("\n")
in12=False
for i,ln in enumerate(lines,1):
    if ln.startswith("### 1.2"): in12=True; continue
    if ln.startswith("### 1.3"): break
    if not in12 or not ln.startswith("| $"): continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    glyphs=cells[0]; chapters=cells[4]
    if "전 장" in chapters: continue
    declared=set(int(x) for x in re.findall(r"\d+",chapters))
    alts=re.findall(r"\$(.+?)\$",glyphs)
    cands=[]
    for a in alts:
        for part in SPLIT.split(a):
            p=re.sub(r"\s+","",part)
            b=re.sub(r"\([^()]*\)$","",p)
            cands.append(p)
            if b!=p: cands.append(b)
    found=set()
    for c in cands:
        if len(c)<2: continue
        for ch,txt in chap_text.items():
            if c in txt: found.add(ch)
    if not found:
        print(f"행{i} {glyphs}: 못 찾음 (선언 {sorted(declared)})"); continue
    extra=sorted(found-declared); missing=sorted(declared-found)
    if extra or missing:
        print(f"행{i} {glyphs}: 선언 {sorted(declared)} / 실제 {sorted(found)}; 선언에 없는 장 {extra}; 본문에 없는 장 {missing}")
