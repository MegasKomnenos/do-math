# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 장 파일의 진술 위치에 맞추어 본다(자리 찾기·대조용)."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
ch11 = open(os.path.join(ROOT, '장v2', '장11.md'), encoding='utf-8').read().split('\n')

# ---- 표 행 파싱
rows = []
for ln in ch11:
    if ln.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        rows.append(cells)
print('표 행 수', len(rows))

# ---- 부록 D 항목 파싱
items = {}
order = []
for f in sorted(glob.glob(os.path.join(ROOT, '장v2', '부록D_장*.md'))):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.\{\{D:', txt)
    for p in parts[1:]:
        label = p.split('}}')[0]
        head = p.split('\n')[0]
        m = re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$', head)
        stmt = m.group(1) if m else '?'
        def field(name):
            mm = re.search(r'\*\*' + name + r'\.\*\*\s*(.*)', p)
            return mm.group(1).strip() if mm else None
        items[label] = dict(file=os.path.basename(f), head=head, stmt=stmt,
                            grade=field('산술 등급'), recalc=field('독립 재계산'),
                            confirm=field('확인하는 진술'))
        order.append(label)
print('부록 D 항목 수', len(items))

row_labels = [r[0].replace('부록 D.{{D:', '').split('}}')[0] for r in rows]
print('표에만 있는 라벨', [l for l in row_labels if l not in items])
print('부록 D에만 있는 라벨', [l for l in order if l not in row_labels])
print('차례 같은가', row_labels == order)
for i,(a,b) in enumerate(zip(row_labels,order)):
    if a!=b: print('  차례 차이', i, a, b)

# ---- 장 파일에서 진술 라벨의 절 찾기
chap_files = {}
for f in glob.glob(os.path.join(ROOT, '장v2', '장*.md')):
    chap_files[os.path.basename(f)] = open(f, encoding='utf-8').read().split('\n')

def find_section(label):
    """label like '2:old-2-5' -> (kind, section) of the statement head in chapter files."""
    tag = '{{' + label + '}}'
    res = []
    for fn, lines in chap_files.items():
        sec = None
        for ln in lines:
            m = re.match(r'^###\s+(\d+\.\d+)', ln)
            if m:
                sec = m.group(1)
            mm = re.match(r'^\*\*(\S+) ' + re.escape(tag), ln)
            if mm:
                res.append((fn, sec, mm.group(1)))
    return res

for r, lab in zip(rows, row_labels):
    it = items[lab]
    print('=' * 100)
    print('D:', lab, '|', it['file'])
    # 확인하는 진술
    if r[1] != it['stmt']:
        print('  [진술 다름] 표:', r[1], '|| D머리:', it['stmt'])
    # 산술 등급
    print('  표 등급:', r[2], '|| D 등급 줄:', it['grade'])
    # 놓인 곳
    stmts = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', r[1])
    locs = []
    for s in stmts:
        locs.append((s, find_section(s)))
    print('  표 놓인 곳:', r[3], '|| 실제:', locs)
    # 재계산 괄호
    rec = it['recalc'] or ''
    m = re.match(r'(〔[^〕]*〕)\s*(.*)', rec, re.S)
    if m:
        br, rest = m.group(1), m.group(2)
        if br != r[4]:
            print('  [괄호 다름]\n    표:', r[4], '\n    D :', br)
        if rest != r[5]:
            # show first differing position
            i = 0
            while i < min(len(rest), len(r[5])) and rest[i] == r[5][i]:
                i += 1
            print('  [서술 다름] 첫 차이 위치', i)
            print('    표:', r[5][max(0, i - 60):i + 120])
            print('    D :', rest[max(0, i - 60):i + 120])
    else:
        print('  [D 독립 재계산 줄 없음/형식 다름]', rec[:100])
