# -*- coding: utf-8 -*-
"""G13: 부록 D(7A·7B·8·9·10) 항목의 「산술 등급」·「독립 재계산」 줄과 장11 11.2 표의 같은 행을 대조한다.
읽기만 한다. 실행: python -I scripts/수학검사2/검토전체_G13_표대조.py
"""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = pathlib.Path(__file__).resolve().parents[2]
files = ['부록D_장7A.md','부록D_장7B.md','부록D_장8.md','부록D_장9.md','부록D_장10.md']

items = {}
for f in files:
    txt = (root/'장v2'/f).read_text(encoding='utf-8')
    heads = list(re.finditer(r'^### D\.\{\{D:([^}]+)\}\}(.*)$', txt, re.M))
    for i, h in enumerate(heads):
        lab = h.group(1)
        end = heads[i+1].start() if i+1 < len(heads) else len(txt)
        body = txt[h.start():end]
        title = h.group(2)
        stm = re.findall(r'\{\{(\d+[AB]?):([^}]+)\}\}', title)
        m_grade = re.search(r'^\*\*산술 등급\.\*\*\s*(.*)$', body, re.M)
        m_ind = re.search(r'^\*\*독립 재계산\.\*\*\s*(.*)$', body, re.M)
        items[lab] = dict(file=f, title=title.strip(), stm=stm,
                          grade=m_grade.group(1).strip() if m_grade else None,
                          ind=m_ind.group(1).strip() if m_ind else None)

t11 = (root/'장v2'/'장11.md').read_text(encoding='utf-8')
rows = {}
for line in t11.splitlines():
    m = re.match(r'^\| 부록 D\.\{\{D:([^}]+)\}\} \|(.*)\|\s*$', line)
    if m:
        cols = [c.strip() for c in m.group(2).split(' | ')]
        rows[m.group(1)] = cols

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

for lab, it in items.items():
    print('='*100)
    print(lab, '|', it['file'])
    if lab not in rows:
        print('  !! 11.2 표에 행 없음'); continue
    cols = rows[lab]
    if len(cols) != 5:
        print('  !! 열 수', len(cols)); print(cols); continue
    stm_col, grade_col, where_col, bracket_col, ind_col = cols
    # 진술
    stm_in_row = re.findall(r'\{\{(\d+[AB]?):([^}]+)\}\}', stm_col)
    print('  제목 진술 :', it['stm'])
    print('  표 진술   :', stm_in_row)
    print('  진술 일치 :', sorted(it['stm']) == sorted(stm_in_row))
    # 등급
    print('  D 산술 등급 줄 :', it['grade'][:200] if it['grade'] else None)
    print('  표 산술 등급   :', grade_col)
    # 독립 재계산
    ind = it['ind'] or ''
    m = re.match(r'〔(.*?)〕\s*(.*)$', ind, re.S)
    if not m:
        print('  !! D 독립 재계산 줄에 꺾쇠 없음'); continue
    br, rest = m.group(1), m.group(2)
    print('  꺾쇠 일치 :', norm('〔'+br+'〕') == norm(bracket_col))
    if norm('〔'+br+'〕') != norm(bracket_col):
        print('    D :', br); print('    표:', bracket_col)
    # 표의 서술 열은 | 를 \vert 로 바꿨을 수 있음
    rest_n = norm(rest).replace('|', '\\vert ')
    ind_n = norm(ind_col)
    same = norm(rest_n) == ind_n or norm(rest) == ind_n
    print('  서술 일치 :', same)
    if not same:
        # 첫 차이 위치
        a, b = norm(rest), ind_n
        k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
        print('    첫 차이 위치', k)
        print('    D :', a[max(0,k-80):k+120])
        print('    표:', b[max(0,k-80):k+120])
    print('  쓰인 곳 :', where_col)
