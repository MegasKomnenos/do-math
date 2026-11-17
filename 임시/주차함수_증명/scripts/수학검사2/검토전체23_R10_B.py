# -*- coding: utf-8 -*-
# 부록 B의 행을 기록 폴더와 맞춘다: 폴더 존재, 식별자=폴더 앞 8자, 제목=record.json title, 시각(파일 mtime 후보), review/ 존재, provenance의 작성자 수.
import re, sys, io, os, json, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]; R = sys.argv[2]
rows = []
for line in open(os.path.join(base, '장v2', '부록B.md'), encoding='utf-8'):
    m = re.match(r'\| (r[0-9a-f]{7}) \| (\d\d-\d\d \d\d:\d\d) \| (.*) \| `(r[0-9a-f]{32})` \|\s*$', line)
    if m: rows.append(m.groups())
print('rows', len(rows))
prev = ''
ids = []
for rid, tm, title, folder in rows:
    ids.append(rid)
    probs = []
    if folder[:8] != rid: probs.append('ID!=folder')
    p = os.path.join(R, folder)
    if not os.path.isdir(p): probs.append('NO FOLDER'); print(rid, probs); continue
    d = json.load(open(os.path.join(p, 'record.json'), encoding='utf-8'))
    if d['title'] != title: probs.append('TITLE DIFF: ' + d['title'])
    if not os.path.isdir(os.path.join(p, 'review')): probs.append('NO review/')
    if not os.path.isfile(os.path.join(p, 'exposition.md')): probs.append('NO exposition.md')
    pv = json.load(open(os.path.join(p, 'provenance.json'), encoding='utf-8')) if os.path.isfile(os.path.join(p, 'provenance.json')) else {}
    peer = pv.get('peer_session'); rev = pv.get('review_session')
    mt = time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(os.path.join(p, 'record.json'))))
    ct = time.strftime('%m-%d %H:%M', time.localtime(os.path.getctime(p)))
    if tm < prev: probs.append('ORDER')
    prev = tm
    ev = os.listdir(os.path.join(p, 'evidence')) if os.path.isdir(os.path.join(p, 'evidence')) else None
    print(rid, tm, '| rec mtime', mt, '| dir ctime', ct, '| peer', bool(peer), '| review', bool(rev), '| ev', (ev[:6] if ev is not None else 'NONE'), '|', probs)
# 중복
print('dups', [x for x in set(ids) if ids.count(x) > 1])
# 인용된 식별자
cited = {}
for f in sorted(glob.glob(os.path.join(base, '장v2', '장*.md')) + glob.glob(os.path.join(base, '장v2', '부록*.md'))):
    if os.path.basename(f).startswith('전_'): continue
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(?<![0-9a-zA-Z_\/])r[0-9a-f]{7}(?![0-9a-f])', txt):
        cited.setdefault(m.group(0), set()).add(os.path.basename(f))
print('cited not in B:', {k: sorted(v) for k, v in cited.items() if k not in ids})
print('B not cited outside B:', [i for i in ids if not (cited.get(i, set()) - {'부록B.md'})])
# 8자보다 긴 식별자(예: r030ffaeb)
for f in sorted(glob.glob(os.path.join(base, '장v2', '장*.md')) + glob.glob(os.path.join(base, '장v2', '부록*.md'))):
    if os.path.basename(f).startswith('전_'): continue
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(?<![0-9a-zA-Z_`/])r[0-9a-f]{8,31}(?![0-9a-f…])', txt):
        print('LONG ID', os.path.basename(f), m.group(0), txt[max(0, m.start()-40):m.end()+20].replace('\n', ' '))
