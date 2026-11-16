# S11: 부록 A·C가 가리키는 라벨의 존재·종류·이름을 진술 머리 색인과 견주고, 11.2절 표의 산술 등급을 진술 머리의 등급과 견준다. 또 두 증명의 폐포 안 계산 진술 전부가 11.3절 계산 열에 있는지 본다.
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
idx = json.load(open('scripts/수학검사2/_S11_idx.json', encoding='utf-8'))
TYPES = '정리|명제|보조정리|따름정리|정의|관찰'
for f in ['장v2/부록A.md', '장v2/부록C.md']:
    print('\n=====', f)
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(' + TYPES + r')\s+`?\{\{(\d+[AB]?:[^}]+)\}\}`?', txt):
        typ, lab = m.group(1), m.group(2)
        e = idx.get(lab)
        if not e: print('  색인 없음:', typ, lab); continue
        if e[0] != typ: print(f'  종류 다름: 부록 {typ} {lab} / 본문 {e[0]} ({e[2]}:{e[3]})')
    for m in re.finditer(r'\{\{(\d+[AB]?:[^}]+)\}\}', txt):
        if m.group(1) not in idx and not m.group(1).startswith('D:'): print('  색인에 없는 라벨:', m.group(1))
# 부록 C 이름 표
print('\n===== 부록 C 「기록이 결과에 붙인 이름」 표: 이 글의 이름 vs 머리 이름')
txt = open('장v2/부록C.md', encoding='utf-8').read()
s = txt.index('### 기록이 결과에 붙인 이름'); e = txt.index('### 기록의 글자와 이 글의 글자')
for line in txt[s:e].split('\n'):
    if line.startswith('| 기록') :
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        if len(cells) < 3: continue
        labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[1])
        for lab in labs:
            e2 = idx.get(lab)
            if not e2: print('  없음', lab); continue
            hm = re.match(r'\(([^;)]*)', e2[4])
            hname = hm.group(1).strip() if hm else ''
            if hname != cells[2]:
                print(f'  이름 다름: {lab} | 부록C「{cells[2]}」 | 머리「{hname}」')
            # 기록 식별자 일치: 기록 [rXXX] in cells[0] vs 머리의 식별자
            ids_c = set(re.findall(r'\[(r[0-9a-f]{7})\]', cells[0]))
            ids_h = set(re.findall(r';\s*([^\]]*)\]', e2[4]))
            idset = set()
            for s2 in ids_h: idset |= set(re.findall(r'r[0-9a-f]{7}', s2))
            if ids_c and not ids_c <= idset:
                print(f'  식별자 불일치: {lab} | 부록C {sorted(ids_c)} | 머리 {sorted(idset)} | 머리: {e2[4][:150]}')
# 11.2 산술 등급 vs 머리 등급
print('\n===== 11.2 표 산술 등급 vs 진술 머리 등급')
for line in open('장v2/장11.md', encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        lab = re.match(r'부록 D\.\{\{D:([^}]+)\}\}', cells[0]).group(1)
        for key in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[1]):
            h = idx[key][4]
            grades = re.findall(r'계산 (?:증거|보조)\(([^)]*)\)', h)
            print(f'  {lab} | {key} | 표: {cells[2]} | 머리: {grades}')
# 폐포 계산 진술 전부 vs 11.3 계산 열
cites = {k: set(v) for k, v in json.load(open('scripts/수학검사2/_S11_citesA.json', encoding='utf-8')).items()}
def closure(root):
    seen=set(); st=[root]
    while st:
        x=st.pop()
        if x in seen or x.startswith('D:'): continue
        seen.add(x); st.extend(cites.get(x, ()))
    return seen
c1 = closure('9:old-7-46'); c2 = closure('10:old-8-37')
comp = {x for x in (c1|c2) if x in idx and '계산' in idx[x][4]}
tab = open('장v2/장11.md', encoding='utf-8').read()
s = tab.index('**공유 입력.**'); e3 = tab.index('### 11.4')
listed = set()
for line in tab[s:e3].split('\n'):
    if line.startswith('| ') and not line.startswith('| 입력') and not line.startswith('|---'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        listed |= set(re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[1]))
print('\n===== 폐포(A) 안 계산 진술 가운데 11.3 계산 열에 없는 것:')
for x in sorted(comp - listed): print('  ', x, '|', idx[x][4][:200], '| 첫째' if x in c1 else '', '| 둘째' if x in c2 else '')
print('===== 11.3 계산 열에 있으나 폐포(A)에 없는 것:', sorted(listed - (c1|c2)))
print('===== 11.3 계산 열에 있으나 머리에 「계산」이 없는 것:', sorted(x for x in listed if x in idx and '계산' not in idx[x][4]))
# 문헌 인용 덧붙임이 있는 진술 가운데 폐포 안의 것
print('\n===== 폐포 안 「문헌 인용」 진술:', sorted(x for x in (c1|c2) if x in idx and '문헌 인용' in idx[x][4]))
print('===== 3:old-3-6 인용:', sorted(cites.get('3:old-3-6', [])), '| 3장 폐포 진술:', sorted(x for x in (c1|c2) if x.startswith('3:')))
