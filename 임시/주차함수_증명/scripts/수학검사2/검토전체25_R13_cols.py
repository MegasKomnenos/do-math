# -*- coding: utf-8 -*-
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
LAB = re.compile(r'\{\{([0-9]+[A-Za-z]?|D):([^}]+)\}\}')
t10 = io.open(os.path.join(base, '장v2/장10.md'), encoding='utf-8').read().split('\n')
dmap, lit = {}, {}
sec = None
for line in t10:
    if line.startswith('### '): sec = line.split()[1]
    if not line.startswith('| ') or line.startswith('|---'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if sec == '10.2' and c[0].startswith('부록 D.'):
        d = LAB.findall(c[0])[0][1]
        for a, b in LAB.findall(c[1]):
            if a != 'D': dmap.setdefault(a + ':' + b, []).append((d, c[2]))
    if sec == '10.3' and len(c) == 3 and c[0] != '문헌':
        au = c[0].split(', *')[0]
        for a, b in LAB.findall(c[2]):
            if a != 'D': lit.setdefault(a + ':' + b, []).append((au, c[1]))
L = io.open(os.path.join(base, '의존지도_v2.md'), encoding='utf-8').read().split('\n')
n = 0
for i, line in enumerate(L[:283], 1):
    if not line.startswith('| `{{'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    k = c[0].strip('`{}')
    # 부록 D
    td = [(b) for a, b in LAB.findall(c[8]) if a == 'D']
    cd = [d for d, g in dmap.get(k, [])]
    if sorted(td) != sorted(cd):
        n += 1; print(i, k, 'D: T', td, 'C', cd)
    for d, g in dmap.get(k, []):
        if ('{{D:%s}}(%s)' % (d, g)) not in c[8]:
            print(i, k, 'D grade text differs:', d, g, '|', c[8][:200])
    if not dmap.get(k) and c[8] != '없음': print(i, k, 'D cell', c[8])
    # 문헌
    tl = lit.get(k, [])
    if not tl:
        if c[7] != '—': print(i, k, 'lit cell but none in 10.3:', c[7][:150])
    else:
        for au, res in tl:
            if au not in c[7]:
                print(i, k, 'lit missing in table:', au)
            if res not in c[7]:
                print(i, k, 'lit result text differs:', au, '|', res[:80])
        cnt = c[7].count(');') + 1
        if cnt != len(tl): print(i, k, 'lit count T', cnt, 'C', len(tl), [a for a, r in tl], '|', c[7][:300])
print('done', n, 'statements with D:', len(dmap), 'with lit:', len(lit))
