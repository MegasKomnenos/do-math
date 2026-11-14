"""두 PDF를 자동 검사로 비교한다: 쪽 수, 줄머리 구두점·조사, 여는 괄호 줄끝, 여백 밖, TeX 유출, 대체 글꼴."""
import sys, collections, re, pymupdf as fitz
PUNCT=set(",.;:)]」』?!"); OPEN=set("(「[『{")
JOSA=("은","는","이","가","을","를","의","에","와","과","로","도","다","이고","이다","에서","으로","라","까지","부터","처럼","보다","마다","이면","면","인")
def lines_of(page):
    d=page.get_text("rawdict"); rows=[]
    for b in d["blocks"]:
        if b["type"]!=0: continue
        for l in b["lines"]:
            for s in l["spans"]:
                for c in s["chars"]:
                    if c["c"].strip(): rows.append((round(c["origin"][1]), c["origin"][0], c["c"], s["font"]))
    rows.sort(); lines=[]
    for r in rows:
        if lines and abs(lines[-1][0]-r[0])<=3: lines[-1][1].append(r)
        else: lines.append([r[0],[r]])
    out=[]
    for y,chars in lines:
        if y>790: continue
        chars.sort(key=lambda t:t[1]); out.append(chars)
    return out
def stats(path):
    doc=fitz.open(path); c=collections.Counter(); ex=collections.defaultdict(list); mm=72/25.4
    tex=re.compile(r"\[a-zA-Z]{2,}|\$")
    for pno in range(doc.page_count):
        page=doc[pno]; r=page.rect; right=r.width-24*mm; bottom=r.height-24*mm
        prev_math=False
        for chars in lines_of(page):
            txt="".join(ch[2] for ch in chars); first=chars[0]; last=chars[-1]
            if first[2] in PUNCT and first[1]<80 and not txt.startswith((".py",".json",".out",".log",".txt",".md",".tsv",".csv")): c["구두점 줄머리"]+=1; ex["구두점 줄머리"].append((pno+1,txt[:40]))
            if last[2] in OPEN and last[1]>480: c["여는 괄호 줄끝"]+=1; ex["여는 괄호 줄끝"].append((pno+1,txt[-30:]))
            ismath=("Type3" in last[3] or "KaTeX" in last[3])
            if prev_math and first[1]<80 and (txt[:2] in JOSA or (txt[:1] in JOSA and (len(txt)<2 or not('가'<=txt[1]<='힣')))): c["조사 줄머리(수식 뒤)"]+=1; ex["조사 줄머리(수식 뒤)"].append((pno+1,txt[:30]))
            prev_math=ismath
            if last[1]>right+2: c["오른쪽 여백 밖"]+=1; ex["오른쪽 여백 밖"].append((pno+1,txt[-30:]))
        t=page.get_text("text")
        if tex.search(t): c["TeX 유출 쪽"]+=1
    print(path, "쪽", doc.page_count)
    for k in ("구두점 줄머리","여는 괄호 줄끝","조사 줄머리(수식 뒤)","오른쪽 여백 밖","TeX 유출 쪽"):
        print(f"  {k}: {c[k]}")
        for e in ex[k][:6]: print("     ",e)
for p in sys.argv[1:]: stats(p)
