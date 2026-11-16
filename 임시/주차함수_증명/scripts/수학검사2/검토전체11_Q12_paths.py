# Q12: 부록 D(장2~장6) 「자료」 줄의 경로 존재 확인 (기록 저장소 + 원고_자료). 돌고 있는 critical_window_rerun/ 안은 보지 않는다.
import re,os,glob,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
REC='C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records'
ROOT='C:/math/임시/주차함수_증명'
files=['장v2/부록D_장2.md','장v2/부록D_장3.md','장v2/부록D_장4.md','장v2/부록D_장5A.md','장v2/부록D_장5B.md','장v2/부록D_장6.md']
def recdir(rid):
    d=glob.glob(os.path.join(REC,rid+'*')); return d[0] if d else None
def to_abs(p):
    p=p.replace('…','')
    if p.startswith('records/'): p=p[8:]
    m=re.match(r'^(r[0-9a-f]{7})[0-9a-f]*/?(.*)$',p)
    if m:
        d=recdir(m.group(1)); 
        return None if d is None else os.path.join(d,m.group(2))
    if p.startswith('원고_자료/'): return os.path.join(ROOT,p)
    return None
def exists(a):
    if a is None: return False
    if any(ch in a for ch in '*?'): return bool(glob.glob(a))
    return os.path.exists(a)
missing=[];total=0;skipped=0
for f in files:
    txt=open(os.path.join(ROOT,f),encoding='utf-8').read()
    for tag,body in re.findall(r'^### D\.\{\{D:([^}]+)\}\}(.*?)(?=^### D\.|\Z)',txt,flags=re.M|re.S):
        m=re.search(r'^\*\*자료\.\*\*\s*(.*)$',body,flags=re.M)
        if not m: continue
        toks=[t.strip() for t in re.findall(r'`([^`]+)`',m.group(1))]
        bases=[]  # 후보 디렉토리(최근 절대 경로의 디렉토리와 그 상위들)
        for t in toks:
            if ' ' in t or t.startswith('-') or '.' not in t and '/' not in t: continue
            if 'critical_window_rerun' in t or (t in ('cert3/','orig/','cache/','logs/','cert/A00.json','G13.json','cert/*_recert_first.json') and tag=='critical-window-rig'): skipped+=1; continue
            total+=1
            a=to_abs(t)
            cands=[a] if a else []
            if a is None or not exists(a):
                for b in bases:
                    cands.append(os.path.join(b,t))
            ok=[c for c in cands if exists(c)]
            if ok:
                hit=ok[0]
                d=os.path.dirname(hit.rstrip('/'))
                # 새 기준 디렉토리: 적중 파일의 디렉토리와 상위 3단계
                nb=[]; x=d
                for _ in range(4):
                    nb.append(x); x=os.path.dirname(x)
                bases=nb+[b for b in bases if b not in nb]
            else:
                missing.append((tag,t))
print('checked',total,'skipped(rerun folder)',skipped,'missing',len(missing))
for m in missing: print(' ',m[0],'|',m[1])
