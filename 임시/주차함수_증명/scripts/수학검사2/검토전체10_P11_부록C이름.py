# -*- coding: utf-8 -*-
"""부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 진술 머리의 괄호와 대조한다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}\s*(?:\((.*?)\))?\s*(?:\[(.*?)\])?\.\*\*')
heads={}
for f in sorted(glob.glob(os.path.join(BASE,'장*.md'))):
    for i, ln in enumerate(open(f,encoding='utf-8').read().split('\n'),1):
        h=HEAD.match(ln)
        if h and h.group(2) not in heads:
            paren = h.group(3) or ''
            # 이름; 기록 ... 분리
            if ';' in paren:
                name, recpart = paren.split(';',1)
            else:
                name, recpart = paren, ''
            heads[h.group(2)] = dict(kind=h.group(1), name=name.strip(), rec=recpart.strip(), file=os.path.basename(f), line=i)
C = open(os.path.join(BASE,'부록C.md'),encoding='utf-8').read()
i0 = C.index('### 기록이 결과에 붙인 이름'); i1 = C.index('### 기록의 글자와 이 글의 글자')
rows=[]
for ln in C[i0:i1].split('\n'):
    if ln.startswith('| 기록 ') or ln.startswith('| 기록['):
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]
        rows.append(c)
print("부록 C 이름 표 행 수:", len(rows))
listed=set()
for c in rows:
    recname, stmt, name = c
    m = re.search(r'\{\{([^}]+)\}\}', stmt); lab = m.group(1) if m else None
    kind = stmt.split(' ')[0]
    listed.add(lab)
    h = heads.get(lab)
    if not h: print(f"** 머리 없음: {stmt}"); continue
    probs=[]
    if h['kind']!=kind: probs.append(f"종류: 표 {kind} / 머리 {h['kind']}")
    if h['name']!=name: probs.append(f"이름: 표 『{name}』 / 머리 『{h['name']}』")
    # 기록 이름 비교: 표의 "기록 [rX]의 Y" vs 머리의 "기록 [rX]의 Y"
    rn = recname.replace('기록 ','기록 ')
    if re.sub(r'\s+',' ',h['rec']) != re.sub(r'\s+',' ',rn):
        probs.append(f"기록 이름: 표 『{rn}』 / 머리 『{h['rec']}』")
    if probs:
        print(f"\n{lab} ({h['file']}:{h['line']})"); [print("   -",p) for p in probs]
print("\n=== 머리에 「기록 [」 괄호가 있으나 부록 C 이름 표에 없는 진술 ===")
for lab,h in heads.items():
    if '기록 [' in h['rec'] and lab not in listed:
        print(f"{lab} ({h['file']}:{h['line']}): ({h['name']}; {h['rec']})")
print("\n=== 머리 괄호에 ';' 없이 기록 이름이 든 경우(혹시) ===")
for lab,h in heads.items():
    if '기록' in h['name']: print(lab, h['name'])
