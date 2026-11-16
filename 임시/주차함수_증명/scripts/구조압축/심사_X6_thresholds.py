# -*- coding: utf-8 -*-
"""심사 X6 — 행·열 문턱 수의 출현 자리를 모은다.
출력: 심사_X6_thresholds.txt — 문턱마다 (장 파일, 행, 머리/증명/산문 구분, 숙주 진술, 발췌)
또한 부등호 뒤에 붙은 4자리 이상 정수를 전수 수집해 후보 문턱 목록을 만든다.
"""
import re, json, os, sys
from collections import defaultdict, Counter
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, '장v2')
g = json.load(open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_graph.json'), encoding='utf-8'))
stmts = g['statements']
num = {}
cnt = {}
for s in stmts:
    ch = s['label'].split(':')[0]
    if ch == 'D': continue
    cnt[ch] = cnt.get(ch, 0) + 1
    num[s['label']] = f"{ch}.{cnt[ch]}"
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
def host_of(f, n):
    for t in stmts:
        if t['file'] == f and t['line'] <= n <= t['body_end']:
            return t['label'], ('머리' if n == t['line'] else '증명/진술')
        for d in t['deferred']:
            if d[0] == f and d[1] <= n <= d[2]:
                return t['label'], '미룬 증명'
    return None, '산문'
# 후보 문턱: 부등호 뒤 정수
INEQ = re.compile(r'(\\ge|\\geq|\\le|\\leq|<|>|\\in\[|\[|,)\s*(\d{3,6})(?![\d.])')
cand = Counter()
where = defaultdict(list)
for f in FILES:
    lines = open(os.path.join(CH, f), encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines):
        for m in INEQ.finditer(l):
            v = int(m.group(2))
            if v >= 100:
                cand[v] += 1
                where[v].append((f, i+1))
THRESH = [10001, 20001, 50001, 2001, 2000, 3131, 3132, 3130, 4000, 6600, 6666, 6667, 6668, 841, 840, 500, 501, 1000, 1001, 30000, 25000, 25001, 170, 700, 701, 249, 250, 103, 102, 1130, 2200, 6934]
out = []
out.append('# 부등호 뒤 정수(100 이상) 빈도 — 상위 60')
for v, c in cand.most_common(60):
    fs = Counter(f for f, _ in where[v])
    out.append(f'{v}\t{c}\t' + ' '.join(f'{k}:{n}' for k, n in sorted(fs.items())))
out.append('')
for T in THRESH:
    pat = re.compile(r'(?<![\d.])' + str(T) + r'(?![\d])')
    out.append(f'===== {T}')
    rows = []
    for f in FILES:
        lines = open(os.path.join(CH, f), encoding='utf-8').read().split('\n')
        for i, l in enumerate(lines):
            if pat.search(l):
                h, kind = host_of(f, i+1)
                m = pat.search(l)
                a = max(0, m.start()-90); b = min(len(l), m.end()+60)
                rows.append((f, i+1, kind, (num.get(h, '') + ' ' + h) if h else '-', l[a:b].replace('\n', ' ')))
    heads = [r for r in rows if r[2] == '머리']
    out.append(f'총 {len(rows)}줄; 머리 {len(heads)}개')
    for r in heads:
        out.append(f'  [머리] {r[0]}:{r[1]} {r[3]} | {r[4]}')
    for r in rows:
        if r[2] != '머리':
            out.append(f'  [{r[2]}] {r[0]}:{r[1]} {r[3]} | {r[4]}')
open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_thresholds.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:62]))
