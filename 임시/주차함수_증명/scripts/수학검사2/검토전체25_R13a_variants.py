# -*- coding: utf-8 -*-
# R13a: tally decorated variants of selected symbol families in chapter files (per chapter),
# to check that every variant in use has a ledger 1.2 row (or is covered by a family row).
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
F = importlib.import_module('검토전체25_R13a_find')
data = F.load()
BS = chr(92)
fams = sys.argv[1:] or [
    BS + 'mathrm{Stays}', BS + 'mathrm{Bd}', BS + 'mathrm{LB}', 's^{' + BS + 'mathrm W}', BS + 'mathrm{Bor}', BS + 'mathrm{DDL}',
    BS + 'mathrm{DD}', BS + 'mathrm{Ren}', BS + 'mathrm{inh}', BS + 'mathrm{top}', BS + 'mathrm{cl}', BS + 'mathrm{KD}',
    BS + 'mathrm{tilt}', BS + 'mathrm{inc}', BS + 'mathrm{pd}', BS + 'mathrm{wg}', BS + 'mathrm{lc}', BS + 'mathrm{nf}',
    BS + 'mathrm{hf}', BS + 'mathrm{vm}', BS + 'mathrm{stp}', BS + 'mathrm{hz}', BS + 'mathrm{src}', BS + 'mathrm{apex}',
    BS + 'mathrm{PM}', BS + 'mathrm{Quad}', BS + 'mathrm{Stem}', BS + 'mathrm{Left}', BS + 'mathrm{rb}', BS + 'mathrm{rq}',
    BS + 'mathrm{sm}', BS + 'mathrm{Gr}', BS + 'mathrm{He}', BS + 'mathrm{km}', BS + 'mathrm{fb}', BS + 'mathrm{Flow}',
    BS + 'mathrm{dup}', BS + 'mathrm{Res}', BS + 'mathrm{loss}', BS + 'mathrm{IH}', BS + 'mathrm{Lip}', BS + 'mathrm{LOW}',
    BS + 'mathrm{BV}', BS + 'mathrm{PF}', BS + 'mathrm{pos}', BS + 'mathrm{tail}', BS + 'mathrm{WIN}', BS + 'mathrm{POS}',
]
deco = re.compile(r"((?:\^\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\^" + BS*2 + r"[a-zA-Z]+|\^[A-Za-z0-9*+\-']|'+|_\{" + BS*2 + r"mathrm\{?[A-Za-z ]+\}?\}|_" + BS*2 + r"[a-z]+|_[>*])*)")
for fam in fams:
    forms = {}
    for ch, b, i, sec, l in data:
        st = 0
        while True:
            p = l.find(fam, st)
            if p < 0: break
            st = p + len(fam)
            if fam.startswith('s^') and p > 0 and (l[p-1].isalpha() or l[:p].rstrip().endswith(BS + 'mathfrak')): continue
            m = deco.match(l, st)
            key = fam + (m.group(1) if m else '')
            forms.setdefault(key, {}).setdefault(ch, 0)
            forms[key][ch] += 1
    if len(forms) <= 1: continue
    print('== ' + fam)
    for key in sorted(forms):
        print('   %-52s %s' % (key, ' '.join('%s:%d' % (c, forms[key][c]) for c in sorted(forms[key], key=int))))
