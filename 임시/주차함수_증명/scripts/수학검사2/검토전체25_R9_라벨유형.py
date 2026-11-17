# 검토전체25 R9: 장9.md가 라벨 앞에 적은 유형 낱말(정리·명제·…)이 그 라벨의 머리 유형과 같은지 대조(자리 찾기용)
import re, glob, io
heads = {}
for f in glob.glob('장v2/*.md'):
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}', line)
        if m: heads[m.group(2)] = m.group(1)
txt = io.open('장v2/장9.md', encoding='utf-8').read()
bad = 0; n = 0
for ln, line in enumerate(txt.split('\n'), 1):
    for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의|부록 D\.) ?((?:\{\{[^}]+\}\}(?:\([^)]{1,12}\))*(?:·|, )?)+)', line):
        typ = m.group(1)
        for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
            n += 1
            if lab.startswith('D:'): continue
            if lab not in heads: print('머리 없음', ln, lab); bad += 1
            elif heads[lab] != typ: print('유형 불일치', ln, typ, lab, heads[lab]); bad += 1
    for m in re.finditer(r'\{\{([^}]+)\}\}', line):
        pre = line[:m.start()]
        if not re.search(r'(정리|명제|보조정리|따름정리|정의|부록 D\.) ?(?:\{\{[^}]+\}\}(?:\([^)]{1,12}\))*(?:·|, )?)*$', pre):
            print('유형 낱말 없이 쓰인 라벨', ln, m.group(1), '…'+pre[-25:])
print('검사한 라벨', n, '어긋남', bad)
