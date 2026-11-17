# 장7A의 인용 자리마다 라벨 앞의 유형 낱말(가운뎃점 연쇄는 앞 낱말을 물려받음)이 정의 머리의 유형과 같은지 본다.
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
kinds = {}
for f in sorted(glob.glob('장v2/*.md')):
    for line in open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|보조정리|명제|따름정리|정의)\s*\{\{([^}]+)\}\}(?!의 증명)', line)
        if m: kinds.setdefault(m.group(2), m.group(1))
src = open('장v2/장7A.md', encoding='utf-8').read().split('\n')
bad = 0; tot = 0
for ln, line in enumerate(src, 1):
    for m in re.finditer(r'(정리|보조정리|명제|따름정리|정의)\s*((?:\{\{[^}]+\}\}(?:\([가-힣ㄱ-ㅎ]\))*(?:·|, )?)+)', line):
        kind = m.group(1)
        if kind == '정리' and line[max(0, m.start() - 2):m.start()] in ('보조', '따름'):
            continue
        for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
            if lab.startswith('D:'): continue
            tot += 1
            if kinds.get(lab) != kind:
                bad += 1; print(ln, kind, lab, '->', kinds.get(lab))
# 유형 낱말 없이 나온 라벨
for ln, line in enumerate(src, 1):
    for m in re.finditer(r'\{\{([^}]+)\}\}', line):
        pre = line[max(0, m.start() - 40):m.start()]
        if not re.search(r'(정리|보조정리|명제|따름정리|정의|D\.)\s*((\{\{[^}]+\}\}(\([가-힣ㄱ-ㅎ]\))*(·|, )?)*)$', pre):
            print('유형 없음:', ln, pre[-30:], m.group(0))
print('checked', tot, 'mismatch', bad)
