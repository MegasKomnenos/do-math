# 장1·장2가 인용하는 라벨 {{X:label}}이 대상 장 파일에 진술 머리로 존재하는지, 진술 유형(정리/명제/보조정리/따름정리/정의)이 맞는지 확인
import re, glob, os
root = r'C:\math\임시\주차함수_증명\장v2'
files = {}
for p in glob.glob(os.path.join(root, '*.md')):
    files[os.path.basename(p)] = open(p, encoding='utf-8').read()
# 라벨 정의: "**유형 {{X:label}}" 꼴
defs = {}
for fn, txt in files.items():
    for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의|문제|관찰|가정)\s+\{\{([^}]+)\}\}', txt):
        defs.setdefault(m.group(2), []).append((m.group(1), fn))
# 부록 D 항목 라벨 "D.{{D:...}}" 정의는 부록D 파일에서 찾는다
ddefs = set()
for fn, txt in files.items():
    if fn.startswith('부록D'):
        for m in re.finditer(r'\{\{(D:[^}]+)\}\}', txt):
            ddefs.add(m.group(1))
for target in ['장1.md', '장2.md']:
    txt = files[target]
    print('====', target)
    seen = set()
    for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의|문제)?\s*\{\{([^}]+)\}\}', txt):
        typ, lab = m.group(1), m.group(2)
        if lab.startswith('D:'):
            if lab not in ddefs: print('부록D 라벨 없음:', lab)
            continue
        if lab not in defs:
            print('정의 없음:', lab, '(인용 유형', typ, ')'); continue
        dtyp = defs[lab][0][0]
        if typ and typ != dtyp:
            # 문맥 출력
            s = max(0, m.start()-40); print('유형 불일치:', lab, '인용', typ, '정의', defs[lab], '| 문맥:', txt[s:m.end()].replace('\n',' '))
    # 요약: 인용된 라벨 수
    labs = set(l for _, l in re.findall(r'(정리|명제|보조정리|따름정리|정의|문제)?\s*\{\{([^}]+)\}\}', txt))
    print('인용 라벨 수', len(labs))
