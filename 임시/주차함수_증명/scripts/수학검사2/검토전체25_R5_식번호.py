# 검토전체25 R5: 장6 식 번호 순서·참조, 달러 짝, 칼표 자리
import re, io
p = '장v2/장6.md'
s = io.open(p, encoding='utf-8').read()
lines = s.split('\n')
tags = [(i + 1, m.group(1)) for i, l in enumerate(lines) for m in re.finditer(r'[\]tag[{](6[.][0-9]+)[}]', l)]
nums = [int(t.split('.')[1]) for _, t in tags]
print('tags:', len(tags), 'sequential:', nums == list(range(1, len(nums) + 1)), 'last', tags[-1])
refs = set(re.findall(r'\((6\.\d+)\)', s))
tagset = set(t for _, t in tags)
print('refs not tagged:', sorted(refs - tagset, key=lambda x: int(x.split('.')[1])))
print('tags never referenced:', sorted(tagset - set(re.findall(r'(?<!tag\{)\((6\.\d+)\)', s)), key=lambda x: int(x.split('.')[1])))
# other chapter eq refs
print('other eq refs:', sorted(set(re.findall(r'\((\d+\.\d+)\)', s)) - refs))
# dollar parity per line (outside display)
indisp = False
for i, l in enumerate(lines):
    if l.strip() == '$$':
        indisp = not indisp
        continue
    if indisp:
        continue
    t = l.replace('$$', '')
    if t.count('$') % 2:
        print('odd $ at line', i + 1)
print('display balanced:', not indisp)
# brace balance per display/inline quick
for i, l in enumerate(lines):
    if l.count('{') != l.count('}'):
        print('brace mismatch line', i + 1, l.count('{'), l.count('}'))
# daggers
for i, l in enumerate(lines):
    for m in re.finditer('†', l):
        print('dagger line', i + 1, ':', l[max(0, m.start() - 30):m.start() + 50].replace('\n', ' '))
