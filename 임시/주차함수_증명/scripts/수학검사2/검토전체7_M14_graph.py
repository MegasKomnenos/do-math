# -*- coding: utf-8 -*-
"""M14: 의존지도 2.1절의 선언(머리 의존 그래프 비순환, 본문 인용 그래프의 강결합 성분 13개, 라벨 379개)을 장 파일에서 다시 센다."""
import re, pathlib, collections, sys
sys.setrecursionlimit(10000)
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
KINDS = "정의|정리|명제|보조정리|따름정리"
head_re = re.compile(r"^\*\*(" + KINDS + r")\s+\{\{([^}]+)\}\}\s*(\((.*?)\))?\s*(\[(.*?)\])?\.?\*\*")
proof_re = re.compile(r"^\*\*(?:" + KINDS + r")\s+\{\{([^}]+)\}\}\s*(?:\([^)]*\))?\s*(?:\((가|나|다|라|마|바|사|아)\)\s*)?의 증명")
ref_re = re.compile(r"\{\{([^}]+)\}\}")
heads = {}; headcite = {}; body = collections.defaultdict(set)
for f in order:
    cur = None
    for line in (CH/(f+".md")).read_text(encoding="utf-8").splitlines():
        mp = proof_re.match(line); mh = head_re.match(line)
        if mh and not mp:
            lab = mh.group(2); heads[lab] = 1; cur = lab
            headcite[lab] = set(ref_re.findall(line)) - {lab}
            continue
        if mp:
            cur = mp.group(1); body[cur] |= set(ref_re.findall(line)); continue
        if cur: body[cur] |= set(ref_re.findall(line))
for l in body: body[l] = {x for x in body[l] if x in heads and x != l}
allrefs = set()
for l in heads: allrefs |= headcite[l] | body[l]
print("heads", len(heads), "distinct cited labels", len(allrefs))
# 머리 선언 의존: 「…에 의존」 부분에 든 라벨만. 머리 줄의 진술문에도 라벨이 들 수 있으나 2.1절은 「머리가 선언한 의존」으로 셌다.
dep = {}
for f in order:
    for line in (CH/(f+".md")).read_text(encoding="utf-8").splitlines():
        mh = head_re.match(line); mp = proof_re.match(line)
        if mh and not mp:
            lab = mh.group(2); status = mh.group(6) or ""
            m = re.search(r"\[(.*?)\]", line)
            dep[lab] = set(ref_re.findall(status)) - {lab}
def acyclic(g):
    color = {}
    def dfs(u, path):
        color[u] = 1; path.append(u)
        for v in g.get(u, ()):
            if v not in g: continue
            if color.get(v) == 1: return path[path.index(v):] + [v]
            if color.get(v) is None:
                r = dfs(v, path)
                if r: return r
        color[u] = 2; path.pop(); return None
    for u in g:
        if color.get(u) is None:
            r = dfs(u, [])
            if r: return r
    return None
cyc = acyclic(dep)
print("머리 선언 의존 그래프 순환:", cyc)
# 전체 인용 그래프의 SCC(Tarjan)
g = {l: (headcite[l] | body[l]) & set(heads) for l in heads}
index = {}; low = {}; onst = set(); st = []; sccs = []; idx = [0]
def strong(v):
    index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); onst.add(v)
    for w in g[v]:
        if w not in index: strong(w); low[v] = min(low[v], low[w])
        elif w in onst: low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        comp = []
        while True:
            w = st.pop(); onst.discard(w); comp.append(w)
            if w == v: break
        if len(comp) > 1: sccs.append(sorted(comp))
for v in g:
    if v not in index: strong(v)
print("본문 인용까지 더한 그래프의 크기 2 이상 강결합 성분:", len(sccs))
for c in sorted(sccs, key=len): print(" ", len(c), c[:6], "..." if len(c) > 6 else "")
