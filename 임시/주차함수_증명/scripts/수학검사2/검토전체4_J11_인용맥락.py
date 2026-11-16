import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = {'9':'장v2/장9.md','10':'장v2/장10.md','7B':'장v2/장7B.md'}
headpat = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}')
proofpat = re.compile(r'^\*\*(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}의 증명')
ctx = {}  # label -> list of (file, line, context)
for ch,f in files.items():
    cur = '준비 문단(절 첫머리)'; sec=''
    mode='prep'
    for i,line in enumerate(open(f,encoding='utf-8'),1):
        m0=re.match(r'^###\s+(\d+\.\d+)',line)
        if m0:
            sec=m0.group(1); cur=f'{sec} 준비 문단'; mode='prep'; continue
        mp=proofpat.match(line)
        mh=headpat.match(line)
        if mp:
            cur=f'{mp.group(1)} {mp.group(2)}의 증명(따로)'; mode='proof'
        elif mh:
            cur=f'{mh.group(1)} {mh.group(2)}'; mode='head'
        elif line.startswith('**증명') :
            cur=cur.replace('(머리)','')+'의 증명'; mode='proof'
        elif line.strip()=='' :
            pass
        # end of proof marker ∎ -> after this line, back to prep
        labels=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',line)
        where = cur if mode!='head' else cur+'(머리/진술)'
        for L in labels:
            if L.split(':')[0] in ('9','10') and ch in ('9','10') and False: pass
            ctx.setdefault(L,[]).append((ch,i,sec,where))
        if '∎' in line and mode=='proof':
            cur=f'{sec} 준비 문단'; mode='prep'
        if mode=='head' and line.strip().endswith('∎'):
            cur=f'{sec} 준비 문단'; mode='prep'
targets = sys.argv[1:] if len(sys.argv)>1 else None
for L in sorted(ctx):
    if targets and L not in targets: continue
    if L.split(':')[0] in ('9','10') : continue   # only earlier-chapter inputs
    print('##', L)
    seen=set()
    for ch,i,sec,where in ctx[L]:
        key=(ch,where)
        if key in seen: continue
        seen.add(key)
        print(f'   장{ch} L{i} [{sec}] {where}')
