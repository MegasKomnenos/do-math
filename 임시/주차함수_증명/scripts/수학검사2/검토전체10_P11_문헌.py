# -*- coding: utf-8 -*-
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
keys = ['Konheim','Weiss','Foata','Riordan','Pollak','Celano','Aguilar','Stanley','Knuth','Flajolet','Sedgewick','Tanner','Robbins','Petersson','Janson','Ibragimov','Ahlfors','Graham','Patashnik','Fortuin','FKG','Jensen','Wallis','Corless','Lambert','Grimmett','Harris','Comtet','Faà','Apostol','Titchmarsh','Euler–Maclaurin','Euler 합','Cauchy','편각','Cayley','Lagrange','지수 공식','부분분수','표준']
for f in sorted(glob.glob(os.path.join(BASE,'장*.md'))):
    if f.endswith('장11.md'): continue
    sec=None; cur=None
    for i, ln in enumerate(open(f,encoding='utf-8').read().split('\n'),1):
        m = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)\s', ln)
        if m: sec=m.group(1); cur=None
        h = HEAD.match(ln)
        if h: cur=h.group(1)+' '+h.group(2)
        if re.match(r'\*\*(정리|명제|보조정리|따름정리)\s+\{\{[^}]+\}\}의 증명', ln):
            cur = re.search(r'\{\{([^}]+)\}\}', ln).group(1)+'의 증명'
        for k in keys:
            if k in ln:
                # 문맥
                for mm in re.finditer(re.escape(k), ln):
                    ctx = ln[max(0,mm.start()-60):mm.end()+60].replace('\n',' ')
                    print(f"{os.path.basename(f)}:{i} §{sec} [{cur}] <{k}> …{ctx}…")
