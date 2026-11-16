# -*- coding: utf-8 -*-
"""K14: 장부 1.2 전역 기호의 「정의 절」을 장 파일의 첫 출현 절과 견준다(후보 표시)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
seq = []
for c in CH:
    sec = re.sub(r'[A-Z]', '', c.replace('장','')) + '.0'
    for ln, line in enumerate(open(os.path.join(ROOT, '장v2', c + '.md'), encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        seq.append((sec, c, ln, line))
def secnum(s):
    a, b = s.split('.')[:2]
    return (int(a), int(b))
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('### 1.2'))
end = next(i for i, l in enumerate(lines) if l.startswith('### 1.3'))
def variants(tok):
    v = {tok, re.sub(r'\{(\w)\}', r'\1', tok), re.sub(r'([_^])(\w)(?![\w{])', r'\1{\2}', tok), tok.replace('^\\prime', "'")}
    return [x for x in v if x]
out = []
for l in lines[start:end]:
    if not l.startswith('| $'): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    if len(cells) < 5: continue
    toks = []
    for g in re.findall(r'\$([^$]+)\$', cells[0]):
        depth = 0; cur = ''
        for ch in g:
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
            if ch == ',' and depth == 0: toks.append(cur); cur = ''
            else: cur += ch
        toks.append(cur)
    decl = re.findall(r'\d+\.\d+', cells[3])
    if not decl: continue
    dmin = min(secnum(x) for x in decl)
    keys = []
    for t in toks:
        core = re.split(r'[(<>=]', t.strip())[0].strip()
        if len(core) <= 2: continue
        keys.extend(variants(core))
    if not keys:
        continue
    found = None
    for sec, c, ln, line in seq:
        if any(k in line for k in keys):
            found = (sec, c, ln); break
    if not found:
        out.append(('장에 없음', cells[0], cells[3])); continue
    fs = secnum(found[0])
    if fs < dmin and not (fs[0] == 1 and fs[1] in (4, 5)) and fs[1] != 0:
        out.append(('먼저 나옴', cells[0], '장부=' + cells[3], '첫 출현=%s(%s:%d)' % found))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_defsec_out.txt'), 'w', encoding='utf-8') as f:
    for o in out: f.write('\t'.join(o) + '\n')
print('flagged', len(out))
