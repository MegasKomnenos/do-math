# 검토전체25 R4: 장5B가 부르는 라벨의 유형 낱말이 정의 머리의 유형과 같은지 본다(자리 찾기용)
import re, glob, io
heads = {}
for f in glob.glob('장v2/*.md'):
    for ln in io.open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|정의|보조정리|따름정리|명제) \{\{([0-9A-Z]+:[^}]+)\}\}', ln)
        if m: heads[m.group(2)] = (m.group(1), f)
txt = io.open('장v2/장5B.md', encoding='utf-8').read()
bad = 0; seen = set()
for m in re.finditer(r'(정리|정의|보조정리|따름정리|명제) ((?:\{\{[^}]+\}\}(?:\([가-힣ㄱ-ㅎ]\))*[·]?)+)', txt):
    typ = m.group(1)
    for lab in re.findall(r'\{\{([^}]+)\}\}', m.group(2)):
        seen.add(lab)
        if lab not in heads: print('NO HEAD', lab); bad += 1
        elif heads[lab][0] != typ:
            print('TYPE MISMATCH', typ, lab, heads[lab]); bad += 1
alll = set(re.findall(r'\{\{([^}]+)\}\}', txt))
print('labels in 5B:', len(alll), 'checked with type word:', len(seen), 'unchecked:', sorted(alll-seen), 'bad:', bad)
