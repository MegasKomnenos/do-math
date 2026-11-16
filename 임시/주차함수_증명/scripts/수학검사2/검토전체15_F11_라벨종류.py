# -*- coding: utf-8 -*-
"""F11: 장11.md가 인용한 라벨의 종류(정리/명제/…)와 절 위치를 장 파일의 진술 머리와 대조한다."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = {}
for l in open(ROOT + r'\대조v2\수학검사2\_F11_heads.tsv', encoding='utf-8'):
    f, ln, sec, kind, ch, lab, rest = l.rstrip('\n').split('\t')
    heads.setdefault((ch, lab), []).append((f, ln, sec, kind, rest))
txt = open(ROOT + r'\장v2\장11.md', encoding='utf-8').read()
# 11.3 표 행에서 각 진술의 '놓인 곳' 열도 대조 (11.2 표)
for ln, line in enumerate(txt.split('\n'), 1):
    # 종류 + 라벨 (가운뎃점 묶음 포함): 종류 뒤 첫 라벨만 직접, 묶음 뒤 라벨은 같은 종류
    for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의) (\{\{(\w+):([^}]+)\}\}(?:·\{\{(\w+):([^}]+)\}\})*)', line):
        kind = m.group(1)
        for ch, lab in re.findall(r'\{\{(\w+):([^}]+)\}\}', m.group(2)):
            h = heads.get((ch, lab))
            if not h:
                print(f'행{ln}: 머리 없음 {kind} {{{{{ch}:{lab}}}}}')
            else:
                kinds = {x[3] for x in h}
                if kind not in kinds:
                    print(f'행{ln}: 종류 불일치 — 장11: {kind} {{{{{ch}:{lab}}}}} / 실제: {kinds} ({h[0][0]} {h[0][1]}행)')
                if len(h) > 1:
                    print(f'행{ln}: 머리 중복 {{{{{ch}:{lab}}}}} {[(x[0],x[1]) for x in h]}')
# 11.2 표의 '놓인 곳' 열 대조
for line in txt.split('\n'):
    if not line.startswith('| 부록 D.{{D:'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    labs = re.findall(r'\{\{(\w+):([^}]+)\}\}', cells[1])
    secs = sorted({heads[(c, l)][0][2] for c, l in labs if (c, l) in heads})
    col = cells[3]
    if set(col.split('·')) != set(secs):
        print(f'[놓인 곳] {cells[0]}: 표 {col} / 실제 {secs}')
# 모든 라벨 참조가 중괄호 짝과 맞는지(깨진 라벨)
for m in re.finditer(r'\{\{([^}]*)\}\}', txt):
    if not re.fullmatch(r'(\w+):[\w\-]+', m.group(1)):
        print('깨진 라벨?', m.group(0))
