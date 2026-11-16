import sys,re
K=sys.argv[1]; targets=sys.argv[2].split(',')
lines=open(K+'/frontier.md',encoding='utf-8').read().split('\n')
heads=[(i,l[3:].strip()) for i,l in enumerate(lines) if l.startswith('## ')]
for idx,(i,h) in enumerate(heads):
    if not any(h==t or h.endswith(t) for t in targets): continue
    j=heads[idx+1][0] if idx+1<len(heads) else len(lines)
    sec=lines[i:j]
    print('########', h, f'(lines {i+1}-{j})')
    for l in sec:
        if l.startswith('State') or l.startswith('- '):
            print('  ', l[:int(sys.argv[3])])
    kw=[l for l in sec if re.search(r"(?i)concern|withdraw|retract|우려|철회",l) or (re.search(r"refuted",l) and not re.search(r"[refuted [^]]*] implies refuted|implies refuted",l))]
    print('   [kw lines]:', len(kw))
    for l in kw: print('     >', l[:300])
