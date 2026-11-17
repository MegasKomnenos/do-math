# -*- coding: utf-8 -*-
# R10: appendix C name table vs statement heads: kind, title, record-name parenthetical; completeness both ways.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md']
heads = {}; order = []
for f in files:
    sec = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,5} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        if not line.startswith('**'): continue
        m = re.match(r'^\*\*(주 정리|정리|명제|보조정리|따름정리|정의)\s*\{\{([^}]+)\}\}\s*', line)
        if not m: continue
        rest = line[m.end():]
        # head ends at first '.**' ; find parenthetical (balanced) at start
        title = ''; recname = ''
        if rest.startswith('('):
            depth = 0
            for j, ch in enumerate(rest):
                if ch == '(': depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0: break
            inner = rest[1:j]
            k = inner.find('; 기록 [')
            if k >= 0: title = inner[:k]; recname = inner[k+2:]
            elif inner.startswith('기록 ['): title = ''; recname = inner
            else: title = inner
        heads[m.group(2)] = dict(kind=m.group(1), file=f, line=i, sec=sec, title=title.strip(), rec=recname.strip())
        order.append(m.group(2))
rows = {}; on = False; rorder = []
for i, line in enumerate(io.open(os.path.join(base, '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 기록이 결과에'): on = True; continue
    if line.startswith('### 기록의 글자'): on = False
    if not on or not line.startswith('| ') or line.startswith('| 기록의 이름') or line.startswith('|---'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    m = re.match(r'^(주 정리|정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}$', c[1])
    if not m: print('row format?', i, c[1]); continue
    if m.group(2) in rows: print('DUP row', i, m.group(2))
    rows[m.group(2)] = dict(line=i, kind=m.group(1), rec=c[0], title=c[2]); rorder.append(m.group(2))
print('rows', len(rows), 'heads with record name', sum(1 for h in heads.values() if h['rec']))
for lab, r in rows.items():
    h = heads.get(lab)
    if not h: print('C%d label missing %s' % (r['line'], lab)); continue
    if h['kind'] != r['kind']: print('C%d KIND %s: C=%s head=%s' % (r['line'], lab, r['kind'], h['kind']))
    if h['title'] != r['title']: print('C%d TITLE %s:\n   C: %s\n   H: %s' % (r['line'], lab, r['title'], h['title']))
    if h['rec'] != r['rec']: print('C%d RECNAME %s (%s:%d):\n   C: %s\n   H: %s' % (r['line'], lab, h['file'], h['line'], r['rec'], h['rec']))
for lab in order:
    if heads[lab]['rec'] and lab not in rows: print('HEAD with record name not in C: %s %s:%d (%s)' % (lab, heads[lab]['file'], heads[lab]['line'], heads[lab]['rec'][:80]))
# order check: table order vs body order
pos = {l: i for i, l in enumerate(order)}
seq = [pos[l] for l in rorder if l in pos]
bad = [(rorder[i], rorder[i+1]) for i in range(len(seq)-1) if seq[i] > seq[i+1]]
print('order inversions (table vs body order):', len(bad)); 
for a, b in bad: print('   ', a, '(§%s)' % heads[a]['sec'], '->', b, '(§%s)' % heads[b]['sec'])
