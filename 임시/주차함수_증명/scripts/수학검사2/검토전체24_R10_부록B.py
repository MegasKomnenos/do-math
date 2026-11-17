# 부록 B의 행(식별자·시각·제목·폴더)을 기록 폴더의 실제 이름·생성 시각·record.json의 title과 맞대고,
# 장 파일·부록 A·C·D가 인용한 식별자 전부가 표에 있는지, 표의 식별자가 어디선가 인용되는지를 센다.
import re, io, sys, os, json, glob, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/장v2/'
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
B = open(root+'부록B.md', encoding='utf-8').read().split('\n')
rows = []
for i, l in enumerate(B):
    m = re.match(r'^\| (r[0-9a-f]{7}) \| (\d\d-\d\d \d\d:\d\d) \| (.*) \| `([0-9a-z]+)` \|$', l)
    if m: rows.append((i+1,)+m.groups())
    elif l.startswith('| r'): print('!! 못 읽은 행', i+1, l[:80])
print('행 수', len(rows))
prev = None
for ln, rid, tm, title, folder in rows:
    p = R + folder
    if not folder.startswith(rid): print(f'[{ln}] 식별자≠폴더 앞 8자: {rid} {folder}')
    if len(folder) != 33: print(f'[{ln}] 폴더 이름 길이 {len(folder)}: {folder}')
    if not os.path.isdir(p): print(f'[{ln}] 폴더 없음: {folder}'); continue
    st = os.stat(p)
    ct = datetime.datetime.fromtimestamp(st.st_ctime)   # Windows: 생성 시각
    got = ct.strftime('%m-%d %H:%M')
    if got != tm: print(f'[{ln}] 시각 다름: 표 {tm} / 폴더 {ct}')
    d = json.load(open(p+'/record.json', encoding='utf-8'))
    if d['title'].strip() != title.strip():
        print(f'[{ln}] 제목 다름 {rid}:\n    표  : {title}\n    기록: {d["title"]}')
    for need in ['exposition.md', 'review']:
        if not os.path.exists(p+'/'+need): print(f'[{ln}] {rid}: {need} 없음')
    if prev and tm < prev: print(f'[{ln}] 시각 순서 어긋남: {prev} > {tm}')
    prev = tm
ids = {r[1] for r in rows}
if len(ids) != len(rows): print('!! 중복 식별자')
# 인용된 식별자
cited = {}
files = sorted(glob.glob(root+'장*.md')) + sorted(glob.glob(root+'부록*.md'))
for f in files:
    name = os.path.basename(f)
    if name == '부록B.md': continue
    for i, l in enumerate(open(f, encoding='utf-8').read().split('\n')):
        for m in re.finditer(r'(?<![0-9a-zA-Z_/])r[0-9a-f]{7}(?![0-9a-f])', l):
            cited.setdefault(m.group(0), []).append((name, i+1))
print('인용된 서로 다른 식별자 수', len(cited))
for c in sorted(cited):
    if c not in ids: print('표에 없는 인용 식별자:', c, cited[c][:4])
for r in sorted(ids):
    if r not in cited: print('어디서도 인용되지 않는 표의 식별자:', r)
# 8자를 넘는 식별자 꼴(r030ffaeb 등)
for f in files:
    name = os.path.basename(f)
    for i, l in enumerate(open(f, encoding='utf-8').read().split('\n')):
        for m in re.finditer(r'(?<![0-9a-zA-Z_/`])r[0-9a-f]{8,31}(?![0-9a-f…])', l):
            print('8자 넘는 식별자 꼴:', name, i+1, m.group(0))
# 인용 위치별 요약: 본문에만/부록에만
only_app = [c for c in cited if all(n.startswith('부록') for n, _ in cited[c])]
print('부록(A·C·D)에서만 인용되는 식별자 수', len(only_app))
