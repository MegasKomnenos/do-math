# -*- coding: utf-8 -*-
"""11.4절 문헌 표: 저자명이 본문(장·부록 D)에 나타나는 자리(진술 블록 또는 절)를 모은다."""
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
HEAD = re.compile(r"\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?:[^}]+)\}\} [\(\[]")
names = ["Konheim","Foata","Pollak","Celano","Aguilar","Stanley","Knuth","Flajolet","Robbins","Petersson","Janson","Ibragimov","Ahlfors","Graham","Fortuin","FKG","Jensen","Wallis","Corless","Lambert","Tanner","Grimmett","Harris","Comtet","Faà","Apostol","Titchmarsh","Euler","Cauchy","편각","Cayley","Lagrange","지수 공식","갈고리","표준"]
files = sorted(glob.glob(root+"장*.md"))+sorted(glob.glob(root+"부록D_*.md"))
res = {n:{} for n in names}
for f in files:
    fn=f.split("/")[-1].replace("\\","/").split("/")[-1]
    cur=None; sec=None; last_end=True
    for l in open(f,encoding="utf-8"):
        m=re.match(r"###+ (\d+\.\d+(\.\d+)?)",l)
        if m: sec=m.group(1); cur=None
        m=re.match(r"### D\.\{\{D:([^}]+)\}\}",l)
        if m: cur="D:"+m.group(1)
        h=HEAD.match(l)
        if h: cur=h.group(2)
        for n in names:
            if n in l:
                res[n].setdefault(fn,set()).add(cur if cur else "절 "+str(sec))
        if "∎" in l and not fn.startswith("부록D"): cur=None
for n in names:
    print("##",n)
    for fn,s in res[n].items(): print("   ",fn, sorted(s))
