# 부록 C 둘째 표(기록의 이름 ↔ 이 글의 진술·이름)를 장 파일의 진술 머리 괄호와 맞댄다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
names = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9']
heads = {}
for n in names:
    for i, l in enumerate(open(base+n+'.md', encoding='utf-8').read().split('\n')):
        m = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(.*?)\.\*\*', l)
        if not m: continue
        kind, lab, rest = m.groups()
        rest = rest.strip()
        # 괄호(제목; 기록 이름) 와 대괄호 표지를 가른다: 표지는 마지막 ' [' 뒤
        k = rest.rfind(' [')
        if rest.startswith('['): paren, mark = '', rest
        elif k >= 0: paren, mark = rest[:k].strip(), rest[k+1:]
        else: paren, mark = rest, ''
        if paren.startswith('(') and paren.endswith(')'): paren = paren[1:-1]
        heads[lab] = (n, i+1, kind, paren, mark)
C = open(base+'부록C.md', encoding='utf-8').read().split('\n')
a = next(i for i,l in enumerate(C) if l.startswith('### 기록이 결과에'))
b = next(i for i,l in enumerate(C) if l.startswith('### 기록의 글자와'))
seen = set(); nrow = 0
for i in range(a, b):
    l = C[i]
    if not l.startswith('| ') or l.startswith('| 기록의 이름') or l.startswith('|---'): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    if len(cells) != 3: print(f'[C {i+1}] 칸 수 {len(cells)}'); continue
    nrow += 1
    rec, stmt, title = cells
    m = re.match(r'^(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}$', stmt)
    if not m: print(f'[C {i+1}] 진술 칸 꼴 다름: {stmt}'); continue
    kind, lab = m.groups()
    if lab in seen: print(f'[C {i+1}] 라벨 중복 {lab}')
    seen.add(lab)
    if lab not in heads: print(f'[C {i+1}] 라벨 없음 {lab}'); continue
    n, ln, hk, paren, mark = heads[lab]
    if hk != kind: print(f'[C {i+1}] 유형 다름 {lab}: 표 {kind} / 본문 {hk} ({n}:{ln})')
    if ';' in paren:
        ht, hr = paren.split(';', 1); ht = ht.strip(); hr = hr.strip()
    else:
        ht, hr = paren.strip(), ''
    if ht != title: print(f'[C {i+1}] 이름 다름 {lab} ({n}:{ln}):\n     표  : {title}\n     본문: {ht}')
    if hr != rec: print(f'[C {i+1}] 기록의 이름 다름 {lab} ({n}:{ln}):\n     표  : {rec}\n     본문: {hr}')
print('표 행 수', nrow)
print('== 머리 괄호에 「기록 [」이 있으나 표에 없는 진술')
for lab, (n, ln, hk, paren, mark) in heads.items():
    if '기록 [' in paren and lab not in seen: print('  ', lab, n, ln, '|', paren[:150])
# 표의 순서가 본문 순서인가
order = [l for l in heads]
idx = [order.index(l) for l in seen if l in heads]
