# 5절 넷째 열(여유 글자)이 그 장에서 쓰이는 1.2 전역 기호·1장 전역·1.1 변수와 (바탕, 글자체)가 겹치는지 본다.
import io,sys,re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
L=open(r"C:/math/임시/주차함수_증명/장부_v2.md",encoding='utf-8').read().split('\n')
FONT={'일반':'it','프락투어':'frak','산세리프':'sf','필기체':'cal'}
G=[]  # (glyph, base, font, chapters set, defch, ln)
for ln in range(50,289):
    c=L[ln-1].strip()[1:-1].split(' | ')
    if len(c)!=7: continue
    base,_,font=c[1].partition('·')
    f=None
    for k,v in FONT.items():
        if font.startswith(k): f=v
    if f is None: continue
    used=c[4].strip()
    chs=set(range(1,11)) if used.startswith('전 장') else set(int(x) for x in re.findall(r'\d+', used))
    m=re.match(r'^(\d+)', c[3].strip()); d=int(m.group(1)) if m else None
    if d: chs.add(d)
    G.append((c[0].strip(), base.strip(), f, chs, d, ln))
BS=chr(92)
def norm(tok):
    tok=tok.strip().strip('$').strip()
    for name,f in (('mathcal','cal'),('mathfrak','frak'),('mathsf','sf')):
        pre=BS+name
        if tok.startswith(pre):
            r=tok[len(pre):].strip().strip('{}').strip()
            return (r,f)
    return (tok,'it')
for ln in range(1185,1195):
    c=L[ln-1].strip()[1:-1].split(' | ')
    ch=int(c[0]); free=c[3]
    toks=re.findall(r'\$[^$]+\$', free)
    fs=[norm(t) for t in toks]
    blocked=defaultdict(list)
    for g,base,f,chs,d,l2 in G:
        if ch in chs or d==1:
            blocked[(base,f)].append((g,l2))
    hits=[(t,blocked[t]) for t in fs if t in blocked]
    print('장',ch,'여유',len(fs),'충돌',len(hits))
    for t,b in hits: print('   ', t, '←', b[:3])
