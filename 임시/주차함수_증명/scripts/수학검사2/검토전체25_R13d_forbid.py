# -*- coding: utf-8 -*-
# 장부 2절 셋째 칸·3절 넷째 칸의 「」 낱말과 $...$ 토큰을 장 파일에서 센다(자리를 찾는 용도; 판정은 원문을 읽고 한다).
import re, io, glob, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lines = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
files = {}
for f in sorted(glob.glob(os.path.join(base, '장v2', '*.md'))):
    files[os.path.basename(f)[:-3]] = io.open(f, encoding='utf-8').read().split('\n')
mode = sys.argv[1]  # 'q2w' words in sec2 col3, 'q2s' symbols in sec2 col3, 'q3w' words in sec3 col4, 'q3p' plain col4
def cells(ln):
    # split on ' | ' outside $...$ and `...`
    out=[]; cur=''; inm=False; inb=False; i=0
    s=ln.strip()
    if s.startswith('|'): s=s[1:]
    if s.endswith('|'): s=s[:-1]
    while i<len(s):
        ch=s[i]
        if ch=='`': inb=not inb
        elif ch=='$' and not inb: inm=not inm
        if ch=='|' and not inm and not inb:
            out.append(cur.strip()); cur=''
        else: cur+=ch
        i+=1
    out.append(cur.strip())
    return out
def count(tok):
    res=[]
    for fn, ls in files.items():
        if fn in ('부록A','부록C','부록B'): continue
        for j,l in enumerate(ls):
            if tok in l: res.append((fn,j+1))
    return res
rng = range(363,445) if mode.startswith('q2') else range(450,688)
col = 2 if mode.startswith('q2') else 3
for i in rng:
    ln = lines[i]
    c = cells(ln)
    if len(c)!=4:
        print('!! row', i+1, 'cells', len(c)); continue
    cell = c[col]
    if mode.endswith('w'):
        toks = re.findall(r'「([^」]+)」', cell)
    elif mode.endswith('s'):
        toks = re.findall(r'\$([^$]+)\$', cell)
    else:
        toks = [t.strip() for t in re.split(r'[,;]', re.sub(r'（[^）]*）|\([^)]*\)', '', cell)) if t.strip()]
    for t in toks:
        r = count(t)
        if r:
            print('%d\t%s\t%d\t%s' % (i+1, t, len(r), ' '.join('%s:%d'%x for x in r[:12])))
