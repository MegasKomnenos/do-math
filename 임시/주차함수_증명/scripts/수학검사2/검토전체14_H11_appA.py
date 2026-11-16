# -*- coding: utf-8 -*-
"""H11: 부록 A의 「처음 정의된 절」과 부록 C 낱말 표의 「처음 정의된 절」을,
장 파일에서 그 기호/낱말이 처음 나오는 절과 대조한다(후보 목록; 사람이 판정)."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
order = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md','장11.md']
lines = []  # (file, ln, sec, normtext, text)
for f in order:
    sec = None
    for ln, line in enumerate(open(os.path.join(root, f), encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        lines.append((f, ln, sec, re.sub(r'\s+', '', line), line))
def first_occ(tok, skip_ch1=True):
    t = re.sub(r'\s+', '', tok)
    for f, ln, sec, nt, line in lines:
        if skip_ch1 and f == '장1.md': continue
        if t in nt: return (f, ln, sec)
    return None
print('===== 부록 A')
A = open(os.path.join(root, '부록A.md'), encoding='utf-8').read().splitlines()
for ln, line in enumerate(A, 1):
    if not line.startswith('| $'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) < 4: continue
    sym = cells[0]; secs = re.findall(r'\d+\.\d+', cells[2])
    first = re.findall(r'\$([^$]+)\$', sym)
    if not first: continue
    tok = first[0]
    tok = re.split(r':=|=|,', tok)[0]
    tok = tok.strip()
    if len(tok) < 2: continue
    occ = first_occ(tok, skip_ch1=not any(s.startswith('1.') for s in secs))
    if occ is None:
        print(f'A{ln}: {sym[:50]!r} 절{secs}: 찾지 못함(토큰 {tok!r})'); continue
    f, l, sec = occ
    if sec not in secs and not (secs and sec and sec.split('.')[0] == secs[0].split('.')[0] and sec.startswith(secs[0])):
        print(f'A{ln}: {sym[:60]!r} A절={secs} 첫출현={f}:{l} 절{sec}  (토큰 {tok!r})')
print('===== 부록 C 낱말 표')
C = open(os.path.join(root, '부록C.md'), encoding='utf-8').read().splitlines()
for ln, line in enumerate(C[6:148], 7):
    if not line.startswith('| ') or line.startswith('|---') or line.startswith('| 이 글의'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) != 3: continue
    term = re.split(r'[,(（]', cells[0])[0].strip()
    secs = re.findall(r'\d+\.\d+', cells[2])
    if not secs or term.startswith('$'): continue
    occ = first_occ(term, skip_ch1=not any(s.startswith('1.') for s in secs))
    if occ is None:
        print(f'C{ln}: {term!r} 절{secs}: 찾지 못함'); continue
    f, l, sec = occ
    if sec not in secs:
        print(f'C{ln}: {term!r} C절={secs} 첫출현={f}:{l} 절{sec}')
