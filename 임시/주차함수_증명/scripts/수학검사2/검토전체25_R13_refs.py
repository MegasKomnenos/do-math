# -*- coding: utf-8 -*-
# 네 파일이 부르는 라벨 {{장:이름}}·{{D:이름}}이 장 파일에 살아 있는지 센다(자리 찾기 전용).
import re, sys, io, json, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
heads = json.load(io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_heads.json'), encoding='utf-8'))
live = set(h['ch'] + ':' + h['lab'] for h in heads)
# all labels defined/used in chapter files
chap = {}
for p in glob.glob(os.path.join(base, '장v2', '*.md')):
    t = io.open(p, encoding='utf-8').read()
    for m in re.finditer(r'\{\{([0-9A-Za-z]+):([^}]+)\}\}', t):
        chap.setdefault(m.group(1) + ':' + m.group(2), set()).add(os.path.basename(p))
dlabels = set(k for k in chap if k.startswith('D:'))
print('chapter label kinds:', sorted(set(k.split(':')[0] for k in chap)))
print('non-statement labels in chapters (not in heads, not D):', sorted(k for k in chap if k not in live and not k.startswith('D:'))[:60])
for fn in ['장부_v2.md', '구조표_v2.md', '의존지도_v2.md']:
    L = io.open(os.path.join(base, fn), encoding='utf-8').read().split('\n')
    miss = {}
    for i, line in enumerate(L, 1):
        for m in re.finditer(r'\{\{([0-9A-Za-z]+):([^}]+)\}\}', line):
            k = m.group(1) + ':' + m.group(2)
            if k not in chap:
                miss.setdefault(k, []).append(i)
    print('==', fn, 'labels not in any chapter file:', len(miss))
    for k in sorted(miss):
        print('  ', k, miss[k][:12])
