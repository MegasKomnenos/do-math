# -*- coding: utf-8 -*-
# R13: 장부·구조표·의존지도에 나오는 {{라벨}}이 현행 장 파일의 머리(또는 부록 D 항목)에 있는지 본다.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('h', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_heads.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
live = {x['label'] for x in h.heads()}
kinds = {x['label']: x['kind'] for x in h.heads()}
import glob, os
BASE = r'C:/math/임시/주차함수_증명/'
D = set()
for f in glob.glob(BASE + '장v2/부록D_*.md'):
    for m in re.finditer(r'^\*\*D\.\{\{(D:[^}]+)\}\}', open(f, encoding='utf-8').read(), flags=re.M):
        D.add(m.group(1))
allD = set()
for f in glob.glob(BASE + '장v2/*.md'):
    allD |= set(re.findall(r'\{\{(D:[^}]+)\}\}', open(f, encoding='utf-8').read()))
print('D heads', len(D), 'D tokens used', len(allD), 'undefined D', sorted(allD - D))
for fn in sys.argv[1:]:
    bad = collections.defaultdict(list)
    kindbad = []
    for ln, line in enumerate(open(BASE + fn, encoding='utf-8'), 1):
        for m in re.finditer(r'\{\{([^}]+)\}\}', line):
            lab = m.group(1)
            if lab.startswith('D:'):
                if lab not in D: bad[lab].append(ln)
            elif lab not in live: bad[lab].append(ln)
            else:
                # 라벨 앞의 종류 낱말이 머리의 종류와 같은지
                pre = line[max(0, m.start() - 12):m.start()]
                km = re.search(r'(따름정리|보조정리|정리|명제|정의) `?$', pre)
                if km and km.group(1) != kinds[lab]:
                    kindbad.append((ln, lab, km.group(1), kinds[lab]))
    print('==', fn, 'dead labels:', len(bad))
    for lab, lns in sorted(bad.items()): print('  ', lab, lns[:12])
    print('  kind mismatches:', len(kindbad))
    for x in kindbad: print('  ', x)
