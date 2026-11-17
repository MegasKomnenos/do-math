# -*- coding: utf-8 -*-
# R10: appendix C letter table, first column: does each symbol of "this text" occur in chapters / appendix D?
# Locator only (whitespace-insensitive fixed substring); each miss is re-checked by hand.
import re, sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md'] + [os.path.basename(x) for x in glob.glob(os.path.join(base, '부록D_장*.md'))]
def nos(s): return re.sub(r'\s+', '', s)
body = nos('\n'.join(io.open(os.path.join(base, f), encoding='utf-8').read() for f in files))
on = False
for i, line in enumerate(io.open(os.path.join(base, '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 기록의 글자'): on = True; continue
    if line.startswith('### 영어를'): on = False
    if not on or not line.startswith('| ') or line.startswith('| 이 글의 글자') or line.startswith('|---'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    miss = []
    for t in re.findall(r'\$([^$]+)\$', c[0]):
        tn = nos(t)
        cands = [tn]
        # variants: drop trailing argument list; ' vs ^\prime ; braces around single superscripts
        core = re.sub(r'\([^()]*\)$', '', tn); cands.append(core)
        BS = chr(92)
        cands.append(tn.replace('^' + BS + 'prime', "'")); cands.append(core.replace('^' + BS + 'prime', "'"))
        cands.append(re.sub('[' + BS + '^][{]([A-Za-z#]+)[}]', lambda m: '^' + m.group(1), core))
        cands.append(re.sub('[' + BS + '^]([A-Za-z])', lambda m: '^{' + m.group(1) + '}', core))
        if not any(x and x in body for x in cands): miss.append(t)
    if miss: print('C%d miss: %s   || col1: %s' % (i, ' ; '.join(miss), c[0][:150]))
