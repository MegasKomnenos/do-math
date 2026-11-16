# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 본문 진술 머리에 맞세워 차이를 출력한다.
판단은 출력을 읽고 사람이 한다. 자리 찾기와 문자열 대조만 한다."""
import re, glob, difflib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'

ch11 = open(ROOT + r'\장11.md', encoding='utf-8').read().split('\n')
rows = []
for ln in ch11:
    if ln.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in ln.strip().strip('|').split(' | ')]
        if len(cells) != 6:
            print('CELLS!=6', len(cells), ln[:80]); continue
        rows.append(cells)
print('11.2 rows:', len(rows))

# 부록 D 항목 파싱
items = {}
for f in sorted(glob.glob(ROOT + r'\부록D_장*.md')):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'\n(?=### D\.\{\{D:)', '\n' + txt)
    for p in parts:
        m = re.match(r'### D\.\{\{D:([^}]+)\}\}\s*(.*)', p)
        if not m: continue
        lab = m.group(1); title = m.group(2).strip()
        d = {'file': f.split('\\')[-1], 'title': title}
        for key in ['확인하는 진술', '산술 등급', '독립 재계산', '범위', '자료']:
            mm = re.search(r'\*\*' + key + r'\.\*\*\s*(.*)', p)
            d[key] = mm.group(1).strip() if mm else None
        items[lab] = d
print('D items:', len(items))

# 본문 진술 머리 수집: label -> (type, section, file)
heads = {}
for f in sorted(glob.glob(ROOT + r'\장*.md')):
    sec = None
    for ln in open(f, encoding='utf-8'):
        ms = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)', ln)
        if ms: sec = ms.group(1)
        for mh in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}', ln):
            lab = mh.group(2)
            if lab not in heads:
                heads[lab] = (mh.group(1), sec, f.split('\\')[-1], ln.strip()[:400])
print('heads:', len(heads))

def labs(s):
    return re.findall(r'(정리|명제|보조정리|따름정리)\s+\{\{(\d+[AB]?:[^}]+)\}\}(\([가-힣]\))?', s)

for cells in rows:
    dlab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
    print('\n' + '=' * 100)
    print('ROW', dlab)
    it = items.get(dlab)
    if not it:
        print('  !! D item not found'); continue
    print('  D file/title:', it['file'], '|', it['title'])
    # 진술 대조
    print('  11.2 진술:', cells[1])
    print('  D 제목 진술:', re.findall(r'\((.*)\)\s*$', it['title']))
    for t, lab, part in labs(cells[1]):
        h = heads.get(lab)
        if not h:
            print('   !! head not found', lab); continue
        flag = '' if h[0] == t else '  !! TYPE MISMATCH head=' + h[0]
        secflag = '' if (h[1] and (h[1] in cells[3].replace('·', ' ').split() or cells[3].startswith(h[1]))) else '  ?? section head=' + str(h[1]) + ' vs 11.2=' + cells[3]
        print(f'   {t} {lab}{part}: head {h[0]} sec {h[1]} ({h[2]}){flag}{secflag}')
        print('     HEAD:', h[3][:300])
    print('  11.2 등급:', cells[2])
    print('  D 산술 등급 줄:', it['산술 등급'])
    br = re.match(r'(〔[^〕]*〕)\s*(.*)', it['독립 재계산'] or '')
    if not br:
        print('  !! D 독립 재계산 꺾쇠 없음:', (it['독립 재계산'] or '')[:100])
        continue
    dbr, drest = br.group(1), br.group(2)
    print('  꺾쇠 11.2:', cells[4])
    print('  꺾쇠 D   :', dbr, '' if dbr == cells[4] else '  !! DIFF')
    if drest.strip() == cells[5].strip():
        print('  독립 재계산 서술: 동일')
    else:
        print('  독립 재계산 서술: 차이 ->')
        a = re.split(r'(?<=다\.)\s', drest.strip()); b = re.split(r'(?<=다\.)\s', cells[5].strip())
        for d in difflib.unified_diff(a, b, 'D', '11.2', lineterm='', n=0):
            if d.startswith(('---', '+++', '@@')): continue
            print('    ', d)
    print('  D 자료 줄:', (it['자료'] or '')[:200])
