# -*- coding: utf-8 -*-
# 2절 둘째 칸·3절 둘째 칸의 $...$ 토큰과 「」 낱말 가운데 장 파일(부록 A·B·C 제외)에 0회인 것을 낸다(후보; 원문을 읽고 판정).
import re, io, glob, os, sys
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lines = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
body = ''
for f in sorted(glob.glob(os.path.join(base, '장v2', '*.md'))):
    if os.path.basename(f)[:3] in ('부록A', '부록B', '부록C'): continue
    body += io.open(f, encoding='utf-8').read() + '\n'
def norm(s):
    return re.sub(r'\s+', '', s.replace('^\prime', "'").replace('\prime', "'").replace('{T}', 'T'))
nb = norm(body)
def cells(ln):
    out_=[]; cur=''; inm=False; inb=False
    s=ln.strip()
    if s.startswith('|'): s=s[1:]
    if s.endswith('|'): s=s[:-1]
    for ch in s:
        if ch=='`': inb=not inb
        elif ch=='$' and not inb: inm=not inm
        if ch=='|' and not inm and not inb:
            out_.append(cur.strip()); cur=''
        else: cur+=ch
    out_.append(cur.strip()); return out_
for a,b in ((365,444),(450,687)):
    for i in range(a-1,b):
        c = cells(lines[i])
        if len(c)!=4: continue
        cell = c[1]
        if cell.startswith('뺌'): continue
        for t in re.findall(r'\$([^$]+)\$', cell):
            if len(t)<4: continue
            if norm(t) not in nb:
                out.write('%d\t$%s$\n' % (i+1, t))
        for t in re.findall(r'「([^」]+)」', cell):
            if norm(t) not in nb:
                out.write('%d\t「%s」\n' % (i+1, t))
