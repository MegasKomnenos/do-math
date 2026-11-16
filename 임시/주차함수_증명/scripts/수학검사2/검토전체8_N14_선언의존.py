# -*- coding: utf-8 -*-
"""머리가 선언한 「…에 의존」 그래프의 비순환성과, 선언 라벨이 머리 줄에 다 있는지, 지도 2.1의 수(380)를 센다."""
import re, sys, os, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
LAB = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
edges={}; pos={}
for name in order:
    for ln,line in enumerate(open(os.path.join(root,"장v2",name+".md"),encoding='utf-8'),1):
        m=HEAD_RE.match(line)
        if m:
            key=f"{m.group(2)}:{m.group(3)}"
            pos[key]=(name,ln)
            edges[key]=[f"{a}:{b}" for a,b in LAB.findall(line[m.end():]) if f"{a}:{b}"!=key]
# 비순환?
import sys
sys.setrecursionlimit(10000)
color={}
cyc=[]
def dfs(u,stack):
    color[u]=1; stack.append(u)
    for v in edges.get(u,[]):
        if color.get(v,0)==1: cyc.append(stack[stack.index(v):]+[v])
        elif color.get(v,0)==0: dfs(v,stack)
    stack.pop(); color[u]=2
for u in edges:
    if color.get(u,0)==0: dfs(u,[])
print("선언 간선 수", sum(len(v) for v in edges.values()), "순환", len(cyc))
for c in cyc[:5]: print("  ", c)
# 선언 의존이 뒤 장을 가리키는 것(전방 의존)
def chno(k): return int(k.split(":")[0])
fwd=[(u,v) for u,vs in edges.items() for v in vs if chno(v)>chno(u)]
print("전방 선언 의존", len(fwd))
for u,v in fwd: print("  ",u,"->",v, pos[u])
