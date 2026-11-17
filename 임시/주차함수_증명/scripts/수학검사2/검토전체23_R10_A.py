# -*- coding: utf-8 -*-
# 부록 A 각 행의 「처음 정의된 절」을 장 파일의 첫 등장 절과 견주어 후보를 낸다(판정은 원문을 열어 한다).
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
# 장 파일: (절, 행, 줄) 목록
lines = []
for fn in files:
    sec = fn.replace('장','').rstrip('AB') + '.0'
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)(?:\.\d+)?', line)
        if m: sec = m.group(1)
        lines.append((sec, fn, i, line))
def split_row(line):
    # 수식 안의 | 는 없다고 보고 단순 분할하되, $...$ 안의 \| 등은 드물다
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    return cells
tbl = None; prevsec = None
for ln, line in enumerate(open(os.path.join(base, '장v2', '부록A.md'), encoding='utf-8').read().split('\n'), 1):
    if line.startswith('### '):
        tbl = line[4:]; prevsec = None; print('#####', tbl); continue
    if not line.startswith('| $') : continue
    cells = split_row(line)
    if len(cells) != 4:
        print('  CELLS', len(cells), 'L%d' % ln, line[:80]); 
    sym = cells[0]; seccell = cells[-2] if len(cells) >= 3 else '?'
    secs = re.findall(r'\d+\.\d+', seccell)
    first = secs[0] if secs else None
    # 순서
    if first and prevsec and tuple(map(int, first.split('.'))) < tuple(map(int, prevsec.split('.'))) and '변수' not in tbl:
        print('  ORDER L%d %s: %s after %s' % (ln, sym[:40], first, prevsec))
    if first: prevsec = first
    # 첫 등장: 기호 셀의 첫 $...$ 덩이
    toks = re.findall(r'\$([^$]+)\$', sym)
    tok = toks[0].split(',')[0].strip() if toks else None
    if tok is None: continue
    # 인수 괄호 앞까지를 핵으로
    core = re.split(r'\(', tok)[0] if not tok.startswith('(') else tok
    core = core.split(':=')[0].split('=')[0].strip()
    hit = None
    for sec, fn, i, l in lines:
        if core in l:
            hit = (sec, fn, i); break
    flag = ''
    if hit is None: flag = 'NOTFOUND'
    elif first and hit[0] != first: flag = 'DIFF'
    if flag:
        print('  %s L%d sym=%s core=[%s] stated=%s first=%s' % (flag, ln, sym[:50], core, seccell[:40], hit))
