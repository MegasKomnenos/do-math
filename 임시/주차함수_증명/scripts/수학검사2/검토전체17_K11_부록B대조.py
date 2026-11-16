import re,glob,io,os,json
root=r'C:\math\임시\주차함수_증명'
rec=r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
B=io.open(root+r'\장v2\부록B.md',encoding='utf-8').read().split('\n')
rows=[]
for l in B:
    if l.startswith('| r'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        rows.append(c)
ids=[c[0] for c in rows]
print('B rows',len(rows),'unique',len(set(ids)))
# ids used in text
used={}
for f in sorted(glob.glob(root+r'\장v2\*.md')):
    name=os.path.basename(f)
    if name=='부록B.md': continue
    txt=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'\br[0-9a-f]{7}\b',txt):
        used.setdefault(m.group(0),set()).add(name)
print('used ids',len(used))
print('used but not in B:',[ (k,sorted(v)) for k,v in used.items() if k not in ids])
print('in B but unused:',[k for k in ids if k not in used])
# folder prefix & existence & title & time
folders=os.listdir(rec) if os.path.isdir(rec) else []
prev=None
for c in rows:
    rid,time,title,folder=c[0],c[1],c[2],c[3].strip('`')
    issues=[]
    if not folder.startswith(rid): issues.append('folder prefix mismatch')
    if folders and folder not in folders: issues.append('folder missing')
    # time order
    if prev and time<prev: issues.append('time order %s<%s'%(time,prev))
    prev=time
    # title from record
    p=os.path.join(rec,folder)
    rtitle=None; rtime=None
    if os.path.isdir(p):
        for cand in ['record.json']:
            fp=os.path.join(p,cand)
            if os.path.exists(fp):
                try:
                    j=json.load(io.open(fp,encoding='utf-8'))
                    rtitle=j.get('title') or j.get('name')
                    rtime=j.get('created_at') or j.get('created') or j.get('time') or j.get('timestamp')
                except Exception as e: rtitle='ERR %s'%e
        if rtitle is None:
            fp=os.path.join(p,'exposition.md')
            if os.path.exists(fp):
                for l in io.open(fp,encoding='utf-8'):
                    if l.startswith('#'): rtitle=l.strip('# \n'); break
    if rtitle and rtitle.replace(' ','')!=title.replace(' ',''):
        issues.append('TITLE B=[%s] rec=[%s]'%(title[:80],str(rtitle)[:80]))
    if issues: print(rid,time,str(rtime)[:19],issues)
print('folders in records not in B:',[f for f in folders if f[:8] not in ids][:20])
