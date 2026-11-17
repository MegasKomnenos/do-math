# 행의 글자 셀 토큰 가운데 지정한 장 파일들에서 0건인 것을, 그 토큰이 행 안에서 놓인 앞뒤 문맥과 함께 보인다(판정 보조).
import io,sys,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
row=int(sys.argv[1]); files=sys.argv[2].split(',')
L=open('장부_v2.md',encoding='utf-8').read().split('\n')[row-1]
cell=L.split(' | ')[0]
texts=''.join(open('장v2/'+f+'.md',encoding='utf-8').read() for f in files)
seen=set()
for m in re.finditer(r'\$([^$]+)\$',cell):
    t=m.group(1)
    if t in seen: continue
    seen.add(t)
    cands=[t]
    for sep in [':=','=','\in','\ge','\le','<','>']:
        if sep in t: cands.append(t.split(sep)[0].strip())
    mm=re.match(r'^(.*?)\(',t)
    if mm and mm.group(1).strip(): cands.append(mm.group(1).strip())
    for part in re.split(r',\s*',t):
        if part.strip(): cands.append(part.strip())
    if all(texts.count(c)==0 for c in cands if c):
        a=max(0,m.start()-70); b=min(len(cell),m.end()+90)
        print('ZERO [%s] ...%s...'%(t,cell[a:b].replace('\n',' ')))
