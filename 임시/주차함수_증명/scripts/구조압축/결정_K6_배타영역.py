# -*- coding: utf-8 -*-
"""결정 K6 — 9장과 10장의 배타 영역을 의존 그래프(라운드13 파생 정본)에서 센다.

주 정리(1:main-theorem)에서 거꾸로 도달되는 노드 집합 R을 구하고,
9장 노드를 모두 뺀 그래프에서 도달되는 집합 R9', 10장 노드를 뺀 그래프의 R10'을 구해
R - R9' (9장과 함께 지울 수 있는 것), R - R10' (10장과 함께 지울 수 있는 것)을 낸다.
선의 방향: source = 입력(근거), target = 소비처. 거꾸로 걷는다(target -> source).
"""
import json, sys, collections
from pathlib import Path

ROOT = Path(r"C:/math/임시/주차함수_증명")
G = json.load(open(ROOT/"dependency_map/작업/파생/dependency_graph.json", encoding="utf-8"))
nodes = G["nodes"]; edges = G["edges"]
print("노드 수", len(nodes), "선 수", len(edges))

num2sid = {n: d["stable_id"] for n, d in nodes.items()}
sid2num = {d["stable_id"]: n for n, d in nodes.items()}
chap = {n: d["chapter"] for n, d in nodes.items()}
kind = {n: d["kind"] for n, d in nodes.items()}
label = {n: d.get("label","") for n, d in nodes.items()}

types = collections.Counter(e["type"] for e in edges)
print("선 종류:", dict(types))

# 거꾸로 인접 리스트: 소비처 -> 입력들
back = collections.defaultdict(set)
fwd = collections.defaultdict(set)
for e in edges:
    back[e["target"]].add(e["source"])
    fwd[e["source"]].add(e["target"])

def reach_back(start, removed=frozenset()):
    seen=set(); st=[start]
    while st:
        x=st.pop()
        if x in seen or x in removed: continue
        seen.add(x)
        for y in back[x]:
            if y not in removed: st.append(y)
    return seen

MAIN = sid2num["1:main-theorem"]
R = reach_back(MAIN)
ch9 = {n for n in nodes if chap[n]==9}
ch10 = {n for n in nodes if chap[n]==10}
print("\n주 정리에서 거꾸로 도달되는 노드:", len(R), "(전체", len(nodes), ")")
unreached = sorted(set(nodes)-R, key=lambda n: tuple(int(p) if p.isdigit() else p for p in n.split('.')))
print("도달되지 않는 노드:", [(n,num2sid[n]) for n in unreached])

print("\n9장 노드", len(ch9), ":", sorted(num2sid[n] for n in ch9))
print("10장 노드", len(ch10), ":", sorted(num2sid[n] for n in ch10))

R9 = reach_back(MAIN, removed=frozenset(ch9))
R10 = reach_back(MAIN, removed=frozenset(ch10))
ex9 = R - R9; ex10 = R - R10
def fmt(S):
    out=collections.defaultdict(list)
    for n in S: out[chap[n]].append((n,num2sid[n],kind[n],label[n]))
    return {c: sorted(v) for c,v in sorted(out.items())}

print("\n=== 9장을 빼면 주 정리에서 도달되지 않게 되는 노드(9장과 함께 지울 수 있는 것) ===")
for c,v in fmt(ex9).items():
    print(f"  {c}장 {len(v)}개:"); [print("    ",x) for x in v]
print("\n=== 10장을 빼면 주 정리에서 도달되지 않게 되는 노드(10장과 함께 지울 수 있는 것) ===")
for c,v in fmt(ex10).items():
    print(f"  {c}장 {len(v)}개:"); [print("    ",x) for x in v]

# 두 장 사이의 선
print("\n=== 9장<->10장 사이의 선 ===")
for e in edges:
    s,t=e["source"],e["target"]
    if (s in ch9 and t in ch10) or (s in ch10 and t in ch9):
        print("  ",e["source_stable_id"],"->",e["target_stable_id"],e["type"],e.get("label",""),e.get("reason",""))

# 각 장이 직접 받는 입력(선 source가 앞 장, target이 그 장)
def direct_inputs(ch):
    S=collections.defaultdict(set)
    for e in edges:
        if e["target"] in ch and chap[e["source"]]<9:
            S[e["source_stable_id"]].add(e["target_stable_id"])
    return S
d9=direct_inputs(ch9); d10=direct_inputs(ch10)
print("\n=== 9장이 앞 장에서 직접 받는 노드 입력", len(d9), "===")
for k in sorted(d9): print("  ",k,"<-",sorted(d9[k]))
print("\n=== 10장이 앞 장에서 직접 받는 노드 입력", len(d10), "===")
for k in sorted(d10): print("  ",k,"<-",sorted(d10[k]))
only9=set(d9)-set(d10); only10=set(d10)-set(d9); both=set(d9)&set(d10)
print("\n직접 입력 가운데 9장만:",sorted(only9))
print("직접 입력 가운데 10장만:",sorted(only10))
print("직접 입력 가운데 둘 다:",sorted(both))

# 7장 접점: 7장 노드 가운데 소비처가 9장/10장/7장-내부뿐인 것
print("\n=== 7장·8장·6장 노드의 소비처(장별) ===")
for n in sorted((n for n in nodes if chap[n] in (6,7,8)), key=lambda n: tuple(int(p) if p.isdigit() else p for p in n.split('.'))):
    cons=collections.Counter(chap[t] for t in fwd[n])
    print(f"  {n:7s} {num2sid[n]:28s} 소비처 장별: {dict(sorted(cons.items()))}")

# 주 정리로 들어오는 선
print("\n=== 주 정리로 들어오는 선 ===")
for e in edges:
    if e["target"]==MAIN: print("  ",e["source_stable_id"],e["type"],e.get("label",""))

# 1장 정리가 9/10장 어느 쪽으로도 닿는지: 9장 빼고 10장 빼고 모두 빼면
R_none = reach_back(MAIN, removed=frozenset(ch9|ch10))
print("\n둘 다 빼면 도달:", len(R_none), " / 9장만 빼면:", len(R9), " / 10장만 빼면:", len(R10), " / 전체:", len(R))
print("9장 배타(앞 장만):", len([n for n in ex9 if chap[n]<9]), " 10장 배타(앞 장만):", len([n for n in ex10 if chap[n]<9]))
