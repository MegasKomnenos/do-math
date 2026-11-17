# -*- coding: utf-8 -*-
# R10: appendix C word table vs ledger section 3 (word, first-definition section, first-edition words).
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..', '..')
L = io.open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
led = {}; on = False
for i, line in enumerate(L, 1):
    if line.startswith('## 3.'): on = True; continue
    if line.startswith('## 4.'): on = False
    if on and line.startswith('| ') and not line.startswith('| 낱말') and not line.startswith('|---'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        if len(c) >= 4: led[c[0]] = dict(line=i, mean=c[1], sec=c[2], old=c[3])
        else: print('ledger3 cells?', i, len(c), line[:80])
C = {}; on = False
for i, line in enumerate(io.open(os.path.join(root, '장v2', '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 낱말'): on = True; continue
    if line.startswith('### 기록이'): on = False
    if on and line.startswith('| ') and not line.startswith('| 이 글의 용어') and not line.startswith('|---'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        C[c[0]] = dict(line=i, rec=c[1], sec=c[2])
print('C rows', len(C), 'ledger3 rows', len(led))
print('C not in ledger3:', [(k, C[k]['line']) for k in C if k not in led])
for k, c in C.items():
    l = led.get(k)
    if not l: continue
    if c['sec'] != l['sec']: print('SEC C%d/L%d %s: C=%s L=%s' % (c['line'], l['line'], k, c['sec'], l['sec']))
    if c['rec'] != l['old']: print('REC C%d/L%d %s\n   C: %s\n   L: %s' % (c['line'], l['line'], k, c['rec'][:200], l['old'][:200]))
if len(sys.argv) > 1:
    print('ledger3 words not in C:', len([k for k in led if k not in C]))
    for k in led:
        if k not in C: print('  L%d %s | %s | old: %s' % (led[k]['line'], k, led[k]['sec'], led[k]['old'][:80]))
