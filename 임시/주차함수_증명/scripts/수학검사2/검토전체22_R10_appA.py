# -*- coding: utf-8 -*-
# R10: appendix A rows: symbol cell, claimed section; first occurrences (fixed string) in chapter files.
# Only a locator: every discrepancy is confirmed by reading the body.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md']
lines = []  # (file, lineno, sec, text)
for f in files:
    sec = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,5} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        lines.append((f, i, sec, line))
def first(tok, n=3):
    out = []
    for f, i, sec, line in lines:
        if tok in line:
            out.append((f, i, sec))
            if len(out) >= n: break
    return out
rows = []
for i, line in enumerate(io.open(os.path.join(base, '부록A.md'), encoding='utf-8'), 1):
    if not line.startswith('| $'): continue
    # split on ' | ' but only first 3 separators from left for sym, then find section cell as 3rd cell
    cells = line.rstrip('\n').strip('|').split(' | ')
    sym = cells[0].strip()
    # the section cell: third cell normally; but meaning cell can contain ' | '? check count
    rows.append((i, sym, cells[2].strip() if len(cells) >= 4 else '??', len(cells)))
for i, sym, sec, n in rows:
    toks = re.findall(r'\$([^$]+)\$', sym)
    print('A%d | %s | claimed %s | cells=%d' % (i, sym, sec, n))
    for t in toks[:3]:
        # strip arguments like (x), (y;x) and leading/trailing spaces, split on ', '
        for part in [p.strip() for p in t.split(', ')]:
            core = re.sub(r'\([^()]*\)$', '', part).strip()
            core = re.sub(r':=.*$', '', core).strip()
            occ = first(core)
            print('     tok %-28s -> %s' % (core, ' ; '.join('%s:%d[%s]' % o for o in occ) if occ else 'NOT FOUND'))
