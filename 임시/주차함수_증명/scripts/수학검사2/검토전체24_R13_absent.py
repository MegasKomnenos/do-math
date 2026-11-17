# -*- coding: utf-8 -*-
# R13: 대응표에서 「옮김」 행이 가리키는 새 라벨의 산 행이 15:52 칸을 무엇으로 적는지,
#      「사본에 없음」 산 행 가운데 옮긴 진술과 참으로 새 진술이 몇인지 센다.
import re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
live = {}; moved = []
for i, line in enumerate(open(r'C:/math/임시/주차함수_증명/대조v2/라벨_번호_대응표_1114.md', encoding='utf-8'), 1):
    if not line.startswith('| `'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    lab = c[0].strip('`')
    if lab.startswith('{{'): live[lab[2:-2]] = (i, c)
    elif c[3].startswith('옮김'):
        moved.append((i, lab, re.search(r'\{\{([^}]+)\}\}', c[3]).group(1), c[4]))
cnt = collections.Counter(live[t][1][4] for i, old, t, n in moved)
print('옮김 행', len(moved), '| 옮긴 곳 산 행의 15:52 칸:', dict(cnt))
no = [k for k, (i, c) in live.items() if c[4] == '사본에 없음']
tg = {m[2] for m in moved}
print('「사본에 없음」 산 행', len(no), '| 옮김 행이 가리키는 것', len([k for k in no if k in tg]), '| 나머지(새 진술)', len([k for k in no if k not in tg]))
for i, old, t, n in moved:
    print('  ', old, '->', t, '| 옛 번호', n, '| 산 행', live[t][0], '행')
