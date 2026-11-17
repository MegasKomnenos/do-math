# -*- coding: utf-8 -*-
# R13: 장부 1.2 「기록의 글자」 열의 기록 식별자가 7절의 같은 글자 행에도 있는지(와 그 반대) 본다. 후보만.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
L = open(S.BASE + '장부_v2.md', encoding='utf-8').read().split(chr(10))
ID = re.compile(r'r[0-9a-f]{7}')
s7 = collections.defaultdict(set)
rows7 = 0
for i in range(1243, 1446):
    line = L[i-1]
    if not line.startswith('|'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if len(c) < 4: print('7절 칸 수', i, len(c)); continue
    rows7 += 1
    ids = set(ID.findall(c[1]))
    for seg in S.math_segments(c[0]):
        k = S.scan(seg)
        if k: s7[(k[0][0], k[0][1])] |= ids
print('7절 행', rows7)
only12 = 0; only7 = 0
for i in range(49, 288):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    ids12 = set(ID.findall(c[6]))
    ids7 = set()
    for sym in S.split_top(c[0]):
        k = S.scan(sym)[0]
        ids7 |= s7.get((k[0], k[1]), set())
    a = ids12 - ids7; b = ids7 - ids12
    if a:
        only12 += 1
        print(i, c[0][:40], '| 1.2에만:', sorted(a), '| 7절에만:', sorted(b)[:6])
print('1.2에만 있는 식별자를 가진 행', only12)
