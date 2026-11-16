# -*- coding: utf-8 -*-
"""부록 C 2절(기록 이름 → 이 글의 진술 → 이 글의 이름)을 진술 머리의 괄호(이름; 기록 [r…]의 …)와 맞춘다.
부록 A의 기호(첫 열)가 장부 1·2절에 문자열로 있는지도 본다. 판단은 출력을 읽고 사람이 한다."""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = {}
for f in sorted(glob.glob(ROOT + r'\장v2\장*.md')):
    for ln in open(f, encoding='utf-8'):
        mh = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(.*?)\]\.\*\*', ln)
        if mh and mh.group(2) not in heads:
            rest = mh.group(3)
            i = rest.rfind(' [')
            paren = rest[:i].strip() if i >= 0 else rest.strip()
            if paren.startswith('(') and paren.endswith(')'): paren = paren[1:-1]
            heads[mh.group(2)] = (mh.group(1), paren, ln.strip()[:300])
C = open(ROOT + r'\장v2\부록C.md', encoding='utf-8').read()
sec2 = C[C.index('### 기록이 결과에 붙인 이름'):C.index('### 기록의 글자와 이 글의 글자')]
rows = [l for l in sec2.split('\n') if l.startswith('| 기록')]
print('C 2절 rows:', len(rows))
n_ok = 0
for r in rows:
    c = [x.strip() for x in r.strip().strip('|').split(' | ')]
    if len(c) != 3: print('!! cells', r[:80]); continue
    m = re.search(r'(정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}', c[1])
    if not m: print('!! no label', r[:80]); continue
    typ, lab = m.group(1), m.group(2)
    h = heads.get(lab)
    if not h: print('!! head missing', lab); continue
    paren = h[1]
    name_head = paren.split(';')[0].strip()
    rec_head = paren.split(';', 1)[1].strip() if ';' in paren else ''
    probs = []
    if h[0] != typ: probs.append(f'TYPE C={typ} head={h[0]}')
    if name_head != c[2]: probs.append(f'NAME C=「{c[2]}」 head=「{name_head}」')
    # 기록 이름 비교: 공백 정규화
    norm = lambda s: re.sub(r'\s+', '', s)
    if norm(rec_head) != norm(c[0]): probs.append(f'REC C=「{c[0]}」 head=「{rec_head}」')
    if probs: print(lab, '|', ' ; '.join(probs))
    else: n_ok += 1
print('fully matching rows:', n_ok)
# 머리에 「기록 […]의 …」가 있는데 C 2절에 없는 진술
in_C = set()
for r in rows:
    m = re.search(r'\{\{([^}]+)\}\}', r.split(' | ')[1])
    if m: in_C.add(m.group(1))
print('\n머리 괄호에 기록 이름이 있으나 C 2절에 없는 진술:')
for lab, (t, paren, ln) in heads.items():
    if '기록 [' in paren and lab not in in_C: print('  ', t, lab, '|', paren[:150])

# 부록 A 기호 ↔ 장부
A = open(ROOT + r'\장v2\부록A.md', encoding='utf-8').read()
L = open(ROOT + r'\장부_v2.md', encoding='utf-8').read()
L12 = L[L.index('## 1. 글자 사전'):L.index('## 3. 낱말 사전')]
print('\n부록 A 기호 가운데 장부 1·2절에 문자열로 없는 것(첫 성분 기준):')
for ln in A.split('\n'):
    if ln.startswith('| $') or ln.startswith('| `'):
        sym = ln.strip().strip('|').split(' | ')[0].strip()
        first = sym.split(', ')[0].strip()
        core = first.strip('$')
        if core and core not in L12:
            print('  ', sym[:80])
