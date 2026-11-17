# 의존지도 1절 표를 장 파일에서 다시 계산한 값과 견준다(절·요지·지위·머리 인용·본문 인용·기록·부록 D·문헌).
import re, sys, json, io
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
allh = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
heads = [o for o in allh if not o['proof']]
H = {o['label']: o for o in heads}
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
# body text per label
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
body = defaultdict(list); headline = {}
for f in files:
    L = open(W+"장v2/"+f+".md", encoding='utf-8').read().split('\n')
    marks = sorted([(o['line'], o) for o in allh if o['file']==f], key=lambda t:t[0])
    for idx,(ln,o) in enumerate(marks):
        end = marks[idx+1][0]-1 if idx+1 < len(marks) else len(L)
        seg = L[ln-1:end]
        if o['proof']:
            body[o['label']].append('\n'.join(seg))   # 뒤로 미룬 증명
        else:
            line = seg[0]
            i = line.find('.**')
            headline[o['label']] = line[:i]
            body[o['label']].append(line[i:] + '\n' + '\n'.join(seg[1:]))
# appendix D / literature from 장10
L10 = open(W+"장v2/장10.md", encoding='utf-8').read().split('\n')
dmap = defaultdict(list); lit = defaultdict(list)
for line in L10:
    if line.startswith('| 부록 D.'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        item = re.search(r'\{\{D:([^}]+)\}\}', c[0]).group(1)
        for k in LAB.findall(c[1]): dmap[k].append((item, c[2]))
T = open(W+"의존지도_v2.md", encoding='utf-8').read().split('\n')
rows = []
for ln in range(11, 284):
    line = T[ln-1]
    if line.startswith('| `{{'):
        c = [x.strip() for x in line.strip()[1:-1].split(' | ')]
        rows.append((ln, c))
print('rows', len(rows), Counter(len(c) for _, c in rows))
seen = []
nd = 0
for ln, c in rows:
    if len(c) != 10: print('CELLS', ln, len(c)); continue
    k = c[0].strip('`')[2:-2]; seen.append(k)
    if k not in H: print('DEAD', ln, k); continue
    o = H[k]
    if c[1] != o['sec']: print('SEC', ln, k, c[1], o['sec'])
    # status
    st = o['status']
    if st is None: exp_st = '정의' if o['kind']=='정의' else '(없음)'
    else: exp_st = st.split(';')[0].strip()
    if c[4] != exp_st: print('STATUS', ln, k, '| map:', c[4][:150], '| head:', exp_st[:150])
    # name
    nm = o['name'] or ''
    if nm and c[3] != nm: print('NAME', ln, k, '| map:', c[3][:100], '| head:', nm[:100])
    # records
    recs = [x.strip() for x in st.split(';',1)[1].split(',')] if (st and ';' in st) else ([] if st else [])
    if st and ';' not in st and o['kind']=='정의': recs=[x.strip() for x in st.split(',')]
    maprecs = re.findall(r'r[0-9a-f]{7}', c[6])
    headrecs = re.findall(r'r[0-9a-f]{7}', st.split(';',1)[1] if (st and ';' in st) else (st or '') if o['kind']=='정의' else '')
    if sorted(set(maprecs)) != sorted(set(headrecs)): print('RECS', ln, k, '| map:', c[6][:120], '| head:', headrecs)
    # head-cited labels & body-cited
    hl = [x for x in LAB.findall(headline[k]) if x != k and not x.startswith('D:')]
    bl = []
    for seg in body[k]:
        for x in LAB.findall(seg):
            if x != k and not x.startswith('D:') and x not in hl and x not in bl: bl.append(x)
    cell = c[5]
    if '본문 인용:' in cell:
        a, b = cell.split('본문 인용:')
    else: a, b = cell, ''
    mh = LAB.findall(a); mb = LAB.findall(b)
    if set(mh) != set(hl): print('HEADCITE', ln, k, '| map-only:', sorted(set(mh)-set(hl)), '| head-only:', sorted(set(hl)-set(mh)))
    if set(mb) != set(bl): 
        nd += 1
        print('BODYCITE', ln, k, '| map-only:', sorted(set(mb)-set(bl)), '| chapter-only:', sorted(set(bl)-set(mb)))
    # appendix D
    md = re.findall(r'\{\{D:([^}]+)\}\}', c[8])
    ed = [i for i,_ in dmap.get(k, [])]
    if sorted(md) != sorted(ed): print('APPD', ln, k, '| map:', c[8][:100], '| 10.2:', ed)
print('missing', [k for k in H if k not in seen], 'order same', seen == [o['label'] for o in heads])
