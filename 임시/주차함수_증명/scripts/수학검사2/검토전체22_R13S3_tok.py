# 장부 한 행의 첫 셀(글자)에서 $...$ 토큰을 뽑아, 지정한 장 파일에서 고정 문자열로 센다(자리 찾기 보조; 판정은 원문으로).
import io,sys,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
row=int(sys.argv[1]); files=sys.argv[2].split(','); col=int(sys.argv[3]) if len(sys.argv)>3 else 1
L=open('장부_v2.md',encoding='utf-8').read().split('\n')[row-1]
# split cells on ' | ' outside math is unreliable; use the simple split and report cell count
cells=L.split(' | ')
print('cells',len(cells))
cell=cells[col-1]
toks=re.findall(r'\$([^$]+)\$',cell)
texts={f:open('장v2/'+f+'.md',encoding='utf-8').read() for f in files}
seen=set()
def cores(t):
    c=[t]
    for sep in [':=','=','\in','\ge','\le','<','>','\sim']:
        if sep in t:
            c.append(t.split(sep)[0].strip())
    m=re.match(r'^(.*?)\(',t)
    if m and m.group(1).strip(): c.append(m.group(1).strip())
    for part in re.split(r',\s*',t):
        if part.strip() and part.strip()!=t: c.append(part.strip())
    out=[]
    for x in c:
        x=x.strip()
        if x and x not in out: out.append(x)
    return out
for t in toks:
    if t in seen: continue
    seen.add(t)
    res=[]
    for c in cores(t):
        cnt=' '.join('%s=%d'%(f,texts[f].count(c)) for f in files)
        res.append('[%s] %s'%(c,cnt))
    print(' ; '.join(res))
