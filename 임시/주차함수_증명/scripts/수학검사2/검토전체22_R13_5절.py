import io,sys,re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L=open(r"C:/math/임시/주차함수_증명/장부_v2.md",encoding='utf-8').read().split('\n')
# 1.2 rows: lines 48..288
by=defaultdict(list); rows={}
for ln in range(48,289):
    line=L[ln-1]
    if not line.startswith('| $') and not line.startswith('| '): continue
    if line.startswith('|---') or line.startswith('| 글자'): continue
    c=line.strip()[1:-1].split(' | ')
    if len(c)!=7:
        print('1.2 CELLS', ln, len(c), line[:80]); continue
    glyph=c[0].strip(); sec=c[3].strip()
    m=re.match(r'^(\d+)\.', sec) or re.match(r'^(\d+)', sec)
    ch=m.group(1) if m else '?'
    by[ch].append((glyph,ln,sec)); rows[glyph]=(ln,sec)
print({k:len(v) for k,v in by.items()})
tot=0
for ln in range(1185,1195):
    c=L[ln-1].strip()[1:-1].split(' | ')
    ch=c[0].strip(); listed=[x.strip() for x in c[1].split('; ')] if c[1].strip() not in ('—','') else []
    exp=[g for g,_,_ in by.get(ch,[])]
    tot+=len(listed)
    for g in listed:
        if g not in exp:
            print('5절-only', ch, g, '| 1.2:', rows.get(g))
    for g,l2,sec in by.get(ch,[]):
        if g not in listed: print('1.2-only', ch, g, 'line', l2, 'sec', sec[:60])
print('total listed', tot, 'total 1.2 rows', len(rows))
for g,l2,sec in by.get('?',[]): print('?', l2, g, sec[:80])
