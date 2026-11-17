# -*- coding: utf-8 -*-
# R13: 장부 5절 둘째 열(그 장이 처음 정의하는 전역 기호)을 1.2의 정의 절에서 다시 만들어 맞대고,
#      넷째 열(여유 글자)이 그 장에서 쓰이는 1.2 전역 기호·1장 전역·1.1 변수와 (바탕 글자, 글자체)가 겹치지 않는지 본다.
import re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
BASE = r'C:/math/임시/주차함수_증명/'
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
rows12 = []
for i in range(49, 288):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    rows12.append((i, c))
bych = collections.defaultdict(list)
for i, c in rows12:
    m = re.match(r'\s*(\d+)\.(\d+)', c[3])
    bych[int(m.group(1))].append(c[0])
rows5 = {}
for i in range(1191, 1202):
    line = L[i-1]
    if not line.startswith('|'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    rows5[c[0]] = (i, c)
    print('5절 행', i, '장', c[0], '칸 수', len(c), '기호 칸 길이', len(c[1]), '낱말 칸 길이', len(c[2]) if len(c) > 2 else None, '여유 칸 길이', len(c[3]) if len(c) > 3 else None)
for ch in sorted(bych):
    key = str(ch)
    if key not in rows5: print('5절에 장', ch, '행 없음'); continue
    i, c = rows5[key]
    have = [x.strip() for x in c[1].split('; ')]
    exp = bych[ch]
    a = [x for x in exp if x not in have]; b = [x for x in have if x not in exp]
    print('장', ch, '1.2 정의 %d개, 5절 %d개' % (len(exp), len(have)), '| 5절에 없음:', a, '| 5절에만:', b)
