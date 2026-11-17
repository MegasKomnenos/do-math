# -*- coding: utf-8 -*-
# R13: 장부 5절 넷째 열(여유 글자)이 그 장에서 쓰이는 1.2 전역 기호·1장 정의 전역 기호·1.1 변수와 (바탕, 글자체)가 겹치지 않는지 본다.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
L = open(S.BASE + '장부_v2.md', encoding='utf-8').read().split(chr(10))
used = collections.defaultdict(dict)   # ch -> base -> row
for i in range(49, 288):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    chs = set(int(x) for x in re.findall(r'\d+', c[4]))
    dch = int(re.match(r'\s*(\d+)', c[3]).group(1))
    chs.add(dch)
    for sym in S.split_top(c[0]):
        base = S.scan(sym)[0][0]
        for ch in (chs | (set(range(1, 11)) if dch == 1 else set())):
            used[ch].setdefault(base, (i, sym))
var = {}
for i in range(27, 42):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    for seg in S.math_segments(c[0]):
        k = S.scan(seg)
        if k: var[k[0][0]] = (i, c[0])
for i in range(1191, 1201):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    ch = int(c[0])
    free = []
    for seg in S.math_segments(c[3]):
        k = S.scan(seg)
        if k: free.append(k[0][0])
    bad = [(b, used[ch][b]) for b in free if b in used[ch]]
    badv = [(b, var[b]) for b in free if b in var]
    print('장', ch, '여유 글자', len(free), '| 그 장 전역과 겹침:', bad[:8], '| 1.1 변수와 겹침:', badv[:8])
