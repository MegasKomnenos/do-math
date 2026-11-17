# -*- coding: utf-8 -*-
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
sys.setrecursionlimit(10000)
base = r'C:/math/임시/주차함수_증명'
LAB = re.compile(r'\{\{([0-9]+[A-Za-z]?):([^}]+)\}\}')
L = io.open(os.path.join(base, '의존지도_v2.md'), encoding='utf-8').read().split('\n')
rows = {}
for i, line in enumerate(L[:283], 1):
    if line.startswith('| `{{'):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        rows[c[0].strip('`{}')] = c
allin = set()
G_all, G_dep = {}, {}
for k, c in rows.items():
    labs = [a + ':' + b for a, b in LAB.findall(c[5])]
    allin.update(labs)
    G_all[k] = set(labs)
    # 선언 의존: 지위 칸의 「…에 의존」 앞 라벨
    st = c[4]
    dep = set()
    for seg in re.findall(r'([^,;]*?)에 의존', st):
        dep.update(a + ':' + b for a, b in LAB.findall(seg))
    G_dep[k] = dep
print('distinct input labels', len(allin), 'all in rows', allin <= set(rows))
def scc(G):
    idx = {}; low = {}; st = []; on = set(); out = []; n = [0]
    def go(v):
        idx[v] = low[v] = n[0]; n[0] += 1; st.append(v); on.add(v)
        for w in G.get(v, ()):
            if w not in G: continue
            if w not in idx:
                go(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in G:
        if v not in idx: go(v)
    return out
big = [c for c in scc(G_dep) if len(c) > 1]
print('declared-dep SCC>1:', big, 'self loops', [k for k in G_dep if k in G_dep[k]])
big2 = [c for c in scc(G_all) if len(c) > 1]
print('all-citation SCC>1 count', len(big2), 'sizes', sorted(len(c) for c in big2))
# compare with the listed groups (2.1절 둘째 문단)
txt = [l for l in L if l.startswith('본문 인용 그래프의 상호 인용 묶음')][0]
groups = [set(a + ':' + b for a, b in LAB.findall(g)) for g in re.findall(r'\{(`.*?`)\}(?:;|$)', txt)]
print('listed groups', len(groups), sorted(len(g) for g in groups))
S1 = sorted(sorted(c) for c in big2); S2 = sorted(sorted(g) for g in groups)
print('same', S1 == S2)
# 선언 의존 라벨이 지위 칸과 머리에서 같은지: 지위 칸의 라벨은 입력 칸 머리 부분에 다 있는가
for k, c in rows.items():
    inp = c[5].split('본문 인용:')[0]
    hl = set(a + ':' + b for a, b in LAB.findall(inp))
    sl = set(a + ':' + b for a, b in LAB.findall(c[4]))
    if not sl <= hl: print('status labs not in head inputs', k, sl - hl)
