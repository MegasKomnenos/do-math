# -*- coding: utf-8 -*-
"""11.2·11.3 표가 등급을 적은 진술의 머리 표지를 뽑아 표의 등급과 나란히 놓는다."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

bl = all_blocks()
hi = head_index(bl)
ch11 = open(os.path.join(CH, '장11.md'), encoding='utf-8').read().split('\n')

print('=== 11.2 표: 확인하는 진술 → 머리 표지')
for ln in ch11:
    if ln.startswith('| 부록 D.{{D:'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[1])
        print('-', c[0].replace('부록 D.{{D:', '').rstrip('}'), '| 표 등급:', c[2])
        for l in labs:
            b = hi.get(l)
            print('    ', l, '|', b['kind'] if b else '?', '|', b['mark'] if b else '머리 없음')

print()
print('=== 11.3 표: 계산 진술과 산술 등급 열의 진술 → 머리 표지')
in113 = False
seen = set()
for ln in ch11:
    if ln.startswith('### 11.3'):
        in113 = True
    if ln.startswith('### 11.4'):
        in113 = False
    if in113 and ln.startswith('| ') and not ln.startswith('| 입력') and '{{' in ln:
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        col = c[1]
        print('-', c[0][:60], '|| 등급열:', col[:300])
        for l in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', col):
            if l in seen:
                continue
            seen.add(l)
            b = hi.get(l)
            print('    ', l, '|', b['kind'] if b else '?', '|', b['mark'] if b else '머리 없음')

print()
print('=== 모든 머리 가운데 「계산」이 든 표지 (표에 빠진 계산 진술이 있는지)')
table_labels = set()
for ln in ch11:
    if ln.startswith('| 부록 D.{{D:'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        table_labels |= set(re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[1]))
for b in bl:
    if b['label'] and b['mark'] and ('계산' in b['mark']):
        flag = '' if b['label'] in table_labels else '  <-- 11.2 표에 없음'
        print(b['file'], b['sec'], b['kind'], b['label'], '|', b['mark'], flag)
print()
print('=== 「문헌 인용」이 든 표지')
for b in bl:
    if b['label'] and b['mark'] and '문헌' in b['mark']:
        print(b['file'], b['sec'], b['kind'], b['label'], '|', b['mark'])
print()
print('=== 「시작점 비명시」가 든 표지')
for b in bl:
    if b['label'] and b['mark'] and '시작점' in b['mark']:
        print(b['file'], b['sec'], b['kind'], b['label'], '|', b['mark'])
