# -*- coding: utf-8 -*-
# R10: every {{label}} used in 장10/부록A/B/C: exists as a statement head? kind word before it matches the head's kind?
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']
heads = {}
for f in files:
    sec = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,5} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        m = re.match(r'^\*\*(주 정리|정리|명제|보조정리|따름정리|정의)\s*\{\{([^}]+)\}\}\s*(\(([^*]*?)\)\s*)?(\[.*?\])?\.?\*\*', line)
        if m:
            heads[m.group(2)] = dict(kind=m.group(1), file=f, line=i, sec=sec, title=(m.group(4) or ''), full=line[:400])
# D labels
import glob
dl = set()
for f in glob.glob(os.path.join(base, '부록D_장*.md')):
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'^### D\.\{\{(D:[^}]+)\}\}', line)
        if m: dl.add(m.group(1))
kinds = ['주 정리','따름정리','보조정리','정리','명제','정의']
for f in ['장10.md','부록A.md','부록B.md','부록C.md']:
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        # walk through label refs, tracking the last kind word (lists like 정리 A·B·명제 C)
        pos = 0; last_kind = None
        for m in re.finditer(r'(주 정리|따름정리|보조정리|정리|명제|정의|부록 D\.|D\.)?\s*\{\{([^}]+)\}\}', line):
            lab = m.group(2); k = m.group(1)
            between = line[pos:m.start()]
            if k: last_kind = k.strip()
            elif not re.fullmatch(r'[·,\s]*', between): last_kind = None
            pos = m.end()
            if lab.startswith('D:'):
                if lab not in dl: print('%s:%d MISSING D label %s' % (f, i, lab))
                continue
            h = heads.get(lab)
            if not h:
                print('%s:%d MISSING label %s' % (f, i, lab)); continue
            if last_kind and last_kind not in ('부록 D.', 'D.') and last_kind != h['kind']:
                print('%s:%d KIND %s {{%s}} but head is %s (%s §%s)' % (f, i, last_kind, lab, h['kind'], h['file'], h['sec']))
            if not last_kind:
                print('%s:%d nokind {{%s}} head %s §%s ctx: %s' % (f, i, lab, h['kind'], h['sec'], line[max(0,m.start()-30):m.end()+5].replace('\n',' ')))
if len(sys.argv) > 1:
    for lab in sys.argv[1:]:
        h = heads.get(lab); print(lab, '->', (h['kind'], h['file'], h['line'], h['sec'], h['title']) if h else None)
