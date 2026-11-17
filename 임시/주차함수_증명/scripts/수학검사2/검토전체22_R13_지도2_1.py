import re, sys, json, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.setrecursionlimit(10000)
W = r"C:/math/임시/주차함수_증명/"
allh = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
heads = [o for o in allh if not o['proof']]
H = {o['label']: o for o in heads}
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
decl = defaultdict(set); full = defaultdict(set)
for f in files:
    L = open(W+"장v2/"+f+".md", encoding='utf-8').read().split('\n')
    marks = sorted([(o['line'], o) for o in allh if o['file']==f], key=lambda t:t[0])
    for idx,(ln,o) in enumerate(marks):
        end = marks[idx+1][0]-1 if idx+1 < len(marks) else len(L)
        seg = '\n'.join(L[ln-1:end]); k = o['label']
        for x in LAB.findall(seg):
            if x != k: full[k].add(x)
        if not o['proof'] and o['status']:
            st = o['status'].split(';')[0]
            for x in LAB.findall(st):
                if x != k: decl[k].add(x)
allin = set().union(*full.values())
print('distinct input labels', len(allin), 'not live:', sorted(allin - set(H)))
def scc(g, nodes):
    idx = {}; low = {}; st = []; on = set(); out = []; c = [0]
    def dfs(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
        for w in g.get(v, ()):
            if w not in idx: dfs(w); low[v] = min(low[v], low[w])
            elif w in on: low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in nodes:
        if v not in idx: dfs(v)
    return out
order = [o['label'] for o in heads]
s1 = [c for c in scc(decl, order) if len(c) > 1]
print('declared-only SCC>1:', len(s1), s1[:3])
s2 = [c for c in scc(full, order) if len(c) > 1]
print('full SCC>1:', len(s2), sorted(len(c) for c in s2))
# compare with document's list
T = open(W+"의존지도_v2.md", encoding='utf-8').read().split('\n')
line = [l for l in T if l.startswith('본문 인용 그래프의 상호 인용 묶음')][0]
groups = [set(LAB.findall(g)) for g in re.findall(r'\{(`\{\{.*?\}\}`)\}', line)]
print('doc groups', len(groups), sorted(len(g) for g in groups))
mine = [set(c) for c in s2]
print('match', all(g in mine for g in groups) and all(m in groups for m in mine))
for m in mine:
    if m not in groups: print('mine-only', sorted(m)[:6], len(m))
for g in groups:
    if g not in mine: print('doc-only', sorted(g)[:6], len(g))
