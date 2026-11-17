# -*- coding: utf-8 -*-
# R13a: for ledger 1.2 rows FROM..TO print the ledger cells (meaning, def section) and, from the
# chapter files, the first occurrence of the row's tokens overall, the first inside the claimed
# definition section, and occurrences followed closely by ':=' (definition candidates).
# Aid for locating the definition site to read; no judgement is made here.
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
F = importlib.import_module('검토전체25_R13a_find')
B = None
src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '검토전체25_R13a_bulk.py'), encoding='utf-8').read()
# reuse token table and bare filter without running the bulk loop
head = src.split('NOBARE =')[0]
ns = {'__file__': os.path.abspath(__file__)}
exec(compile(head, 'bulk_head', 'exec'), ns)
T = ns['T']; bare_ok = ns['bare_ok']; data = ns['data']; led = ns['led']
NOBARE = set(range(118, 288))
a, b = int(sys.argv[1]), int(sys.argv[2])
CTX = int(sys.argv[3]) if len(sys.argv) > 3 else 170
extra = {}
for arg in sys.argv[4:]:
    n, t = arg.split('=', 1); extra.setdefault(int(n), []).append(t)
def secmatch(sec, claimed):
    # claimed like '2.7' matches sec '2.7' or '2.7.x'; '5.5' matches '5.5.3'
    return sec == claimed or sec.startswith(claimed + '.')
for n in range(a, b + 1):
    row = led[n-1]
    cells = row.split(' | ')
    if len(cells) != 7:
        print('L%d ?? cells=%d' % (n, len(cells))); continue
    toks = extra.get(n) or T.get(n)
    print('=' * 100)
    print('L%d  %s' % (n, cells[0][2:]))
    print('  뜻: %s' % cells[2][:int(os.environ.get('MEAN','260'))])
    print('  정의 절: %s   | 쓰이는 장: %s' % (cells[3], cells[4]))
    if not toks:
        print('  (no tokens)'); continue
    claimed = re.findall(r'\d+\.\d+', cells[3])
    first = None; insec = {}; defs = []
    for ch, bn, i, sec, l in data:
        for t in toks:
            st = 0
            while True:
                p = l.find(t, st)
                if p < 0: break
                st = p + len(t)
                if n not in NOBARE and not bare_ok(l, p): continue
                item = (bn, i, sec, l[max(0, p-CTX):p+len(t)+CTX])
                if first is None: first = item
                for c in claimed:
                    if secmatch(sec, c) and c not in insec and not bn.startswith('부록'): insec[c] = item
                tail = l[p:p+len(t)+60]
                if ':=' in tail and len(defs) < 4: defs.append(item)
    def pr(tag, it):
        print('  [%s] %s:%d [%s] ...%s...' % (tag, it[0], it[1], it[2], it[3]))
    if first: pr('first', first)
    for c in claimed:
        if c in insec:
            if insec[c] != first: pr('in ' + c, insec[c])
        else:
            print('  [in %s] NONE FOUND in that section' % c)
    shown = 0
    for d in defs:
        if d == first or d in insec.values(): continue
        ok = any(secmatch(d[2], c) for c in claimed) or not insec
        if ok and shown < 2:
            pr(':=', d); shown += 1
