# -*- coding: utf-8 -*-
# R13: 1.2 행의 기호(글자체 명령·그리스 바탕)가 「쓰이는 장」 밖의 장에 나타나는 첫 자리를 보인다(같은 양인지 사람이 판정).
import re, sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('s', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_sym.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
BASE = S.BASE
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
a, b = int(sys.argv[1]), int(sys.argv[2])
only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None
# 장별 (key -> 첫 문맥)
first = {}
for ch, files in S.CH.items():
    d = {}
    for f in files:
        for ln, line in enumerate(open(BASE + '장v2/' + f + '.md', encoding='utf-8'), 1):
            line2 = re.sub(r'\{\{[^}]*\}\}', lambda m: ' ' * len(m.group(0)), line)
            for m in re.finditer(r'\$\$(.+?)\$\$|\$([^$]+)\$', line2):
                seg = m.group(1) or m.group(2)
                for bs, sp, ns, sb in S.scan(seg):
                    k = (bs, sp)
                    if k not in d:
                        d[k] = '[%s:%d] %s' % (f, ln, line[max(0, m.start() - 60):m.end() + 40].strip())
                    # 첨자 꼴까지 구분한 집계
                    d.setdefault(('CNT', bs, sp), {}).setdefault(sb, 0)
                    d[('CNT', bs, sp)][sb] += 1
    first[ch] = d
for i in range(a, b + 1):
    line = L[i-1]
    if not line.startswith('|'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    listed = sorted(int(x) for x in re.findall(r'\d+', c[4]))
    for sym in S.split_top(c[0]):
        ks = S.scan(sym)
        base, sup, ns, sb = ks[0]
        if len(base) == 1: continue
        if only and str(i) not in only: continue
        for ch in first:
            if ch in listed: continue
            if (base, sup) in first[ch]:
                subs = first[ch][('CNT', base, sup)]
                print(i, sym, '— 장', ch, '첨자 꼴:', dict(sorted(subs.items(), key=lambda kv: -kv[1])[:6]))
                print('     ', first[ch][(base, sup)][:260])
