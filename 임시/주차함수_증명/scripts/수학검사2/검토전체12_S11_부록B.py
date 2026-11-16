# S11: 부록 B의 식별자 목록을 본문·부록이 인용한 식별자, 기록 폴더 이름, 시각 순서와 견준다.
import re, io, sys, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = open('장v2/부록B.md', encoding='utf-8').read()
rows = [l for l in B.split('\n') if l.startswith('| r')]
ids_B = []; folders = {}; times = []
for l in rows:
    c = [x.strip() for x in l.strip().strip('|').split(' | ')]
    ids_B.append(c[0]); folders[c[0]] = c[3].strip('`'); times.append(c[1])
print('부록 B 행 수', len(rows), '중복:', [i for i in set(ids_B) if ids_B.count(i) > 1])
print('시각 순서 단조:', all(times[i] <= times[i+1] for i in range(len(times)-1)), [ (times[i], times[i+1]) for i in range(len(times)-1) if times[i] > times[i+1]])
print('폴더 이름 앞 8글자 일치:', all(folders[i].startswith(i) for i in ids_B), [i for i in ids_B if not folders[i].startswith(i)])
recdir = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records'
existing = set(os.listdir(recdir))
print('폴더 존재하지 않음:', [folders[i] for i in ids_B if folders[i] not in existing])
cited = {}
for f in sorted(glob.glob('장v2/*.md')) + ['장부_v2.md']:
    if f.endswith('부록B.md'): continue
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'r[0-9a-f]{7}(?![0-9a-f])', txt):
        cited.setdefault(m.group(0), set()).add(os.path.basename(f))
print('본문·부록에 인용되었으나 부록 B에 없음:', {k: sorted(v) for k, v in cited.items() if k not in ids_B})
print('부록 B에 있으나 어디에도 인용 없음:', [i for i in ids_B if i not in cited])
print('부록 B에 있고 장 파일(장1–장10)에는 없고 부록 A/C/D에만 있음:', [i for i in ids_B if i in cited and not any(v.startswith('장') for v in cited[i])])
# 기록 제목 대조: record.json 또는 exposition.md 첫 줄
import json
print('\n제목 대조(기록의 exposition.md 첫 제목 줄 vs 부록 B 내용):')
for l in rows:
    c = [x.strip() for x in l.strip().strip('|').split(' | ')]
    d = os.path.join(recdir, c[3].strip('`'))
    title = None
    for cand in ['exposition.md', 'record.json']:
        p = os.path.join(d, cand)
        if os.path.exists(p):
            if cand.endswith('.json'):
                try:
                    j = json.load(open(p, encoding='utf-8')); title = j.get('title') or j.get('name')
                except Exception as e: title = f'(json 오류 {e})'
            else:
                for line in open(p, encoding='utf-8'):
                    if line.startswith('#'): title = line.strip('# \n'); break
            if title: break
    same = (title or '').replace(' ', '') == c[2].replace(' ', '')
    print(('  같음 ' if same else '  다름 ') + c[0], '| B:', c[2][:70], '| 기록:', (title or '')[:90])
