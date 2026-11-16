# -*- coding: utf-8 -*-
"""11.3 표의 입력 진술마다, 9장·10장의 어느 블록과 7.7절 정리 7:old-6-22 블록이 그 라벨을 인용하는지 나열한다."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

bl = all_blocks()
hi = head_index(bl)
ch11 = open(os.path.join(CH, '장11.md'), encoding='utf-8').read().split('\n')

targets = [b for b in bl if b['file'] in ('장9.md', '장10.md')]
t622 = hi.get('7:old-6-22')
if t622:
    targets.append(t622)

def who_cites(label):
    tag = '{{' + label + '}}'
    out = []
    for b in targets:
        if b['label'] == label:
            continue
        txt = b['text']
        if tag in txt:
            # 머리(의존 표지)에서만인지, 본문/증명에서인지
            head = b.get('headline', '')
            inhead = tag in head
            body = tag in txt.replace(head, '', 1)
            where = ('머리' if inhead else '') + ('+' if inhead and body else '') + ('본문' if body else '')
            nm = f"{b['kind']} {b['label']}" if b['label'] else f"준비({b['file']} {b['sec']} 행{b['start']+1})"
            out.append(f"{nm}[{where}]")
    return out

in113 = False
for ln in ch11:
    if ln.startswith('### 11.3'):
        in113 = True
    if ln.startswith('### 11.4'):
        in113 = False
    if in113 and ln.startswith('| ') and not ln.startswith('| 입력') and '{{' in ln:
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[0])
        print('=' * 90)
        print('행:', c[0][:120])
        for i in range(2, len(c)):
            print('  표 인용열%d:' % (i - 1), c[i][:700])
        for l in labs:
            b = hi.get(l)
            print('  *', l, '(' + (b['kind'] if b else '?') + ')', '→ 인용:', '; '.join(who_cites(l)) or '없음')
