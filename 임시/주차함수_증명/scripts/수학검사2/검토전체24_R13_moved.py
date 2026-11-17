# -*- coding: utf-8 -*-
# R13: 대응표의 옮김 행 번호·뺌 행이 가리키는 라벨이 현행 머리에 있는지 본다.
import re, sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('h', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_heads.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
hs = h.heads(); by = {x['label']: x for x in hs}
dead = set()
rows = []
with open(r'C:/math/임시/주차함수_증명/대조v2/라벨_번호_대응표_1114.md', encoding='utf-8', newline='') as fh:
    for i, line in enumerate(fh, 1):
        line = line.rstrip('\r\n')
        if not line.startswith('| `'): continue
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        rows.append((i, cells, line))
        if cells[0].startswith('`('): dead.add(cells[0].strip('`()'))
print('dead labels', len(dead), 'dead∩live', sorted(dead & set(by)))
for i, c, line in rows:
    if not c[0].startswith('`('): continue
    m = re.match(r'^옮김 → `\{\{([^}]+)\}\}` (\d+\.\d+)$', c[3])
    if c[3].startswith('옮김'):
        if not m: print('MOVEFMT', i, c[3]); continue
        lab, num = m.groups()
        x = by.get(lab)
        if not x: print('MOVE-NOHEAD', i, lab)
        else:
            if x['num'] != num: print('MOVE-NUM', i, lab, num, x['num'])
            if x['kind'] != c[1]: print('MOVE-KIND', i, c[0], c[1], '->', x['kind'])
            nm = x['name'] or '—'
            if nm != c[2]: print('MOVE-NAME', i, c[0], '\n  T:', c[2], '\n  H:', nm)
    # 뺌 행의 이름 칸에 나오는 라벨
    for lab in re.findall(r'`(\d+:[A-Za-z0-9\-′]+)`', c[2]):
        if lab not in by:
            print('DEADREF', i, c[0], '->', lab, '(뺌 표에 있음)' if lab in dead else '(어디에도 없음)')
    for lab in re.findall(r'\{\{(\d+:[^}]+)\}\}', c[2]):
        if lab not in by: print('DEADREF2', i, c[0], '->', lab)
