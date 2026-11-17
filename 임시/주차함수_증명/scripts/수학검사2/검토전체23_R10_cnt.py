# -*- coding: utf-8 -*-
# 낱말의 파일별 등장 수(장 파일·부록 D·부록 A/B/C). 사용: cnt.py <base> 낱말...
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록A','부록B','부록C'] + [os.path.basename(f)[:-3] for f in sorted(glob.glob(os.path.join(base, '장v2', '부록D_장*.md')))]
T = {fn: open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read() for fn in files}
for t in sys.argv[2:]:
    out = []
    for fn in files:
        c = T[fn].count(t)
        if c: out.append('%s:%d' % (fn.replace('부록D_장', 'D'), c))
    print('%s => %s' % (t, ' '.join(out) if out else '없음'))
