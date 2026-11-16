# -*- coding: utf-8 -*-
"""장부 1.2의 「쓰이는 장」 열을 장 파일에서 글자가 실제로 나타나는 장과 견준다(근사: 첫 글자의 LaTeX 문자열 검색)."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
files = {1:["장1"],2:["장2"],3:["장3"],4:["장4"],5:["장5A","장5B"],6:["장6"],7:["장7A","장7B"],8:["장8"],9:["장9"],10:["장10"],11:["장11"]}
text = {ch: "\n".join(open(os.path.join(root,"장v2",f+".md"),encoding='utf-8').read() for f in fs) for ch,fs in files.items()}
def norm(s):
    s = s.replace(" ","").replace("\,","").replace("\!","").replace("\;","")
    s = s.replace("\tfrac","\frac").replace("\dfrac","\frac")
    return s
ntext = {ch: norm(t) for ch,t in text.items()}
rows=[]
insec=False
for ln_no,line in enumerate(open(os.path.join(root,"장부_v2.md"),encoding='utf-8'),1):
    if line.startswith("### 1.2"): insec=True; continue
    if line.startswith("### 1.3"): break
    if insec and line.startswith("| $"):
        cells=[c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells)<5: continue
        sym=cells[0]; used=cells[4]
        rows.append((ln_no,sym,used))
def parse_used(u):
    if "전 장" in u: return set(range(1,12))
    return set(int(x) for x in re.findall(r"\d+",u))
for ln_no,sym,used in rows:
    # 첫 기호(쉼표로 나뉜 첫 항목)
    first = sym.strip("$").split(", ")[0].split(",")[0]
    first = first.split(":=")[0]
    key = norm(first)
    # 인수 괄호 제거: $g(x)$ -> g(  ; $A_\ell(x)$ -> A_\ell
    key = re.sub(r"\([^()]*\)$","",key)
    if len(key)<2 and not key.startswith("\\"): 
        # 단일 글자: 단어 경계로 검색
        pat = re.compile(r"(?<![A-Za-z\])"+re.escape(key)+r"(?![A-Za-z])")
    else:
        pat = re.compile(re.escape(key)+r"(?![A-Za-z])")
    found = {ch for ch,t in ntext.items() if pat.search(t)}
    declared = parse_used(used)
    if found != declared:
        print(f"행{ln_no} {sym} | 장부: {sorted(declared)} | 검색({key}): {sorted(found)} | 장부만: {sorted(declared-found)} | 검색만: {sorted(found-declared)}")
