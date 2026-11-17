# -*- coding: utf-8 -*-
"""R13c 검산 보조: 장부 1.2(45-287행)에서 첫 칸에 토큰이 든 행의 행 번호·첫 칸 머리·끝 세 칸을 보인다. 읽기 전용.
(셀 쪼개기는 자리를 찾는 용도일 뿐이고, 지적에 쓰는 값은 그 행 원문을 따로 열어 확인한다.)"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
L = io.open('장부_v2.md', encoding='utf-8', newline='').read().split('\n')
for tok in sys.argv[1:]:
    print('==', tok)
    for i in range(45, 288):
        s = L[i - 1]
        cells = s.split(' | ')
        if tok in cells[0]:
            print('  L%d first=%s ... | %s' % (i, cells[0][:160], ' | '.join(c[:140] for c in cells[-4:])))
