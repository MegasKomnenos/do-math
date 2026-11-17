# -*- coding: utf-8 -*-
# R10: appendix A rows: claimed section vs sections of the labels named in the row (locator only).
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md']
heads = {}
for f in files:
    sec = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,5} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        m = re.match(r'^\*\*(주 정리|정리|명제|보조정리|따름정리|정의)\s*\{\{([^}]+)\}\}', line)
        if m: heads[m.group(2)] = (m.group(1), f, i, sec)
for i, line in enumerate(io.open(os.path.join(base, '부록A.md'), encoding='utf-8'), 1):
    if not line.startswith('| $'): continue
    cells = line.rstrip('\n').strip('|').split(' | ')
    labs = re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[1])
    if not labs: continue
    claimed = cells[2].strip()
    info = ['%s§%s' % (l, heads[l][3]) for l in labs]
    print('A%d %s | claimed %s | %s' % (i, cells[0].strip()[:40], claimed, ' ; '.join(info)))
