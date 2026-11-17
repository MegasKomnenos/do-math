# -*- coding: utf-8 -*-
# 장 파일에서 한글 낱말 뒤 괄호 안에 영어 낱말을 적은 자리(영어 병기 후보)를 낸다.
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
pat = re.compile(r'[가-힣」][ ]?\(([A-Za-z][A-Za-z \-–]{3,60})[\);,]')
for fn in files:
    sec = ''
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        l2 = re.sub(r'\$[^$]*\$', '§', line)
        for mm in pat.finditer(l2):
            print(fn, 'L%d' % i, sec, '|', l2[max(0, mm.start()-30):mm.end()+10])
