# -*- coding: utf-8 -*-
# R10: appendix A rows vs ledger 1.1/1.2 rows (same symbol cell): compare meaning, section, record letters.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..', '..')
def norm(s): return s.replace('`', '').strip()
led = {}; sec = ''
L = io.open(os.path.join(root, '장부_v2.md'), encoding='utf-8').read().split('\n')
for i, line in enumerate(L, 1):
    if line.startswith('### 1.1'): sec = '1.1'
    elif line.startswith('### 1.2'): sec = '1.2'
    elif line.startswith('### 1.3') or line.startswith('## 2'): sec = ''
    if sec and line.startswith('| $'):
        c = line.strip().strip('|').split(' | ')
        c = [x.strip() for x in c]
        if sec == '1.1' and len(c) >= 4: led[c[0]] = dict(sec=sec, line=i, mean=norm(c[1]), dsec=None, rec=None, note=c[3])
        elif sec == '1.2' and len(c) >= 7: led[c[0]] = dict(sec=sec, line=i, mean=norm(c[2]), dsec=norm(c[3]), rec=norm(c[6]))
        else: print('ledger row cells?', i, len(c))
A = {}
for i, line in enumerate(io.open(os.path.join(root, '장v2', '부록A.md'), encoding='utf-8'), 1):
    if line.startswith('| $'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        A[c[0]] = dict(line=i, mean=norm(c[1]), dsec=norm(c[2]), rec=norm(c[3]))
print('A rows', len(A), 'ledger rows', len(led))
print('A not in ledger:', [k for k in A if k not in led])
print('ledger not in A:', [(k, led[k]['sec'], led[k]['line']) for k in led if k not in A])
for k, a in A.items():
    l = led.get(k)
    if not l: continue
    if a['mean'] != l['mean']: print('MEAN A%d/L%d %s\n  A: %s\n  L: %s' % (a['line'], l['line'], k, a['mean'][:300], l['mean'][:300]))
    if l['dsec'] is not None and a['dsec'] != l['dsec']: print('DSEC A%d/L%d %s: A=%s L=%s' % (a['line'], l['line'], k, a['dsec'], l['dsec']))
    if l['rec'] is not None and a['rec'] != l['rec']: print('REC A%d/L%d %s\n  A: %s\n  L: %s' % (a['line'], l['line'], k, a['rec'][:300], l['rec'][:300]))
    if l['dsec'] is None: print('VAR A%d/L%d %s: A dsec=%s rec=%s | ledger note: %s' % (a['line'], l['line'], k, a['dsec'], a['rec'], l['note'][:120]))
