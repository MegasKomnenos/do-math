# 부록 B의 표(식별자·시각·제목·폴더)를 기록 폴더의 record.json과 폴더 생성 시각에 맞대고, 글 전체가 인용한 식별자와 표의 식별자를 견준다.
import re, io, sys, os, json, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
rec = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
rows = []
for ln in open(base + '부록B.md', encoding='utf-8').read().split('\n'):
    m = re.match(r'\| (r[0-9a-f]{7}) \| (\d\d-\d\d \d\d:\d\d) \| (.*) \| `(r[0-9a-f]{32})` \|$', ln)
    if m: rows.append(m.groups())
print('rows', len(rows))
prev = ''
for rid, t, title, folder in rows:
    msgs = []
    if not folder.startswith(rid): msgs.append('id/folder prefix mismatch')
    p = rec + folder
    if not os.path.isdir(p): msgs.append('folder missing'); print(rid, msgs); continue
    j = json.load(open(p + '/record.json', encoding='utf-8'))
    if j.get('title') != title: msgs.append('TITLE DIFF\n   B: ' + title + '\n   R: ' + str(j.get('title')))
    st = os.stat(p)
    ct = time.strftime('%m-%d %H:%M', time.localtime(st.st_ctime))
    if ct != t: msgs.append(f'time B={t} ctime={ct}')
    if t < prev: msgs.append('ORDER')
    prev = t
    sub = sorted(os.listdir(p))
    if 'review' not in sub: msgs.append('no review/')
    if 'exposition.md' not in sub: msgs.append('no exposition.md')
    ev = p + '/evidence'
    evs = sorted(os.listdir(ev)) if os.path.isdir(ev) else None
    print(rid, t, '| ev:', evs if evs is None else evs[:8], '|', '; '.join(msgs) if msgs else 'ok')
# 인용된 식별자
ids_tab = set(r[0] for r in rows)
cited = {}
for f in sorted(glob.glob(base + '*.md')):
    fn = os.path.basename(f)
    if fn == '부록B.md': continue
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'\br[0-9a-f]{7}\b', txt):
        cited.setdefault(m.group(0), set()).add(fn)
print('cited ids', len(cited))
print('cited but not in B:', {k: sorted(v) for k, v in cited.items() if k not in ids_tab})
print('in B but not cited:', sorted(ids_tab - set(cited)))
# 8글자 넘게 적힌 식별자 꼴
for f in sorted(glob.glob(base + '*.md')):
    fn = os.path.basename(f)
    if fn == '부록B.md': continue
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'r[0-9a-f]{8,}', txt):
        print('long id', fn, m.group(0))
