# -*- coding: utf-8 -*-
"""H14: 의존지도 2.1절의 수치(입력 열 라벨 379개, 머리 선언 그래프 비순환, 본문 인용 그래프 강결합 성분 15개)를 1절 표에서 다시 센다."""
import io, os, re, sys
sys.setrecursionlimit(10000)
ROOT = r"C:\math\임시\주차함수_증명"
LABEL_RE = re.compile(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}")
BS=chr(92)
CELL_SPLIT = re.compile("(?<!" + BS + BS + ")" + BS + "|")
tab=io.open(os.path.join(ROOT,"의존지도_v2.md"),encoding="utf-8").read().split("\n")
nodes=[]; head_edges={}; all_edges={}; inputs=set()
for ln in tab:
    if ln.startswith("## 2."): break
    if not ln.startswith("| `{{"): continue
    c=[x.strip() for x in CELL_SPLIT.split(ln.strip()[1:-1])]
    if len(c)!=10: continue
    key=c[0].strip("`{}"); nodes.append(key)
    inp=c[5]
    if inp=="—": hl=set(); bl=set()
    else:
        parts=inp.split("본문 인용:")
        hl=set(LABEL_RE.findall(parts[0])); bl=set(LABEL_RE.findall(parts[1])) if len(parts)>1 else set()
    # 지위 열의 「…에 의존」 선언 라벨
    decl=set(LABEL_RE.findall(c[4]))
    head_edges[key]=hl|decl
    all_edges[key]=hl|bl|decl
    inputs|=hl|bl
print("입력 열 라벨(중복 제외):",len(inputs),"; 1절 밖 라벨:",sorted(inputs-set(nodes)))
# cycles in head graph
def has_cycle(g):
    color={}
    def dfs(u):
        color[u]=1
        for v in g.get(u,()):
            if v not in g: continue
            if color.get(v)==1: return True
            if color.get(v) is None and dfs(v): return True
        color[u]=2; return False
    return any(color.get(u) is None and dfs(u) for u in g)
print("머리 선언 그래프 순환:",has_cycle(head_edges))
# SCC (Tarjan) on all_edges
index={}; low={}; st=[]; on=set(); sccs=[]; idx=[0]
def strong(v):
    index[v]=low[v]=idx[0]; idx[0]+=1; st.append(v); on.add(v)
    for w in all_edges.get(v,()):
        if w not in all_edges: continue
        if w not in index: strong(w); low[v]=min(low[v],low[w])
        elif w in on: low[v]=min(low[v],index[w])
    if low[v]==index[v]:
        comp=[]
        while True:
            w=st.pop(); on.discard(w); comp.append(w)
            if w==v: break
        if len(comp)>1: sccs.append(sorted(comp))
for v in all_edges:
    if v not in index: strong(v)
print("강결합 성분(크기 2 이상):",len(sccs))
for s in sorted(sccs,key=lambda x:(len(x),x)): print("  ",", ".join(s))
