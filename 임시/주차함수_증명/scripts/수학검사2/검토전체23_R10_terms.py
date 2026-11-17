# -*- coding: utf-8 -*-
# 부록 B의 기록 폴더(.md 전부; review 포함)에서 낱말의 등장 기록 수와 예를 센다. 사용: terms.py <base> <records> 낱말...
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]; R = sys.argv[2]
folders = re.findall(r'`(r[0-9a-f]{32})`', open(os.path.join(base, '장v2', '부록B.md'), encoding='utf-8').read())
texts = {}
for f in folders:
    acc = []
    for dp, dn, fns in os.walk(os.path.join(R, f)):
        for fn in fns:
            if fn.endswith('.md'):
                try: acc.append((os.path.relpath(os.path.join(dp, fn), os.path.join(R, f)), open(os.path.join(dp, fn), encoding='utf-8').read()))
                except Exception as e: pass
    texts[f[:8]] = acc
for t in sys.argv[3:]:
    hits = []; ex = None; expo = 0
    for rid, acc in texts.items():
        found = False
        for rel, s in acc:
            j = s.find(t)
            if j >= 0:
                found = True
                if rel == 'exposition.md': expo += 1
                if ex is None: ex = (rid, rel, s[max(0, j-40):j+len(t)+40].replace('\n', ' '))
        if found: hits.append(rid)
    print('%s: 기록 %d개(exposition %d) %s | 예: %s' % (t, len(hits), expo, hits[:6], ex))
