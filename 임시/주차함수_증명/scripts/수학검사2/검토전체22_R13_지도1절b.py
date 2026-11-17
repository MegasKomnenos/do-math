import re, sys, json, io
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = [o for o in json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8')) if not o['proof']]
H = {o['label']: o for o in heads}
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
L10 = open(W+"장v2/장10.md", encoding='utf-8').read().split('\n')
lit = defaultdict(list); inlit = False
for ln, line in enumerate(L10, 1):
    if line.startswith('### 10.3'): inlit = True
    if inlit and line.startswith('| ') and not line.startswith('| 문헌') and not line.startswith('|---'):
        c = [x.strip() for x in line.strip()[1:-1].split(' | ')]
        if len(c) != 3: print('10.3 cells', ln, len(c)); continue
        auth = c[0].split(',')[0].strip()
        for k in LAB.findall(c[2]): lit[k].append((auth, ln, c[0][:40]))
T = open(W+"의존지도_v2.md", encoding='utf-8').read().split('\n')
for ln in range(11, 284):
    line = T[ln-1]
    if not line.startswith('| `{{'): continue
    c = [x.strip() for x in line.strip()[1:-1].split(' | ')]
    k = c[0].strip('`')[2:-2]; o = H[k]
    mo = re.match(r'^\d+:old-(\d+)-(\d+)$', k)
    exp = f"{o['kind']} {mo.group(1)}.{mo.group(2)}" if mo else '새 진술'
    if c[2] != exp: print('FIRST', ln, k, '| map:', c[2], '| exp:', exp)
    # literature: authors
    cell = c[7]
    exp_auth = sorted(set(a for a,_,_ in lit.get(k, [])))
    if cell in ('—', ''):
        if exp_auth: print('LIT missing in map', ln, k, exp_auth)
    else:
        miss = [a for a in exp_auth if a not in cell]
        if miss: print('LIT map lacks', ln, k, miss, '| map:', cell[:150])
        # authors in map not in 10.3 for this label
        parts = [p.strip() for p in re.split(r';\s*', cell)]
        for p in parts:
            a = p.split('(')[0].strip()
            a0 = a.split(',')[0].strip()
            if a0 and a0 not in exp_auth: print('LIT map extra', ln, k, a, '| 10.3 has:', exp_auth)
    if not o['name'] : print('NONAME', ln, k, '| 요지:', c[3][:90], '| 비고:', c[9][:80])
