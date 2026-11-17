# -*- coding: utf-8 -*-
# R10: appendix B: time vs folder ctime; peer presence; citation coverage both ways. Read-only.
import re, sys, io, os, json, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, '..', '..', '장v2')
rec = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
rows = []
for line in io.open(os.path.join(base, '부록B.md'), encoding='utf-8'):
    m = re.match(r'^\| (r[0-9a-f]{7}) \| ([^|]+) \| (.*) \| `([^`]+)` \|$', line.rstrip())
    if m: rows.append(m.groups())
ids = set(r[0] for r in rows)
allrec = sorted(os.listdir(rec))
pref = {}
for d in allrec: pref.setdefault(d[:8], []).append(d)
print('prefix collisions among all records:', [k for k, v in pref.items() if len(v) > 1])
nopeer = []; tdiff = []
for rid, tm, title, folder in rows:
    p = os.path.join(rec, folder)
    ct = time.strftime('%m-%d %H:%M', time.localtime(os.stat(p).st_ctime))
    if ct != tm.strip(): tdiff.append((rid, tm, ct))
    pj = json.load(io.open(os.path.join(p, 'provenance.json'), encoding='utf-8'))
    if not pj.get('peer_session'): nopeer.append(rid)
    if not pj.get('review_session'): print('no review session', rid)
print('time diffs:', tdiff)
print('no peer:', nopeer)
noev = [d[:8] for d in allrec if not os.path.isdir(os.path.join(rec, d, 'evidence'))]
print('records w/o evidence (all 350):', noev, 'listed in B:', [x for x in noev if x in ids])
# citations
files = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md','부록A.md','부록C.md'] + sorted(os.path.basename(x) for x in glob.glob(os.path.join(base, '부록D_장*.md')))
cited = {}
for f in files:
    txt = io.open(os.path.join(base, f), encoding='utf-8').read()
    for m in re.finditer(r'(?<![0-9a-zA-Z_/\`])r[0-9a-f]{7}(?![0-9a-zA-Z])', txt):
        cited.setdefault(m.group(0), {}).setdefault(f, 0)
        cited[m.group(0)][f] += 1
c = set(cited)
print('cited not in B:', sorted(c - ids))
for x in sorted(c - ids): print('   ', x, cited[x], 'folder exists:', x in pref)
print('in B not cited:', sorted(ids - c))
# which B ids are cited only in appendices A/C
only_app = [i for i in sorted(ids & c) if all(f.startswith('부록') for f in cited[i])]
print('cited only in appendices:', only_app)
for i in only_app: print('   ', i, cited[i])
# longer ids (r + 8 hex) appearing
for f in files:
    txt = io.open(os.path.join(base, f), encoding='utf-8').read()
    for m in re.finditer(r'(?<![0-9a-zA-Z_/\`])r[0-9a-f]{8,}', txt):
        print('long id', f, m.group(0), txt[max(0,m.start()-40):m.end()+20].replace('\n',' '))
