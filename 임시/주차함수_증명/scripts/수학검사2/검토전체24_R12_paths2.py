# R12: 「자료」 줄의 기록 파일이 (1) 기록에 그 이름으로 있고 (2) 묶음 원고_자료/<식별자>/ 에 있는지 (엄격)
import re,os,glob
ROOT=r"C:/math/임시/주차함수_증명"
REC=r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
recdirs={d[:8]:d for d in os.listdir(REC)}
bundle=ROOT+'/원고_자료'
def in_bundle(rid,base):
    hits=[p for p in glob.glob(os.path.join(bundle,rid,'**','*'),recursive=True) if os.path.basename(p)==base or os.path.basename(p).endswith('__'+base)]
    return bool(hits)
for fn in ['부록D_장7A.md','부록D_장7B.md','부록D_장8.md','부록D_장9.md']:
    txt=open(ROOT+'/장v2/'+fn,encoding='utf-8').read()
    print('=====',fn)
    for m in re.finditer(r'\*\*자료\.\*\*(.*?)\n\n',txt,flags=re.S):
        line=m.group(1)
        toks=re.findall(r'`([^`]+)`',line)
        cur=None; curdir=None; sess=False
        for t in toks:
            if t.startswith('records/'):
                mm=re.match(r'records/(r[0-9a-f]{7})…/(.*)',t); rid,rel=mm.group(1),mm.group(2); cur=rid; sess=False
                p=os.path.join(REC,recdirs[rid],rel)
                if '*' in rel:
                    g=glob.glob(p); print('  glob',t,len(g),'in record;', sum(in_bundle(rid,os.path.basename(x)) for x in g),'in bundle'); curdir=os.path.dirname(p); continue
                if os.path.isdir(p):
                    curdir=p
                    files=[x for x in glob.glob(os.path.join(p,'**','*'),recursive=True) if os.path.isfile(x)]
                    miss=[os.path.relpath(x,p) for x in files if not in_bundle(rid,os.path.basename(x))]
                    print('  DIR',t,len(files),'files; not in bundle:',len(miss), miss[:6])
                    continue
                curdir=os.path.dirname(p)
                if not os.path.exists(p): print('  NOT IN RECORD',t)
                elif not in_bundle(rid,os.path.basename(rel)): print('  not in bundle',t)
            elif t.startswith('원고_자료/'):
                sess=True
            elif not sess and cur and re.search(r'\.(py|txt|json|c|npy|out|md|jsonl|log|sh)$',t) and ' ' not in t and '*' not in t and '…' not in t:
                hits=glob.glob(os.path.join(REC,recdirs[cur],'**',t),recursive=True)
                if not hits: print('  NOT IN RECORD (bare)',t,'ctx',cur)
                elif not in_bundle(cur,os.path.basename(t)): print('  not in bundle (bare)',t,'ctx',cur)
