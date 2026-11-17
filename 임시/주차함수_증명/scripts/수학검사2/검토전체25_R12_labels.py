# -*- coding: utf-8 -*-
"""R12: 부록 D(7A,7B,8,9)가 쓰는 라벨이 장 파일에 진술 머리(또는 부록 D 항목 머리)로 있는지, 붙은 유형 낱말이 머리의 유형과 같은지 본다."""
import re, os, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r'C:\math\임시\주차함수_증명\장v2'
heads = {}
for f in glob.glob(os.path.join(B, '*.md')):
    for line in open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{([0-9A-Z]+:[^}]+)\}\}', line)
        if m: heads[m.group(2)] = (m.group(1), os.path.basename(f))
        m = re.match(r'### D\.\{\{(D:[^}]+)\}\}', line)
        if m: heads[m.group(1)] = ('부록 D', os.path.basename(f))
for fn in ['부록D_장7A.md', '부록D_장7B.md', '부록D_장8.md', '부록D_장9.md']:
    txt = open(os.path.join(B, fn), encoding='utf-8').read()
    print('==', fn)
    seen = set()
    # typed references: "<유형> {{a}}·{{b}}" chains
    for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의|부록 D\.|D\.)\s?((?:\{\{[^}]+\}\}(?:\([^)]*\))?[·]?)+)', txt):
        typ = m.group(1)
        for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
            if lab not in heads:
                print('  MISSING', lab); continue
            ht = heads[lab][0]
            t = '부록 D' if typ in ('부록 D.', 'D.') else typ
            if ht != t and (lab, t) not in seen:
                seen.add((lab, t)); print('  TYPE?', lab, '쓰인 유형:', t, '머리 유형:', ht, '|', txt[max(0, m.start()-30):m.end()+10].replace('\n', ' '))
    for lab in set(re.findall(r'\{\{([^}]+)\}\}', txt)):
        if lab not in heads: print('  UNDEFINED LABEL', lab)
