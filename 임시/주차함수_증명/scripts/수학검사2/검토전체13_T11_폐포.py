# -*- coding: utf-8 -*-
"""T11: 두 증명(9:old-7-46, 10:old-8-37)의 인용 폐포를 근사 계산해 11.3 표의 공유/고유 분류와 맞춘다(자리 찾기용 근사; 판단은 원문 읽기로)."""
import re, os, glob, json
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\w+):([\w\-]+)\}\}')
lab_re = re.compile(r'\{\{(\d+):([\w\-]+)\}\}')
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
edges = {}; prep_edges = {}
for ch in order:
    f = os.path.join(CH, ch + '.md')
    cur = None; kind = '준비'; pending = set()
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        m = head_re.match(line)
        if m:
            cur = f"{m.group(2)}:{m.group(3)}"; kind = '본문'
            edges.setdefault(cur, set()); prep_edges.setdefault(cur, set())
            prep_edges[cur] |= pending; pending = set()
        labs = {f"{a}:{b}" for a, b in lab_re.findall(line)}
        if kind == '본문' and cur:
            edges[cur] |= labs - {cur}
        else:
            pending |= labs
        if '∎' in line and kind == '본문':
            kind = '준비'
def closure(start, use_prep):
    seen = set(); stack = [start]
    while stack:
        x = stack.pop()
        if x in seen or x not in edges: continue
        seen.add(x)
        nxt = set(edges[x]) | (prep_edges.get(x, set()) if use_prep else set())
        stack.extend(nxt - seen)
    return seen
for use_prep in (False, True):
    C1 = closure('9:old-7-46', use_prep); C2 = closure('10:old-8-37', use_prep)
    print(f"\n===== prep={use_prep}: |C1|={len(C1)} |C2|={len(C2)} shared={len(C1&C2)} only1={len(C1-C2)} only2={len(C2-C1)}")
    # 11.3 표 분류
    lines = open(os.path.join(CH, '장11.md'), encoding='utf-8').read().split('\n')
    shared_rows = lines[87:109]; u1_rows = lines[114:121]; u2_rows = lines[126:129]
    def labs_of(rows): 
        s = set()
        for r in rows:
            c = r.split(' | ')
            if len(c) > 1: s |= {f"{a}:{b}" for a, b in lab_re.findall(c[0])}
        return s
    S, U1, U2 = labs_of(shared_rows), labs_of(u1_rows), labs_of(u2_rows)
    print("표 공유:", len(S), "표 고유1:", len(U1), "표 고유2:", len(U2))
    for lab in sorted(S):
        tag = ('C1' if lab in C1 else '--') + ('C2' if lab in C2 else '--')
        if tag != 'C1C2': print(f"  공유 행인데 폐포는 {tag}: {lab}")
    for lab in sorted(U1):
        tag = ('C1' if lab in C1 else '--') + ('C2' if lab in C2 else '--')
        if tag != 'C1--': print(f"  고유1 행인데 폐포는 {tag}: {lab}")
    for lab in sorted(U2):
        tag = ('C1' if lab in C1 else '--') + ('C2' if lab in C2 else '--')
        if tag != '--C2': print(f"  고유2 행인데 폐포는 {tag}: {lab}")
    # 9장·10장·7B old-6-22 증명이 직접 인용하는 앞 장 진술 중 표에 없는 것
    direct9 = set(); direct10 = set()
    for x in edges:
        if x.startswith('9:') and x in C1: direct9 |= {l for l in edges[x] if not l.startswith(('9:','10:'))}
        if x.startswith('10:') and x in C2: direct10 |= {l for l in edges[x] if not l.startswith(('9:','10:'))}
    direct9 |= {l for l in edges.get('7:old-6-22', set()) if not l.startswith(('9:','10:'))}
    allrows = S | U1 | U2
    # 표의 모든 라벨(계산 진술 열 포함)
    alllabs = {f"{a}:{b}" for a, b in lab_re.findall('\n'.join(lines[83:130]))}
    print("  9장(+7:old-6-22) 직접 인용 앞장 진술 중 11.3 어디에도 없음:", sorted(direct9 - alllabs))
    print("  10장 직접 인용 앞장 진술 중 11.3 어디에도 없음:", sorted(direct10 - alllabs))
    if use_prep:
        json.dump({k: sorted(v) for k, v in edges.items()}, open(os.path.join(ROOT,'대조v2','수학검사2','_T11_edges.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=0)
        json.dump({'C1': sorted(C1), 'C2': sorted(C2)}, open(os.path.join(ROOT,'대조v2','수학검사2','_T11_closure.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=0)
