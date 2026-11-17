# R12: 「자료」 줄의 경로가 실제로 있는지 (읽기 전용)
import re,os,glob,sys
ROOT=r"C:/math/임시/주차함수_증명"
REC=r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
recdirs={d[:8]:d for d in os.listdir(REC)}
bundle=ROOT+'/원고_자료'
for fn in ['부록D_장7A.md','부록D_장7B.md','부록D_장8.md','부록D_장9.md']:
    txt=open(ROOT+'/장v2/'+fn,encoding='utf-8').read()
    print('=====',fn)
    # split into items
    for m in re.finditer(r'\*\*자료\.\*\*(.*?)\n\n',txt,flags=re.S):
        line=m.group(1)
        toks=re.findall(r'`([^`]+)`',line)
        cur_rec=None; cur_dir=None; cur_sess=None
        for t in toks:
            t0=t
            if t.startswith('records/'):
                mm=re.match(r'records/(r[0-9a-f]{7})…/(.*)',t)
                rid,rel=mm.group(1),mm.group(2)
                cur_rec=rid; 
                p=os.path.join(REC,recdirs.get(rid,'??'),rel)
                ok=os.path.exists(p)
                cur_dir=os.path.dirname(p) if not os.path.isdir(p) else p
                # bundle copy?
                base=os.path.basename(rel.rstrip('/'))
                inb=os.path.exists(os.path.join(bundle,rid,base)) or os.path.exists(os.path.join(bundle,rid,rel)) or bool(glob.glob(os.path.join(bundle,rid,'*'+base))) or bool(glob.glob(os.path.join(bundle,rid,'**',base),recursive=True))
                if not ok or not inb: print('  REC',ok,'BUNDLE',inb,t)
                cur_sess=None
            elif t.startswith('원고_자료/'):
                p=os.path.join(ROOT,t)
                ok=os.path.exists(p)
                cur_sess=p if os.path.isdir(p) else os.path.dirname(p)
                if not ok: print('  SESS missing',t)
            else:
                if ' ' in t or t.startswith('python') or '…' in t or '*' in t: continue
                if not re.search(r'\.(py|txt|json|c|npy|out|md|jsonl|log|sh)$',t) and not t.endswith('/'): continue
                cands=[]
                if cur_sess: cands.append(os.path.join(cur_sess,t))
                if cur_dir: cands.append(os.path.join(cur_dir,t))
                if cur_rec: cands+=glob.glob(os.path.join(REC,recdirs[cur_rec],'**',t),recursive=True)
                if not any(os.path.exists(c) for c in cands): print('  REL missing?',t,'(ctx',cur_rec, os.path.basename(cur_sess) if cur_sess else None,')')
