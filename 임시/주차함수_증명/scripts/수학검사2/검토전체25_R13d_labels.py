# -*- coding: utf-8 -*-
import json, re, io, glob, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
heads = json.load(io.open(os.path.join(base, 'scripts', '수학검사2', '검토전체25_R13_heads.json'), encoding='utf-8'))
if isinstance(heads, dict):
    for k in heads:
        if isinstance(heads[k], list):
            heads = heads[k]; break
labs = {}
for h in heads:
    labs[h['ch']+':'+h['lab']] = h
lines = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
# all label occurrences anywhere in chapter files (statements + D items + eq labels)
alltext = {}
for f in sorted(glob.glob(os.path.join(base, '장v2', '*.md'))):
    alltext[os.path.basename(f)] = io.open(f, encoding='utf-8').read()
dheads = set()
for fn, t in alltext.items():
    if fn.startswith('부록D'):
        for m in re.finditer(r'^#+\s.*?\{\{(D:[^}]+)\}\}', t, re.M):
            dheads.add(m.group(1))
for i in range(358, 688):
    ln = lines[i]
    for m in re.finditer(r'\{\{([^}]+)\}\}', ln):
        lab = m.group(1)
        ctx = ln[max(0, m.start()-30):m.end()+20]
        if lab.startswith('D:'):
            st = 'D-head' if lab in dheads else 'D-MISSING'
            if st != 'D-head':
                print(i+1, lab, st, '|', ctx)
        else:
            if lab not in labs:
                print(i+1, lab, 'MISSING', '|', ctx)
            else:
                h = labs[lab]
                # kind check: word before the label
                pre = ln[max(0, m.start()-12):m.start()]
                km = re.search(r'(정리|보조정리|명제|따름정리|정의|비고|가설|추측)\s*`?$', pre)
                kind = h.get('kind') or h.get('종류')
                if km and km.group(1) != kind:
                    print(i+1, lab, 'KIND', km.group(1), '!=', kind, '|', ctx)
print('dheads', len(dheads), 'labs', len(labs))
