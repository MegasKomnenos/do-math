# -*- coding: utf-8 -*-
# R10: check appendix B rows against record folders (existence, title, time, review/, evidence layout)
# and against citations in chapter/appendix files. Read-only.
import re, sys, io, os, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
rec = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
rows = []
for line in io.open(os.path.join(base, '부록B.md'), encoding='utf-8'):
    m = re.match(r'^\| (r[0-9a-f]{7}) \| ([^|]+) \| (.*) \| `([^`]+)` \|$', line.rstrip())
    if m: rows.append(m.groups())
print('rows', len(rows))
ids = [r[0] for r in rows]
print('dup ids', [i for i in ids if ids.count(i) > 1])
# order by time
times = [r[1].strip() for r in rows]
print('time sorted:', times == sorted(times))
for rid, tm, title, folder in rows:
    p = os.path.join(rec, folder)
    probs = []
    if not folder.startswith(rid): probs.append('folder prefix mismatch')
    if not os.path.isdir(p): probs.append('NO FOLDER'); print(rid, probs); continue
    for need in ['exposition.md', 'record.json', 'review']:
        if not os.path.exists(os.path.join(p, need)): probs.append('missing ' + need)
    try:
        j = json.load(io.open(os.path.join(p, 'record.json'), encoding='utf-8'))
        if j.get('title', '').strip() != title.strip():
            probs.append('TITLE DIFF\n   B: %s\n   R: %s' % (title, j.get('title')))
    except Exception as e:
        probs.append('json err %s' % e)
    prov = os.path.join(p, 'provenance.json')
    tinfo = ''
    if os.path.exists(prov):
        try:
            pj = json.load(io.open(prov, encoding='utf-8'))
            tinfo = json.dumps(pj, ensure_ascii=False)[:300]
        except Exception as e:
            tinfo = 'prov err'
    ev = os.path.join(p, 'evidence')
    evl = sorted(os.listdir(ev)) if os.path.isdir(ev) else None
    rv = os.path.join(p, 'review')
    rvl = sorted(os.listdir(rv))[:6] if os.path.isdir(rv) else None
    print(rid, tm, '| probs:', probs, '| ev:', (evl[:8] if evl is not None else 'NO evidence/'), '| review:', rvl)
    if len(sys.argv) > 1: print('   prov:', tinfo)
