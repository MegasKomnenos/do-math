# -*- coding: utf-8 -*-
# R10: compare 10.2 table rows with appendix D items (heading statements, grade line, bracket). Read-only.
import re, sys, io, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
items = {}
order = []
for f in sorted(glob.glob(os.path.join(base, '부록D_장*.md'))):
    cur = None
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'^### D\.\{\{(D:[^}]+)\}\}(.*)$', line)
        if m:
            cur = m.group(1); items[cur] = dict(file=os.path.basename(f), head=m.group(2).strip(), grade='', bracket='')
            order.append(cur)
        elif cur and line.startswith('**산술 등급.**'):
            items[cur]['grade'] = line.strip()
        elif cur and line.startswith('**독립 재계산.**'):
            m2 = re.search(r'〔[^〕]*〕', line)
            items[cur]['bracket'] = m2.group(0) if m2 else 'NO BRACKET'
rows = {}
roworder = []
for line in io.open(os.path.join(base, '장10.md'), encoding='utf-8'):
    if line.startswith('| 부록 D.{{'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        lab = re.search(r'\{\{(D:[^}]+)\}\}', cells[0]).group(1)
        rows[lab] = cells; roworder.append(lab)
print('D items:', len(order), 'rows:', len(roworder))
print('order equal:', order == roworder)
if order != roworder:
    print(order); print(roworder)
for lab in order:
    it = items[lab]; r = rows.get(lab)
    print('====', lab, it['file'])
    if not r: print('  NO ROW'); continue
    print('  bracket equal:', it['bracket'] == r[4])
    if it['bracket'] != r[4]:
        print('   D :', it['bracket']); print('   10:', r[4])
    hl = sorted(set(re.findall(r'\{\{(\d+:[^}]+)\}\}', it['head'])))
    rl = sorted(set(re.findall(r'\{\{(\d+:[^}]+)\}\}', r[1])))
    print('  stmts equal:', hl == rl, '' if hl == rl else (hl, rl))
    print('  row grade:', r[2], '| sec:', r[3])
    print('  D grade  :', it['grade'][:400])
