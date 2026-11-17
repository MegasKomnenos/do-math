# -*- coding: utf-8 -*-
# R13: 1.2 전역 기호의 (바탕, 위첨자)가 「쓰이는 장」 밖의 장에 나타나는데 1.3의 그 장 묶음에도 등록이 없는 것을 찾는다.
#      후보일 뿐이며 원문으로 확인한다.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
BASE = S.BASE
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
# 1.3 묶음 -> 장
loc = collections.defaultdict(set)   # ch -> set of (base, sup)
locbase = collections.defaultdict(set)
for i in range(295, 358):
    line = L[i-1]
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    chs = collections.Counter(int(x) for x in re.findall(r'\{\{(\d+):', line))
    secs = re.findall(r'(?<![\d.])(\d{1,2})\.\d{1,2}(?:\.\d)?(?![\d])', c[1] if len(c) > 1 else '')
    for s_ in secs[:3]: chs[int(s_)] += 2
    m = re.match(r'^(\d)장', c[1]) or re.match(r'^(\d)장', c[0])
    if m: chs[int(m.group(1))] += 5
    if not chs: print('1.3 행', i, '장 판정 불가', c[1][:60]); continue
    top = [ch for ch, n in chs.most_common() if n >= max(chs.values()) / 2 and 1 <= ch <= 10]
    for seg in S.math_segments(line):
        for bs, sp, ns, sb in S.scan(seg):
            for ch in top:
                loc[ch].add((bs, sp)); locbase[ch].add(bs)
cnt = S.chapter_counts()
for i in range(49, 288):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    listed = sorted(int(x) for x in re.findall(r'\d+', c[4]))
    for sym in S.split_top(c[0]):
        base, sup, ns, sb = S.scan(sym)[0]
        if len(base) == 1 and not sup: continue
        key = (base, sup, '*')
        for ch in cnt:
            if ch in listed or cnt[ch][key] == 0: continue
            reg = (base, sup) in loc[ch]
            regb = base in locbase[ch]
            if not reg:
                print(i, sym, '| 장', ch, '에', cnt[ch][key], '번 | 1.3 그 장 묶음에 같은 (바탕,위첨자):', reg, '| 같은 바탕:', regb)
