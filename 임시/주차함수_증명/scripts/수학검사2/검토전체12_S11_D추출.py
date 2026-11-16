# S11: 부록 D 항목의 머리·산술 등급·독립 재계산 줄을 뽑아 11.2절 표의 행과 나란히 둔다.
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
items = {}
for f in sorted(glob.glob('장v2/부록D_*.md')):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### ', txt)
    for p in parts[1:]:
        head, _, body = p.partition('\n')
        m = re.match(r'D\.\{\{D:([^}]+)\}\}', head)
        if not m: continue
        lab = m.group(1)
        d = {'file': f, 'head': head}
        for key in ['산술 등급', '독립 재계산', '자료', '범위']:
            mm = re.search(r'(?m)^\*\*' + key + r'\.\*\*\s*(.*)$', body)
            d[key] = mm.group(1) if mm else None
        items[lab] = d
rows = []
for line in open('장v2/장11.md', encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        rows.append(cells)
print('D 항목 수', len(items), '/ 표 행 수', len(rows))
tab_labels = [re.match(r'부록 D\.\{\{D:([^}]+)\}\}', r[0]).group(1) for r in rows]
print('표에 없는 D 항목:', [l for l in items if l not in tab_labels])
print('D에 없는 표 행:', [l for l in tab_labels if l not in items])
for r in rows:
    lab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', r[0]).group(1)
    it = items.get(lab)
    if not it: continue
    print('\n==========', lab, '|', it['file'])
    print('D머리:', it['head'])
    print('표 확인하는 진술:', r[1])
    print('D 산술 등급:', it['산술 등급'])
    print('표 산술 등급:', r[2])
    print('표 쓰인 곳:', r[3])
    print('D 범위:', it['범위'])
    print('D 독립 재계산:', it['독립 재계산'])
    print('표 재계산:', r[4])
    print('표 독립 재계산:', r[5])
    # 꺾쇠 괄호 비교
    dm = re.match(r'(〔[^〕]*〕)\s*(.*)$', it['독립 재계산'] or '')
    if dm:
        print('--- 꺾쇠 같음:', dm.group(1) == r[4])
        print('--- 본문 같음:', dm.group(2).strip() == r[5].strip())
        if dm.group(2).strip() != r[5].strip():
            import difflib
            a, b = dm.group(2).strip(), r[5].strip()
            sm = difflib.SequenceMatcher(None, a, b)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op != 'equal':
                    print('    diff', op, 'D:', repr(a[max(0,i1-15):i2+15]), '| 표:', repr(b[max(0,j1-15):j2+15]))
