# -*- coding: utf-8 -*-
"""11.3절 입력 표: 각 입력 라벨이 9장·10장의 어느 진술 블록(머리+증명)과 정리 7:old-6-22의 증명에 나타나는지 센다."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\} [\(\[]")
def blocks(fname):
    t = open(root+fname, encoding="utf-8").read().split("\n")
    out = {}; cur=None; buf=[]; sec=None; secs={}
    for l in t:
        if l.startswith("### "): 
            if cur: out[cur]="\n".join(buf); cur=None; buf=[]
            sec=l[4:].split(" ")[0]; continue
        m = HEAD.match(l)
        if m:
            if cur: out[cur]="\n".join(buf)
            cur=m.group(2); buf=[l]; secs[cur]=sec
            # block ends at ∎ line
        elif cur:
            buf.append(l)
            if "∎" in l: out[cur]="\n".join(buf); cur=None; buf=[]
    if cur: out[cur]="\n".join(buf)
    return out, secs
b9,s9 = blocks("장9.md"); b10,s10 = blocks("장10.md"); b7,s7 = blocks("장7B.md")
proof622 = b7["7:old-6-22"]
ch11 = open(root+"장11.md", encoding="utf-8").read().split("\n")
in_tables=False
for l in ch11:
    if l.startswith("**공유 입력") or l.startswith("**첫째 증명") or l.startswith("**둘째 증명"): print("\n####", l); continue
    if not l.startswith("| ") or l.startswith("| 입력") or l.startswith("|---"): continue
    cells=[c.strip() for c in l.strip().strip("|").split(" | ")]
    if len(cells)<3: continue
    labs = re.findall(r"\{\{(\d+[AB]?:[^}]+)\}\}", cells[0])
    print("\n행:", cells[0][:120])
    for lab in labs:
        in9=[k for k,v in b9.items() if "{{"+lab+"}}" in v]
        in10=[k for k,v in b10.items() if "{{"+lab+"}}" in v]
        p622 = "{{"+lab+"}}" in proof622
        print(f"  {lab}: 9장={in9} | 10장={in10} | 6-22증명={p622}")
    print("  표 첫째:", cells[2][:300])
    if len(cells)>3: print("  표 둘째:", cells[3][:300])
