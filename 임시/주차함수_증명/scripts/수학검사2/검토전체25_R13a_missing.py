# -*- coding: utf-8 -*-
# R13a: roman-name / font-letter symbols appearing in >=2 chapters, compared with ledger 1.2 first cells.
# Aid for locating candidates; each candidate is then read in the chapter files.
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
F = importlib.import_module('검토전체25_R13a_find')
data = F.load()
led = io.open(os.path.join(F.base, '장부_v2.md'), encoding='utf-8').read().split('\n')
cells12 = ' '.join(led[n-1].split(' | ')[0] for n in range(49, 288))
txt12 = '\n'.join(led[42:288]); txt13 = '\n'.join(led[288:358])
BS = chr(92)
pats = [BS*2 + r'mathrm\{[A-Za-z]+\}', BS*2 + r'mathcal [A-Z]', BS*2 + r'mathfrak [A-Za-z]', BS*2 + r'mathsf [A-Za-z]', BS*2 + r'mathsf\{[A-Za-z]+\}']
deco = re.compile(r'(\^\{' + BS*2 + r'mathrm\{?[A-Za-z ]+\}?\}|_\{' + BS*2 + r'mathrm\{?[A-Za-z ]+\}?\}|\^' + BS*2 + r'[a-z]+|\^\{' + BS*2 + r'[a-z]+\})')
use = {}
for ch, b, i, sec, l in data:
    for p in pats:
        for m in re.finditer(p, l):
            tok = m.group(0)
            rest = l[m.end():m.end()+24]
            d = deco.match(rest)
            key = tok + (d.group(0) if d else '')
            use.setdefault(key, {}).setdefault(ch, 0)
            use[key][ch] += 1
def k(x): return int(x)
skip = set(BS + 'mathrm{' + x + '}' for x in ('i', 'e', 'Re', 'Im', 'Arg', 'Gamma', 'Beta'))
basere = re.compile(BS*2 + r'math[a-z]+ ?\{?[A-Za-z]+\}?')
for key in sorted(use):
    chs = sorted(use[key], key=k)
    if len(chs) < 2 or key in skip: continue
    if key in cells12: continue
    base = basere.match(key).group(0)
    print('%-44s ch %s | base in 1.2 heads:%s  key in 1.2 text:%s  in 1.3:%s' % (key, ','.join('%s:%d' % (c, use[key][c]) for c in chs), base in cells12, key in txt12, key in txt13))
