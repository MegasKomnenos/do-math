import re, sys, json, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = [o for o in json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8')) if not o['proof']]
H = {o['label']: o for o in heads}
L = open(W+"장부_v2.md", encoding='utf-8').read().split('\n')
rows=[]
for ln in range(689, 1179):
    line = L[ln-1]
    if not line.startswith('|'): 
        if line.strip(): print('NONROW', ln, line[:200])
        continue
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    rows.append((ln, c))
print('rows', len(rows), Counter(len(c) for _, c in rows))
live=[]; dead=[]
for ln, c in rows:
    if len(c) != 6: print('CELLS', ln, len(c), c[:2]); continue
    lab = c[5]
    m = re.match(r'^\{\{(\d+:[^}]+)\}\}$', lab)
    if m:
        k = m.group(1); live.append(k)
        if k not in H: print('DEAD-AS-LIVE', ln, k); continue
        o = H[k]
        if o['kind'] != c[1]: print('KIND', ln, k, c[1], o['kind'])
        if o['sec'] != c[4]: print('SEC', ln, k, c[4], o['sec'])
        # name
        hn = o['name'] or ''
        # split head name at '; 기록' / ', 기록'
        mm = re.match(r'^(.*?)(?:; )?(기록 \[.*)$', hn)
        own, rec = (mm.group(1), mm.group(2)) if mm else (hn, '')
        if own != c[2]: print('NAME', ln, k, '| ledger:', c[2], '| head:', own)
        if rec != c[3]: print('RECNAME', ln, k, '| ledger:', c[3], '| head:', rec)
        # first edition number
        mo = re.match(r'^\d+:old-(\d+)-(\d+)$', k)
        exp = f"{mo.group(1)}.{mo.group(2)}" if mo else '—'
        if c[0] != exp: print('FIRSTNUM', ln, k, c[0], exp)
    else:
        dead.append((ln, lab, c))
print('live rows', len(live), 'dups', [k for k,v in Counter(live).items() if v>1])
print('missing live labels', [k for k in H if k not in live])
print('order same', live == [o['label'] for o in heads])
print('dead rows', len(dead))
json.dump(dead, open(W+"scripts/수학검사2/검토전체22_R13_4절_dead.json",'w',encoding='utf-8'), ensure_ascii=False)
print(Counter(c[4] for _,_,c in dead).most_common(8))
print(Counter(re.sub(r'[^(){}]*','',lab)[:2] for _,lab,_ in dead))
