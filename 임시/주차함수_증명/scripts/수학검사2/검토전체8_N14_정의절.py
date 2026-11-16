# -*- coding: utf-8 -*-
r"""장부 1.2의 「정의 절」과 장 파일에서 그 글자가 처음 나타나는 절을 견준다(감사 규칙 1: 정의 전 사용 0).
근사 검색: 첫 기호의 LaTeX 문자열(공백 제거)을 장 파일(공백 제거)에서 찾는다."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
CH_RE = re.compile(r"^## (\d+)\."); SEC_RE = re.compile(r"^#{3,4} (\d+\.\d+(?:\.\d+)?)")
lines=[]  # (chapter, sec, file, lineno, normalized text)
chapter=None; sec=None
for name in order:
    for ln,line in enumerate(open(os.path.join(root,"장v2",name+".md"),encoding='utf-8'),1):
        m=CH_RE.match(line)
        if m: chapter=int(m.group(1)); sec=f"{chapter}.0"
        m=SEC_RE.match(line)
        if m: sec=m.group(1)
        lines.append((chapter, sec, name, ln, line.replace(" ","").replace("\,","").replace("\!","").replace("\;","").replace("\tfrac","\frac").replace("\dfrac","\frac")))
def seckey(s):
    return tuple(int(x) for x in s.split("."))
rows=[]; insec=False
for ln_no,line in enumerate(open(os.path.join(root,"장부_v2.md"),encoding='utf-8'),1):
    if line.startswith("### 1.2"): insec=True; continue
    if line.startswith("### 1.3"): break
    if insec and line.startswith("| $"):
        cells=[c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells)>=5: rows.append((ln_no,cells[0],cells[3]))
for ln_no,sym,defsec in rows:
    first = sym.strip("$").split(", ")[0].split(",")[0].split(":=")[0]
    key = first.replace(" ","").replace("\,","")
    key = re.sub(r"\([^()]*\)$","",key)
    if len(key)<2 and not key.startswith("\\"):
        pat=re.compile(r"(?<![A-Za-z\])"+re.escape(key)+r"(?![A-Za-z])")
    else:
        pat=re.compile(re.escape(key)+r"(?![A-Za-z])")
    hit=None
    for ch,sc,name,ln,txt in lines:
        if ch==1 and sc in ("1.4","1.5"):  # 1.4 개관·1.5 좌표표는 미리 부르는 것이 설계
            continue
        if pat.search(txt): hit=(sc,name,ln); break
    ds=re.findall(r"\d+\.\d+",defsec)
    if not ds: continue
    dmin=min(ds,key=seckey)
    if hit is None:
        print(f"행{ln_no} {sym}: 검색 실패({key}) | 정의 절 {defsec}"); continue
    if seckey(hit[0])<seckey(dmin) and not hit[0].startswith(dmin+"."):
        print(f"행{ln_no} {sym}: 정의 절 {defsec} 보다 앞선 첫 출현 {hit[0]} ({hit[1]}:{hit[2]}) [키 {key}]")
