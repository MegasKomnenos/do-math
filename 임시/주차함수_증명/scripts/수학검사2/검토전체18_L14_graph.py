import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명'
rows = {}
with open(os.path.join(root, '의존지도_v2.md'), encoding='utf-8') as fh:
    for i, line in enumerate(fh, 1):
        if i > 409: break
        m = re.match(r'\| `\{\{([^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            rows[m.group(1)] = m.group(6)
alllabs = set()
decl = {}
full = {}
for lab, inp in rows.items():
    labs = re.findall(r'\{\{([^}]+)\}\}', inp)
    alllabs.update(labs)
    d = inp.split('본문 인용:')[0]
    decl[lab] = set(re.findall(r'\{\{([^}]+)\}\}', d))
    full[lab] = set(labs)
print('rows', len(rows), 'distinct labels in inputs', len(alllabs), 'all in rows:', alllabs <= set(rows))
# cycle check on declared graph
import sys
sys.setrecursionlimit(10000)
def has_cycle(g):
    color = {}
    def dfs(u):
        color[u] = 1
        for v in g.get(u, ()):
            if color.get(v) == 1: return True
            if color.get(v) is None and dfs(v): return True
        color[u] = 2
        return False
    return any(color.get(u) is None and dfs(u) for u in g)
print('declared graph cyclic:', has_cycle(decl))
# SCCs on full graph (Tarjan)
index = {}; low = {}; onst = set(); st = []; sccs = []; idx = [0]
def sc(v):
    index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); onst.add(v)
    for w in full.get(v, ()):
        if w not in full: continue
        if w not in index:
            sc(w); low[v] = min(low[v], low[w])
        elif w in onst:
            low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        comp = []
        while True:
            w = st.pop(); onst.discard(w); comp.append(w)
            if w == v: break
        if len(comp) > 1: sccs.append(comp)
for v in full:
    if v not in index: sc(v)
print('SCCs size>=2:', len(sccs), sorted(len(c) for c in sccs))
