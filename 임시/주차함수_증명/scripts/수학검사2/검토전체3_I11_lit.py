# -*- coding: utf-8 -*-
"""11.4 문헌 표 대조: 저자 이름이 본문 어디에 나오는지(절·진술) 색인한다."""
import re, os, sys, io, glob
sys.path.insert(0, os.path.dirname(__file__))
from 검토전체3_I11_index import CH
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?|D):([^}]+)\}\}(.*)$")
DHEAD = re.compile(r"^### D\.\{\{D:([^}]+)\}\}")
SEC = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)[ .]")
names = sys.argv[1:]
for f in sorted(glob.glob(os.path.join(CH,"*.md"))):
    if os.path.basename(f) in ("장11.md","부록B.md","부록C.md"): continue
    cur=None; sec=None; mode="prose"
    for ln,L in enumerate(open(f,encoding="utf-8"),1):
        m=SEC.match(L)
        if m: sec=m.group(2); cur=None; mode="prose"
        h=HEAD.match(L); dh=DHEAD.match(L)
        if h: cur=f"{h.group(1)} {h.group(2)}:{h.group(3)}"; mode="head"
        elif dh: cur=f"D.{dh.group(1)}"; mode="D"
        elif L.startswith("**증명"): mode="proof"
        elif mode=="head" and L.strip(): mode="stmt"
        for nm in names:
            if re.search(nm, L):
                ctx = cur if (mode!="prose" or cur and cur.startswith("D.")) else f"(산문; 앞 진술 {cur})"
                print(f"{nm:12s} {os.path.basename(f)} §{sec} L{ln} [{mode}] {ctx}")
        if mode=="proof" and L.strip().endswith("∎"): mode="prose"; cur=None
