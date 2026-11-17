# -*- coding: utf-8 -*-
"""라벨(부분 문자열)로 heads.json 항목을 보여 준다."""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
heads = json.load(open(os.path.join(here, '검토전체22_R13_heads.json'), encoding='utf-8'))
for q in sys.argv[1:]:
    for h in heads:
        if h.get('proof'): continue
        if q == h['label'] or (q.endswith('*') and h['label'].startswith(q[:-1])):
            print('%s | %s | %s절 | %s:%d | %s | %s | [%s]' % (h['label'], h['kind'], h['sec'], h['file'], h['line'], h['num'], h['name'], h['status']))
