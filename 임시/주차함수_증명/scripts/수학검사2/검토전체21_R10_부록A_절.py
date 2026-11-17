# 부록 A 각 행의 기호를 장 파일에서 처음 나타나는 자리와 비교한다(고정 문자열 검색).
import re,sys
chs=["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
sec={}
texts={}
for c in chs:
    lines=open(f"장v2/{c}.md",encoding="utf-8").read().split("\n")
    texts[c]=lines
    cur=None;m=[]
    for i,l in enumerate(lines):
        h=re.match(r"^#{2,4} (\d+(?:\.\d+)*)",l)
        if h: cur=h.group(1)
        m.append(cur)
    sec[c]=m
A=open("장v2/부록A.md",encoding="utf-8").read().split("\n")
def first_occ(tok):
    for c in chs:
        for i,l in enumerate(texts[c]):
            if tok in l:
                return c,i+1,sec[c][i]
    return None
for l in A:
    if not l.startswith("| $"): continue
    cells=[x.strip() for x in l.strip().strip("|").split(" | ")]
    if len(cells)<3: continue
    symcell,claim=cells[0],cells[2]
    toks=re.findall(r"\$([^$]+)\$",symcell)
    toks2=[]
    for t in toks:
        for part in re.split(r",\s*",t):
            part=part.strip()
            part=re.sub(r"(:=|=).*$","",part).strip()
            if part: toks2.append(part)
    res=[]
    for t in toks2:
        r=first_occ(t)
        res.append((t,r))
    claimed=re.findall(r"\d+\.\d+",claim)
    found=[r[2] for t,r in res if r]
    flag=""
    if any(r is None for t,r in res): flag+=" NOTFOUND"
    if found and claimed and not any(f in claimed for f in found): flag+=" MISMATCH"
    print(f"{symcell[:60]:60s} | 주장 {claim:14s} | 발견 {[(t,r) for t,r in res]}{flag}")
