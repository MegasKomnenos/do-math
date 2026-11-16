# -*- coding: utf-8 -*-
"""F11: 부록 B의 식별자·제목·폴더를 기록 폴더와 대조하고, 글 전체가 인용한 식별자 집합과 비교한다."""
import re, os, glob, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
REC = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
rows = []
for l in open(ROOT + r'\장v2\부록B.md', encoding='utf-8'):
    m = re.match(r'\| (r[0-9a-f]{7}) \| ([^|]+) \| (.*) \| `(r[0-9a-f]{32})` \|\s*$', l)
    if m: rows.append(m.groups())
print('부록 B 행 수:', len(rows))
folders = {d[:8]: d for d in os.listdir(REC)}
print('기록 폴더 수:', len(folders))
ids_B = []
for rid, tm, title, folder in rows:
    ids_B.append(rid)
    if rid not in folders: print('!! 폴더 없음', rid); continue
    if folders[rid] != folder: print('!! 폴더 이름 불일치', rid, folder, folders[rid])
    p = os.path.join(REC, folder)
    has = {x: os.path.exists(os.path.join(p, x)) for x in ['exposition.md', 'record.json', 'review', 'evidence']}
    # 제목·시각
    rj = os.path.join(p, 'record.json')
    rtitle = rtime = None
    if os.path.exists(rj):
        try:
            j = json.load(open(rj, encoding='utf-8'))
            rtitle = j.get('title'); rtime = j.get('created') or j.get('created_at') or j.get('time') or j.get('timestamp')
        except Exception as e: print('json err', rid, e)
    if rtitle is None:
        ex = os.path.join(p, 'exposition.md')
        if os.path.exists(ex):
            first = open(ex, encoding='utf-8').readline().strip()
            rtitle = first.lstrip('# ').strip()
    flag = ''
    if rtitle and rtitle.strip() != title.strip(): flag += ' [제목 다름]'
    missing = [k for k, v in has.items() if not v]
    if missing: flag += f' [없음: {missing}]'
    print(rid, tm, '|', (rtime or '?')[:16], flag)
    if flag and '[제목 다름]' in flag:
        print('   B :', title); print('   기록:', rtitle)
# 시각 순 확인
print('시각 순 정렬인가:', [r[1] for r in rows] == sorted([r[1] for r in rows]))
# 글 전체의 식별자
cited = {}
for f in glob.glob(ROOT + r'\장v2\*.md'):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'\br([0-9a-f]{7})\b', t):
        cited.setdefault('r' + m.group(1), set()).add(os.path.basename(f))
setB = set(ids_B)
print('부록 B에 없는데 인용된 식별자:', {k: sorted(v) for k, v in cited.items() if k not in setB})
print('부록 B에 있으나 어디에도(부록 B 밖) 인용되지 않은 식별자:', sorted(k for k in setB if k not in cited or cited[k] == {'부록B.md'}))
print('기록 폴더에 있으나 부록 B에 없는 기록 수:', len([k for k in folders if k not in setB]))
