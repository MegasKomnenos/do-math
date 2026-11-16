# -*- coding: utf-8 -*-
"""H11: 11.2절 표의 각 행을 부록 D 항목과 대조한다.
열: 확인하는 진술(머리의 괄호 진술 목록), 산술 등급(D「산술 등급」줄 첫 등급), 놓인 곳, 재계산 꺾쇠, 독립 재계산 서술."""
import re, glob, os, sys, io, json, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
labelmap = json.load(open(os.path.join(os.path.dirname(__file__), '_H11_labelmap.json'), encoding='utf-8'))
# parse D items
items = {}
for f in sorted(glob.glob(os.path.join(root, '부록D_장*.md'))):
    cur = None
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^### D\.\{\{D:([^}]+)\}\}\s*(.*?)\s*\((.*)\)\s*$', line.strip())
        if m:
            cur = m.group(1)
            items[cur] = {'file': os.path.basename(f), 'line': ln, 'title': m.group(2), 'stmts_head': m.group(3), 'fields': {}}
            continue
        m = re.match(r'^\*\*([^*]+)\.\*\*\s*(.*)$', line.strip())
        if m and cur:
            items[cur]['fields'][m.group(1)] = m.group(2)
print('D items parsed:', len(items))
# parse 11.2 table
T = open(os.path.join(root, '장11.md'), encoding='utf-8').read().splitlines()
rows = []
for ln, line in enumerate(T, 1):
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        if len(cells) != 6:
            print('CELLS?', ln, len(cells)); continue
        rows.append((ln, cells))
print('table rows:', len(rows))
def norm(s):
    return re.sub(r'\s+', ' ', s).strip()
def stmt_set(s):
    # returns list of (type,label) expanding '·' chains and (가) suffixes
    out = []
    for m in re.finditer(r'(정리|명제|보조정리|따름정리)\s+((?:\{\{[^}]+\}\}(?:\([^)]*\))?(?:·|,\s*)?)+)', s):
        typ = m.group(1)
        for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
            out.append((typ, lab))
    return out
for ln, cells in rows:
    dlab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
    it = items.get(dlab)
    if not it:
        print(ln, dlab, 'NO D ITEM'); continue
    F = it['fields']
    # 1. statements
    ts = stmt_set(cells[1]); hs = stmt_set(it['stmts_head'])
    if set(ts) != set(hs):
        print(f'{ln} {dlab}: STMT 표={ts} D머리={hs}')
    # also check head type vs labelmap
    for typ, lab in ts:
        if lab in labelmap and labelmap[lab][0] != typ:
            print(f'{ln} {dlab}: TYPE 표 {typ} vs 머리 {labelmap[lab][0]} {lab}')
    # 2. grade
    g = F.get('산술 등급', '')
    first = re.split(r'[(;.。]', g)[0].strip()
    grades_table = [x.strip() for x in cells[2].split(',')]
    grades_D_all = re.findall(r'정확 정수·유리수|방향 반올림 구간|binary64 사전 오차 해석|\d+자리 평가|배정밀도 평가', g)
    if norm(first) not in [norm(x) for x in grades_table] and set(grades_table) != set(grades_D_all[:len(grades_table)]):
        print(f'{ln} {dlab}: GRADE 표={cells[2]!r}  D첫={first!r}  D전체={g[:160]!r}')
    # 3. section: find section of each statement's head
    # 4. recomputation bracket & text
    rec = F.get('독립 재계산', '')
    mb = re.match(r'(〔[^〕]*〕)\s*(.*)$', rec)
    if not mb:
        print(f'{ln} {dlab}: D 독립 재계산 꺾쇠 없음: {rec[:80]}')
    else:
        br, body = mb.groups()
        if norm(br) != norm(cells[4]):
            print(f'{ln} {dlab}: BRACKET\n   표: {cells[4]}\n   D : {br}')
        if norm(body) != norm(cells[5]):
            # show diff
            a = norm(body); b = norm(cells[5])
            sm = difflib.SequenceMatcher(None, a, b)
            diffs = [(tag, a[i1:i2], b[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal']
            print(f'{ln} {dlab}: TEXT differs ({len(diffs)} ops):')
            for d in diffs[:12]:
                print('     ', d[0], 'D:', repr(d[1][:120]), '| 표:', repr(d[2][:120]))
# section check: need section of each cited statement
sec_of = {}
for f in sorted(glob.glob(os.path.join(root, '장*.md'))):
    cur = None
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', line)
        if m: cur = m.group(1)
        m2 = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{([^}]+)\}\}', line)
        if m2 and cur: sec_of[m2.group(2)] = cur
print('--- section check')
for ln, cells in rows:
    dlab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
    secs = sorted({sec_of.get(lab, '?') for _, lab in stmt_set(cells[1])})
    tsecs = sorted(cells[3].split('·'))
    if secs != tsecs:
        print(f'{ln} {dlab}: SEC 표={tsecs} 실제={secs}')
