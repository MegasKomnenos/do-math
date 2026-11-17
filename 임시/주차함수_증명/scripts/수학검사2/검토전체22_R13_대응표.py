import re, sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = [o for o in json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8')) if not o['proof']]
H = {o['label']: o for o in heads}
L = open(W+"대조v2/라벨_번호_대응표_1114.md", encoding='utf-8').read().split('\n')
rows = []
for ln, line in enumerate(L, 1):
    if line.startswith('| `{{'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append((ln, cells))
print('rows', len(rows), 'cell counts', sorted(set(len(c) for _, c in rows)))
seen = []
for ln, c in rows:
    lab = c[0].strip('`')[2:-2]
    seen.append(lab)
    if lab not in H:
        print('NOT-IN-CHAPTERS', ln, c); continue
    o = H[lab]
    name = o['name'] if o['name'] else '—'
    probs = []
    if c[1] != o['kind']: probs.append(('kind', c[1], o['kind']))
    if c[2] != name: probs.append(('name', c[2], name))
    if c[3] != o['num']: probs.append(('num', c[3], o['num']))
    if c[-1] != o['sec']: probs.append(('sec', c[-1], o['sec']))
    if probs: print('DIFF', ln, lab, probs)
print('missing from table', [k for k in H if k not in seen])
from collections import Counter
print('dups', [k for k, v in Counter(seen).items() if v > 1])
# order check
order = [o['label'] for o in heads]
tab = [s for s in seen if s in H]
print('order same', order == tab)
