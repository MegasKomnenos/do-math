# -*- coding: utf-8 -*-
"""라벨들의 인용 자리를 문맥과 함께 출력한다. 사용: python -I 심사_X6_cites.py 라벨 [라벨...]"""
import sys, json, os, re
ROOT = r"C:\math\임시\주차함수_증명"
g = json.load(open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_graph.json'), encoding='utf-8'))
by = {s['label']: s for s in g['statements']}
def ctx(f, n, lab, w=110):
    l = open(os.path.join(ROOT, '장v2', f), encoding='utf-8').read().split('\n')[n-1]
    i = l.find('{{'+lab+'}}')
    return l[max(0, i-w):i+len(lab)+4+w].replace('\n', ' ')
for lab in sys.argv[1:]:
    s = by.get(lab)
    print('#####', lab, s['kind'] if s else '?', s['name'][:40] if s else '', f"{s['file']}:{s['line']}" if s else '')
    for site in g['cited_anywhere'].get(lab, []):
        f, n = site.split(':'); n = int(n)
        # 어느 진술의 본문 안인가
        host = [t['label'] for t in g['statements'] if t['file'] == f and t['line'] <= n <= t['body_end']]
        host += [t['label'] for t in g['statements'] for d in t['deferred'] if d[0] == f and d[1] <= n <= d[2]]
        print(f'  {site} [host={host}]', ctx(f, n, lab))
