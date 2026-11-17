# -*- coding: utf-8 -*-
# R10: locate keyword occurrences with section and enclosing statement/proof context. Read-only.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '장v2')
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','부록D_장2.md','부록D_장3.md','부록D_장4.md','부록D_장5A.md','부록D_장7A.md','부록D_장7B.md','부록D_장8.md','부록D_장9.md']
kws = sys.argv[1:-1] if sys.argv[-1].isdigit() else sys.argv[1:]
width = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 70
for f in files:
    sec = ''; ctx = ''
    for i, line in enumerate(io.open(os.path.join(base, f), encoding='utf-8'), 1):
        m = re.match(r'^#{2,4} (D\.\{\{[^}]+\}\}|\d+(?:\.\d+)*)', line)
        if m: sec = m.group(1); ctx = ''
        m = re.match(r'^\*\*((?:정리|명제|보조정리|따름정리|정의) \{\{[^}]+\}\})', line)
        if m: ctx = m.group(1)
        elif line.startswith('**증명'):
            ctx = (ctx.split(' 증명')[0] + ' 증명') if ctx else '증명'
        elif line.strip() and not line.startswith(('$$','|','**')) and ctx.endswith('증명') and prev_end:
            ctx = ctx + '뒤'
        prev_end = line.rstrip().endswith('∎')
        for kw in kws:
            for m in re.finditer(re.escape(kw), line):
                s = max(0, m.start()-width); e = min(len(line), m.end()+width)
                print('%s:%d [%s] <%s> …%s…' % (f, i, sec, ctx, line[s:e].strip().replace('\n',' ')))
