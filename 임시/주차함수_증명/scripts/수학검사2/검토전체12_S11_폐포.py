# S11: 두 증명(정리 9:old-7-46, 정리 10:old-8-37)이 진술 단위로 거슬러 올라가며 만나는 진술의 집합(폐포)을 세고,
# 11.3절 세 표의 분류(공유/첫째 고유/둘째 고유)와 견준다. 변형 A: 진술 머리+증명만. 변형 B: 앞선 준비 문단(뒤 문단)도 다음 진술에 귀속.
import re, io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HDR = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|관찰)\s+\{\{(\d+[AB]?:[^}]+)\}\}')
LAB = re.compile(r'\{\{(\d+[AB]?:[^}]+)\}\}')
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
citesA = collections.defaultdict(set); citesB = collections.defaultdict(set)
pending = []  # 뒤 문단 lines awaiting next header
for ch in files:
    cur = None; state = None
    for line in open(f'장v2/{ch}.md', encoding='utf-8'):
        m = HDR.match(line)
        if line.startswith('#'):
            pending = []  # 절 경계에서 끊음
            continue
        if m:
            cur = m.group(2); state = 'stmt'
            labs = set(LAB.findall(line)) - {cur}
            citesA[cur] |= labs; citesB[cur] |= labs
            for pl in pending: citesB[cur] |= set(LAB.findall(pl)) - {cur}
            pending = []
            continue
        if cur is None: continue
        labs = set(LAB.findall(line)) - {cur}
        if state in ('stmt', 'proof'):
            citesA[cur] |= labs; citesB[cur] |= labs
            if '∎' in line and (state == 'proof' or re.search(r'증명', line)):
                state = 'after'
            elif re.match(r'^\*\*.*증명', line):
                state = 'proof'
        else:
            pending.append(line)
def closure(root, cites):
    seen = set(); stack = [root]
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x)
        stack.extend(cites.get(x, ()))
    return seen
for name, cites in [('A(진술+증명)', citesA), ('B(+준비 문단)', citesB)]:
    c1 = closure('9:old-7-46', cites); c2 = closure('10:old-8-37', cites)
    c1 = {x for x in c1 if not x.startswith('D:')}; c2 = {x for x in c2 if not x.startswith('D:')}
    print(f'\n===== 변형 {name}: 첫째 {len(c1)} 둘째 {len(c2)} 공유 {len(c1&c2)}')
    tab = open('장v2/장11.md', encoding='utf-8').read()
    s = tab.index('**공유 입력.**'); e1 = tab.index('**첫째 증명의 고유 입력.**'); e2 = tab.index('**둘째 증명의 고유 입력.**'); e3 = tab.index('### 11.4')
    def firstcol(block):
        out = set()
        for line in block.split('\n'):
            if line.startswith('| ') and not line.startswith('| 입력') and not line.startswith('|---'):
                cells = line.split(' | ')
                out |= set(LAB.findall(cells[0]))
        return out
    shared = firstcol(tab[s:e1]); only1 = firstcol(tab[e1:e2]); only2 = firstcol(tab[e2:e3])
    print('표 공유 입력 가운데 첫째 폐포에 없음:', sorted(shared - c1))
    print('표 공유 입력 가운데 둘째 폐포에 없음:', sorted(shared - c2))
    print('표 첫째 고유 가운데 둘째 폐포에 있음:', sorted(only1 & c2))
    print('표 첫째 고유 가운데 첫째 폐포에 없음:', sorted(only1 - c1))
    print('표 둘째 고유 가운데 첫째 폐포에 있음:', sorted(only2 & c1))
    print('표 둘째 고유 가운데 둘째 폐포에 없음:', sorted(only2 - c2))
    both = c1 & c2
    listed = shared | only1 | only2
    pre = {x for x in both if not x.startswith(('9:', '10:'))}
    print('폐포 공유(9·10장 밖) 가운데 표 어디에도 없음:', sorted(pre - listed))
    o1 = {x for x in (c1 - c2) if not x.startswith(('9:', '10:'))}
    print('첫째만 폐포(9·10장 밖) 가운데 표 어디에도 없음:', sorted(o1 - listed))
    o2 = {x for x in (c2 - c1) if not x.startswith(('9:', '10:'))}
    print('둘째만 폐포(9·10장 밖) 가운데 표 어디에도 없음:', sorted(o2 - listed))
    # 어느 길로 닿는지: 9·10장 밖 입력에 대해 직접 인용하는 9·10·7B 진술
    if name.startswith('A'):
        import json
        json.dump({k: sorted(v) for k, v in citesA.items()}, open('scripts/수학검사2/_S11_citesA.json', 'w', encoding='utf-8'), ensure_ascii=False)
