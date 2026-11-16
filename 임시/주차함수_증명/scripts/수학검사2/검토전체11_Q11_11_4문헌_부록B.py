# -*- coding: utf-8 -*-
"""11.4 문헌 표의 저자명이 본문 어디에 나오는지 자리를 모으고, 부록 B의 식별자·폴더를 기록 폴더와 맞춘다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명\장v2'
REC = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'

files = sorted(glob.glob(ROOT + r'\장*.md')) + sorted(glob.glob(ROOT + r'\부록D_*.md'))
# 절·진술 위치 추적
def locate(f):
    out = []
    sec = None; cur = None
    for ln in open(f, encoding='utf-8'):
        ms = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)', ln)
        if ms: sec = ms.group(1); cur = None
        mh = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}', ln)
        if mh: cur = mh.group(1) + ' ' + mh.group(2)
        md = re.match(r'### D\.\{\{D:([^}]+)\}\}', ln)
        if md: cur = 'D.' + md.group(1)
        out.append((sec, cur, ln))
    return out
loc = {f: locate(f) for f in files}

authors = ['Konheim', 'Foata', 'Pollak', 'Celano', 'Aguilar', 'Stanley', 'Knuth', 'Flajolet', 'Tanner', 'Robbins', 'Petersson',
           'Janson', 'Ibragimov', 'Ahlfors', 'Graham', 'Fortuin', 'FKG', 'Jensen', 'Wallis', 'Corless', 'Lambert', 'Grimmett', 'Harris',
           'Comtet', 'Faà', 'Apostol', 'Titchmarsh', 'Euler', 'Cauchy', 'Cayley', 'Lagrange', 'Borel–Tanner', '표준', '문헌 인용', 'Stirling', 'Maclaurin', '편각']
for a in authors:
    print('\n### ' + a)
    for f in files:
        for sec, cur, ln in loc[f]:
            if a in ln:
                idx = ln.find(a)
                print(f'  {f.split(chr(92))[-1]} §{sec} [{cur}] …{ln[max(0,idx-60):idx+80].strip()}…')

# 부록 B
print('\n\n### 부록 B 대조')
B = open(ROOT + r'\부록B.md', encoding='utf-8').read()
brows = re.findall(r'^\| (r[0-9a-f]{7}) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|', B, re.M)
print('B rows:', len(brows))
ids_B = {r[0]: r for r in brows}
folders = set(os.listdir(REC)) if os.path.isdir(REC) else set()
print('record folders:', len(folders))
for rid, t, title, folder in brows:
    flags = []
    if folder not in folders: flags.append('FOLDER MISSING')
    if not folder.startswith(rid): flags.append('ID/FOLDER MISMATCH')
    # record.json에서 제목·시각 확인
    rj = os.path.join(REC, folder, 'record.json')
    if os.path.exists(rj):
        try:
            d = json.load(open(rj, encoding='utf-8'))
            rt = d.get('title') or d.get('name') or ''
            ts = d.get('created_at') or d.get('timestamp') or d.get('created') or ''
            if rt and rt.strip() != title.strip(): flags.append('TITLE DIFF: ' + rt[:120])
            flags.append('ts=' + str(ts)[:19] + ' B=' + t)
        except Exception as e:
            flags.append('json err ' + str(e)[:40])
    else:
        flags.append('no record.json')
    print(rid, '|', ' ; '.join(flags))
# 본문에 인용된 식별자 전부
cited = set()
for f in files + [ROOT + r'\부록A.md', ROOT + r'\부록C.md']:
    cited |= set(re.findall(r'r[0-9a-f]{7}', open(f, encoding='utf-8').read()))
cited = {c for c in cited if re.fullmatch(r'r[0-9a-f]{7}', c)}
print('\ncited in text but not in B:', sorted(cited - set(ids_B)))
print('in B but not cited anywhere:', sorted(set(ids_B) - cited))
# 폴더 접두 8글자 겹침 검사
pref = {}
for fo in folders:
    pref.setdefault(fo[:8], []).append(fo)
print('prefix collisions:', {k: v for k, v in pref.items() if len(v) > 1})
