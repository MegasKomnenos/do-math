# -*- coding: utf-8 -*-
# 부록 C 낱말 표의 「기록의 용어」 칸에서 낱말 후보를 뽑아 기록(.md/.json/.txt)에 나오는 기록 수를 센다(후보 추출은 거칠다 — 0건인 것만 원문으로 다시 본다).
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]; R = sys.argv[2]
folders = re.findall(r'`(r[0-9a-f]{32})`', open(os.path.join(base, '장v2', '부록B.md'), encoding='utf-8').read())
blob = {}
for f in folders:
    acc = []
    for dp, dn, fns in os.walk(os.path.join(R, f)):
        for fn in fns:
            if fn.endswith(('.md', '.json', '.txt')):
                try: acc.append(open(os.path.join(dp, fn), encoding='utf-8').read())
                except Exception: pass
    blob[f[:8]] = '\n'.join(acc)
txt = open(os.path.join(base, '장v2', '부록C.md'), encoding='utf-8').read()
seg = txt.split('### 낱말: 이 글의 용어와 기록의 용어')[1].split('### 기록이 결과에 붙인 이름')[0]
for line in seg.split('\n'):
    if not line.startswith('| ') or line.startswith('| 이 글의') or line.startswith('|---'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) != 3: print('CELLS', len(cells), line[:60]); continue
    mine, rec, sec = cells
    # 후보: 「…」 안, 그리고 쉼표·쌍반점으로 나눈 조각에서 괄호 설명을 뗀 것
    cands = re.findall(r'「([^」]+)」', rec)
    for piece in re.split(r'[,;]', re.sub(r'\([^)]*\)', '', rec)):
        p = piece.strip()
        if p and '「' not in p and '은 ' not in p and '는 ' not in p and not p.startswith('—'): cands.append(p)
    res = []
    for c in dict.fromkeys(cands):
        n = sum(1 for b in blob.values() if c in b)
        res.append('%s=%d' % (c, n))
    print('%s  ||  %s' % (mine, '  '.join(res)))
