# -*- coding: utf-8 -*-
# 장7A가 인용하는 라벨마다: 장7A에서 붙인 유형 낱말과, 그 라벨을 머리로 가진 진술의 유형·이름을 나란히 출력한다.
import re, io, glob, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
heads = {}
for f in sorted(glob.glob('장v2/*.md')):
    for ln, line in enumerate(io.open(f, encoding='utf-8'), 1):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의|보기|사실|관찰) \{\{([^}]+)\}\}\s*(\([^\[]*?\))?\s*(\[[^\]]*\])?', line)
        if m:
            heads[m.group(2)] = (m.group(1), (m.group(3) or '')[:90], (m.group(4) or '')[:160], os.path.basename(f), ln)
        m = re.match(r'### D\.\{\{([^}]+)\}\}(.*)', line)
        if m:
            heads[m.group(1)] = ('부록D', m.group(2)[:90], '', f, ln)
txt = io.open('장v2/장7A.md', encoding='utf-8').read().split('\n')
seen = {}
for ln, line in enumerate(txt, 1):
    for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의|부록 D\.)?\s?((?:\{\{[^}]+\}\}[·]?)+)', line):
        kind = m.group(1)
        for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
            seen.setdefault(lab, []).append((ln, kind))
for lab in sorted(seen):
    h = heads.get(lab)
    print(lab, '=>', h)
    print('    uses:', seen[lab])
