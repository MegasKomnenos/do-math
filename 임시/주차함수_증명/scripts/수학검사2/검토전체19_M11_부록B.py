# -*- coding: utf-8 -*-
"""부록 B: 식별자·폴더·제목이 기록 디렉토리와 맞는지, 본문·부록이 인용한 식별자 집합과 맞는지."""
import re, os, sys, io, glob, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
REC = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'

B = open(os.path.join(ROOT, '장v2', '부록B.md'), encoding='utf-8').read().split('\n')
rows = []
for ln in B:
    if ln.startswith('| r'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        rows.append(c)
print('부록 B 행 수', len(rows))
folders = sorted(os.listdir(REC))
print('기록 폴더 수', len(folders))
ids_B = [r[0] for r in rows]
print('중복 식별자', [i for i in ids_B if ids_B.count(i) > 1])
for r in rows:
    rid, when, title, folder = r[0], r[1], r[2], r[3].strip('`')
    p = os.path.join(REC, folder)
    probs = []
    if not os.path.isdir(p):
        probs.append('폴더 없음')
    else:
        if not folder.startswith(rid):
            probs.append('식별자≠폴더 앞 8글자')
        for sub in ('exposition.md', 'record.json', 'review'):
            if not os.path.exists(os.path.join(p, sub)):
                probs.append(sub + ' 없음')
        # 제목
        t = None
        rj = os.path.join(p, 'record.json')
        if os.path.exists(rj):
            try:
                d = json.load(open(rj, encoding='utf-8'))
                t = d.get('title') or d.get('제목')
                created = d.get('created') or d.get('created_at') or d.get('time') or d.get('timestamp')
            except Exception as e:
                probs.append('record.json 읽기 실패 ' + str(e)[:40]); created = None
        if t is None:
            ex = os.path.join(p, 'exposition.md')
            if os.path.exists(ex):
                for l in open(ex, encoding='utf-8'):
                    if l.startswith('#'):
                        t = l.lstrip('#').strip(); break
        if t is not None and t.replace(' ', '') != title.replace(' ', ''):
            probs.append('제목 다름: 기록=' + str(t)[:150])
        if created and when.replace(' ', '') not in str(created).replace(' ', '').replace('T', ' ').replace('-', '-'):
            probs.append('시각? 기록=' + str(created)[:40])
    print(rid, '|', '; '.join(probs) or 'OK')

# 폴더 가운데 부록 B에 없는 것
folder_ids = [f[:8] for f in folders]
print('부록 B에 없는 기록 폴더:', [f for f in folder_ids if f not in ids_B])
# 본문·부록에서 인용된 식별자
cited = {}
for f in glob.glob(os.path.join(ROOT, '장v2', '*.md')):
    txt = open(f, encoding='utf-8').read()
    for m in re.findall(r'\[(r[0-9a-f]{7})\]', txt):
        cited.setdefault(m, set()).add(os.path.basename(f))
    for m in re.findall(r'\[[^\]]*;\s*((?:r[0-9a-f]{7}(?:,\s*)?)+)\]', txt):
        for x in re.findall(r'r[0-9a-f]{7}', m):
            cited.setdefault(x, set()).add(os.path.basename(f) + '(머리)')
print('인용된 식별자 수', len(cited))
print('인용되었으나 부록 B에 없음:', {k: sorted(v) for k, v in cited.items() if k not in ids_B})
print('부록 B에 있으나 인용 안 됨:', [i for i in ids_B if i not in cited])
# 폴더 이름에 없는 식별자
print('기록 폴더가 없는 인용 식별자:', [k for k in cited if k not in folder_ids])
