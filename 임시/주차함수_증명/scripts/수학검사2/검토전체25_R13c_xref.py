# -*- coding: utf-8 -*-
"""R13c 검산 보조: 장부 332-357행에서 다른 절·묶음을 가리키는 구절(「N.M 묶음」「N.M 진술」「N.M 전역」「N.M 국소」
「N.M의 $」「N.M절」)을 문맥과 함께 뽑아 사람이 읽고 맞대게 한다. 판정은 하지 않는다. 읽기 전용."""
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
L = io.open('장부_v2.md', encoding='utf-8').read().split('\n')
pat = re.compile(r'(\d+\.\d+(?:\.\d+)?)\s*(묶음|진술|전역|국소|증명 국소|의 \$)')
a = int(sys.argv[1]); b = int(sys.argv[2])
for i in range(a, b + 1):
    s = L[i - 1]
    for m in pat.finditer(s):
        p = m.start()
        print('L%d [%s %s] ...%s...' % (i, m.group(1), m.group(2), s[max(0, p - 70):p + 120]))
