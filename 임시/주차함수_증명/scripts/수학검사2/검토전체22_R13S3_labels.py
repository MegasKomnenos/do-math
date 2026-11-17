import json,io,sys,re,glob,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
heads=json.load(open('scripts/수학검사2/검토전체22_R13_heads.json',encoding='utf-8'))
H={h['label']:h for h in heads if not h.get('proof')}
txt={}
for f in glob.glob('장v2/*.md'):
    txt[os.path.basename(f)]=open(f,encoding='utf-8').read()
lines=open('장부_v2.md',encoding='utf-8').read().split('\n')
lo,hi=int(sys.argv[1]),int(sys.argv[2])
for n in range(lo,hi+1):
    L=lines[n-1]
    for m in re.finditer(r'(\S{0,6})\s?`?\{\{([0-9A-Z]+:[^}]+)\}\}`?(\([^)]{1,6}\))?',L):
        pre,lab,part=m.group(1),m.group(2),m.group(3) or ''
        h=H.get(lab)
        if h:
            kind_ok = (h['kind'] in pre) or not any(k in pre for k in ['정의','정리','보조정리','명제','따름정리'])
            # 보조정리 contains 정리: handle
            if '보조정리' in pre: kind_ok = h['kind']=='보조정리'
            elif '따름정리' in pre: kind_ok = h['kind']=='따름정리'
            elif '정리' in pre: kind_ok = h['kind']=='정리'
            print(n, lab, part, '|', pre, '->', h['kind'], h['sec'], h['num'], '' if kind_ok else '  <<< KIND?')
        else:
            where=[f for f,t in txt.items() if '{{'+lab+'}}' in t]
            print(n, lab, part, '|', pre, '-> NOT A HEAD; occurs in', where if where else 'NOWHERE <<<')
