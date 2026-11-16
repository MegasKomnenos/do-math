import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files=['장v2/장%s.md'%c for c in ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']]
# build statement text blocks and section texts
blocks={}  # label -> text (head through ∎)
sections={} # '2.5' -> text
headpat=re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}')
for f in files:
    sec=None; cur=None
    for line in open(f,encoding='utf-8'):
        m0=re.match(r'^###\s+(\d+\.\d+)',line)
        if m0: sec=m0.group(1); sections.setdefault(sec,''); cur=None
        if sec: sections[sec]+=line
        mh=headpat.match(line)
        mp=re.match(r'^\*\*(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}의 증명',line)
        if mp: cur=mp.group(2)
        elif mh: cur=mh.group(2)
        if cur: blocks[cur]=blocks.get(cur,'')+line
        if '∎' in line: cur=None
rows=[]
for l in open('장v2/장11.md',encoding='utf-8'):
    if l.startswith('| ') and '|' in l[2:] and ('*' in l.split('|')[1]) :
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        if len(cells)==3: rows.append(cells)
kw={'Konheim':['Konheim'],'Foata':['Pollak','Foata'],'Celano':['Celano'],'Aguilar':['Aguilar'],'Corollary 5.1.6':['지수 공식'],'Proposition 5.3.2':['Cayley'],'Theorem 5.4.2':['Lagrange'],'Knuth, *The Art':['갈고리'],'Flajolet':['임계값','T(1/e)'],'Robbins':['Robbins'],'Petersson':['Petersson'],'Janson':['Janson'],'Ibragimov':['Ibragimov'],'Ahlfors':['Cauchy','편각','부분분수','coth'],'Graham':['Euler'],'Fortuin':['FKG'],'Jensen':['Jensen'],'Wallis':['Wallis'],'Corless':['Lambert','Corless'],'Tanner':['Tanner'],'OEIS':['제타','zeta'],'Grimmett':['Harris'],'Harris, *A lower':['Harris'],'Comtet':['Faà'],'Apostol':['Euler'],'Titchmarsh':['Titchmarsh','Euler']}
for cells in rows:
    src=cells[0]; place=cells[2]
    keys=None
    for k,v in kw.items():
        if k in src: keys=v; break
    if not keys: print('?? no kw for',src[:40]); continue
    labs=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',place)
    secs=re.findall(r'(\d+\.\d+)절',place)
    for L in labs:
        t=blocks.get(L,'')
        if not any(k in t for k in keys):
            print(f'[{src[:30]}] {L}: 진술 본문에 {keys} 없음')
    for s in secs:
        t=sections.get(s,'')
        if not any(k in t for k in keys):
            print(f'[{src[:30]}] {s}절: 절 본문에 {keys} 없음')
print('rows checked',len(rows))
