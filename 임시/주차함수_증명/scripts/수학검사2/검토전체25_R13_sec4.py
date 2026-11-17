# -*- coding: utf-8 -*-
import re, sys, io, os, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명'
heads = json.load(io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_heads.json'), encoding='utf-8'))
hl = {h['ch'] + ':' + h['lab']: h for h in heads}
L = io.open(os.path.join(base, '장부_v2.md'), encoding='utf-8').read().split('\n')
rows = []
for i in range(693, 1184):
    l = L[i]
    if l.startswith('| ') and not l.startswith('|---'):
        c = [x.strip() for x in l.strip().strip('|').split(' | ')]
        # 빈 칸 처리: ' |  | ' 는 split(' | ')로 빈 문자열이 된다
        c = [x.strip() for x in re.split(r'\s\|\s?', l.strip()[2:-1].strip() + ' ')]
        rows.append((i + 1, c, l))
print('rows', len(rows), collections.Counter(len(c) for i, c, l in rows))
live = []; other = []
for i, c, l in rows:
    m = re.fullmatch(r'\{\{([0-9]+):([^}]+)\}\}', c[-1]) if c else None
    if m:
        live.append((i, c, m.group(1) + ':' + m.group(2)))
    else:
        other.append((i, c, l))
print('live', len(live), 'other', len(other))
seen = collections.Counter(k for i, c, k in live)
print('dup live labels', [k for k, v in seen.items() if v > 1])
print('heads not in §4', [k for k in hl if k not in seen])
print('§4 live not in heads', [(i, k) for i, c, k in live if k not in hl])
order = [k for i, c, k in live]
print('order equals head order', order == [h['ch'] + ':' + h['lab'] for h in heads])
for i, c, k in live:
    if k not in hl: continue
    h = hl[k]
    d = []
    if c[1] != h['kind']: d.append('kind %s/%s' % (c[1], h['kind']))
    if c[4] != h['sec']: d.append('sec %s/%s' % (c[4], h['sec']))
    nm = h['name'] or ''
    # 머리 괄호 = 이 글의 이름[; 기록 …]
    parts = nm.split('; ', 1)
    own = parts[0] if not parts[0].startswith('기록 [') else ''
    rec = parts[1] if len(parts) > 1 else (parts[0] if parts[0].startswith('기록 [') else '')
    if c[2] != own: d.append('own T[%s] C[%s]' % (c[2], own))
    if c[3] != rec: d.append('rec T[%s] C[%s]' % (c[3], rec))
    if d: print(i, k, ' || '.join(d))
# 첫 판 번호 열: 중복·순서
fp = collections.Counter(c[0] for i, c, k in live if c[0] != '—')
print('dup first-ed numbers among live', [k for k, v in fp.items() if v > 1])
fpall = collections.Counter(c[0] for i, c, l in rows if re.fullmatch(r'[0-9]+\.[0-9]+', c[0]))
print('dup first-ed numbers among all', [k for k, v in fpall.items() if v > 1])
json.dump([(i, c) for i, c, l in other], io.open(os.path.join(base, 'scripts/수학검사2/검토전체25_R13_sec4_other.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0)
print(collections.Counter(c[-1][:12] for i, c, l in other).most_common(12))
