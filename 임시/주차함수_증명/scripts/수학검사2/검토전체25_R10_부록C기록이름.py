# 부록 C 이름 표의 「기록 [r…]의 X」에서 X가 그 기록(record.json의 주장 id, 폴더 안 md 문서)에 실제로 있는지 찾는다. 자리 찾기용.
import re, io, sys, os, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/'
rec = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
folders = {d[:8]: d for d in os.listdir(rec)}
cache = {}
def load(rid):
    if rid in cache: return cache[rid]
    p = rec + folders[rid]
    j = json.load(open(p + '/record.json', encoding='utf-8'))
    ids = set()
    for key in ('claims', 'nodes', 'relations', 'solutions', 'glossary'):
        for c in j.get(key, []) or []:
            if isinstance(c, dict) and 'id' in c: ids.add(c['id'])
    md = ''
    for root, ds, fs in os.walk(p):
        if os.sep + 'review' in root: continue
        for f in fs:
            if f.endswith('.md') or f.endswith('.txt') or f.endswith('.tex'):
                try: md += open(os.path.join(root, f), encoding='utf-8').read() + '\n'
                except Exception: pass
    cache[rid] = (ids, md, json.dumps(j, ensure_ascii=False))
    return cache[rid]
txt = open(base + '장v2/부록C.md', encoding='utf-8').read().split('\n')
start = txt.index('### 기록이 결과에 붙인 이름과 이 글의 번호')
end = txt.index('### 기록의 글자와 이 글의 글자')
def norm(s):
    return re.sub(r'[\s\$*]', '', s)
for k in range(start, end):
    ln = txt[k]
    m = re.match(r'\| (.*) \| (정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \| (.*) \|$', ln)
    if not m: continue
    recname = m.group(1)
    # 「기록 [rX]의 …」 조각으로 나눔
    parts = re.split(r'(?=기록 \[r[0-9a-f]{7}\])', recname)
    for p in parts:
        mm = re.match(r'기록 \[(r[0-9a-f]{7})\](?:의)? ?(.*)', p.strip().rstrip(',').rstrip('와').rstrip('과').strip())
        if not mm: 
            if p.strip(): print(k+1, 'UNPARSED', p)
            continue
        rid, names = mm.groups()
        ids, md, js = load(rid)
        nmd = norm(md); njs = norm(js)
        for nm in re.split(r',\s*|와 |과 ', names):
            nm = nm.strip().rstrip(',')
            if not nm: continue
            if re.fullmatch(r'[a-z0-9][a-z0-9\-]+', nm):
                ok = nm in ids
                tag = 'claim-id'
            else:
                ok = norm(nm) in nmd or norm(nm) in njs
                tag = 'text'
            if not ok: print(k+1, m.group(3), rid, tag, 'NOT FOUND:', nm)
