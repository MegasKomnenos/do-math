# 장9의 라벨 인용이 존재하는지, 머리의 의존 목록 유형 낱말이 실제 진술 유형과 맞는지 센다.
import re, glob, io
heads = {}
for f in glob.glob('장v2/*.md'):
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의|관찰|가정) \{\{([^}]+)\}\}', line)
        if m: heads[m.group(2)] = m.group(1)
        for m2 in re.finditer(r'^### D\.\{\{([^}]+)\}\}', line):
            heads[m2.group(1)] = 'D'
txt = io.open('장v2/장9.md', encoding='utf-8').read()
refs = set(re.findall(r'\{\{([^}]+)\}\}', txt))
missing = [r for r in refs if r not in heads]
print("missing labels:", missing)
# dependency lists
for line in txt.split('\n'):
    m = re.match(r'\*\*(정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}.*?\[(.*?)\]\.\*\*', line)
    if not m: continue
    lab, bracket = m.group(2), m.group(3)
    dm = re.search(r'((?:(?:정리|명제|보조정리|따름정리) \{\{[^}]+\}\}(?:·\{\{[^}]+\}\})*(?:·)?)+)에 의존', bracket)
    if not dm: continue
    deplist = dm.group(1)
    cur = None
    for tok in re.finditer(r'(정리|명제|보조정리|따름정리)|\{\{([^}]+)\}\}', deplist):
        if tok.group(1): cur = tok.group(1)
        else:
            l = tok.group(2); actual = heads.get(l)
            if actual != cur: print(f"TYPE MISMATCH in {lab}: {l} written as {cur}, actual {actual}")
print("checked heads:", sum(1 for line in txt.split('\n') if re.match(r'\*\*(정리|명제|보조정리|따름정리) \{\{', line)))
# ch9 heads with their status strings, for review
for line in txt.split('\n'):
    m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(.*?)\*\*', line)
    if m: print(m.group(1), m.group(2), '|', re.sub(r'\$[^$]*\$','$',m.group(3))[:230])
