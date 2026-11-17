# -*- coding: utf-8 -*-
# R13a: ledger 1.2 rows vs appendix A rows (same first cell): definition section and meaning text.
# Prints rows whose def-section cells differ, rows missing on either side, and (with arg 'diff')
# rows whose meaning text differs after removing backticks. Aid only; each hit is read in the originals.
import io, os, re, sys, difflib
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
led = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
app = io.open(os.path.join(base, '장v2', '부록A.md'), encoding='utf-8').read().split('\n')
L = {}
for n in range(49, 288):
    c = led[n-1].split(' | ')
    if len(c) != 7: print('ledger L%d cells=%d' % (n, len(c))); continue
    L[c[0][2:].strip()] = (n, c[2].strip(), c[3].strip(), c[6].rstrip(' |').strip())
A = {}
for i, l in enumerate(app, 1):
    if not l.startswith('| $') and not l.startswith('| ('): continue
    c = l.split(' | ')
    if len(c) != 4: print('appA L%d cells=%d: %s' % (i, len(c), l[:60])); continue
    A[c[0][2:].strip()] = (i, c[1].strip(), c[2].strip(), c[3].rstrip(' |').strip())
norm = lambda s: s.replace('`', '')
print('ledger rows', len(L), 'appA rows', len(A))
for k in L:
    if k not in A: print('NOT IN appA: L%d %s' % (L[k][0], k))
for k in A:
    if k not in L and A[k][0] >= 24: print('NOT IN ledger 1.2: A%d %s' % (A[k][0], k))
print('--- def-section differences')
for k in L:
    if k in A and norm(L[k][2]) != norm(A[k][2]):
        print('L%d/A%d %s : ledger [%s] vs appA [%s]' % (L[k][0], A[k][0], k, L[k][2], A[k][2]))
print('--- record-letter cell differences')
for k in L:
    if k in A and norm(L[k][3]) != norm(A[k][3]):
        print('L%d/A%d %s' % (L[k][0], A[k][0], k))
        if 'rec' in sys.argv:
            print('    ledger: %s' % L[k][3][:500]); print('    appA  : %s' % A[k][3][:500])
if 'diff' in sys.argv:
    print('--- meaning differences')
    for k in L:
        if k in A and norm(L[k][1]) != norm(A[k][1]):
            a, b = norm(L[k][1]), norm(A[k][1])
            sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
            parts = []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != 'equal':
                    parts.append('%s: L[%s] A[%s]' % (tag, a[i1:i2][:160], b[j1:j2][:160]))
            print('L%d/A%d %s' % (L[k][0], A[k][0], k))
            for p in parts[:6]: print('     ' + p)
