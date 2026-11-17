# -*- coding: utf-8 -*-
import re, sys, io, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
items = {}
for f in sorted(glob.glob(base + '/장v2/부록D_장*.md')):
    txt = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^### ', txt)
    for p in parts[1:]:
        m = re.match(r'D\.\{\{D:([a-z0-9\-A-Z]+)\}\}(.*)', p)
        key = m.group(1)
        head = p.split('\n')[0]
        grade = re.search(r'(?m)^\*\*산술 등급\.\*\*(.*)$', p)
        rec = re.search(r'(?m)^\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)', p)
        items[key] = (os.path.basename(f), head, grade.group(1).strip() if grade else None, rec.group(1) if rec else None)
ch10 = open(base + '/장v2/장10.md', encoding='utf-8').read()
rows = {}
for line in ch10.split('\n'):
    m = re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (.*) \|$', line)
    if m:
        rows[m.group(1)] = m.groups()[1:]
for k, (f, head, grade, rec) in items.items():
    print('=====', k, f)
    print('HEAD:', head)
    print('GRADE(D):', grade)
    if k in rows:
        st, g, loc, r = rows[k]
        print('ROW stmts:', st)
        print('ROW grade:', g, '| loc:', loc)
        print('BRACKET same:', r.strip() == (rec or '').strip())
        if r.strip() != (rec or '').strip():
            print('  ROW:', r)
            print('  D  :', rec)
    else:
        print('NO ROW')
for k in rows:
    if k not in items:
        print('ROW WITHOUT ITEM', k)
