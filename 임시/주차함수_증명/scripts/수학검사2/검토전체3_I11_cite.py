# -*- coding: utf-8 -*-
"""장 파일에서 라벨 인용 자리를 색인한다: 각 인용이 어느 진술의 머리/진술문/증명/준비 문단에 있는지."""
import re, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CH = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?|D):([^}]+)\}\}(.*)$")
SEC = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)[ .]")
def scan(fname):
    out=[]
    cur=None; sec=None; mode="prose"; last=None
    for ln,L in enumerate(open(os.path.join(CH,fname),encoding="utf-8"),1):
        m=SEC.match(L)
        if m: sec=m.group(2); cur=None; mode="prose"
        h=HEAD.match(L)
        if h:
            cur=f"{h.group(1)} {h.group(2)}:{h.group(3)}"; last=cur; mode="head"
        elif L.startswith("**증명"):
            mode="proof"
        elif mode=="head" and L.strip():
            mode="stmt"
        for mm in re.finditer(r"\{\{(\d+[AB]?):([^}]+)\}\}",L):
            lab=f"{mm.group(1)}:{mm.group(2)}"
            if h and lab==f"{h.group(2)}:{h.group(3)}": continue
            out.append((sec,cur if mode!="prose" else f"(준비 문단; 앞 진술 {last})",mode,ln,lab))
        if mode=="proof" and L.strip().endswith("∎"):
            mode="prose"; cur=None
    return out
if __name__=="__main__":
    files=sys.argv[1:]
    bylab=defaultdict(list)
    for f in files:
        for sec,cur,mode,ln,lab in scan(f):
            bylab[lab].append(f"{f}§{sec} L{ln} [{mode}] {cur}")
    for lab in sorted(bylab):
        print("##",lab)
        for x in bylab[lab]: print("   ",x)
