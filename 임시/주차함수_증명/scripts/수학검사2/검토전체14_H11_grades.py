# -*- coding: utf-8 -*-
"""H11: 진술 머리의 계산 증거/계산 보조 등급을 11.2 표의 등급과 대조하고,
부록 C 이름 표(기록의 이름 / 이 글의 진술 / 이 글의 이름)를 머리와 대조한다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
heads = {}
for f in sorted(glob.glob(os.path.join(root, '장*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{([^}]+)\}\}\s*(?:\((.*?)\))?\s*(?:\[(.*?)\])?\.\*\*', line)
        if m and '의 증명' not in line[:m.end()]:
            heads[m.group(2)] = dict(type=m.group(1), paren=m.group(3), tag=m.group(4), where=f'{os.path.basename(f)}:{ln}')
print('heads', len(heads))
# grades from heads
G = ['정확 정수·유리수', '방향 반올림 구간', 'binary64 사전 오차 해석']
head_grades = {}
for lab, h in heads.items():
    t = h['tag'] or ''
    if '계산' in t:
        gs = set()
        for m in re.finditer(r'계산 (?:증거|보조)\(([^)]*)\)', t):
            for g in G:
                if g in m.group(1): gs.add(g)
            for g in re.findall(r'\d+자리 평가|배정밀도 평가', m.group(1)): gs.add(g)
        head_grades[lab] = (gs, t)
# 11.2 table
T = open(os.path.join(root, '장11.md'), encoding='utf-8').read().splitlines()
tab = {}
for line in T:
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[1])
        for lab in labs:
            tab.setdefault(lab, set()).update(x.strip() for x in cells[2].split(','))
print('--- heads with 계산 but not in 11.2 table:')
for lab in head_grades:
    if lab not in tab: print('   ', lab, heads[lab]['where'], head_grades[lab][1][:150])
print('--- 11.2 statements whose head has no 계산 tag:')
for lab in tab:
    if lab not in head_grades: print('   ', lab, heads.get(lab, {}).get('where'), (heads.get(lab, {}).get('tag') or '')[:150])
print('--- grade differences (head vs 11.2 union over rows):')
for lab in tab:
    if lab in head_grades and head_grades[lab][0] != tab[lab]:
        print('   ', lab, 'head=', sorted(head_grades[lab][0]), 'table=', sorted(tab[lab]), '|', heads[lab]['where'])
# 11.3 tables' grade column
print('--- 11.3 계산 진술과 산술 등급 열 vs head grades:')
in113 = False
for ln, line in enumerate(T, 1):
    if line.startswith('### 11.3'): in113 = True
    if line.startswith('### 11.4'): in113 = False
    if in113 and line.startswith('| ') and not line.startswith('| 입력') and not line.startswith('|---'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        col = cells[1]
        if col == '없음': continue
        # split by ';'
        for part in col.split(';'):
            gs = {g for g in G if g in part}
            labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', part.split(':')[0]) if ':' in part else []
            for lab in labs:
                hg = head_grades.get(lab, (set(), ''))[0]
                if hg != gs:
                    print(f'   행{ln} {lab}: 11.3={sorted(gs)} head={sorted(hg)} ({heads.get(lab,{}).get("where")})')
# 부록 C 이름 표
print('--- 부록 C 이름 표 vs heads')
C = open(os.path.join(root, '부록C.md'), encoding='utf-8').read().splitlines()
crows = {}
for ln, line in enumerate(C, 1):
    m = re.match(r'^\| (.+?) \| (정리|명제|보조정리|따름정리) \{\{([^}]+)\}\} \| (.+?) \|\s*$', line)
    if m:
        crows[m.group(3)] = (ln, m.group(1), m.group(2), m.group(4))
print('C rows', len(crows))
for lab, (ln, recname, typ, name) in crows.items():
    h = heads.get(lab)
    if not h: print(f'   C{ln}: no head for {lab}'); continue
    if h['type'] != typ: print(f'   C{ln}: TYPE {typ} vs {h["type"]} {lab}')
    paren = h['paren'] or ''
    hname = paren.split(';')[0].strip()
    hrec = paren.split(';', 1)[1].strip() if ';' in paren else ''
    def norm(s): return ''.join(ch for ch in s.replace('\mathsf','').replace('\mathrm','').replace('\,','') if not ch.isspace() and ch not in '${}')
    if norm(hname) != norm(name):
        print(f'   C{ln}: NAME C={name!r} head={hname!r} ({lab})')
    if norm(hrec) != norm(recname):
        print(f'   C{ln}: RECNAME C={recname!r} head={hrec!r} ({lab})')
# heads with record names not in C
for lab, h in heads.items():
    paren = h['paren'] or ''
    if ';' in paren and lab not in crows:
        print(f'   head not in C: {lab} {h["where"]} ({paren[:100]})')
