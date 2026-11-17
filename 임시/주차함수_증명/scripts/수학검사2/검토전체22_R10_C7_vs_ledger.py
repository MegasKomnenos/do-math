# -*- coding: utf-8 -*-
# R10: appendix C letter table vs ledger section 7; appendix C name table vs ledger section 4.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..', '..')
def norm(s): return re.sub(r'\s+', ' ', s.replace('`', '')).strip()
L = io.open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
led7 = []; on = False
for i, line in enumerate(L, 1):
    if line.startswith('## 7.'): on = True; continue
    if line.startswith('## 8.'): on = False
    if on and line.startswith('| ') and not line.startswith('| 이 글의 글자') and not line.startswith('|---'):
        c = [norm(x) for x in line.strip().strip('|').split(' | ')]
        led7.append((i, c))
C7 = []; on = False
for i, line in enumerate(io.open(os.path.join(root, '장v2', '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 기록의 글자'): on = True; continue
    if line.startswith('### 영어를'): on = False
    if on and line.startswith('| ') and not line.startswith('| 이 글의 글자') and not line.startswith('|---'):
        c = [norm(x) for x in line.strip().strip('|').split(' | ')]
        C7.append((i, c))
print('C7 rows', len(C7), 'ledger7 rows', len(led7))
lk = {}
for i, c in led7: lk.setdefault((c[0], c[1]), []).append((i, c))
used = set()
def strip_notes(s):
    # ledger-only audit notes in parentheses such as (확인), (Q68), (세션 결정 ..), dated notes
    s = re.sub(r'\((확인|Q\d+)\)', '', s)
    return norm(s)
for i, c in C7:
    key = (c[0], c[1])
    if key not in lk: print('C%d not in ledger7 (col1,col2): %s | %s' % (i, c[0][:80], c[1][:60])); continue
    li, lc = lk[key][0]; used.add(li)
    for j, name in [(2, 'record letters'), (3, 'shift')]:
        if len(c) > j and len(lc) > j and c[j] != lc[j] and strip_notes(c[j]) != strip_notes(lc[j]):
            print('C%d/L%d %s differ [%s]\n   C: %s\n   L: %s' % (i, li, name, c[0][:50], c[j][:330], lc[j][:330]))
for i, c in led7:
    if i not in used: print('ledger7 row not in C: L%d %s | %s' % (i, c[0][:80], c[1][:50]))
