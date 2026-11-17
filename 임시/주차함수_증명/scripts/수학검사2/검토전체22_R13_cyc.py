import re, sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
allh = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
def segs(k):
    out=[]
    for o in allh:
        if o['label']!=k: continue
        f=o['file']; L=open(W+"장v2/"+f+".md",encoding='utf-8').read().split('\n')
        marks=sorted(x['line'] for x in allh if x['file']==f)
        nxt=[m for m in marks if m>o['line']]
        end=nxt[0]-1 if nxt else len(L)
        out.append((f,o['line'],end,L))
    return out
w=int(sys.argv[1])
for pair in sys.argv[2:]:
    a,b=pair.split(',')
    for x,y in ((a,b),(b,a)):
        for f,s,e,L in segs(x):
            for ln in range(s,e+1):
                t=L[ln-1]
                for m in re.finditer(re.escape('{{'+y+'}}'), t):
                    i=m.start()
                    where='HEAD' if ln==s and i < t.find('.**') else ('headline' if ln==s else 'body')
                    print(f"[{x} cites {y}] {f}:{ln} ({where}; seg {s}-{e}): …{t[max(0,i-w):i+w]}…")
    print()
