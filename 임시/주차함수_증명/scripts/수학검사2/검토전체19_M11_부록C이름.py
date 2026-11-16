# -*- coding: utf-8 -*-
"""부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」: 라벨의 존재·종류·이름이 머리와 맞는지, 머리의 「기록 …의 …」와 맞는지."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

bl = all_blocks()
hi = head_index(bl)
C = open(os.path.join(CH, '부록C.md'), encoding='utf-8').read().split('\n')
sec = None
rows = []
for ln in C:
    if ln.startswith('### '):
        sec = ln[4:].strip()
    if sec and sec.startswith('기록이 결과에') and ln.startswith('| ') and '{{' in ln:
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        rows.append(c)
print('행 수', len(rows))
listed = set()
for c in rows:
    recname, stmt, ourname = c
    m = re.match(r'(정리|보조정리|명제|따름정리|정의) \{\{([^}]+)\}\}', stmt)
    if not m:
        print('[형식]', stmt); continue
    kind, lab = m.groups()
    listed.add(lab)
    b = hi.get(lab)
    if not b:
        print('[라벨 없음]', stmt); continue
    probs = []
    if b['kind'] != kind:
        probs.append(f"종류: 부록C={kind}, 머리={b['kind']}")
    headname = (b['name'] or '')
    # 머리 이름은 '이름; 기록 …' 꼴
    hn = headname.split(';')[0].strip()
    hrec = headname.split(';', 1)[1].strip() if ';' in headname else ''
    if hn != ourname:
        probs.append(f"이름: 부록C=「{ourname}」, 머리=「{hn}」")
    # 기록 이름 비교(느슨): 머리의 기록 부분과 부록 C 첫 열
    if hrec and hrec.replace(' ', '') != recname.replace(' ', ''):
        probs.append(f"기록이름: 부록C=「{recname}」, 머리=「{hrec}」")
    if not hrec:
        probs.append(f"머리에 기록 이름 없음(부록C=「{recname}」); 머리 이름=「{headname}」")
    print(lab, '|', '; '.join(probs) or 'OK')

print()
print('=== 머리에 「기록 [」이 든 진술 가운데 부록 C 표에 없는 것')
for b in bl:
    if b['label'] and b['name'] and '기록' in b['name'] and b['label'] not in listed:
        print(b['file'], b['sec'], b['kind'], b['label'], '|', b['name'])
