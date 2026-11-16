# -*- coding: utf-8 -*-
"""H11: 장v2 전체가 대괄호/표지로 인용한 기록 식별자 집합과 부록 B의 집합을 맞추고,
부록 B의 폴더가 실제로 있는지, 제목·시각이 기록과 맞는지 본다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
recdir = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
ids_text = {}
for f in sorted(glob.glob(os.path.join(root, '*.md'))):
    b = os.path.basename(f)
    if b == '부록B.md':
        continue
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'\b(r[0-9a-f]{7})\b', line):
            ids_text.setdefault(m.group(1), []).append(f'{b}:{ln}')
B = open(os.path.join(root, '부록B.md'), encoding='utf-8').read().splitlines()
rows = []
for line in B:
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    m = None
    if len(cells) == 4 and re.fullmatch(r'r[0-9a-f]{7}', cells[0]):
        class M:
            def __init__(s, c): s.c = c
            def groups(s): return (s.c[0], s.c[1], s.c[2], s.c[3].strip('`'))
        m = M(cells)
    if m:
        rows.append(m.groups())
idsB = {r[0] for r in rows}
print('B rows:', len(rows), 'ids in text:', len(ids_text))
print('in text not in B:', sorted(set(ids_text) - idsB))
for i in sorted(set(ids_text) - idsB):
    print('   ', i, ids_text[i][:5])
print('in B not in text:', sorted(idsB - set(ids_text)))
# folder existence & title/time
folders = os.listdir(recdir)
prev = None
for rid, when, title, folder in rows:
    ok = folder in folders
    if not ok:
        print('NO FOLDER', rid, folder)
        continue
    if not folder.startswith(rid):
        print('ID/FOLDER MISMATCH', rid, folder)
    # title from exposition.md first heading or record.json
    rec_title = None; rec_time = None
    rj = os.path.join(recdir, folder, 'record.json')
    if os.path.exists(rj):
        try:
            d = json.load(open(rj, encoding='utf-8'))
            rec_title = d.get('title') or d.get('name')
            rec_time = d.get('created_at') or d.get('timestamp') or d.get('time') or d.get('created')
        except Exception as e:
            print('json err', rid, e)
    ex = os.path.join(recdir, folder, 'exposition.md')
    ex_title = None
    if os.path.exists(ex):
        for line in open(ex, encoding='utf-8'):
            if line.startswith('# '):
                ex_title = line[2:].strip(); break
    def norm(s):
        return re.sub(r'[\s\*\$\{}]', '', s or '')
    t_ok = norm(title) == norm(rec_title) or norm(title) == norm(ex_title)
    if not t_ok:
        print('TITLE?', rid, '\n   B  :', title, '\n   rec:', rec_title, '\n   exp:', ex_title)
    if rec_time:
        mm = re.search(r'(\d\d)-(\d\d)[T ](\d\d):(\d\d)', str(rec_time))
        if mm:
            t = f'{mm.group(1)}-{mm.group(2)} {mm.group(3)}:{mm.group(4)}'
            if t != when.strip():
                print('TIME?', rid, 'B:', when.strip(), 'rec:', rec_time)
            if prev and t < prev:
                print('ORDER?', rid, t, '<', prev)
            prev = t
    else:
        print('no time', rid, (list(d.keys()) if os.path.exists(rj) else 'no record.json'))
    # review dir
    if not os.path.isdir(os.path.join(recdir, folder, 'review')):
        print('NO review/', rid)
print('folders total:', len(folders))
