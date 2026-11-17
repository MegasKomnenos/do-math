# -*- coding: utf-8 -*-
"""장부 358-682행에 나오는 라벨 {{N:name}}을 뽑아 heads.json과 대조: 살아 있는지, 앞에 적힌 종류가 맞는지."""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
heads = json.load(open(os.path.join(here, '검토전체22_R13_heads.json'), encoding='utf-8'))
H = {}
for h in heads:
    if not h.get('proof'):
        H[h['label']] = h
lines = open(os.path.join(here, '..', '..', '장부_v2.md'), encoding='utf-8').read().split('\n')
a, b = 358, 682
if len(sys.argv) > 2: a, b = int(sys.argv[1]), int(sys.argv[2])
kinds = ['정의', '정리', '보조정리', '명제', '따름정리']
# 식 라벨·D 라벨은 따로
eqdead = []
for ln in range(a, b + 1):
    l = lines[ln - 1]
    for m in re.finditer(r'\{\{([0-9A-Z]+):([^}]+)\}\}', l):
        lab = m.group(1) + ':' + m.group(2)
        pre = l[max(0, m.start() - 14):m.start()]
        if lab in H:
            h = H[lab]
            km = re.search(r'(따름정리|보조정리|정리|명제|정의)\s*`?$', pre)
            if km and km.group(1) != h['kind']:
                print('종류 불일치 %d: %s  장부=%s  현행=%s (%s:%d, %s절)' % (ln, lab, km.group(1), h['kind'], h['file'], h['line'], h['sec']))
        else:
            print('머리 없음 %d: %s   앞글: %s' % (ln, lab, pre.replace('\n', ' ')))
