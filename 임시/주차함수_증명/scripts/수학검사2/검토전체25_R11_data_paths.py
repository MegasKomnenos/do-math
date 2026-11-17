# R11: 부록 D(장2·3·4·5A) 「자료」 줄의 파일 이름이 자료 묶음(원고_자료/)과 기록 폴더에 실제로 있는지 대조
import os, re, io, glob
root = '원고_자료'
REC = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records'
bundle = {}
for dp, dn, fn in os.walk(root):
    for f in fn:
        bundle.setdefault(f, []).append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
recfiles = {}
def rec_index(rid):
    if rid in recfiles: return recfiles[rid]
    d = glob.glob(REC + '/' + rid + '*')
    s = {}
    if d:
        for dp, dn, fn in os.walk(d[0]):
            for f in fn: s.setdefault(f, []).append(os.path.relpath(os.path.join(dp, f), d[0]).replace(os.sep, '/'))
    recfiles[rid] = s
    return s
for fn in ['부록D_장2.md', '부록D_장3.md', '부록D_장4.md', '부록D_장5A.md']:
    txt = io.open('장v2/' + fn, encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\}.*?(?=^### |\Z)', txt, re.S | re.M):
        item = m.group(1); body = m.group(0)
        dl = re.search(r'^\*\*자료\.\*\*(.*)$', body, re.M).group(1)
        rid = None; miss_b = []; miss_r = []; n = 0
        for tok in re.findall(r'`([^`]+)`', dl):
            mm = re.match(r'records/(r[0-9a-f]{7})…/(.*)', tok)
            if mm: rid = mm.group(1); path = mm.group(2)
            elif tok.startswith('원고_자료/'): rid = 'SESSION'; path = tok[len('원고_자료/'):]
            else: path = tok
            base = path.rstrip('/').split('/')[-1]
            if '*' in base or '.' not in base: continue
            n += 1
            if rid == 'SESSION':
                if base not in bundle: miss_b.append(tok)
            else:
                cands = bundle.get(base, []) + [p for k, v in bundle.items() if k.endswith('__' + base) for p in v]
                if not any(c.startswith(rid + '/') for c in cands): miss_b.append((rid, tok))
                if base not in rec_index(rid): miss_r.append((rid, tok))
        print(item, 'files named:', n, '| not in bundle:', miss_b, '| not in record:', miss_r)
