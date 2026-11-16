# K13: read xcert_iv results to check the figures quoted in D.xcert-partAB
import json,glob,os
D=r'C:\math\임시\주차함수_증명\원고_자료\세션_재계산\xcert_iv'
def load(pat):
    rows=[]
    for p in sorted(glob.glob(os.path.join(D,pat))):
        for line in open(p,encoding='utf-8'):
            line=line.strip()
            if line: rows.append((os.path.basename(p),json.loads(line)))
    return rows
B=load('resB_p*.jsonl'); print('B rows',len(B))
r0=[r for _,r in B if r.get('k')==501][0]; print('keys',sorted(r0.keys())[:40])
for key in ('k','c','R_U','sL','sU','min_b0','b0_min','n_X','ok','width'):
    if key in r0: print(key, r0[key])
if 'sL' in r0 and 'sU' in r0: print('width 501', r0['sU']-r0['sL'])
c3=[r['k'] for _,r in B if r.get('c')==3]; print('c=3 count',len(c3), min(c3) if c3 else None, max(c3) if c3 else None)
print('k>=607 all c=4:', all(r.get('c')==4 for _,r in B if r['k']>=607))
for name,pat in (('Aint','resAint_p*.jsonl'),('A1','resA1_p*.jsonl')):
    R=load(pat); print(name,'rows',len(R),'files',sorted(set(f for f,_ in R)))
    r=R[0][1]; print(' keys',sorted(r.keys())[:40])
    best=None; maxratio=0
    for f,r in R:
        K1=r.get('K1') or (r.get('interval') or [None,None])[0]; K2=r.get('K2') or (r.get('interval') or [None,None])[1]
        if K1 is None: continue
        maxratio=max(maxratio,K2/K1)
        sL2=r.get('sL_K2') or r.get('sL2') or (r.get('sigma_K2') or [None])[0]
        if sL2 is not None:
            v=K1*sL2/K2
            if best is None or v<best[0]: best=(v,K1,K2)
    print(' max K2/K1',maxratio,' min interior',best)
