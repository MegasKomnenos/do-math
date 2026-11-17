# -*- coding: utf-8 -*-
# R10: list statement heads (label, kind, title, bracket) with file/section. Read-only.
import re, sys, io, glob, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']
head_re = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|주 정리)\s*\{\{([^}]+)\}\}\s*(\([^*]*?\))?\s*(\[[^\]]*(?:\][^\]*]*)*\])?\.?\*\*')
out = []
for f in files:
    sec = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1)
        if line.startswith('**'):
            m = re.match(r'^\*\*(.+?)\*\*', line)
            if m and '{{' in m.group(1):
                h = m.group(1)
                lab = re.search(r'\{\{([^}]+)\}\}', h).group(1)
                out.append(dict(file=f, line=i, sec=sec, label=lab, head=h))
if len(sys.argv) > 1:
    pat = sys.argv[1]
    for o in out:
        if pat in o['label'] or pat in o['head']:
            print(o['file'], o['line'], o['sec'], o['head'])
else:
    for o in out:
        print(o['file'], o['line'], o['sec'], o['head'])
