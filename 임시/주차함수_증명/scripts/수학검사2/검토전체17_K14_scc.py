# -*- coding: utf-8 -*-
"""K14: 의존지도 2.1절의 수치(인용 라벨 수·선언 그래프 비순환·본문 인용 그래프의 강결합 성분)를 장 파일에서 다시 센다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.setrecursionlimit(10000)
ROOT = r'C:\math\임시\주차함수_증명'
CH = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([^}]+)\}\}((?!의 증명).*?)\*\*')
PROOF = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([^}]+)\}\}의 증명')
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
segs = {}; heads = {}; order = []
for c in CH:
    cur = None
    for line in open(os.path.join(ROOT, '장v2', c + '.md'), encoding='utf-8').read().split('\n'):
        m = HEAD.match(line); mp = PROOF.match(line)
        if m:
            lab = '{{%s:%s}}' % (m.group(2), m.group(3)); cur = lab; heads[lab] = line; segs.setdefault(lab, []).append(('H', line)); order.append(lab)
        elif mp:
            lab = '{{%s:%s}}' % (mp.group(2), mp.group(3)); cur = lab; segs.setdefault(lab, []).append(('P', line))
        elif cur:
            segs[cur].append(('B', line))
decl = {}; full = {}
cited = set()
for lab in order:
    h = set('{{%s}}' % x for x in LAB.findall(heads[lab])) - {lab}
    b = set()
    for k, line in segs[lab]:
        if k != 'H':
            b |= set('{{%s}}' % x for x in LAB.findall(line))
    b -= {lab}
    decl[lab] = h; full[lab] = h | b
    cited |= h | b
print('distinct cited labels', len(cited), 'all in heads:', cited <= set(order))
# 선언 그래프 비순환
def has_cycle(g):
    color = {}
    def dfs(u):
        color[u] = 1
        for v in g.get(u, ()):
            if v not in g: continue
            if color.get(v) == 1: return True
            if color.get(v) is None and dfs(v): return True
        color[u] = 2; return False
    return any(color.get(u) is None and dfs(u) for u in g)
print('declared graph has cycle:', has_cycle(decl))
# Tarjan SCC on full
index = {}; low = {}; st = []; on = set(); sccs = []; idx = [0]
def sc(v):
    index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); on.add(v)
    for w in full.get(v, ()):
        if w not in full: continue
        if w not in index:
            sc(w); low[v] = min(low[v], low[w])
        elif w in on:
            low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        comp = []
        while True:
            w = st.pop(); on.discard(w); comp.append(w)
            if w == v: break
        sccs.append(comp)
for v in order:
    if v not in index: sc(v)
big = [sorted(c) for c in sccs if len(c) >= 2]
print('SCCs size>=2:', len(big))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_scc_out.txt'), 'w', encoding='utf-8') as f:
    for c in sorted(big, key=len):
        f.write('%d\t%s\n' % (len(c), ', '.join(c)))
