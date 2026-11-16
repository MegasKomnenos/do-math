# -*- coding: utf-8 -*-
"""D2·D3: 행 문턱(10001/20001)과 열 문턱(2001, 3131/3132, 4000, 6600, 6666/6667/6668, 25001 등)의 출현 전수."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = sorted(glob.glob(os.path.join(ROOT, '장v2', '*.md')))
files.append(os.path.join(ROOT, '장부_v2.md'))
HEAD = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의)\s+(\{\{[^}]+\}\})')
toks = ['10001','10000','20001','20000','50001','50000','2001','3131','3132','3130','4000','6600','6666','6667','6668','25001','25000','501','840','841','2000','2k+103','2k+41','0.48k']
from collections import defaultdict, Counter
cnt = defaultdict(Counter)
hits = defaultdict(list)
for f in files:
    name = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().split('\n')
    cur = None
    for i, ln in enumerate(lines, 1):
        m = HEAD.match(ln)
        if m: cur = m.group(2)
        for t in toks:
            # 수 토큰은 앞뒤가 숫자가 아니어야 함(예: 10001이 100010의 일부가 아니게)
            pat = re.escape(t) if not t[0].isdigit() else r'(?<![\d.])' + re.escape(t) + r'(?![\d])'
            n = len(re.findall(pat, ln))
            if n:
                cnt[t][name] += n
                for mm in re.finditer(pat, ln):
                    s=max(0,mm.start()-50); e=min(len(ln),mm.end()+50)
                    hits[t].append((name,i,cur,ln[s:e]))
for t in toks:
    print('==', t, '총', sum(cnt[t].values()), dict(cnt[t]))
print()
for t in ['10001','20001','2001','3131','3132','4000','6600','6666','6667','6668']:
    print('#####', t)
    for h in hits[t]:
        print(f'{h[0]}:{h[1]} | {h[2]} | …{h[3]}…')
    print()
