# -*- coding: utf-8 -*-
# R10: appendix C word table: first occurrences of each term in chapter files (locator only).
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']
lines = []
for f in files:
    sec = f.replace('.md','') + '머리'
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,5} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        lines.append((f, i, sec, line))
on = False
for i, line in enumerate(io.open(os.path.join(base, '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 낱말'): on = True; continue
    if line.startswith('### 기록이'): on = False
    if not on or not line.startswith('| ') or line.startswith('| 이 글의 용어') or line.startswith('|---'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    for term in [t.strip() for t in re.split(r'[,·]', re.sub(r'\([^()]*\)', '', c[0])) if t.strip()]:
        term_n = term.replace('$\mathsf P$', '').strip()
        occ = [(f, n, s) for f, n, s, l in lines if term_n and term_n in l]
        secs = []
        for f, n, s in occ:
            if s not in secs: secs.append(s)
        # sections where the term co-occurs with a definitional phrase on the same line near it
        dfn = []
        for f, n, s, l in lines:
            if term_n and term_n in l:
                for m in re.finditer(re.escape(term_n), l):
                    win = l[m.end():m.end()+25]
                    if re.match(r'(이|라|이라|이라고|라고|으로|로)?\s*(라 부른다|이라 부른다|부른다|부르자|한다|하자|부르며|부르고|라 하고|이라 하고|라 하며|이라 하며|라 하자|이라 하자|라 한다|이라 한다)', win):
                        if s not in dfn: dfn.append(s)
        print('C%d %-14s claimed %-12s | first secs: %s | defining-phrase secs: %s' % (i, term, c[2], ' '.join(secs[:5]), ' '.join(dfn[:5])))
