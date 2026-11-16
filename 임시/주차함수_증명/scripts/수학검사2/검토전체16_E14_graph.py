# -*- coding: utf-8 -*-
"""E14: 의존지도 2.1절의 현행 주장(라벨 381개, 순환 0, 강결합 성분 17)을 1절 표에서 다시 센다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
heads=set()
for line in open(f"{ROOT}/scripts/수학검사2/_E14_heads.tsv", encoding='utf-8'):
    f, ln, sec, kind, ch, lab, paren, status = line.rstrip("\n").split("\t")
    if status.startswith("의 증명") or (paren=="" and status.startswith("의")): continue
    heads.add(f"{ch}:{lab}")
lines = open(f"{ROOT}/의존지도_v2.md", encoding='utf-8').read().split("\n")
s = next(i for i,l in enumerate(lines) if l.startswith("## 1."))
e = next(i for i,l in enumerate(lines) if l.startswith("### 1.1"))
decl={}; body={}
allcited=set()
for l in lines[s:e]:
    if not l.startswith("| `{{"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    lab=re.match(r'`\{\{(\d+:[^}]+)\}\}`', cells[0]).group(1)
    inputs=cells[5]
    head_part, _, body_part = inputs.partition('본문 인용:')
    d=set(re.findall(r'\{\{(\d+:[^}]+)\}\}', head_part))
    b=set(re.findall(r'\{\{(\d+:[^}]+)\}\}', body_part))
    decl[lab]=d; body[lab]=b; allcited|=d|b
print("진술 수:", len(decl), "| 인용 라벨(중복 제외):", len(allcited), "| 장 파일 밖 라벨:", sorted(allcited-heads))
# 순환 검사(선언 의존)
import sys
sys.setrecursionlimit(10000)
def cycles(graph):
    color={}
    found=[]
    def dfs(u, stack):
        color[u]=1; stack.append(u)
        for v in graph.get(u,()):
            if color.get(v,0)==1: found.append(stack[stack.index(v):]+[v])
            elif color.get(v,0)==0: dfs(v, stack)
        stack.pop(); color[u]=2
    for u in graph:
        if color.get(u,0)==0: dfs(u, [])
    return found
cy = cycles(decl)
print("선언 의존 그래프 순환:", len(cy), cy[:3])
# 강결합 성분(선언+본문)
full={k: decl[k]|body[k] for k in decl}
index={}; low={}; onst=set(); st=[]; sccs=[]; idx=[0]
def sc(v):
    index[v]=low[v]=idx[0]; idx[0]+=1; st.append(v); onst.add(v)
    for w in full.get(v,()):
        if w not in full: continue
        if w not in index: sc(w); low[v]=min(low[v],low[w])
        elif w in onst: low[v]=min(low[v],index[w])
    if low[v]==index[v]:
        comp=[]
        while True:
            w=st.pop(); onst.discard(w); comp.append(w)
            if w==v: break
        if len(comp)>1: sccs.append(sorted(comp))
for v in full:
    if v not in index: sc(v)
print("크기 2 이상 강결합 성분:", len(sccs))
for c in sccs: print("  ", len(c), c[:6], "..." if len(c)>6 else "")
