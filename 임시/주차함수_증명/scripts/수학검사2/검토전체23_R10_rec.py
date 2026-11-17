# -*- coding: utf-8 -*-
# 기록 exposition.md의 지정 행을 낸다. 사용: rec.py <records> id:line[-line][:file] ...
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = sys.argv[1]
W = int(os.environ.get('W', '330'))
for a in sys.argv[2:]:
    parts = a.split(':')
    rid = parts[0]; rng = parts[1]; fn = parts[2] if len(parts) > 2 else 'exposition.md'
    d = glob.glob(os.path.join(R, rid + '*'))[0]
    p = os.path.join(d, fn)
    L = open(p, encoding='utf-8').read().split('\n')
    lo, hi = (rng.split('-') + [rng])[:2] if '-' in rng else (rng, rng)
    for i in range(int(lo), int(hi) + 1):
        print('[%s %s L%d] %s' % (rid, fn, i, L[i-1][:W]))
