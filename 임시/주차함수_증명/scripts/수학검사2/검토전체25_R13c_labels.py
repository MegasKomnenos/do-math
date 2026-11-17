# -*- coding: utf-8 -*-
"""R13c 검산: 장부_v2.md 332-357행이 드는 라벨({{장:이름}}, `장:이름`, D.이름)이
현행 진술 머리(검토전체25_R13_heads.json)와 부록 D 항목 머리에 살아 있는지 본다. 읽기 전용."""
import io, sys, json, re, glob
sys.stdout.reconfigure(encoding='utf-8')
H = json.load(io.open('scripts/수학검사2/검토전체25_R13_heads.json', encoding='utf-8'))
labels = set('%s:%s' % (h['ch'], h['lab']) for h in H)
dl = set()
for f in glob.glob('장v2/부록D_*.md'):
    for m in re.finditer(r'^### D\.\{\{(D:[^}]+)\}\}', io.open(f, encoding='utf-8').read(), re.M):
        dl.add(m.group(1))
print('heads', len(labels), 'D items', len(dl))
L = io.open('장부_v2.md', encoding='utf-8').read().split('\n')
for i in range(332, 358):
    s = L[i - 1]
    for m in sorted(set(re.findall(r'\{\{([0-9D]+:[^}]+)\}\}', s))):
        if m not in labels and m not in dl:
            print('L%d 죽은 라벨(중괄호) %s' % (i, m))
    for m in sorted(set(re.findall(r'`([0-9]+:[A-Za-z0-9\-]+)`', s))):
        if m not in labels:
            print('L%d 죽은 라벨(백틱 맨꼴) %s' % (i, m))
    for m in sorted(set(re.findall(r'D\.([A-Za-z][A-Za-z0-9\-]+)', s))):
        if 'D:' + m not in dl:
            print('L%d 살아 있지 않은 D 이름(맨꼴) D.%s' % (i, m))
