# J12: 부록 D 자료 줄의 경로가 실제로 있는지 확인 (records/ 는 기록 원본, 원고_자료/ 는 자료 묶음)
import re,glob,os,sys
REC="C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
PROJ="C:/math/임시/주차함수_증명"
files=sys.argv[1:]
def expand(p):
    # p like records/r81e7051…/evidence/x or records/<fullid>/...
    parts=p.split('/')
    if parts[0]=='records':
        rid=parts[1].rstrip('…')
        cands=glob.glob(os.path.join(REC,rid+'*'))
        if not cands: return None
        return os.path.join(cands[0],*parts[2:])
    if parts[0]=='원고_자료':
        return os.path.join(PROJ,p)
    return None
for f in files:
    txt=open(f,encoding='utf-8').read()
    for m in re.finditer(r'\*\*자료\.\*\*(.*)',txt):
        line=m.group(1)
        prefix_records = '경로 접두는 `records/`' in line
        lastdir=None; missing=[]; total=0
        for tok in re.findall(r'`([^`]+)`',line):
            tok=tok.strip()
            if tok.startswith('--') or ' ' in tok or tok in ('records/',): continue
            if re.match(r'^r[0-9a-f]{7}',tok) and prefix_records: tok='records/'+tok
            if tok.startswith('records/') or tok.startswith('원고_자료/'):
                full=expand(tok)
                if full is None: missing.append(tok); total+=1; continue
                lastdir=os.path.dirname(full) if not full.endswith('/') else full
            else:
                if lastdir is None: continue
                full=os.path.join(lastdir,tok)
            total+=1
            # glob for wildcard
            if '*' in full:
                if not glob.glob(full): missing.append(tok)
            elif not os.path.exists(full): missing.append(tok)
        head=txt[:m.start()].rfind('### D.')
        name=txt[head:head+60].split('\n')[0]
        print(os.path.basename(f),'|',name[:50],'| checked',total,'| missing',missing)
