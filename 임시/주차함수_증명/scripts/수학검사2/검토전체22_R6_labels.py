# 장7A가 인용하는 라벨의 정의 머리를 찾아 적는다(자리 찾기 용도).
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('장v2/장7A.md', encoding='utf-8').read()
labels = sorted(set(re.findall(r'\{\{([0-9A-Z]+:[^}]+)\}\}', src)))
heads = {}
for f in sorted(glob.glob('장v2/*.md')):
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'\*\*(정리|보조정리|명제|따름정리|정의|주 정리|관찰|예)\s*\{\{([^}]+)\}\}(.*?)\*\*', line)
        if m:
            heads.setdefault(m.group(2), []).append((f, i, m.group(1), m.group(3)[:230]))
        m = re.match(r'#+\s*D\.\{\{([^}]+)\}\}(.*)', line)
        if m:
            heads.setdefault(m.group(1), []).append((f, i, 'D', m.group(2)[:120]))
for l in labels:
    print(l, '->', heads.get(l, 'NOT FOUND'))
