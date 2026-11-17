# -*- coding: utf-8 -*-
r"""R13b 검산 보조: 장부_v2.md 289–331행이 `{{장:이름}}`·{{D:이름}} 꼴로 가리키는 라벨이
현행 진술 머리 목록(검토전체25_R13_heads.json)과 부록 D 항목 머리(### D.{{D:이름}})에 살아 있는지 본다.
사용: python -I 검토전체25_R13b_labels.py [시작행=289] [끝행=331]
"""
import io, re, sys, json, glob
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'C:/math/임시/주차함수_증명/'
a = int(sys.argv[1]) if len(sys.argv) > 1 else 289
b = int(sys.argv[2]) if len(sys.argv) > 2 else 331
L = io.open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
H = json.load(io.open(BASE + 'scripts/수학검사2/검토전체25_R13_heads.json', encoding='utf-8'))
live = set('%s:%s' % (h['ch'], h['lab']) for h in H)
dlive = set()
for f in glob.glob(BASE + '장v2/부록D_장*.md'):
    for l in io.open(f, encoding='utf-8').read().split('\n'):
        m = re.match(r'#+ D\.\{\{D:([^}]+)\}\}', l)
        if m:
            dlive.add(m.group(1))
print('산 진술 라벨', len(live), '개, 부록 D 항목', len(dlive), '개')
bad = 0
for i in range(a - 1, b):
    for m in re.finditer(r'\{\{([0-9A-Za-z]+):([^}]+)\}\}', L[i]):
        ch, lab = m.group(1), m.group(2)
        ok = (lab in dlive) if ch == 'D' else ('%s:%s' % (ch, lab) in live)
        if not ok:
            bad += 1
            print('죽은 라벨  장부 %d행  {{%s:%s}}  …%s…' % (i + 1, ch, lab, L[i][max(0, m.start() - 60):m.end() + 40]))
    # 중괄호 없이 적힌 라벨 꼴(`4:hermite-nu` 등)
    for m in re.finditer(r'`([0-9]+):([a-zA-Z0-9-]+)`', L[i]):
        if '%s:%s' % (m.group(1), m.group(2)) not in live:
            bad += 1
            print('죽은 라벨(중괄호 없음)  장부 %d행  %s' % (i + 1, m.group(0)))
print('죽은 라벨 수', bad)
