# -*- coding: utf-8 -*-
# 인수 "파일:행" 마다 그 행을 품는(바로 앞의) 진술 머리를 낸다.
import json, io, os, sys
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
heads = json.load(io.open(os.path.join(base, 'scripts', '수학검사2', '검토전체25_R13_heads.json'), encoding='utf-8'))
for a in sys.argv[1:]:
    f, n = a.split(':'); n = int(n)
    best = None
    for h in heads:
        if h['file'] == f and h['line'] <= n:
            if best is None or h['line'] > best['line']: best = h
    out.write('%s -> %s\n' % (a, '%s {{%s:%s}} (%s) 절 %s 번호 %s @%d' % (best['kind'], best['ch'], best['lab'], best['name'], best['sec'], best['num'], best['line']) if best else None))
