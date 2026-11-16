# -*- coding: utf-8 -*-
"""L11 검토 보조 3: 11.3절 표가 적지 않은 (인용 진술, 입력) 쌍의 실제 문장을 뽑아 읽기용으로 출력한다."""
import sys, os, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
spec = importlib.util.spec_from_file_location("g", os.path.join(os.path.dirname(__file__), "검토전체6_L11_graph.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
blocks, graph, closure = g.blocks, g.graph, g.closure

pairs = [
 ('9:old-7-23','6:old-6-19'),('9:old-7-23','6:increment-bounds'),
 ('9:old-7-22','9:H-star-plus'),('9:old-7-22','6:D-bound'),
 ('9:old-7-12','6:old-7-13'),('9:old-7-12','8:old-6-33'),('9:old-7-12','2:old-2-31'),
 ('10:old-8-23','6:old-7-13'),
 ('10:old-8-3','7:threshold-unit-ratio'),('10:old-8-3','2:old-2-31'),
 ('9:old-7-11','8:old-6-23'),
 ('9:old-7-18','8:old-6-33'),('9:old-7-18','8:old-6-29'),('9:old-7-18','6:old-7-21'),
 ('9:old-7-27','8:old-6-33'),('9:old-7-27','8:old-6-29'),
 ('9:old-7-31','6:old-7-24'),
 ('9:centroid-stop','2:old-2-10'),
 ('10:old-8-19','2:old-2-45'),('10:old-8-19','2:old-2-37'),
 ('10:old-8-8','6:DD-lower-bound'),('10:old-8-17','6:DD-lower-bound'),('10:old-8-14','6:old-8-12'),
 ('10:old-8-2','2:old-2-26'),
 ('9:old-7-28','2:old-2-38'),('9:old-7-28','2:old-2-39'),
 ('10:old-8-25','6:old-8-13'),('10:old-8-25','6:old-8-12'),
 ('9:head-sum-1','5:old-5-18'),
]
for c, x in pairs:
    b = blocks[c]
    print(f"\n##### {c} ({b['file']} {b['sec']} L{b['line']}) -> {x}")
    for i, l in [(b['line'], b['head'])] + b['body']:
        key = '{{' + x + '}}'
        pos = l.find(key)
        while pos >= 0:
            print(f"  L{i}: …{l[max(0,pos-200):pos+120]}…")
            pos = l.find(key, pos + 1)

print("\n##### 9:old-7-2 를 인용하는 블록:", [c for c in blocks if '9:old-7-2' in graph[c]])
for c in [c for c in blocks if '9:old-7-2' in graph[c]]:
    b = blocks[c]
    for i, l in [(b['line'], b['head'])] + b['body']:
        if '{{9:old-7-2}}' in l: print(f"  {c} L{i}: …{l[max(0,l.find('{{9:old-7-2}}')-200):l.find('{{9:old-7-2}}')+100]}…")
print("\n##### 10:old-8-1 블록 인용:", sorted(graph.get('10:old-8-1', [])))
print("##### 10:families 블록 인용:", sorted(graph.get('10:families', [])))
cl = closure('6:cor-L')
print("\n##### 6:cor-L 닫힘(6장):", sorted(x for x in cl if x.startswith('6:')))
tbl = ['6:pair-rearrange','6:diag-first-layer','6:classes-increase','6:pointwise','6:chain-count','6:class-polynomial','6:log-derivative','6:insertion','6:split-mass','6:concave-split','6:highest-long-cell','6:geometric-mean','6:trapezoid','6:survival-factor']
print("표에 있고 닫힘에 없음:", [x for x in tbl if x not in cl])
print("닫힘에 있고 표에 없음:", sorted(x for x in cl if x.startswith('6:') and x not in tbl))
for x in ['6:insertion','6:log-derivative','6:trapezoid']:
    print(f"  {x} 를 인용하는 블록:", [c for c in blocks if x in graph[c]])
# who cites 9:old-7-23, 9:old-7-22, 9:old-7-12, 9:old-7-11, 9:old-7-18, 9:centroid-stop, 10:old-8-19, 10:old-8-8, 10:old-8-17, 10:old-8-2, 10:old-8-3
print()
for x in ['9:old-7-23','9:old-7-22','9:old-7-12','9:old-7-11','9:old-7-18','9:old-7-27','9:centroid-stop','10:old-8-19','10:old-8-8','10:old-8-17','10:old-8-2','10:old-8-3','10:old-8-14','10:old-8-25']:
    print(f"{x} 를 인용하는 블록: {sorted(c for c in blocks if x in graph[c])}")
