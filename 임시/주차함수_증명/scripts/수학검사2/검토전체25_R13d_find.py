# -*- coding: utf-8 -*-
# 표준입력의 줄마다 고정 문자열을 장 파일에서 찾아 (파일:행:절) 목록과 수를 낸다. 자리를 찾는 용도.
# 사용: python -I 이파일 [max] [ctx]  < 패턴들 ; 줄 머리가 '@파일접두 '이면 그 파일만.
import re, io, glob, os, sys
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mx = int(sys.argv[1]) if len(sys.argv) > 1 else 6
ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
files = {}
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록A','부록B','부록C','부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
for n in order:
    ls = io.open(os.path.join(base, '장v2', n + '.md'), encoding='utf-8').read().split('\n')
    sec = []; cur = ''
    for l in ls:
        m = re.match(r'^#+\s+(D\.\{\{D:[^}]+\}\}|[0-9]+(?:\.[0-9]+)*)', l)
        if m: cur = m.group(1)
        sec.append(cur)
    files[n] = (ls, sec)
pats = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read().split('\n')
for p in pats:
    if not p.strip(): continue
    only = None
    if p.startswith('@'):
        only, p = p[1:].split(' ', 1)
    hits = []
    for n in order:
        if only and not n.startswith(only): continue
        if not only and n in ('부록A', '부록B', '부록C'): continue
        ls, sec = files[n]
        for j, l in enumerate(ls):
            c = l.count(p)
            if c:
                hits.append((n, j + 1, sec[j], c, l))
    tot = sum(h[3] for h in hits)
    out.write('=== %s  [%d회/%d줄]\n' % (p, tot, len(hits)))
    for h in hits[:mx]:
        if ctx:
            i = h[4].find(p)
            out.write('   %s:%d(%s) …%s…\n' % (h[0], h[1], h[2], h[4][max(0, i - ctx):i + len(p) + ctx]))
        else:
            out.write('   %s:%d(%s)\n' % (h[0], h[1], h[2]))
    if len(hits) > mx and not ctx:
        out.write('   + ' + ' '.join('%s:%d' % (h[0], h[1]) for h in hits[mx:mx + 30]) + '\n')
