# -*- coding: utf-8 -*-
# R13a: ledger section 2 (quantity dictionary) vs section 1.2: for each Q row whose first written
# symbol in "쓰는 글자·이름" is a 1.2 row head (or one of its comma parts), compare the definition
# section cells. Aid only; hits are read in the originals.
import io, os, re
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
led = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
rows = {}
for n in range(49, 288):
    c = led[n-1].split(' | ')
    head = c[0][2:].strip()
    rows[head] = (n, c[3].strip())
    inner = head.strip('$')
    for part in inner.split(', '):
        rows.setdefault('$' + part.strip() + '$', (n, c[3].strip()))
secnums = lambda s: re.findall(r'\d+\.\d+(?:\.\d+)?', s)
for n in range(365, 446):
    l = led[n-1]
    if not l.startswith('| (Q'): continue
    c = l.split(' | ')
    if len(c) != 4:
        print('L%d cells=%d' % (n, len(c))); continue
    q = re.match(r'\| \((Q\d+)\)', l).group(1)
    use = c[1]
    dsec = c[3].rstrip(' |').strip()
    if use.startswith('뺌'): continue
    syms = re.findall(r'\$[^$]+\$', use)
    hit = None
    for s in syms[:3]:
        if s in rows: hit = s; break
    if not hit:
        print('L%d %s: first symbols %s not a 1.2 head | def %s' % (n, q, syms[:2], dsec[:40])); continue
    ln, d12 = rows[hit]
    a, b = secnums(dsec), secnums(d12)
    if not a or not b or a[0] != b[0]:
        print('L%d %s %s: section 2 def [%s] vs 1.2 L%d def [%s]' % (n, q, hit, dsec[:80], ln, d12[:80]))
