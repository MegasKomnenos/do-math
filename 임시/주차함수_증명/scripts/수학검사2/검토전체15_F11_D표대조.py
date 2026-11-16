# -*- coding: utf-8 -*-
"""F11: 11.2절 표의 각 행을 부록 D 항목과 대조하고, 장 파일의 진술 머리를 TSV로 덤프한다."""
import re, glob, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
D_ITEMS = {}
for f in sorted(glob.glob(os.path.join(ROOT, '장v2', '부록D_장*.md'))):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### D\.\{\{D:([^}]+)\}\}', txt)
    # parts: [pre, label1, body1, label2, body2, ...]
    for i in range(1, len(parts), 2):
        label, body = parts[i], parts[i+1]
        head = body.split('\n', 1)[0].strip()
        def line(name):
            m = re.search(r'(?m)^\*\*' + name + r'\.\*\*\s*(.*)$', body)
            return m.group(1).strip() if m else None
        D_ITEMS[label] = dict(file=os.path.basename(f), head=head,
                              claim=line('확인하는 진술'), grade=line('산술 등급'),
                              recalc=line('독립 재계산'), src=line('출처'))
print('부록 D 항목 수:', len(D_ITEMS))
# 11.2 표
ch11 = open(os.path.join(ROOT, '장v2', '장11.md'), encoding='utf-8').read().split('\n')
rows = [l for l in ch11 if l.startswith('| 부록 D.{{D:')]
print('11.2 표 행 수:', len(rows))
seen = []
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split(' | ')]
    if len(cells) != 6:
        print('!! 열 수 이상', len(cells), r[:80]); continue
    dlab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
    seen.append(dlab)
    it = D_ITEMS.get(dlab)
    if not it:
        print('!! 부록 D에 없는 라벨', dlab); continue
    # 진술: D 머리 괄호
    m = re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$', it['head'])
    head_stmts = m.group(1) if m else '?'
    # 라벨 집합 비교
    tl = set(re.findall(r'(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}', cells[1]))
    hl = set(re.findall(r'(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}', head_stmts))
    if tl != hl:
        print(f'[진술 불일치] D.{dlab}\n   표: {cells[1]}\n   D머리: {head_stmts}')
    # 등급
    dg = it['grade'] or ''
    print(f'D.{dlab} | 표 등급: {cells[2]} | D 등급줄: {dg[:160]}')
    # 재계산 꺾쇠
    rc = it['recalc'] or ''
    mb = re.match(r'(〔[^〕]*〕)\s*(.*)$', rc, re.S)
    if not mb:
        print('   !! D 독립 재계산 줄에 꺾쇠 없음'); continue
    br, rest = mb.group(1), mb.group(2).strip()
    if br != cells[4]:
        print(f'   [꺾쇠 불일치]\n   표: {cells[4]}\n   D : {br}')
    rest2 = rest.replace('이 문단 머리의 꺾쇠 괄호', '「재계산」 열의 꺾쇠 괄호')
    if rest2 != cells[5]:
        # 차이 위치
        a, b = rest2, cells[5]
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]: k += 1
        print(f'   [서술 불일치] 첫 차이 위치 {k}\n   D : …{a[max(0,k-60):k+120]}\n   표: …{b[max(0,k-60):k+120]}')
missing = [l for l in D_ITEMS if l not in seen]
print('표에 없는 D 항목:', missing)
dup = [l for l in seen if seen.count(l) > 1]
print('표에서 중복된 D 항목:', set(dup))
# 진술 머리 덤프
out = open(os.path.join(ROOT, '대조v2', '수학검사2', '_F11_heads.tsv'), 'w', encoding='utf-8')
for f in sorted(glob.glob(os.path.join(ROOT, '장v2', '장*.md'))):
    sec = ''
    for ln, l in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', l)
        if m: sec = m.group(1)
        for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}([^*]*)\*\*', l):
            out.write('\t'.join([os.path.basename(f), str(ln), sec, m.group(1), m.group(2), m.group(3), m.group(4).strip()]) + '\n')
out.close()
