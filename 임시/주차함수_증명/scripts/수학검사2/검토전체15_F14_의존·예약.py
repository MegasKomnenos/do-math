# -*- coding: utf-8 -*-
"""F14: (1) 의존지도 2.1의 수치 주장(입력 라벨 383, 머리 선언 그래프 비순환, 상호 인용 묶음 16) 재계산;
(2) 6절 예약 글자(바탕 글자만의 이탤릭 P·Q·W·X, 라틴 엘 l, 점근 기호 O·o)의 수식 구간 안 출현;
(3) 장부 4절 범위의 기록 식별자 셋."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
def rd(p):
    return open(p, encoding='utf-8').read()
dm = rd(os.path.join(ROOT, '의존지도_v2.md'))
s1 = dm[dm.index('## 1. 진술별 입력 표'):dm.index('### 1.1 뺌·대체된 라벨')]
rows = {}
for line in s1.split('\n'):
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) < 10 or not cells[0].startswith('`{{'):
        continue
    lab = re.match(r'`\{\{(\d+:[A-Za-z0-9-]+)\}\}`', cells[0]).group(1)
    status, inputs = cells[4], cells[5]
    rows[lab] = (status, inputs)
labs_all = set()
head_edges = {}
all_edges = {}
for lab, (status, inputs) in rows.items():
    ins = set(re.findall(r'\{\{(\d+:[A-Za-z0-9-]+)\}\}', inputs))
    labs_all |= ins
    first = inputs.split('본문 인용:')[0]
    head_edges[lab] = set(re.findall(r'\{\{(\d+:[A-Za-z0-9-]+)\}\}', first)) | set(re.findall(r'\{\{(\d+:[A-Za-z0-9-]+)\}\}', status))
    all_edges[lab] = ins
print('행 수', len(rows), '입력 열 라벨(중복 제외)', len(labs_all), '머리 없는 라벨', sorted(labs_all - set(rows)))
# acyclic check on head_edges
def has_cycle(g):
    color = {}
    def dfs(u, path):
        color[u] = 1
        for v in g.get(u, ()):
            if v not in g:
                continue
            if color.get(v) == 1:
                return path + [u, v]
            if color.get(v) is None:
                r = dfs(v, path + [u])
                if r:
                    return r
        color[u] = 2
        return None
    for u in g:
        if color.get(u) is None:
            r = dfs(u, [])
            if r:
                return r
    return None
print('머리 선언 그래프 순환:', has_cycle(head_edges))
# SCCs of all_edges (Tarjan)
sys.setrecursionlimit(10000)
index = {}; low = {}; onstack = set(); stack = []; sccs = []; idx = [0]
def sc(v):
    index[v] = low[v] = idx[0]; idx[0] += 1; stack.append(v); onstack.add(v)
    for w in all_edges.get(v, ()):
        if w not in all_edges:
            continue
        if w not in index:
            sc(w); low[v] = min(low[v], low[w])
        elif w in onstack:
            low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        comp = []
        while True:
            w = stack.pop(); onstack.discard(w); comp.append(w)
            if w == v:
                break
        if len(comp) > 1:
            sccs.append(sorted(comp))
for v in all_edges:
    if v not in index:
        sc(v)
print('본문 인용 포함 그래프의 크기 2 이상 강결합 성분 수:', len(sccs))
for c in sccs:
    print('  ', len(c), c[:6], '…' if len(c) > 6 else '')

print('\n### (2) 6절 예약 글자의 수식 구간 안 출현')
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
CTRL = re.compile(r'\\(mathcal|mathfrak|mathsf|mathrm|mathbb|mathbf|mathscr|operatorname|tilde|hat|bar|dot|vec|widetilde|underline|overline|mathit|text)\s*\{?\s*$')
def hits(pat, s):
    out = []
    for m in re.finditer(pat, s):
        if CTRL.search(s[:m.start()]):
            continue
        out.append(m)
    return out
pats = {
 'bare P': r'(?<![A-Za-z\\_^{])P(?![A-Za-z_^(])',
 'bare Q': r'(?<![A-Za-z\\_^{])Q(?![A-Za-z_^(])',
 'bare W': r'(?<![A-Za-z\\_^{])W(?![A-Za-z_^(])',
 'bare X': r'(?<![A-Za-z\\_^{])X(?![A-Za-z_^(])',
 'latin l': r'(?<![A-Za-z\\_^{])l(?![A-Za-z])',
 'O(/o(': r'(?<![A-Za-z\\_^{])[Oo]\(',
}
for fn in CH:
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    for ln, line in enumerate(txt.split('\n'), 1):
        for m in re.finditer(r'\$\$(.+?)\$\$|\$(.+?)\$', line):
            s = m.group(1) or m.group(2)
            for name, pat in pats.items():
                hs = hits(pat, s)
                if hs:
                    print(f'  {name}: {fn}:{ln}: {s[:110]}')
print('\n### (3) 장부 4절 범위의 기록 식별자')
jb = rd(os.path.join(ROOT, '장부_v2.md'))
s4 = jb[jb.index('## 4. 이름 사전'):jb.index('## 5. 장별 배정')]
for r in ['ra88ba51', 'rb1d8cd5', 'r4daca3d']:
    print(' ', r, '4절 출현', s4.count(r), '| 1.2 출현', jb[jb.index('### 1.2'):jb.index('### 1.3')].count(r), '| 1.3 출현', jb[jb.index('### 1.3'):jb.index('## 2. 양 사전')].count(r))
