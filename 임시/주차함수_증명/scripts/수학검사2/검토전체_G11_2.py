# -*- coding: utf-8 -*-
"""G11: 인용 간선 탐색 — 둘째 증명 폐포가 9장을 품는 간선, old-6-14·cor-L 사슬."""
import re, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_src = open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체_G11_1.py", encoding='utf-8').read().split("# 2. 부록 D 항목")[0]
_src = _src.replace("sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')", "")
exec(_src)
cites = {lab: set(x for x in re.findall(r"\{\{([^}]+)\}\}", '\n'.join(s['block'])) if x in stmts and x != lab) for lab, s in stmts.items()}
print("== 9장 라벨을 인용하는 9장 밖 진술 ==")
for lab, cs in sorted(cites.items()):
    if lab.startswith('9:'): continue
    tgt = [c for c in cs if c.startswith('9:')]
    if tgt:
        print(f"  {lab} ({stmts[lab]['file']} L{stmts[lab]['line']}) -> {tgt}")
print("== 7:old-6-22 를 인용하는 진술 ==")
for lab, cs in sorted(cites.items()):
    if '7:old-6-22' in cs:
        print(f"  {lab} ({stmts[lab]['file']} L{stmts[lab]['line']})")
print("== 10.7절 산문이 인용하는 라벨 ==")
sec107 = '\n'.join(sections.get(('text', '10.7'), []))
print(sorted(set(re.findall(r"\{\{([^}]+)\}\}", sec107))))
print("== 10:old-8-37 블록이 인용하는 라벨 ==")
print(sorted(cites['10:old-8-37']))
print("== cor-L 블록 인용 ==", sorted(cites['6:cor-L']))
for x in ['6:pair-rearrange','6:diag-first-layer','6:classes-increase','6:pointwise','6:chain-count','6:class-polynomial','6:log-derivative','6:insertion','6:split-mass','6:concave-split','6:highest-long-cell','6:geometric-mean','6:trapezoid','6:survival-factor']:
    print("   ", x, '->', sorted(cites.get(x, [])))
print("== 6:insertion/log-derivative/trapezoid 를 인용하는 진술 ==")
for t in ['6:insertion','6:log-derivative','6:trapezoid']:
    print("  ", t, [lab for lab, cs in cites.items() if t in cs])
print("== 7:old-6-15 블록 길이/인용 ==", len(stmts['7:old-6-15']['block']), sorted(cites['7:old-6-15']))
print("== 7:old-6-21 블록 인용 ==", sorted(cites['7:old-6-21']))
