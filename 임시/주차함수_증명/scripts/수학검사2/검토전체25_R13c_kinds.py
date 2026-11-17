# -*- coding: utf-8 -*-
"""R13c 검산: 장부 332-357행에서 「종류 `{{라벨}}`(·`{{라벨}}`…)」 꼴로 적힌 진술의 종류(정리·보조정리·명제·따름정리·정의)가
현행 머리(검토전체25_R13_heads.json)와 맞는지, 그리고 「N.M `{{라벨}}`」 꼴의 절 번호가 맞는지 후보를 뽑는다.
후보는 사람이 그 행 원문을 열어 확인한다. 읽기 전용."""
import io, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
H = json.load(io.open('scripts/수학검사2/검토전체25_R13_heads.json', encoding='utf-8'))
d = {'%s:%s' % (h['ch'], h['lab']): h for h in H}
L = io.open('장부_v2.md', encoding='utf-8').read().split('\n')
kinds = '정리|보조정리|명제|따름정리|정의'
pat = re.compile(r'(?<![가-힣])(%s) ((?:`\{\{[0-9]+:[^}]+\}\}`(?:\([^)]{1,12}\))?(?:[·–]|, )?)+)' % kinds)
lab = re.compile(r'\{\{([0-9]+:[^}]+)\}\}')
secpat = re.compile(r'(\d+\.\d+) ((?:`\{\{[0-9]+:[^}]+\}\}`(?:[·–]|, )?)+)')
for i in range(332, 358):
    s = L[i - 1]
    for m in pat.finditer(s):
        k = m.group(1)
        for x in lab.findall(m.group(2)):
            h = d.get(x)
            if h is None:
                print('L%d 죽은 라벨 %s' % (i, x))
            elif h['kind'] != k:
                p = m.start()
                print('L%d 종류 후보: 장부 「%s」 / 머리 「%s」 %s  ...%s...' % (i, k, h['kind'], x, s[max(0, p - 30):p + 110]))
    for m in secpat.finditer(s):
        sec = m.group(1)
        for x in lab.findall(m.group(2)):
            h = d.get(x)
            if h is not None and h['sec'] != sec:
                p = m.start()
                print('L%d 절 후보: 장부 「%s」 / 머리 절 「%s」 %s ...%s...' % (i, sec, h['sec'], x, s[max(0, p - 30):p + 110]))
