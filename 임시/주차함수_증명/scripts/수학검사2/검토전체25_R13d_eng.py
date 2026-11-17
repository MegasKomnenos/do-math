# -*- coding: utf-8 -*-
# 장 파일 본문에서 한글 바로 뒤 괄호 안에 로마자 낱말만 든 자리(영어 병기 후보)를 모은다.
import re, io, glob, os, sys
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in sorted(glob.glob(os.path.join(base, '장v2', '장*.md'))):
    for i, l in enumerate(io.open(f, encoding='utf-8').read().split('\n')):
        l2 = re.sub(r'\$[^$]*\$', '$', l)
        for m in re.finditer(r'([가-힣]+)\(([A-Za-z][A-Za-z \-–]{2,40})\)', l2):
            out.write('%s:%d\t%s(%s)\n' % (os.path.basename(f)[:-3], i + 1, m.group(1), m.group(2)))
