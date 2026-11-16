import json, os, re, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
K=r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge"
B=open(r"장v2/부록B.md",encoding='utf-8').read()
rows=re.findall(r'^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|',B,re.M)
KST=datetime.timezone(datetime.timedelta(hours=9))
prev=None; bad=0
for rid,time,title,folder in rows:
    ev=os.path.join(K,'events',folder+'.json')
    if not os.path.exists(ev): print(rid,'no event'); continue
    j=json.load(open(ev,encoding='utf-8'))
    t=datetime.datetime.fromtimestamp(j['at'],KST).strftime('%m-%d %H:%M')
    if t!=time.strip(): print(rid,'B:',time.strip(),'event:',t,'seq',j['sequence']); bad+=1
    if prev and j['at']<prev: print('order!',rid)
    prev=j['at']
    if rid=='rfc69320': print('rfc69320 sequence =',j['sequence'])
print('rows',len(rows),'time mismatches',bad)
