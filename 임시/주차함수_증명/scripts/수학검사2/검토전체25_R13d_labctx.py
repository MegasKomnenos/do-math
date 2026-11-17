# -*- coding: utf-8 -*-
# 장부 359-688행이 부르는 라벨마다 현행 머리(종류·이름·절·번호)와 장부의 앞뒤 문맥을 나란히 낸다(눈으로 대조하는 용도).
import json, re, io, os, sys
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
heads = json.load(io.open(os.path.join(base, 'scripts', '수학검사2', '검토전체25_R13_heads.json'), encoding='utf-8'))
labs = {h['ch'] + ':' + h['lab']: h for h in heads}
lines = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a - 1, b):
    ln = lines[i]
    for m in re.finditer(r'\{\{([^}]+)\}\}', ln):
        lab = m.group(1)
        if lab.startswith('D:'): continue
        h = labs[lab]
        out.write('%d {{%s}} = %s %s | 이름: %s | 절 %s | %s:%d\n      장부: …%s…\n' % (i + 1, lab, h['kind'], h['num'], h['name'], h['sec'], h['file'], h['line'], ln[max(0, m.start() - 70):m.end() + 90]))
